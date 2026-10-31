<!-- dev_principle:start -->
## 개발 원칙

이 프로젝트는 `dev_principle` 스킬의 원칙을 따른다. 세부 규칙이 필요하면 그 스킬의 참조 문서를 읽는다.

**진행 순서**: 기획과 기능 정의, 아키텍처 설계, 하위 모듈 구현 순서로 진행한다. 앞의 두 단계는 결과(`docs/features.md` 초안, 디렉토리 트리와 모듈 매핑)를 보여주고 승인받는다. 구현 중에는 선택을 묻지 않고, 갈린 지점은 끝에 모아 보고한다. 삭제, 권한 변경, 외부 배포처럼 되돌리기 어려운 실행은 먼저 확인받는다.

**코드**

- 층: `api`, `service`, `agent`, `repository`, `client`, `schema`, `common`. 의존은 위에서 아래로만.
- 파일명 `<대상>_<역할>.py`. `utils.py`, `helpers.py` 금지. 클래스명은 파일명과 맞춘다.
- import 는 두 그룹. 외부를 줄 길이 오름차순, 한 줄 띄고, 로컬을 줄 길이 내림차순.
- 모든 함수에 타입 힌트. 모든 `.py` 첫머리에 최대 2줄 모듈 docstring. 주석은 왜(why)만.
- 상태나 의존이 있으면 기능 단위 클래스로 묶고 생성자로 주입한다. 추상 클래스 금지, 상속 깊이 1에서 2.
- 로거는 `common/logger.py` 의 structlog 커스텀 로거만. 개발은 rich 콘솔, 운영은 `LOG_FORMAT=json`.
- 에이전트는 LangGraph 로만 구현한다. Deepagents 금지.
- 같은 작업을 두 번 실행해도 결과가 같게 만든다. `ensure_x()`, `IF NOT EXISTS`, upsert, DB 유니크 제약.
- Python 패키지 관리는 uv(`pyproject.toml` + `uv.lock`), 환경 관리는 Docker 와 Docker Compose(`compose.yaml`). pip, poetry, conda, 손으로 만든 venv 금지. 검사는 pytest, mypy.

**테스트**: `tests/unit/test_{기능명}_{단위구현모듈명}.py`(atomic 모듈), `tests/integ/test_{기능명}.py`(기능 파이프라인). 외부 API 는 항상 mock. 테스트 안 주석 최소화. 공개 함수마다 정상 하나, 실패나 경계 하나.

**문서**: `docs/features.md`(기능과 구현 파일, 테스트 매칭), `docs/api_spec.md`(API 명세, 재호출 결과 포함), 화면이 있으면 `docs/view_spec.md`. 작업할 때마다 그 작업 안에서 갱신한다. 생성 시각을 넣지 않는다.

**보안**: 입력은 pydantic 으로 검증, 출력은 자동 이스케이프(`dangerouslySetInnerHTML`, `|safe` 금지), SQL 은 바인딩, `shell=True` 금지, 비밀값은 환경변수와 `SecretStr`, 외부 호출은 타임아웃과 허용 목록, LLM 출력과 검색 문서는 신뢰하지 않는 입력.

**작업마다 크리티컬 포인트 점검**: API 부하, 내부 로직 자원 점유, 보안, 구조 효율. 결과를 보고에 한 줄씩 남긴다.

**끝내기 전**: 한 번 더 실행하면 어떻게 되는지 답할 수 있어야 한다. `uv run pytest`, `uv run mypy` 를 마지막 수정 이후에 돌린다. 검증한 것과 하지 않은 것을 구분해서 보고한다.
<!-- dev_principle:end -->
