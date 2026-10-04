# 코드 규칙

`refactoring_service` 스킬의 참조 문서. 설계문서가 있든 없든 항상 읽는다.

설계문서와 기본 방안은 **무엇을 어떤 구조로 바꿀지**를 정하고, 이 문서는 **바꾼 코드가 어떤 모양이어야 하는지**를 정한다. 리팩토링으로 손대는 모든 Python 모듈에 적용한다. 기본 방안으로 진행할 때는 대상 서비스의 Python 모듈 전체가 대상이고, 설계문서로 진행할 때는 설계문서가 다루는 모듈이 대상이다. 설계문서의 지시가 이 규칙과 부딪히면 어느 쪽도 임의로 고르지 않고 사용자에게 묻는다. 묻는 방식은 `SKILL.md` 의 "설계문서와 코드 규칙이 부딪힐 때"를 따른다.

이 문서가 다루지 않는 판단(무엇을 만들지 말지, 얼마나 단순하게 갈지, 의도적으로 감수한 한계를 어떻게 표시할지)은 `develop_rule` 스킬의 규칙을 기본으로 따른다. 두 문서가 같은 주제를 다르게 말하면 이 문서가 우선한다.

특히 추상화가 그렇다. `develop_rule` 은 요청하지 않은 추상화를 만들지 않게 하지만, 이 스킬을 실행하는 동안에는 **기능 관점의 추상화를 적극적으로 한다는 기준이 우선한다.** 이 스킬에서는 기능 단위로 객체를 묶는 일이 곧 요청받은 작업이다. `develop_rule` 의 최소주의는 추상화 이외의 판단(새 의존성, 새 인프라, 쓰이지 않는 설정과 스캐폴딩)에 적용한다.

Python 이 아닌 코드(프론트엔드 등)에는 호출 계층, 공통 모듈, 파일 최상단 주석의 세 원칙을 적용하고, 나머지는 `develop_rule` 스킬의 규칙을 따른다. 타입 힌트, pytest, mypy, uv, FastAPI 처럼 Python 에 묶인 항목은 적용하지 않는다.

## 목차

- 호출 계층과 모듈명
- 멱등성과 공통 모듈
- 타입 힌트
- 객체화와 상속
- 파일 최상단 주석
- 테스트
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
├── repository/                # 저장 층: DB 와 파일 접근
│   └── post_repository.py
├── client/                    # 외부 시스템 연동
│   └── mail_client.py
├── schema/                    # 요청과 응답 모델
│   └── post_schema.py
└── common/                    # 모든 층이 쓰는 공통 모듈
    ├── logger.py
    └── settings.py
