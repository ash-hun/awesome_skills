# 경계 층: 요청·이벤트·외부 호출

HTTP 핸들러, 큐 컨슈머, 웹훅 수신, 외부 시스템 호출을 다룬다.

이 층의 전제는 하나다. **네트워크 너머의 상대는 언제든 같은 것을 두 번 보낸다.** 클라이언트 재시도, 로드밸런서 타임아웃 후 재전송, 메시지 큐의 at-least-once 보장, 사용자의 더블클릭, 결제사의 웹훅 재전송. 이건 예외 상황이 아니라 정상 동작이다.

그래서 "중복이 오면 어쩌지"가 아니라 **"중복은 온다, 두 번째를 어떻게 처리할 것인가"** 로 설계한다.

---

## HTTP 메서드의 계약

| 메서드 | 멱등한가 | 의미 |
|---|---|---|
| GET, HEAD | 예 | 상태를 안 바꾼다 |
| PUT | 예 | "이 리소스를 이 상태로 만들어라" |
| DELETE | 예 | "이 리소스가 없는 상태로 만들어라" |
| POST | **아니오** | "이 컬렉션에 새로 만들어라" |

이건 관례가 아니라 **계약**이다. 클라이언트 라이브러리, 프록시, 브라우저가 이 계약을 믿고 GET/PUT/DELETE를 자동 재시도한다. 그러니 계약을 지켜라 — 상태를 바꾸는 GET을 만들면 프리페치나 크롤러가 그걸 실행시킨다.

**DELETE는 없는 것을 지울 때 성공으로 응답한다.** 목표 상태("없음")에 이미 도달했기 때문이다. 404를 주면 클라이언트가 재시도 중 에러를 보고 실패로 오인한다.

```python
@router.delete("/orders/{order_id}")
def delete_order(order_id: str, session=Depends(get_session)):
    session.execute(delete(Order).where(Order.id == order_id))
    session.commit()
    return Response(status_code=204)   # 있었든 없었든 204
```

**생성이 본질적으로 POST라면** 아래 idempotency key로 멱등성을 얹는다.

---

## Idempotency Key

클라이언트가 요청마다 고유 키를 생성해 보내고, 서버는 그 키로 "이미 처리한 요청인가"를 판단한다. Stripe 등 결제 API의 표준 패턴이다.

```python
@router.post("/payments")
def create_payment(
    body: PaymentRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session=Depends(get_session),
):
    # 1. 키를 먼저 선점한다. 유니크 제약이 동시 요청을 하나만 통과시킨다.
    inserted = session.execute(
        insert(IdempotencyRecord)
        .values(key=idempotency_key, status="in_progress")
        .on_conflict_do_nothing(index_elements=["key"])
        .returning(IdempotencyRecord.key)
    ).first()

    if inserted is None:
        # 2. 이미 있는 키 — 저장된 응답을 그대로 돌려준다
        record = session.get(IdempotencyRecord, idempotency_key)
        if record.status == "in_progress":
            return Response(status_code=409)   # 아직 처리 중, 나중에 재시도하라
        return JSONResponse(record.response, status_code=record.status_code)

    # 3. 실제 처리
    result = charge(body)
    record = session.get(IdempotencyRecord, idempotency_key)
    record.status, record.response, record.status_code = "done", result.dict(), 201
    session.commit()
    return JSONResponse(result.dict(), status_code=201)
```

**설계 포인트 세 가지:**

1. **선점을 먼저 한다.** "조회 후 없으면 처리"로 짜면 동시 요청 두 개가 둘 다 통과한다. `on_conflict_do_nothing` + 유니크 제약이 실질적 잠금 역할을 한다.
2. **응답을 저장한다.** 두 번째 요청에 "이미 처리됨"이 아니라 **첫 번째와 똑같은 응답**을 준다. 클라이언트는 자기 요청이 성공했는지만 알면 되고, 재시도인지 아닌지 구분할 필요가 없다.
3. **키에 TTL을 둔다.** 무한히 쌓이면 테이블이 터진다. 24시간~7일이 흔한 선택이고, 클라이언트 재시도 창보다 넉넉하면 된다.

**키를 누가 만드는가:** 클라이언트가 만든다. 서버가 요청 본문 해시로 만들면 "의도적으로 같은 결제를 두 번" 하는 정당한 경우를 막아버린다. 사용자가 같은 금액을 두 번 결제할 수도 있다.

---

## 중복 이벤트 (큐·웹훅)

대부분의 메시지 큐(SQS, Kafka, Pub/Sub)는 **at-least-once**를 보장한다. "정확히 한 번"은 대개 마케팅 문구이거나 무거운 제약이 붙는다. 컨슈머가 중복을 흡수한다고 가정하고 짜라.

