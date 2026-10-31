# 코드 규칙

`dev_principle` 스킬의 참조 문서. 코드를 쓰거나 고칠 때, refactor 모드에서는 항상 읽는다. 지은 코드가 어떤 모양이어야 하는지를 정한다.

Python 이 아닌 코드(프론트엔드 등)에는 호출 계층, 공통 모듈, 파일 최상단 주석, 주석 규칙을 적용한다. 타입 힌트, pytest, mypy, uv, FastAPI 처럼 Python 에 묶인 항목은 적용하지 않는다.

## 목차

- 호출 계층과 모듈명
- import 순서
- 함수와 모듈의 경계
- 멱등성과 공통 모듈
- 타입 힌트
- 객체화와 상속
- 파일 최상단 주석
- 상수와 주석
- 도구
- OpenAPI 문서

## 호출 계층과 모듈명

기준은 하나다. **import 경로만 읽고 그 모듈의 역할을 알 수 있어야 한다.** `from app.repository.post_repository import PostRepository` 는 파일을 열지 않아도 게시글을 저장소에서 읽고 쓰는 모듈임을 알 수 있다. `from app.utils import helper` 는 아무것도 알려주지 않는다.

디렉토리 이름이 층을, 파일 이름이 대상과 역할을 말하게 한다.

```
app/
├── main.py                    # 조립만 한다. 업무 로직 없음
├── api/                       # 진입 층: 요청 해석, 응답 변환
│   └── post_router.py
├── service/                   # 업무 층: 규칙과 흐름
│   └── post_service.py
├── agent/                     # LangGraph 그래프, 노드, 도구
│   └── summary_graph.py
├── repository/                # 저장 층: DB 와 파일 접근
│   └── post_repository.py
├── client/                    # 외부 시스템 연동 (LLM 포함)
│   └── mail_client.py
├── schema/                    # 요청과 응답 모델
│   └── post_schema.py
└── common/                    # 모든 층이 쓰는 공통 모듈
    ├── logger.py
    └── settings.py
```

프로젝트가 이미 다른 층 이름을 쓰고 있으면(`routers`, `domain`, `infra` 등) 그 이름을 따른다. 위 트리는 층 이름이 없을 때의 기본값이다. 층은 필요한 것만 만든다. 에이전트가 없으면 `agent/` 는 없다.

의존 방향은 한쪽으로만 흐른다.

- `api` 는 `service` 를 부른다. `repository`, `client`, `agent` 를 직접 부르지 않는다.
- `service` 는 `agent`, `repository`, `client` 를 부른다. `api` 를 import 하지 않는다.
- `agent` 는 `repository`, `client` 를 부를 수 있다. `api`, `service` 를 import 하지 않는다.
- `repository` 와 `client` 는 위 층을 import 하지 않는다.
- `common` 은 어느 층에서나 import 할 수 있고, `common` 자신은 어떤 층도 import 하지 않는다.
- `schema` 는 다른 층의 로직을 import 하지 않는다.

순환을 피하려고 함수 안에 넣은 지연 import 도 역방향 의존으로 본다. 작업을 끝내기 전에 아래 층 디렉토리에서 위 층을 import 하는 줄을 grep 해서 결과가 비어 있는지 확인한다.

이름 규칙:

- 파일 이름은 `<대상>_<역할>.py` 로 쓴다. `post_service.py`, `post_repository.py`, `mail_client.py`, `summary_graph.py`.
- `utils.py`, `helpers.py`, `misc.py`, `manager.py`, `handler.py` 처럼 역할을 말하지 않는 이름을 쓰지 않는다. 그런 파일이 이미 있으면 안의 내용을 역할별로 나눠 제자리에 보낸다.
- 클래스 이름은 파일 이름과 맞춘다. `post_service.py` 에는 `PostService`.
- 같은 대상은 모든 층에서 같은 낱말로 부른다. 한 층에서 `post`, 다른 층에서 `article` 이면 경로만으로 연결을 읽을 수 없다. 이 낱말은 `features.md` 의 기능 ID, 테스트 파일명과도 같다.

## import 순서

두 그룹으로 나눈다. 외부(표준 라이브러리와 서드파티)를 위에 모아 **줄 길이 오름차순**, 한 줄 띄고, 로컬 참조를 **줄 길이 내림차순**.