```

프로젝트가 이미 다른 층 이름을 쓰고 있으면(`routers`, `domain`, `infra` 등) 그 이름을 따른다. 위 트리는 층 이름이 없을 때의 기본값이다.

의존 방향은 한쪽으로만 흐른다.

- `api` 는 `service` 를 부른다. `repository` 나 `client` 를 직접 부르지 않는다.
- `service` 는 `repository` 와 `client` 를 부른다. `api` 를 import 하지 않는다.
- `repository` 와 `client` 는 위 층을 import 하지 않는다.
- `common` 은 어느 층에서나 import 할 수 있고, `common` 자신은 어떤 층도 import 하지 않는다.
- `schema` 는 다른 층의 로직을 import 하지 않는다.

리팩토링이 끝나면 방향을 실제로 확인한다. 아래 층 디렉토리에서 위 층을 import 하는 줄을 grep 해서 결과가 비어 있어야 한다. 순환을 피하려고 함수 안에 넣은 지연 import 도 역방향 의존으로 본다.

이름 규칙:

- 파일 이름은 `<대상>_<역할>.py` 로 쓴다. `post_service.py`, `post_repository.py`, `mail_client.py`.
- `utils.py`, `helpers.py`, `misc.py`, `manager.py`, `handler.py` 처럼 역할을 말하지 않는 이름을 쓰지 않는다. 그런 파일이 이미 있으면 안의 내용을 역할별로 나눠 제자리에 보낸다.
- 클래스 이름은 파일 이름과 맞춘다. `post_service.py` 에는 `PostService`.
- 같은 대상은 모든 층에서 같은 낱말로 부른다. 한 층에서 `post`, 다른 층에서 `article` 이면 경로만으로 연결을 읽을 수 없다.

## 멱등성과 공통 모듈

모든 모듈은 두 번 실행해도 한 번 실행한 것과 같은 상태가 되어야 한다.

- import 시점에 부작용을 일으키지 않는다. 모듈 최상위에서 DB 연결, 파일 생성, 네트워크 호출을 하지 않는다. 그런 일은 명시적으로 부르는 함수나 생성자 안에 둔다.
- 초기화, 기동, 시드는 맞추는 방식으로 쓴다. `CREATE TABLE IF NOT EXISTS`, `mkdir(exist_ok=True)`, upsert.
- 로깅 설정처럼 여러 번 불릴 수 있는 설정 함수는 다시 불려도 핸들러가 중복 등록되지 않게 한다.
- 쓰기 경로가 재시도되어도 결과가 같은지 확인한다. 같지 않은데 고치려면 동작이 바뀌는 경우는 고치지 않고 변경 문서의 비고에 적는다.

재사용되는 것은 `common` 으로 모은다.

- 두 곳 이상에서 쓰는 코드가 대상이다. 한 곳에서만 쓰는 코드를 미리 옮기지 않는다.
- 특정 도메인을 아는 코드는 `common` 에 넣지 않는다. `common` 은 어떤 층도 import 하지 않는다는 규칙이 여기서 깨진다.

**logger 는 반드시 공통 모듈로 둔다.** `common/logger.py` 하나가 로깅 설정을 전부 가진다.

```python
"""
프로젝트 전체가 쓰는 로거를 만든다.

로깅 포맷과 출력 대상은 이 모듈에서만 정한다. 모든 층의 모듈이 get_logger 를 불러
자기 이름의 로거를 받고, 이 모듈은 common.settings 외에 아무것도 import 하지 않는다.
"""
import logging

_configured: bool = False


def get_logger(name: str) -> logging.Logger:
    """name 의 로거를 돌려준다. 첫 호출에서만 루트 로거를 설정한다."""
    global _configured
    if not _configured:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        _configured = True
    return logging.getLogger(name)
```

- 각 모듈은 `logger = get_logger(__name__)` 한 줄로 받는다.
- `logging.basicConfig` 호출과 핸들러 추가는 `common/logger.py` 밖에 두지 않는다.
- `print` 로 남기던 로그는 logger 로 옮긴다.
- 기존에 쓰던 로그 포맷과 레벨이 있으면 그 값을 유지한다.

## 타입 힌트

모든 함수와 메서드의 인자와 반환값에 타입 힌트를 붙인다. 예외 없이 필수다.

- 반환값이 없으면 `-> None` 을 쓴다. 생략하지 않는다.
- 컨테이너는 원소 타입까지 쓴다. `list` 가 아니라 `list[Post]`, `dict` 가 아니라 `dict[str, int]`.
- 구조가 정해진 dict 를 주고받지 않는다. dataclass, pydantic 모델, `TypedDict` 로 바꾼다.
- 값이 없을 수 있으면 `Post | None` 으로 드러낸다.
- `Any` 는 피한다. 써야 하면 이유를 주석으로 남긴다.
- `# type: ignore` 는 오류 코드를 지정하고 이유를 적는다. `# type: ignore[import-untyped]  # 스텁 없는 라이브러리`.
- 클래스 속성과 모듈 수준 상수에도 타입을 붙인다.

mypy 통과로 확인한다. 타입을 붙이다가 실제 불일치(`None` 이 올 수 있는데 검사하지 않음, 문자열과 숫자가 섞임)를 발견하면 그건 버그다. 타입 오류를 없애려고 동작을 바꾸지 않는다. 현재 동작을 유지하는 타입을 붙이고 변경 문서의 비고에 적는다.

## 객체화와 상속

적극적으로 객체로 묶는다.

- 상태와 그 상태를 다루는 함수들이 함께 다니면 클래스로 만든다. 같은 인자(`db`, `settings`, `client`)를 여러 함수가 반복해서 받고 있으면 그 인자가 생성자로 가야 한다는 신호다.
- 의존(DB 세션, 설정, 외부 클라이언트)은 생성자로 주입한다. 모듈 전역을 직접 참조하지 않는다. 테스트에서 바꿔 끼울 수 있게 된다.
- 함께 다니는 값 묶음은 dataclass 나 pydantic 모델로 만든다. 튜플과 dict 로 넘기지 않는다.
- 상태가 없는 순수한 변환은 함수로 남겨도 된다. 객체화의 목적은 상태와 의존을 한곳에 모으는 것이다.

