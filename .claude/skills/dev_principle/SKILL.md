---
name: dev_principle
description: >
  코드를 짓고 고치는 모든 작업에 적용하는 절대 개발 원칙. 기획과 기능 정의, 아키텍처 설계,
  하위 모듈 구현 순서로 진행하고 앞의 두 단계는 승인받는다. 같은 입력이면 같은 결과가 나오게
  만든다(최소 구현, 멱등성, 코드에서 유도한 문서). 기능 단위 객체화, 타입 힌트, 정해진 import
  순서와 파일명, structlog 커스텀 로거, LangGraph 전용 에이전트, 기능 기준 단위 테스트와 통합
  테스트(외부 API 는 항상 mock), docs/api_spec.md, view_spec.md, features.md 상시 최신화,
  XSS, 인젝션, 비밀값, 프롬프트 인젝션 방어, 작업마다 크리티컬 포인트(API 부하, 자원 점유,
  보안, 구조) 점검을 강제한다. 기존 서비스 리팩토링은 refactor 모드로 계획 승인과 변경 문서를
  남긴다. Use when the user says "멱등", "idempotent", "재실행해도 안전하게", "중복 방지",
  "yagni", "과잉설계", "API 명세", "화면 정의서", "기능 정의서", "features.md",
  "테스트 짜줘", "보안 점검", "XSS", "로거 만들어", "에이전트 만들거야", "LangGraph",
  "리팩토링해줘", "인수인계", "over-engineered", "handoff", or invokes /dev_principle.
  그리고 사용자가 무언가를 만들거나 고치겠다고 선언하면 "~~ 개발할거야", "~~ 만들거야",
  "~~ 만들자", "~~ 붙일거야", "~~ 구현할거야", "~~ 짜줘", "서비스 하나 세우자", "API 붙이자",
  "환경 세팅하자", "파이프라인 만들거야", "I'm going to build", "let's build",
  "let's implement", "set up a service" 처럼 원칙을 언급하지 않아도 이 스킬을 켠다. 개발 착수
  선언 자체가 트리거다. 코드가 아닌 요청(일반 지식, 산문, 번역, 요약)에는 쓰지 않는다.
argument-hint: "[refactor <설계문서 경로>|review|audit|debt|docs|handoff]"
license: MIT
---

# dev_principle: 절대 개발 원칙

이 스킬은 무엇을 어떤 순서로 짓고, 지은 것이 어떤 모양이어야 하며, 무엇을 남겨야 끝난 것인지를 정한다. 한 번 켜지면 이후 모든 구현 판단에 적용되고 파일마다 다시 부를 필요가 없다. 해제는 `"stop dev_principle"`, `"normal mode"`, `/dev_principle off`.

**명제: 같은 입력이면 같은 결과가 나와야 한다.** 세 축으로 강제한다.

- **최소**: 짓지 않은 코드가 가장 재현 가능하다. 존재하지 않는 것은 깨지지도 갈라지지도 않는다.
- **수렴**: 지은 것은 두 번 실행해도 같은 상태로 간다. 새 환경에서 가장 비싼 실패는 에러가 아니라 중간까지 실행되고 죽은 상태다. 멱등하면 복구는 그냥 다시 실행이다.
- **투영**: 문서는 코드에서 유도한다. 코드가 그대로면 재생성해도 diff 가 없다.

## 모드

| 인자 | 모드 | 성격 | 읽을 것 |
|---|---|---|---|
| 없음 | 개발 모드. 이 문서 전체 | 지속 | 필요한 참조만 |
| `refactor [설계문서 경로]` | 기존 서비스 리팩토링과 변경 문서 | 단발 | `references/refactor.md` |
| `review` | 지금의 diff 에서 과잉설계 찾기 | 단발 | `references/review.md` |
| `audit` | 저장소 전체 과잉설계 감사 | 단발 | `references/review.md` |
| `debt` | `ponytail:`, `idempotent:` 마커 장부 | 단발 | `references/debt.md` |
| `docs` | 문서 3종 생성과 갱신 | 단발 | `references/docs.md` |
| `handoff` | 대화를 인수인계 문서로 압축 | 단발 | `references/handoff.md` |