```python
import yaml
from pathlib import Path
from dataclasses import dataclass

from app.repository.post_repository import PostRepository
from app.common.logger import get_logger
from app.schema.post_schema import Post
```

길이순은 취향이 아니라 프로젝트 합의다. 정렬 규칙이 하나로 고정돼 있으면 import 블록의 diff 가 의미 있는 변경만 담는다. 길이가 같으면 알파벳순.

- 쓰지 않는 import 는 넣지 않는다.
- `from __future__ import annotations` 를 습관으로 붙이지 않는다. 지원 하한이 3.10 이상이면 `X | None` 이 그냥 동작한다. 넣기 전에 묻는다. 이 줄을 지우면 무엇이 깨지는가?
- 와일드카드 import(`from x import *`)를 쓰지 않는다.

## 함수와 모듈의 경계

**함수 하나는 결정 하나, 또는 부수효과 하나.** 둘 다 하지 않는다. 계산과 I/O 가 섞이면 테스트할 때마다 DB 가 필요해지고, 두 번 불러도 되는지에 답할 수 없다.

```python
def calculate_total(items: list[OrderItem]) -> Decimal:
    total = sum(i.price * i.qty for i in items)
    return total * Decimal("0.9") if total > 100_000 else total


def apply_order_total(order_id: int, total: Decimal) -> None:
    db.execute(update(Order).where(Order.id == order_id).values(total=total))
```

이 경계가 atomic 모듈의 경계다. 단위 테스트는 이 단위에 붙고, 통합 테스트는 이 단위들을 이은 파이프라인에 붙는다.

## 멱등성과 공통 모듈

모든 모듈은 두 번 실행해도 한 번 실행한 것과 같은 상태가 되어야 한다. 층별 기법은 `references/idempotency-*.md`.

- import 시점에 부작용을 일으키지 않는다. 모듈 최상위에서 DB 연결, 파일 생성, 네트워크 호출을 하지 않는다. 그런 일은 명시적으로 부르는 함수나 생성자 안에 둔다.
- 초기화, 기동, 시드는 맞추는 방식으로 쓴다. `CREATE TABLE IF NOT EXISTS`, `mkdir(exist_ok=True)`, upsert.
- `uuid4()`, `datetime.now()`, `random` 은 결정 로직 안에서 부르지 않는다. 경계에서 만들어 주입한다.

재사용되는 것은 `common` 으로 모은다.

- 두 곳 이상에서 쓰는 코드가 대상이다. 한 곳에서만 쓰는 코드를 미리 옮기지 않는다.
- 특정 도메인을 아는 코드는 `common` 에 넣지 않는다.
- **logger 는 반드시 `common/logger.py` 의 structlog 커스텀 로거를 쓴다.** `assets/logger.py` 를 복사해 시작하고, 규칙은 `references/logging.md`.
- **설정은 `common/settings.py` 하나에서 읽는다.** `pydantic-settings` 로 환경변수를 받고 비밀값은 `SecretStr`.

## 타입 힌트

모든 함수와 메서드의 인자와 반환값에 타입 힌트를 붙인다. 예외 없이 필수다.

- 반환값이 없으면 `-> None` 을 쓴다. 생략하지 않는다.
- 컨테이너는 원소 타입까지 쓴다. `list[Post]`, `dict[str, int]`.
- 구조가 정해진 dict 를 주고받지 않는다. dataclass, pydantic 모델, `TypedDict` 로 바꾼다.
- 값이 없을 수 있으면 `Post | None` 으로 드러낸다.
- `Any` 는 피한다. 써야 하면 이유를 주석으로 남긴다.
- `# type: ignore` 는 오류 코드를 지정하고 이유를 적는다. `# type: ignore[import-untyped]  # 스텁 없는 라이브러리`.
- 클래스 속성과 모듈 수준 상수에도 타입을 붙인다.

`uv run mypy` 로 확인한다. 손댄 모듈에서 오류 0.

## 객체화와 상속

기능 단위로 적극적으로 객체로 묶는다.