추상화는 기능 관점에서 적극적으로 한다.

- 추상화의 단위는 "무엇을 하는가"다. 저장한다, 조회한다, 알림을 보낸다, 본문을 변환한다 같은 기능 하나가 클래스나 메서드 하나의 경계가 된다. 부르는 쪽은 그 기능의 이름만 알고 내부 절차를 알지 못해야 한다.
- 여러 곳에 흩어진 같은 기능은 한 객체로 끌어올린다. 호출부에 절차(연결을 열고, 쿼리를 만들고, 결과를 변환하고)가 그대로 드러나 있으면 아직 추상화되지 않은 것이다.
- 이름은 기능을 말한다. `PostRepository.find_published()` 는 무엇을 하는지 말하고, `PostRepository.run_query(sql)` 은 어떻게 하는지를 호출자에게 떠넘긴다.

**추상 클래스는 가급적 쓰지 않는다.** `ABC` 와 `@abstractmethod` 로 몸통 없는 뼈대를 먼저 세우지 않는다. 뼈대만 있는 클래스는 기능을 하나도 갖지 않으면서 읽을 단계만 늘린다.

- 공통 동작은 실제로 동작하는 구현을 가진 구체 클래스에 둔다. 예: `BaseRepository` 가 공통 조회와 저장을 직접 구현하고 `PostRepository`, `TagRepository` 가 상속해 자기 기능만 더한다.
- 주입받는 객체의 타입은 그 구체 클래스로 적는다. 테스트에서 대체 객체가 필요하면 그 구체 클래스를 상속해 필요한 메서드만 바꾼다. 타입 약속만을 위한 `typing.Protocol` 도 몸통 없는 뼈대이므로 같은 기준으로 쓰지 않는다.
- 추상 클래스가 꼭 필요하다고 판단되면 계획에 이유와 함께 적어 승인받는다.

상속은 적절할 때 쓴다.

- 여러 클래스가 같은 기능을 실제로 공유하고 "A 는 B 의 한 종류다"가 성립할 때 쓴다.
- **깊이는 1에서 2를 권장한다.** `object` 는 세지 않는다. 기반 클래스에서 구현 클래스로 바로 가면 1, 중간 클래스를 하나 거치면 2. 3 이상이 필요해 보이면 상속 대신 조합(다른 객체를 속성으로 갖기)으로 푼다.
- 코드 재사용만이 목적이고 "한 종류다"가 성립하지 않으면 조합을 쓴다.
- 하위 클래스가 기반 클래스의 메서드를 재정의할 때 인자와 반환 타입을 바꾸지 않는다.

## 파일 최상단 주석

모든 `.py` 파일의 첫머리에 모듈 docstring 을 쓴다. 내용은 **전체 프로젝트 관점에서 이 모듈이 무엇인지**다.

- 어느 층에 속하고 어떤 책임을 지는가
- 누가 이 모듈을 부르고, 이 모듈은 무엇을 부르는가
- 이 모듈이 하지 않는 일 중 헷갈리기 쉬운 것 (있을 때만)

파일 안의 함수와 클래스 목록을 나열하지 않는다. 그건 파일을 열면 보인다. 3줄에서 6줄 정도로 쓴다.

```python
"""
게시글 업무 규칙을 담당하는 업무 층 모듈.

api.post_router 가 호출하고, 저장은 repository.post_repository 에 맡긴다.
공개 여부 판정과 슬러그 생성 규칙이 여기에 있다. HTTP 요청과 응답 형태는
알지 못하며 그 변환은 api 층의 책임이다.
"""
```

- 작성 날짜, 작성자, 변경 이력을 넣지 않는다. git 이 가진 정보다.
- 내용이 없는 `__init__.py` 에도 그 패키지가 어떤 층인지 한 줄을 쓴다.

## 테스트

테스트는 종류에 따라 쓰는 방식과 보장하는 것이 다르다. 그래서 디렉토리부터 나눈다.