참조 문서는 그 주제를 다룰 때 읽는다. 미리 다 읽지 않는다.

## 켤 때 한 번: 원칙을 프로젝트에 고정

세션이 길어져 대화가 압축되면 이 내용이 컨텍스트에서 밀려나고 원칙이 조용히 꺼진다. 그래서 처음 켤 때 `assets/claude-md-card.md` 를 현재 프로젝트의 `CLAUDE.md` 에 고정한다.

- `CLAUDE.md` 가 없으면 만들고, 있으면 끝에 덧붙인다.
- `<!-- dev_principle:start -->` 부터 `<!-- dev_principle:end -->` 까지 마커로 감싼다. 마커가 이미 있으면 그 구간만 교체한다.
- 예전 `<!-- develop_rule:start -->` 구간이 있으면 그 구간을 새 카드로 교체한다. 두 카드가 함께 있으면 서로 다른 규칙을 말한다.

묻지 않고 수행하고 한 줄로 알린다.

## 진행 순서: 기획, 아키텍처, 하위 모듈

거시에서 미시로 내려간다. 순서를 거꾸로 밟으면 구현해 둔 모듈이 나중에 정한 기능 정의와 맞지 않아 버려진다.

1. **기획과 기능 정의**: 서비스가 무엇을 하는지, 기능 목록, 기능별 입력과 결과, 범위 밖을 정한다. 결과물은 `docs/features.md` 초안이다.
2. **아키텍처 설계**: 층 구조와 디렉토리 트리, 기능별로 어떤 atomic 모듈이 필요한지와 그 모듈들을 잇는 파이프라인, 상태 저장 위치, 외부 연동, 에이전트가 있으면 LangGraph 그래프 구조를 정한다. 결과물은 `features.md` 의 모듈 매핑과 `api_spec.md` 의 엔드포인트 목록 초안이다.
3. **하위 모듈 구현**: atomic 모듈을 구현하고 단위 테스트를 붙인 뒤, 파이프라인으로 엮고 통합 테스트를 붙인다.

**1과 2가 끝날 때마다 AskUserQuestion 으로 승인받는다.** 선택지는 **이대로 진행** / **수정 후 진행** / **중단**. 설명은 위에서 아래로 한다. 서비스 전체를 한 문장으로 말하고, 구조를 보여주고, 그다음 세부로 내려간다. 승인 전에는 다음 단계의 코드를 쓰지 않는다.

이미 있는 서비스에 작은 변경을 할 때는 1과 2를 확인 단계로 밟는다. `features.md` 와 현재 구조를 읽고, 기능 정의나 아키텍처가 바뀌지 않으면 승인 없이 3으로 간다. 기능이 추가되거나 층 구조, 외부 연동, 공개 API 가 바뀌면 해당 단계의 승인을 받는다.

## 진행 규칙

**하위 모듈 구현 중에는 선택을 묻지 않는다.** 라이브러리, 파일 배치, 자연 키 후보처럼 갈리는 지점이 나오면 가장 그럴듯한 쪽을 골라 끝까지 간다. 질문은 승인 게이트 두 곳과 아래 경우에만 한다.

- 되돌리기 어렵거나 위험한 실행: 권한 변경, 파일과 데이터 삭제, 외부로 나가는 배포와 전송, 보안상 문제가 될 수 있는 명령. 무엇을 왜 실행하는지 한 줄로 밝히고 승인을 받는다.

**갈렸던 지점은 끝에 모아 보고한다.** "A로 갔고 이유는 B, 바꾸려면 C". 자연 키처럼 데이터가 쌓인 뒤에 되돌리기 어려운 결정은 반드시 넣는다.

## 사다리: 짓기 전에

처음 성립하는 칸에서 멈춘다. 문제와 그 문제가 닿는 코드를 먼저 읽고 나서 탄다.

1. 애초에 필요한가? 아직 오지 않은 요구를 위한 것이면 만들지 않는다.
2. 이미 이 코드베이스에 있나? 있으면 쓴다. 같은 일을 하는 코드가 둘이 되면 정본이 둘이 된다.
3. 표준 라이브러리나 이미 설치된 의존성으로 되나? 쓴다.
4. 플랫폼 네이티브 기능으로 되나? DB 제약, `<input type="date">`, CSS.
5. 그때서야 동작하는 최소 구현.

