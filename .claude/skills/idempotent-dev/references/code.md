# 코드 층: 부수효과 격리와 모듈 분리

도메인 로직, 데이터 변환, 서비스/유스케이스 클래스, 배치 처리를 다룬다.

이 층의 멱등성은 DB 문법이 아니라 **설계**로 얻는다. 핵심 구조는 하나다: **결정하는 코드와 세상을 바꾸는 코드를 분리한다.** 결정 코드는 몇 번을 불러도 같은 답을 내므로 자동으로 멱등하고, 세상을 바꾸는 코드는 얇고 적어서 하나씩 멱등하게 만들 수 있다.

---

## 순수한 핵심, 얇은 껍질

부수효과를 경계로 밀어내고 가운데를 순수하게 유지한다. 이 구조에서는 "이거 두 번 불러도 되나?"라는 질문이 **경계에 있는 소수의 함수에만** 적용된다.

```python
# ── 순수 핵심: I/O 없음, 같은 입력 → 항상 같은 출력 ──────────────
@dataclass(frozen=True)
class PricedOrder:
    order_id: str
    subtotal: Decimal
    discount: Decimal
    total: Decimal

def price_order(items: list[Item], coupon: Coupon | None) -> PricedOrder:
    subtotal = sum(i.price * i.qty for i in items)
    discount = coupon.apply(subtotal) if coupon else Decimal(0)
    return PricedOrder(..., total=subtotal - discount)

# ── 얇은 껍질: I/O만, 로직 없음 ────────────────────────────────
def finalize_order(session, order_id: str, coupon_code: str | None) -> PricedOrder:
    items = load_items(session, order_id)
    coupon = load_coupon(session, coupon_code) if coupon_code else None
    priced = price_order(items, coupon)          # 순수
    save_pricing(session, priced)                # 멱등 (upsert)
    return priced
```

**이 구조의 실질적 이득:**
- `price_order`는 DB 없이 테스트된다. 쿠폰 조합 20가지를 20줄로 검증할 수 있다.
- 재실행 안전성 검토 대상이 `save_pricing` 하나로 줄어든다.
- 로직이 바뀌어도 I/O 코드를 안 건드린다.

**언제 이 구조가 과한가:** 함수 하나짜리 CRUD, 로직이 없는 조회 엔드포인트. 분리할 결정이 없으면 분리하지 마라. 이건 원칙이지 의식이 아니다.

---

## 결정론을 깨는 것들

같은 입력에 같은 출력이 나오지 않으면 순수 함수가 아니고, 테스트도 재실행도 불안정해진다. 아래는 조용히 결정론을 깨는 흔한 원인이다.

```python
# 나쁨 — 호출 시점에 따라 결과가 달라진다
def make_receipt(order):
    return Receipt(id=uuid4(), issued_at=datetime.now(), total=order.total)

# 좋음 — 비결정적 값은 경계에서 만들어 주입한다
def make_receipt(order, receipt_id: str, issued_at: datetime):
    return Receipt(id=receipt_id, issued_at=issued_at, total=order.total)
```

주입하면 테스트에서 고정값을 넣을 수 있고, 재시도할 때 **같은 ID를 다시 넘겨** 중복 생성을 막을 수 있다. 이게 API 층의 idempotency key와 이어지는 지점이다 (`api.md` 참고).

같은 이유로 조심할 것: `random`, `time.time()`, 환경변수 직접 읽기, 전역 설정 객체, 딕셔너리 순회 순서에 의존하는 로직.

---

## 상태를 숨기지 마라

모듈 수준 가변 상태와 캐시는 "같은 입력 → 같은 출력"을 조용히 깬다. 첫 호출과 두 번째 호출의 결과가 달라지는데, 함수 시그니처만 봐서는 알 수 없다.

```python
# 나쁨 — 전역 캐시. 두 번째 호출은 DB를 안 본다. 테스트 간에 상태가 샌다.
_config_cache = {}
def get_config(key):
    if key not in _config_cache:
        _config_cache[key] = db.query(Config).get(key)
    return _config_cache[key]

# 좋음 — 캐시가 명시적 의존성이다. 교체·초기화·비활성화가 가능하다.
class ConfigService:
    def __init__(self, session, cache: dict | None = None):
        self._session = session
        self._cache = cache if cache is not None else {}

    def get(self, key):
        if key not in self._cache:
            self._cache[key] = self._session.query(Config).get(key)
        return self._cache[key]
```