```
tests/
├── conftest.py
├── unit/                      # 모듈별 단위 테스트
│   ├── service/
│   │   └── test_post_service.py
│   ├── repository/
│   │   └── test_post_repository.py
│   └── common/
│       └── test_logger.py
└── integ/                     # API 수준 시나리오 e2e 테스트
    └── test_post_publish_flow.py
```

디렉토리 이름은 `tests/` 로 통일한다. 기존 디렉토리가 `test/` 처럼 다른 이름이면 `tests/` 로 옮기고, 그 경로를 가리키는 설정(`pyproject.toml` 의 `testpaths`, CI 스크립트, Dockerfile, `.dockerignore`)을 같이 고친다. 옮긴 사실은 변경 문서에 적는다.

**단위 테스트 (`unit/`)**

- 모듈별로 둔다. 리팩토링 후의 모든 모듈이 자기 테스트 파일을 하나씩 가진다.
- 디렉토리 구조를 소스의 층 구조와 맞춘다. `app/service/post_service.py` 의 테스트는 `tests/unit/service/test_post_service.py`.
- 모듈 하나를 떼어내 검증한다. 그 모듈이 의존하는 것은 생성자 주입으로 대체한다.
- 공개 함수와 메서드마다 정상 경로, 경계값, 실패 경로를 쓴다.
- DB, 네트워크, 파일 시스템 없이 돈다. 저장 층처럼 DB 접근 자체가 책임인 모듈은 메모리 DB 나 임시 파일을 쓴다.

**통합 시나리오 테스트 (`integ/`)**

- API 수준의 시나리오 e2e 테스트가 중심이다. HTTP 엔드포인트로 요청을 넣고 응답을 확인하며, 진입 층에서 저장 층까지 실제 코드를 관통한다. FastAPI 의 `TestClient` 를 쓴다.
- 파일 이름은 모듈이 아니라 시나리오로 짓는다. `test_post_publish_flow.py`.
- 여러 요청이 이어지는 흐름을 담는다. 만들고, 조회하고, 고치고, 다시 조회하는 식으로 사용자가 실제로 거치는 순서를 따른다.
- 테스트용 DB 를 실제로 쓴다. 각 테스트가 자기 상태를 스스로 준비하고 실행 순서에 의존하지 않는다.
- 주요 흐름마다 하나 이상, 엔드포인트마다 적어도 한 시나리오에 등장하게 쓴다.

**둘 다 통과해야 끝난다.** 브랜치를 배포하기 전에 `unit/` 과 `integ/` 를 모두 돌려 통과시킨다. 한쪽만 통과한 상태로 리팩토링을 끝났다고 하지 않는다.

**기존 테스트 분석**

기존 테스트를 무시하지 않는다. 기존 테스트는 원작성자가 "이 동작은 깨지면 안 된다"고 적어둔 요구사항이다. 리팩토링 전에 테스트를 하나씩 읽고 **의도**를 파악한다. 단언문이 무엇을 비교하는지가 아니라 그 테스트가 무엇을 보장하려는지를 읽는다.

분석 결과를 계획에 표로 넣는다.

| 테스트 | 의도 | 대상 모듈 | 분류 |
|---|---|---|---|
| `test_draft_not_listed` | 비공개 글이 목록 API 에 노출되지 않음을 보장 | 게시글 조회 흐름 | integ |

- 테스트를 옮기거나 고치더라도 의도는 남아야 한다. 리팩토링 후에도 같은 보장을 하는 테스트가 있어야 한다.
- 이상해 보이는 단언(빈 문자열을 돌려주길 기대함 등)도 요구사항으로 취급한다. 고치지 않는다.
- 의도를 읽을 수 없는 테스트는 추측으로 분류하지 않고 계획 단계에서 묻는다.
- 테스트를 지우지 않는다. 대상 코드가 사라져 의미가 없어진 테스트는 계획에 표시해 승인받은 뒤에 지우고 비고에 적는다.
- 기존 테스트가 다루지 않는 영역을 분석에서 함께 적는다. 그 영역이 특성 테스트를 쓸 자리다.

`unittest` 스타일의 기존 테스트는 pytest 가 그대로 실행하므로 다시 쓰지 않아도 된다. 새로 쓰는 테스트는 pytest 스타일(함수, `assert`, fixture)로 쓴다.

## 도구