사다리가 줄이는 것은 새 의존성, 새 인프라, 쓰이지 않는 설정과 스캐폴딩이다. **기능 단위 객체화는 줄이는 대상이 아니다.** 기능을 객체로 묶는 일은 아래 코드 규칙이 요구하는 작업이다.

버그는 증상이 아니라 근본 원인에서 고친다. 고치기 전에 건드릴 함수의 호출자를 전부 grep 한다.

## 코드 규칙

상세와 예시는 `references/code-rules.md`. 코드를 쓰거나 고칠 때 읽는다.

- **호출 계층**: `api`, `service`, `repository`, `client`, `agent`, `schema`, `common`. 의존은 위에서 아래로 한 방향만 흐른다. 프로젝트가 이미 다른 층 이름을 쓰면 그 이름을 따른다.
- **파일명**: `<대상>_<역할>.py`. `utils.py`, `helpers.py`, `misc.py`, `manager.py`, `handler.py` 금지. 클래스명은 파일명과 맞춘다. 같은 대상은 모든 층에서 같은 낱말로 부른다.
- **import 순서**: 두 그룹. 외부(표준 라이브러리와 서드파티)를 줄 길이 오름차순, 한 줄 띄고, 로컬을 줄 길이 내림차순. 쓰지 않는 import 와 `from __future__ import annotations` 는 넣지 않는다.
- **타입 힌트**: 모든 함수와 메서드의 인자와 반환값에 필수. `-> None` 생략 금지. 구조가 정해진 dict 는 dataclass, pydantic, `TypedDict` 로 바꾼다.
- **기능 단위 객체화**: 상태나 주입할 의존이 있으면 클래스로 묶고 의존은 생성자로 주입한다. 추상 클래스(`ABC`, 몸통 없는 `Protocol`)는 쓰지 않는다. 상속 깊이는 1에서 2. 상태도 의존도 없는 순수 변환은 함수로 둔다.
- **모듈 docstring**: 모든 `.py` 첫머리에 프로젝트 관점에서 이 모듈이 무엇인지 최대 2줄. 함수 목록, 날짜, 작성자는 쓰지 않는다.
- **상수와 주석**: 모듈 상수는 import 직후에 모은다. 주석은 왜(why)만 쓴다.
- **도구**: Python 프로젝트의 패키지 관리는 uv(`pyproject.toml` + `uv.lock`), 환경 관리는 Docker 와 Docker Compose(`Dockerfile` + `compose.yaml`). 앱과 DB 같은 의존 서비스를 compose 로 띄운다. pip, poetry, conda, 손으로 만든 venv 를 쓰지 않는다. 검사는 pytest, mypy. 이미지 태그에 `latest` 금지.
- **OpenAPI**: FastAPI 엔드포인트마다 기능 설명, 인자 설명, 사용 예제. 과하게 쓰지 않는다.

## 로깅: structlog 커스텀 로거

`common/logger.py` 하나가 로깅 설정을 전부 가진다. 각 모듈은 `logger = get_logger(__name__)` 한 줄로 받는다. `print`, `logging.basicConfig`, 모듈마다 따로 만든 핸들러는 쓰지 않는다.

- structlog 로 구조화 로그를 남긴다. 개발 환경은 rich 기반 콘솔 출력, 운영 환경은 JSON 출력. `LOG_FORMAT` 환경변수 하나로 바꾼다.
- 설정 함수는 몇 번 불려도 한 번만 설정한다.
- 요청 ID 같은 문맥은 `contextvars` 로 묶는다. 메시지 문자열에 끼워 넣지 않는다.
- 비밀값과 개인정보는 로그에 남기지 않는다. 마스킹 프로세서가 마지막 방어선이다.

템플릿은 `assets/logger.py`, 상세는 `references/logging.md`.

## 에이전트: LangGraph 만

에이전트는 모두 LangGraph 로 구현한다. **Deepagents 는 쓰지 않는다.** 다른 에이전트 프레임워크(CrewAI, AutoGen 등)도 들이지 않는다.