캐시 자체가 문제가 아니라 **숨어 있는 것**이 문제다. 생성자로 드러나면 테스트에서 빈 딕셔너리를 넘기면 되고, 무효화 시점도 소유자가 결정한다.

`functools.lru_cache`도 같은 함정이다. 순수 함수에 붙이면 안전하고, DB나 파일을 읽는 함수에 붙이면 프로세스 수명 내내 낡은 값을 잡고 있는다.

---

## class와 함수의 경계

**함수로 충분한 경우:** 입력을 받아 결과를 내는 것 이상을 하지 않을 때. 대부분의 도메인 로직이 여기 해당한다.

**class가 맞는 경우:**
- 여러 메서드가 같은 의존성(DB 세션, HTTP 클라이언트, 설정)을 공유한다
- 생애주기 동안 유지되는 상태가 있다
- 같은 인터페이스의 구현이 여러 개다 (결제사 A/B, 로컬/S3 저장소)

**class인데 함수여야 하는 신호:**
- 메서드가 하나뿐이고 이름이 `run` / `execute` / `process`다
- 모든 메서드가 `self`를 안 쓴다 (`@staticmethod` 모음)
- `__init__`이 비어 있거나 인자를 그대로 필드에 넣기만 한다

```python
# 과하다 — 상태도 의존성도 없다
class TotalCalculator:
    def calculate(self, items):
        return sum(i.price * i.qty for i in items)

# 이걸로 충분하다
def calculate_total(items) -> Decimal:
    return sum(i.price * i.qty for i in items)
```

**데이터 묶음에는 `@dataclass(frozen=True)`를 우선 고려해라.** 불변이면 "이 객체가 도중에 바뀌었나?"를 걱정할 필요가 없어지고, 이는 재실행 안전성 추론을 크게 단순화한다.

---

## 파일과 디렉토리

목적으로 나눈다. 종류로 나누지 않는다.

```
# 종류별 — 기능 하나 고치는 데 5개 파일을 연다
models.py  schemas.py  services.py  routers.py  utils.py

# 목적별 — 기능의 멱등성을 한 디렉토리에서 검증한다
order/      __init__.py  models.py  pricing.py  repository.py  router.py
payment/    __init__.py  models.py  gateway.py  repository.py  router.py
```

목적별 구조의 실질적 이점은 **부수효과의 지역성**이다. "주문 관련 상태를 바꾸는 코드가 어디 있나?"의 답이 `order/repository.py` 하나로 좁혀진다. 종류별 구조에서는 `services.py` 2000줄을 훑어야 한다.

`utils.py`가 커지면 그 안에 이름 없는 도메인 개념이 있다는 뜻이다. 함수 3~4개가 같은 주제를 다루면 그 주제로 모듈을 만들어 옮겨라.

---

## 배치 처리

배치는 중간에 죽는 게 정상이라고 가정해라. 10만 건 중 4만 건에서 죽었을 때 처음부터 다시 돌려도 안전해야 한다.

```python
def process_pending(session, batch_size=500):
    while True:
        rows = (session.query(Job)
                .filter(Job.status == "pending")
                .limit(batch_size).all())
        if not rows:
            break
        for row in rows:
            result = compute(row.payload)         # 순수
            row.result, row.status = result, "done"   # 상태 전이가 진행 표시다
        session.commit()                          # 배치 단위 커밋
```

**핵심은 "무엇이 남았는지"를 데이터가 스스로 말하게 하는 것이다.** `status == "pending"` 조회가 곧 재개 지점이므로 별도의 체크포인트 파일이 필요 없다. 오프셋이나 카운터를 외부에 저장하면 그게 또 다른 동기화 대상이 된다.

**주의:** `compute`가 외부 API를 호출한다면 커밋 전에 죽었을 때 그 호출은 이미 일어난 상태다. 이 경계는 `api.md`의 "커밋 전 죽는 문제"에서 다룬다.