```python
def handle_payment_succeeded(event: dict, session):
    event_id = event["id"]

    # 처리 기록을 먼저 선점 — 통과 못 하면 이미 처리된 이벤트다
    claimed = session.execute(
        insert(ProcessedEvent)
        .values(event_id=event_id, source="stripe")
        .on_conflict_do_nothing(index_elements=["event_id"])
        .returning(ProcessedEvent.event_id)
    ).first()

    if claimed is None:
        return   # 이미 처리됨 — 조용히 성공 응답. 재전송을 멈추게 한다.

    apply_payment(session, event["data"])
    session.commit()   # 처리 기록과 실제 변경이 같은 트랜잭션이다
```

**핵심은 마지막 줄이다.** 처리 기록(`ProcessedEvent`)과 실제 상태 변경이 **같은 트랜잭션**에 있어야 한다. 따로 커밋하면 "기록은 됐는데 처리는 안 된" 상태가 생기고, 재전송이 와도 걸러져서 영영 처리되지 않는다.

**웹훅 응답 코드:** 중복이라 무시했어도 **2xx를 돌려줘라.** 4xx/5xx를 주면 발신자가 계속 재전송한다. "이미 처리했다"는 발신자 입장에서 성공이다.

**자연 멱등 연산을 선호해라.** 처리 기록 테이블 없이 끝낼 수 있으면 그게 더 낫다.

```python
# 재실행에 취약 — 두 번 오면 두 번 더해진다
user.points += event["points"]

# 자연 멱등 — 몇 번을 적용해도 같다
user.tier = event["tier"]
```

증가(`+=`)는 멱등하지 않고, 대입(`=`)은 멱등하다. 이벤트 페이로드를 설계할 수 있는 입장이라면 "얼마 늘려라"보다 "최종값은 이것이다"를 보내게 만들어라.

---

## 커밋 전에 죽는 문제

가장 다루기 까다로운 지점이다. 외부 API를 호출하고 그 결과를 DB에 쓰기 직전에 프로세스가 죽으면, **외부 세계는 바뀌었는데 우리는 그 사실을 모른다.** 재실행하면 외부 호출이 한 번 더 일어난다.

DB 트랜잭션은 외부 API를 롤백해주지 않는다. 해결책은 세 가지다.

**1. 외부 시스템이 idempotency key를 지원하면 그걸 써라.** 가장 깔끔하다. 재실행 시 같은 키를 보내면 상대가 알아서 중복을 막는다. 이때 키는 **재실행해도 같아야 하므로** 요청 시점에 만들어 저장해두고, 재시도 때 다시 읽어 쓴다 (`uuid4()`를 호출 직전에 만들면 재실행마다 달라진다).

```python
# 1단계: 의도를 먼저 기록한다 (키 포함)
attempt = PaymentAttempt(order_id=order_id, idem_key=str(uuid4()), status="pending")
session.add(attempt); session.commit()

# 2단계: 외부 호출 — 여기서 죽어도 attempt에 키가 남아 있다
result = gateway.charge(amount, idempotency_key=attempt.idem_key)

# 3단계: 결과 확정
attempt.status, attempt.external_id = "done", result.id
session.commit()
```

재실행 시 `status == "pending"`인 attempt를 찾아 **같은 키로** 다시 호출하면, 상대가 첫 호출의 결과를 돌려준다.

**2. 조회로 확인할 수 있으면 확인해라.** 외부 API에 "이 주문 ID로 결제된 게 있나?"를 물을 수 있다면, 호출 전에 조회해서 건너뛴다. 조회와 호출 사이에 여전히 틈이 있지만 창이 훨씬 좁아진다.

**3. 둘 다 안 되면 사용자에게 알려라.** 어떤 외부 시스템은 멱등성을 지원하지 않고 조회도 안 된다. 이건 코드로 해결되는 문제가 아니다. 그 지점을 주석으로 명시하고, 중복이 발생했을 때 어떻게 감지·정정할지(정산 배치, 알림)를 사용자와 함께 정해라. **조용히 위험을 남기지 마라.**

---

## 이 층의 체크리스트

- [ ] 상태를 바꾸는 엔드포인트에 같은 요청을 두 번 보내면 어떻게 되는가?
- [ ] 중복 방지가 애플리케이션 코드에만 있고 유니크 제약이 없지 않은가?
- [ ] 처리 기록과 실제 상태 변경이 같은 트랜잭션에 있는가?
- [ ] 웹훅/컨슈머가 중복을 만났을 때 2xx로 응답하는가?
- [ ] DELETE가 없는 리소스에 대해 성공을 돌려주는가?
- [ ] 외부 호출 직후~커밋 직전에 죽는 경로를 짚었는가? 대책이 셋 중 무엇인가?
- [ ] idempotency key가 재실행 시에도 같은 값인가? (호출 직전 생성이 아닌가)