- 상태는 `TypedDict` 나 pydantic 모델로 선언한다. 노드는 상태를 받아 바뀐 부분만 돌려주는 atomic 모듈이다.
- LLM, 도구, 외부 호출은 생성자로 주입한다. 그래야 테스트에서 mock 으로 바꿀 수 있다.
- 재시도와 중단 후 재개는 checkpointer 와 `thread_id` 로 처리한다. `recursion_limit` 과 호출 타임아웃을 항상 건다.

상세는 `references/agent.md`.

## 테스트

테스트는 서비스 기능을 기준으로 두 종류만 쓴다. 상세는 `references/testing.md`.

- **단위 테스트** `tests/unit/test_{기능명}_{단위구현모듈명}.py`: 기능을 구현하는 atomic 모듈 하나를 떼어내 검증한다.
- **통합 테스트** `tests/integ/test_{기능명}.py`: 여러 atomic 모듈을 파이프라인으로 엮은 서비스 관점의 기능 동작을 검증한다.
- **외부 API 연동은 항상 mock 으로 대체한다.** LLM 호출, 결제, 메일, 서드파티 HTTP 전부. 실제 네트워크로 나가는 테스트는 쓰지 않는다.
- 테스트 안에는 주석을 거의 쓰지 않는다. 테스트 함수 이름이 무엇을 보장하는지 말한다.
- 많이 쓰지 않는다. 분기와 변환이 있는 atomic 모듈만 단위 테스트를 갖고, 공개 함수마다 정상 경로 하나와 가장 중요한 실패나 경계 하나. 기능마다 통합 테스트 파일 하나.

## 문서: 세 개를 항상 최신으로

서비스는 `docs/` 아래에 세 문서를 가진다. 작업을 할 때마다 그 작업 안에서 갱신한다. 나중으로 미루면 안 한다. 작성 규칙은 `references/docs.md`.

| 파일 | 내용 | 언제 있나 |
|---|---|---|
| `docs/features.md` | 서비스 기능 목록, 기능별 설명, 기능을 구현하는 파일과 테스트 매칭 | 항상 |
| `docs/api_spec.md` | API 명세. 엔드포인트마다 재호출하면 어떻게 되는지 포함 | API 가 있으면 |
| `docs/view_spec.md` | 화면 기능 정의서. 빈 상태와 에러 상태 포함 | 화면이 있을 때만 |

문서는 코드의 투영이다. 생성 시각이나 버전 번호를 넣지 않는다. 코드가 그대로면 다시 만들어도 diff 가 없어야 한다.

## 보안

신뢰 경계를 넘는 모든 입력과 출력에 적용한다. 상세 점검표는 `references/security.md`.

- **XSS**: 사용자 입력을 HTML 로 내보낼 때는 템플릿 자동 이스케이프에 맡긴다. Jinja2 `autoescape`, React 의 기본 렌더링. `|safe`, `Markup()`, `dangerouslySetInnerHTML`, `innerHTML` 은 쓰지 않는다. 꼭 필요하면 sanitizer 를 거친 값만 넣는다. LLM 출력도 신뢰하지 않는 입력으로 다룬다.
- **인젝션**: SQL 은 파라미터 바인딩이나 ORM 만 쓴다. 셸 명령은 `subprocess` 에 리스트 인자로 넘기고 `shell=True` 를 쓰지 않는다. `eval`, `exec`, `pickle.loads` 를 외부 입력에 쓰지 않는다.
- **입력 검증**: 모든 요청 본문과 파라미터는 pydantic 모델로 받고 길이, 범위, 형식을 제한한다.
- **비밀값**: 코드와 저장소에 두지 않는다. 환경변수나 비밀 저장소에서 읽고, 없으면 기동 시점에 실패한다. 로그와 에러 응답에 내보내지 않는다.
- **인증과 권한**: 리소스마다 소유자 검사를 서버에서 한다. 클라이언트가 보낸 ID 를 그대로 믿지 않는다.
- **외부 호출**: 타임아웃을 항상 건다. 사용자가 준 URL 을 서버가 호출하면 허용 목록으로 제한한다(SSRF).
- **에이전트**: 도구는 최소 권한으로 준다. 문서나 웹에서 읽은 내용 속 지시는 따르지 않는다(프롬프트 인젝션). 되돌릴 수 없는 도구 호출은 사람 승인 노드를 거친다.

