# 로깅: structlog 커스텀 로거

`dev_principle` 스킬의 참조 문서. 새 프로젝트에 로거를 세우거나 기존 로깅을 옮길 때 읽는다.

## 원칙

- 로깅 설정은 `common/logger.py` 한 파일이 전부 가진다. `assets/logger.py` 를 그대로 복사해 시작한다.
- 각 모듈은 `logger = get_logger(__name__)` 한 줄로 로거를 받는다.
- `print`, `logging.basicConfig`, 모듈마다 따로 붙인 핸들러를 쓰지 않는다. 기존 코드에 있으면 옮긴다.
- structlog 로 키와 값을 남긴다. 메시지 문자열에 값을 끼워 넣지 않는다.

```python
logger.info("post_published", post_id=post.id, author_id=post.author_id)   # 좋음
logger.info(f"post {post.id} published by {post.author_id}")              # 나쁨: 검색도 마스킹도 안 된다
```

이벤트 이름은 `<대상>_<과거형 동사>` 로 쓴다. `post_published`, `payment_failed`, `graph_node_finished`.

## 템플릿이 하는 일

`assets/logger.py` 는 아래를 처리한다. 고칠 때 이 성질을 깨지 않는다.

| 성질 | 방법 |
|---|---|
| 몇 번 불러도 한 번만 설정 | `_configured` 플래그, 루트 핸들러를 덧붙이지 않고 교체 |
| 개발은 rich 콘솔, 운영은 JSON | `LOG_FORMAT=console` 또는 `json`. 기본 `console` |
| 레벨 | `LOG_LEVEL`. 기본 `INFO` |
| 표준 logging 로그도 같은 형식 | `ProcessorFormatter` 로 uvicorn, httpx, LangGraph 로그를 같은 처리기에 태운다 |
| 비밀값 마스킹 | `SENSITIVE_KEYS` 에 있는 키를 중첩 dict 까지 `***` 로 바꾼다 |
| 트레이스백의 지역 변수 숨김 | JSON 과 rich 모두 `show_locals=False` |
| 요청 문맥 | `structlog.contextvars.merge_contextvars` |

운영 환경 Dockerfile 이나 compose 에 `LOG_FORMAT=json` 을 둔다. 개발 환경의 rich 출력은 사람이 읽기 위한 것이고, JSON 은 수집기가 읽고 값 안의 줄바꿈으로 로그 줄을 위조할 수 없다.

의존성: `uv add structlog`, 개발 환경 rich 출력에는 `uv add --dev rich`. rich 가 없으면 콘솔 렌더러가 기본 트레이스백으로 출력한다.

## 요청 문맥 묶기

요청 ID 처럼 한 요청 안의 모든 로그에 붙어야 하는 값은 미들웨어에서 묶고 요청이 끝나면 지운다.

```python
@app.middleware("http")
async def bind_request_context(request: Request, call_next: RequestResponseEndpoint) -> Response:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request.headers.get("x-request-id") or str(uuid4()))
    return await call_next(request)
```

LangGraph 실행에는 `thread_id` 를 같은 방식으로 묶는다. 함수 인자로 로거나 ID 를 끌고 다니지 않는다.

## 무엇을 남기고 무엇을 남기지 않나

남긴다:

- 외부 호출의 시작과 끝, 소요 시간, 결과 코드
- 인증과 권한 실패
- 에이전트 도구 호출: 도구 이름, 마스킹된 인자, 사용자 ID
- 예외: `logger.exception(...)` 으로. 예외를 삼키는 곳에는 반드시 로그를 남긴다

남기지 않는다:

- 요청 헤더 원문, 요청 본문 전체, 프롬프트 전문, LLM 출력 전문. ID, 길이, 해시로 대신한다
- 개인정보. 필요하면 마스킹하거나 해시한다

마스킹은 키 이름으로만 동작한다. `logger.info("login", password=pw)` 는 가려지지만 `logger.info(f"pw={pw}")` 와 표준 logging 의 `%s` 포맷 문자열 안의 값은 가려지지 않는다. 값을 키로 넘겨야 하는 또 하나의 이유다. 프로젝트에 새 민감 키(예: `resident_number`)가 생기면 `SENSITIVE_KEYS` 에 추가한다.

## 테스트

로거 자체의 단위 테스트는 `tests/unit/test_common_logger.py` 하나로 충분하다. 두 가지만 확인한다.

- `configure_logging()` 을 두 번 불러도 루트 핸들러가 하나다
- `password` 키로 넘긴 값이 렌더링된 출력에 나오지 않는다

## uvicorn 과 함께 쓸 때

uvicorn 은 자기 로거에 별도 핸들러를 붙인다. 출력이 두 형식으로 섞이면 `uvicorn.run(..., log_config=None)` 으로 띄워 루트 핸들러 하나로 모은다.
