# 테스트

`dev_principle` 스킬의 참조 문서. 테스트를 새로 쓰거나 옮길 때 읽는다.

테스트의 기준은 서비스 기능이다. 기능 목록은 `docs/features.md` 에 있고, 테스트 파일 이름이 그 기능 이름을 그대로 쓴다. 그래서 `features.md` 의 기능 하나를 보면 그 기능의 테스트 파일을 바로 찾을 수 있다.

## 두 종류

| 종류 | 위치와 이름 | 검증하는 것 |
|---|---|---|
| 단위 테스트 | `tests/unit/test_{기능명}_{단위구현모듈명}.py` | 기능을 구현하는 atomic 모듈 하나 |
| 통합 테스트 | `tests/integ/test_{기능명}.py` | 여러 atomic 모듈을 파이프라인으로 엮은 서비스 관점의 기능 동작 |

이 외의 종류(성능, 스냅샷, e2e 브라우저)는 사용자가 요청할 때만 만든다.

```
tests/
├── conftest.py
├── unit/
│   ├── test_post_publish_slug_builder.py
│   ├── test_post_publish_post_repository.py
│   └── test_summary_draft_node.py
└── integ/
    ├── test_post_publish.py
    └── test_summary.py
```

- `{기능명}` 은 `features.md` 의 기능 ID 와 같은 snake_case 낱말이다. 문서와 파일명이 다른 낱말을 쓰면 연결이 끊긴다.
- `{단위구현모듈명}` 은 테스트 대상 파일명에서 `.py` 를 뺀 것이다. `app/service/slug_builder.py` 면 `slug_builder`.
- 한 모듈이 여러 기능에 쓰이면 그 모듈을 처음 만든 기능, 또는 가장 핵심인 기능 이름으로 한 번만 쓴다. 기능마다 복제하지 않는다.
- `tests/unit`, `tests/integ` 아래에 하위 디렉토리를 만들지 않는다. 파일명이 기능과 모듈을 이미 말한다.

## 외부 API 는 항상 mock

외부 시스템으로 나가는 호출은 단위 테스트든 통합 테스트든 **항상** mock 으로 바꾼다. LLM, 결제, 메일, 문자, 서드파티 HTTP, 클라우드 스토리지 전부다. 실제 네트워크로 나가면 테스트가 느려지고 돈이 들고 상대 상태에 따라 결과가 흔들린다. 같은 입력에 같은 결과가 나오지 않는 테스트는 아무것도 보장하지 않는다.

- 외부 호출은 `client` 층 클래스로 모여 있고 생성자로 주입된다. 테스트는 그 클래스를 상속한 대체 객체나 `unittest.mock.create_autospec` 으로 바꿔 끼운다.
- httpx 를 직접 쓰는 client 자체를 테스트할 때는 `httpx.MockTransport` 나 respx 로 응답을 고정한다.
- LLM 은 `GenericFakeChatModel` 같은 가짜 채팅 모델을 주입한다. `references/agent.md` 참고.
- 실수로 실제 네트워크에 나가지 않도록 `conftest.py` 에서 막는다. pytest-socket 의 `--disable-socket` 이나 소켓 생성을 막는 fixture 하나면 된다.

내부 자원은 외부 API 가 아니다. DB 는 단위 테스트에서 메모리 DB 나 임시 파일, 통합 테스트에서 테스트용 DB 를 실제로 쓴다. 파일 시스템은 `tmp_path`.

## 단위 테스트

- atomic 모듈 하나를 떼어내 검증한다. 그 모듈이 의존하는 것은 생성자 주입으로 바꾼다.
- 대상은 공개 함수와 메서드다. 비공개 함수(`_` 로 시작)를 직접 부르지 않는다.
- 분기, 반복, 변환, 파싱, 돈과 보안 경로가 있는 모듈만 단위 테스트를 갖는다. 위임만 하는 얇은 래퍼와 설정 조립 코드는 통합 테스트가 덮는다.

## 통합 테스트

- 기능 하나당 파일 하나. 그 기능의 진입점(HTTP 엔드포인트면 FastAPI `TestClient`, 배치면 실행 함수, 에이전트면 컴파일한 그래프)으로 들어가 실제 모듈들을 관통한다.
- 사용자가 실제로 거치는 순서를 따른다. 만들고, 조회하고, 고치고, 다시 조회한다.
- 각 테스트가 자기 상태를 준비한다. 실행 순서에 의존하지 않는다.
- 엔드포인트마다 적어도 한 시나리오에 등장해야 한다.

## 분량: 많이 쓰지 않는다

테스트가 많으면 리팩토링할 때마다 같이 고쳐야 할 코드가 늘고, 무엇이 핵심 보장인지가 묻힌다.

- 공개 함수 하나에 테스트는 **정상 경로 하나, 가장 중요한 실패나 경계 하나**. 더 필요한 분기가 있으면 `pytest.mark.parametrize` 로 한 함수에 모은다.
- 통합 테스트 파일 하나에 **주요 시나리오 하나, 대표 실패 시나리오 하나**. 기능의 성격상 더 필요하면 그때 추가한다.
- 같은 사실을 단위와 통합에서 두 번 확인하지 않는다. 경계값은 단위에서, 흐름은 통합에서.
- 픽스처는 두 파일 이상에서 쓸 때만 `conftest.py` 로 올린다.

## 주석

테스트 안에는 주석을 거의 쓰지 않는다. 함수 이름이 무엇을 보장하는지 말한다.

```python
def test_publish_rejects_duplicate_slug(client: TestClient) -> None:
    client.post("/posts", json={"title": "첫 글"})

    res = client.post("/posts", json={"title": "첫 글"})

    assert res.status_code == 409
```

- 이름은 `test_<동작>_<조건이나 기대>` 로 쓴다.
- 준비, 실행, 확인을 빈 줄로 나눈다. `# given`, `# when`, `# then` 주석은 붙이지 않는다.
- 주석은 왜 이상해 보이는 값을 기대하는지처럼 코드로 읽을 수 없는 이유가 있을 때만 한 줄.
- 파일 첫머리 docstring 은 한 줄. 어느 기능의 무엇을 검증하는지.

## 도구

- pytest. 설정은 `pyproject.toml` 의 `[tool.pytest.ini_options]`, `testpaths = ["tests"]`.
- `uv run pytest tests/unit`, `uv run pytest tests/integ` 를 따로 돌릴 수 있어야 하고, 작업을 끝내기 전에는 `uv run pytest` 로 둘 다 돌린다.
- 새 테스트는 pytest 스타일(함수, `assert`, fixture). 기존 `unittest` 스타일 테스트는 pytest 가 그대로 실행하므로 다시 쓰지 않는다.

## 기존 프로젝트의 테스트 이름이 다를 때

기존 테스트가 다른 구조(`tests/unit/service/test_post_service.py` 등)면 refactor 모드에서 이 규칙으로 옮긴다. refactor 모드가 아닌 일반 작업에서는 새로 쓰는 테스트만 이 규칙을 따르고, 기존 파일은 그 작업이 건드리는 것만 옮긴다. 옮길 때 테스트의 의도는 보존한다. 의도 분석 방법은 `references/refactor.md` 의 "기존 테스트 분석".