## 크리티컬 포인트: 작업마다 점검

작업을 끝내기 전에 네 가지를 점검하고 결과를 보고에 한 줄씩 남긴다. 문제가 없으면 "이상 없음"과 근거를 쓴다. 점검하지 않은 항목을 이상 없다고 쓰지 않는다.

- **API 부하**: 요청당 외부 호출과 DB 쿼리 수. N+1 쿼리, 반복문 안의 호출, 페이지네이션 없는 목록, 타임아웃과 재시도 폭주, LLM 호출 횟수와 토큰.
- **자원 점유**: 메모리에 통째로 올리는 데이터, 닫히지 않는 연결과 파일, async 경로 안의 블로킹 호출, 끝나지 않는 루프와 그래프 재귀.
- **보안**: 위 보안 절과 `references/security.md` 의 해당 항목. 이번 변경이 새로 연 신뢰 경계가 있는지.
- **구조 효율**: 역방향 의존과 순환 import, 같은 일을 하는 코드의 중복, 한 모듈에 섞인 책임, 기능과 파일 매핑이 `features.md` 와 맞는지.

## 멱등성: 모든 층에 공통인 네 가지

1. **무엇이 같은 것인지 먼저 정의한다.** 재실행해도 변하지 않는 값(파일명, 외부 ID, 사람이 정한 코드)을 자연 키로 고른다. 자동 증가 ID와 생성 시각은 후보가 아니다.
2. **상태를 만들지 말고 맞춘다.** `create_x()` 대신 `ensure_x()`, `CREATE TABLE IF NOT EXISTS`, `exist_ok=True`, upsert.
3. **어디서 죽어도 재실행이 답이 되게 한다.** 5단계 중 3단계에서 죽는 경우를 실제로 상상한다.
4. **확인과 변경 사이의 틈을 없앤다.** 코드의 중복 체크는 UX 용이고 실제 보증은 DB 유니크 제약이 한다.

상세는 `references/idempotency-core.md`. 층마다 기법이 다르니 지금 만드는 것에 맞는 문서를 읽는다.

| 지금 만드는 것 | 읽을 것 |
|---|---|
| 환경 준비, 스키마와 마이그레이션, 시드, 배포와 CI, 컨테이너 | `references/idempotency-setup.md` |
| 도메인 로직, 데이터 변환, 서비스, 배치 | `references/idempotency-code.md` |
| HTTP 핸들러, 큐 컨슈머, 웹훅, 외부 시스템 호출 | `references/idempotency-api.md` |

층 하나만 처리하고 멱등하다고 선언하지 않는다. 핸들러에 중복 방지를 넣어 놓고 DB 에 유니크 제약이 없으면 동시 요청 두 개가 통과한다.

## 마커 규약

의도적으로 감수한 한계는 코드에 남긴다. 표시되지 않은 의도는 버그와 구분되지 않는다.

- `# ponytail: <천장>, <업그레이드 조건>`: 알려진 한계를 감수한 단순화
- `# idempotent: <이유>, <해결 방법>`: 의도적 비멱등

장부는 하나이고 `/dev_principle debt` 가 둘 다 모은다.

## 게으르지 않을 것

절대 단순화하지 않는다: 신뢰 경계의 입력 검증, 데이터 손실을 막는 에러 처리, 보안, 접근성 기본, 사용자가 명시적으로 요청한 것. 문제 이해에도 게으르지 않는다. 사다리는 해법을 줄이지 읽기를 줄이지 않는다.

## 끝내기 전에

1. 이걸 지금 한 번 더 실행하면 어떻게 되나? 말로 답할 수 있어야 한다.
2. 중복 방지가 코드에만 있고 DB 제약에는 없지 않은가?
3. 손댄 모든 `.py` 에 모듈 docstring, 타입 힌트가 있고 import 순서와 파일명 규칙을 지켰나? `uv run mypy` 가 손댄 모듈에서 오류 0인가?
4. 바뀐 기능에 단위 테스트와 통합 테스트가 있고, 외부 API 가 전부 mock 이고, `uv run pytest` 가 마지막 수정 이후에 통과했나?
5. `features.md`, `api_spec.md`, `view_spec.md`(화면이 있으면)를 이번 변경에 맞춰 갱신했나?
6. 크리티컬 포인트 네 가지를 점검하고 결과를 적었나?
7. 마커를 남길 곳이 있나?
8. 검증한 것과 검증하지 않은 것을 구분해서 말했나? 돌려본 것만 확인했다고 한다.