- 상태와 그 상태를 다루는 함수들이 함께 다니면 클래스로 만든다. 같은 인자(`db`, `settings`, `client`)를 여러 함수가 반복해서 받고 있으면 그 인자가 생성자로 가야 한다는 신호다.
- 의존(DB 세션, 설정, 외부 클라이언트, LLM)은 생성자로 주입한다. 모듈 전역을 직접 참조하지 않는다. 테스트에서 mock 으로 바꿔 끼우는 경로가 이것이다.
- 함께 다니는 값 묶음은 dataclass 나 pydantic 모델로 만든다. 튜플과 dict 로 넘기지 않는다.
- 상태도 의존도 없는 순수한 변환은 함수로 둔다. 객체화의 목적은 상태와 의존을 한곳에 모으는 것이다. `__init__` 이 비어 있고 메서드가 `self` 를 쓰지 않는 클래스는 함수로 내린다.

추상화의 단위는 "무엇을 하는가"다.

- 저장한다, 조회한다, 알림을 보낸다, 본문을 변환한다 같은 기능 하나가 클래스나 메서드 하나의 경계가 된다. 부르는 쪽은 그 기능의 이름만 알고 내부 절차를 알지 못해야 한다.
- 여러 곳에 흩어진 같은 기능은 한 객체로 끌어올린다.
- 이름은 기능을 말한다. `PostRepository.find_published()` 는 무엇을 하는지 말하고, `PostRepository.run_query(sql)` 은 어떻게 하는지를 호출자에게 떠넘긴다.

**추상 클래스는 쓰지 않는다.** `ABC` 와 `@abstractmethod` 로 몸통 없는 뼈대를 먼저 세우지 않는다. 타입 약속만을 위한 `typing.Protocol` 도 같은 기준이다.

- 공통 동작은 실제로 동작하는 구현을 가진 구체 클래스에 둔다. 예: `BaseRepository` 가 공통 조회와 저장을 직접 구현하고 `PostRepository` 가 상속해 자기 기능만 더한다.
- 주입받는 객체의 타입은 그 구체 클래스로 적는다. 테스트의 대체 객체는 그 구체 클래스를 상속하거나 `create_autospec` 으로 만든다.
- 추상 클래스가 꼭 필요하다고 판단되면 아키텍처 단계 승인에 이유와 함께 올린다.

상속은 "A 는 B 의 한 종류다"가 성립할 때만 쓴다. 깊이는 1에서 2(`object` 는 세지 않는다). 3 이상이 필요해 보이면 조합으로 푼다. 하위 클래스가 메서드를 재정의할 때 인자와 반환 타입을 바꾸지 않는다.

## 파일 최상단 주석

모든 `.py` 파일의 첫머리에 모듈 docstring 을 쓴다. 내용은 **전체 프로젝트 관점에서 이 모듈이 무엇인지**다. **최대 2줄.**

- 첫 줄: 어느 층에서 무엇을 맡는가
- 필요하면 다음 줄: 누가 부르고 무엇을 부르는가, 헷갈리기 쉬운 하지 않는 일

```python
"""게시글 공개 규칙을 맡는 업무 층 모듈.
post_router 가 부르고 저장은 post_repository 에 맡긴다. HTTP 형태는 모른다."""
```

- 함수와 클래스 목록, 작성 날짜, 작성자, 변경 이력을 넣지 않는다.
- 2줄로 안 담기면 파일이 두 가지 일을 하고 있다는 신호다. 문장을 늘리지 말고 파일을 나눈다.
- 내용이 없는 `__init__.py` 에도 그 패키지가 어떤 층인지 한 줄을 쓴다.

## 상수와 주석

모듈 상수는 import 직후에 모아 선언하고, 함수 안에 리터럴로 흩뿌리지 않는다. 설정 기본값이 여러 곳에 흩어져 있으면 같은 설정을 두 번 읽으면 같은 값인지를 눈으로 확인할 수 없다.

주석은 왜(why)만 남긴다. 코드가 이미 말하는 것을 한국어로 번역하지 않는다.

```python
# 결제사가 같은 웹훅을 최대 3회 재전송한다. event_id 로 걸러야 중복 적립이 안 생긴다.
if processed_events.contains(event_id):
    return
```

의도적으로 감수한 한계는 `# ponytail:`, 의도적 비멱등은 `# idempotent:` 마커로 남긴다.