| 용도 | 도구 | 명령 |
|---|---|---|
| 패키지 관리 | uv | `uv sync`, `uv add <패키지>`, `uv add --dev <패키지>` |
| 테스트 | pytest | `uv run pytest` |
| 정적 검사 | mypy | `uv run mypy <패키지 디렉토리>` |

**uv**

- 의존성은 `pyproject.toml` 에 선언하고 `uv.lock` 을 함께 둔다.
- 프로젝트가 `requirements.txt` 나 다른 도구를 쓰고 있으면 묻지 않고 uv 로 옮긴다. 옮기면서 버전을 올리지 않는다. 기존에 고정된 버전을 그대로 가져온다.
- 옮긴 경우 Dockerfile 과 CI 의 설치 명령도 같이 고치고, 배포할 때 달라지는 점을 변경 문서의 비고에 적는다.
- pytest 와 mypy 는 개발 의존성으로 넣는다.

**pytest**

- 설정은 `pyproject.toml` 의 `[tool.pytest.ini_options]` 에 둔다. `testpaths` 에 테스트 디렉토리를 적는다.
- `uv run pytest tests/unit` 과 `uv run pytest tests/integ` 를 따로 돌릴 수 있어야 한다. 배포 전에는 `uv run pytest` 로 둘 다 돌린다.

**mypy**

- 설정은 `pyproject.toml` 의 `[tool.mypy]` 에 둔다.

```toml
[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = true
disallow_incomplete_defs = true
warn_return_any = true
warn_unused_ignores = true
```

- `python_version` 은 프로젝트가 실제로 쓰는 버전으로 맞춘다.
- 타입 스텁이 없는 서드파티 라이브러리는 그 모듈에만 `ignore_missing_imports` 를 건다. 전역으로 걸지 않는다.
- 리팩토링 전에도 한 번 돌려 오류 수를 기준선으로 기록한다. 리팩토링 후에는 대상 모듈에서 오류가 0이어야 한다.

## OpenAPI 문서

엔드포인트마다 아래 셋을 반드시 넣는다.

- **기능 설명**: 이 API 가 무엇을 하는지. `summary` 한 줄, 한 줄로 부족할 때만 `description` 을 한 문장에서 세 문장.
- **인자 설명**: 경로 인자, 쿼리 인자, 본문 필드 각각의 의미.
- **사용 예제**: 요청 예와 응답 예.

설명은 과하지 않게 쓴다. Swagger 화면은 호출하는 사람이 훑어보는 곳이다.

- 내부 구현(어느 테이블을 조회하는지, 어떤 클래스를 거치는지)을 쓰지 않는다.
- 이름을 되풀이하는 설명을 쓰지 않는다. `id: 아이디` 는 정보가 없다. `id: 게시글 고유 번호` 처럼 무엇의 무엇인지를 쓴다.
- 인자 설명은 한 줄이다. 의미, 단위, 허용 범위, 기본값 중 호출자에게 필요한 것만.
- 같은 내용을 `summary` 와 `description` 에 반복하지 않는다.

작성 기준은 FastAPI 다. `summary`, `description`, `Field`, `Query`, `Path` 의 `description` 과 `examples` 로 채운다.

```python
class PostCreateRequest(BaseModel):
    title: str = Field(description="게시글 제목. 1자 이상 120자 이하", examples=["첫 글"])
    published: bool = Field(default=False, description="공개 여부. 생략하면 비공개")


@router.get(
    "/posts",
    summary="게시글 목록 조회",
    description="공개된 게시글을 최신순으로 돌려준다.",
    response_model=PostListResponse,
)
def list_posts(
    tag: str | None = Query(default=None, description="이 태그가 붙은 글만 조회", examples=["python"]),
    limit: int = Query(default=20, ge=1, le=100, description="한 번에 가져올 개수"),
) -> PostListResponse:
    ...
```

- 응답 예는 응답 모델의 `model_config = {"json_schema_extra": {"examples": [...]}}` 나 필드의 `examples` 로 넣는다.
- 예제 값은 실제로 호출이 성공하는 값이어야 한다.
- 문서 메타데이터만 추가한다. 경로, 메서드, 인자 이름, 기본값, 응답 형태는 바꾸지 않는다. `ge`, `le` 같은 검증 조건을 새로 넣으면 동작이 바뀌므로 기존에 있던 것만 유지한다.