## 출력

코드 먼저. 그다음 짧게: 갈렸던 지점, 건너뛴 것과 필요해지는 조건, 크리티컬 포인트 점검 결과, 검증 결과. 설명이 코드보다 길면 설명을 지운다. 사용자가 명시적으로 요청한 설명은 온전히 준다.

## 안티패턴 빠른 조회

| 증상 | 왜 위험한가 | 대신 |
|---|---|---|
| `CREATE TABLE`, `mkdir`, `INSERT` 를 맨몸으로 | 두 번째 실행에서 터진다 | `IF NOT EXISTS`, `exist_ok=True`, upsert |
| `SELECT` 후 `INSERT` | 동시 실행 시 둘 다 통과 | `ON CONFLICT`, 유니크 제약 |
| `requirements.txt` + `pip install` | 실행 시점 인덱스에 따라 결과가 갈린다 | `pyproject.toml` + `uv.lock` + `uv sync` |
| 외부 API 호출 후 커밋 | 커밋 전 죽으면 외부만 반영된다 | 호출 전 의도 기록, 호출 후 상태 확정 |
| `time.time()`, `random`, `uuid4()` 를 결정 로직에 | 같은 입력이 같은 출력을 안 낸다 | 경계에서 생성해 주입 |
| `ABC` 로 만든 몸통 없는 뼈대 | 기능 없이 읽을 단계만 늘린다 | 동작하는 구체 기반 클래스 |
| 테스트가 실제 외부 API 를 호출 | 느리고 비용이 들고 결과가 흔들린다 | client 를 주입하고 mock |
| `print`, 모듈마다 `logging.basicConfig` | 출력 형식이 갈리고 비밀값이 샌다 | `common/logger.py` 의 `get_logger` |
| f-string 으로 만든 SQL, `shell=True` | 인젝션 | 파라미터 바인딩, 리스트 인자 |
| `dangerouslySetInnerHTML`, Jinja2 `\|safe` | XSS | 자동 이스케이프, sanitizer |
| Deepagents, 자체 제작 에이전트 루프 | 상태와 재개를 보장할 수 없다 | LangGraph `StateGraph` + checkpointer |

## 참조 파일

- `references/code-rules.md`: 호출 계층, 파일명, import 순서, 타입 힌트, 객체화, docstring, 도구, OpenAPI
- `references/logging.md`: structlog 커스텀 로거
- `references/agent.md`: LangGraph 에이전트 구현 규칙
- `references/testing.md`: 단위 테스트와 통합 테스트, mock, 네이밍, 분량
- `references/docs.md`: `features.md`, `api_spec.md`, `view_spec.md` 작성 규칙
- `references/security.md`: 보안 점검표
- `references/idempotency-core.md`, `idempotency-setup.md`, `idempotency-code.md`, `idempotency-api.md`: 멱등성
- `references/refactor.md`, `references/default-plan.md`: refactor 모드
- `references/review.md`, `references/debt.md`, `references/handoff.md`: 단발 모드

`assets/` 에는 `CLAUDE.md` 카드, 로거 템플릿, 문서 템플릿 세 개, 리팩토링 변경 문서 템플릿이 있다.

## 경계

이 스킬은 무엇을 짓는지를 지배하지 어떻게 말하는지는 지배하지 않는다. 말투는 `humanism_talk` 가 맡는다. 코드가 아닌 요청(일반 지식, 산문, 번역, 요약)에는 적용하지 않는다.

## 크레딧

- 최소주의 축: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT)
- 인수인계: [mattpocock/skills](https://github.com/mattpocock/skills) (MIT)
- 보안 점검표: `references/security.md` 의 출처 절 참고
- 수렴과 투영 축, 리팩토링, 테스트와 문서 규칙: 이 저장소