## 도구

| 용도 | 도구 | 명령 |
|---|---|---|
| 패키지 관리 | uv | `uv sync`, `uv add <패키지>`, `uv add --dev <패키지>` |
| 테스트 | pytest | `uv run pytest` |
| 정적 검사 | mypy | `uv run mypy <패키지 디렉토리>` |
| 환경 관리 | Docker, Docker Compose | `docker compose up -d`, `docker compose run --rm app uv run pytest` |

Python 프로젝트는 패키지 관리를 uv 로, 환경 관리를 Docker 와 Docker Compose 로 나눈다. 의존성 목록을 정하는 건 uv 이고, 그 의존성이 돌아가는 OS, Python 버전, DB 같은 의존 서비스를 정하는 건 compose 다. pip, poetry, pipenv, conda, pyenv 와 손으로 만든 venv 는 쓰지 않는다.

**uv**

- 의존성은 `pyproject.toml` 에 선언하고 `uv.lock` 을 커밋한다. `requirements.txt` 를 만들지 않는다.
- 프로젝트가 다른 도구를 쓰고 있으면 uv 로 옮긴다. 옮기면서 버전을 올리지 않는다. Dockerfile 과 CI 의 설치 명령도 같이 고친다.
- pytest, mypy 는 개발 의존성으로 넣는다.

**mypy**: 설정은 `pyproject.toml` 의 `[tool.mypy]`.

```toml
[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = true
disallow_incomplete_defs = true
warn_return_any = true
warn_unused_ignores = true
```

`python_version` 은 프로젝트가 실제로 쓰는 버전으로 맞춘다. 스텁이 없는 서드파티 라이브러리는 그 모듈에만 `ignore_missing_imports` 를 건다.

**Docker, Docker Compose**

- 저장소 루트에 `Dockerfile` 과 `compose.yaml` 을 둔다. 앱, DB, 캐시처럼 서비스가 기대는 것은 전부 compose 서비스로 선언한다. 로컬에 DB 를 따로 설치해 쓰지 않는다.
- 이미지 안에서 의존성은 `uv sync --frozen` 으로 설치한다. `pip install` 을 쓰지 않는다.
- 설정은 compose 의 `environment` 나 `env_file` 로 넣는다. 비밀값은 `.env` 로 두고 커밋하지 않는다.
- 이미지 태그에 `latest` 를 쓰지 않는다. 레이어 배치와 헬스체크는 `references/idempotency-setup.md`, 보안 설정은 `references/security.md`.

## OpenAPI 문서

FastAPI 엔드포인트마다 아래 셋을 넣는다.

- **기능 설명**: `summary` 한 줄. 부족할 때만 `description` 한 문장에서 세 문장.
- **인자 설명**: 경로 인자, 쿼리 인자, 본문 필드 각각의 의미.
- **사용 예제**: 요청 예와 응답 예.

설명은 과하지 않게 쓴다.

- 내부 구현(어느 테이블, 어느 클래스)을 쓰지 않는다.
- 이름을 되풀이하는 설명을 쓰지 않는다. `id: 아이디` 대신 `id: 게시글 고유 번호`.
- 인자 설명은 한 줄. 의미, 단위, 허용 범위, 기본값 중 호출자에게 필요한 것만.

```python
class PostCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=120, description="게시글 제목", examples=["첫 글"])
    published: bool = Field(default=False, description="공개 여부. 생략하면 비공개")


@router.get("/posts", summary="게시글 목록 조회", response_model=PostListResponse)
def list_posts(
    tag: str | None = Query(default=None, description="이 태그가 붙은 글만 조회", examples=["python"]),
    limit: int = Query(default=20, ge=1, le=100, description="한 번에 가져올 개수"),
) -> PostListResponse:
    ...
```

- 응답 예는 응답 모델의 `model_config = {"json_schema_extra": {"examples": [...]}}` 나 필드의 `examples` 로 넣는다.
- 예제 값은 실제로 호출이 성공하는 값이어야 한다. 실제 토큰이나 개인정보를 넣지 않는다.
- OpenAPI 설명과 `docs/api_spec.md` 가 같은 사실을 말해야 한다.
