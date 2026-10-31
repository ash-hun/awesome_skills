# 보안 점검표

`dev_principle` 스킬의 참조 문서. 코드를 쓸 때 해당 절을 읽고, 작업을 끝내기 전 크리티컬 포인트의 보안 항목을 점검할 때 다시 본다.

대상 스택은 Python, FastAPI, LangGraph, structlog, uv, Docker 와 웹 프론트엔드(React 또는 순수 HTML)다. 각 줄 끝의 꺾쇠는 출처다. 출처 목록은 문서 끝에 있다.

이 문서는 점검표다. 이번 변경이 닿는 절만 본다. 백엔드만 고쳤는데 프론트엔드 절까지 적용하려고 코드를 늘리지 않는다.

## 목차

- 입력과 출력: XSS, 인젝션
- 인증과 권한
- 비밀값과 설정
- 로깅
- 외부 호출: SSRF, 타임아웃
- 의존성과 공급망
- Docker
- LLM 과 에이전트
- 출처

## 입력과 출력: XSS, 인젝션

- 모든 요청 본문, 쿼리, 경로 인자를 pydantic 모델로 받는다. `model_config = ConfigDict(extra="forbid")`, 길이와 범위 제한, 허용 값은 `Literal` 이나 Enum. [A]
- Jinja2 는 `autoescape=True` 또는 `select_autoescape()` 로 둔다. 사용자 입력과 LLM 출력에 `|safe`, `Markup()` 을 쓰지 않는다. [C]
- React 에서 신뢰하지 않는 데이터를 `dangerouslySetInnerHTML` 에 넣지 않는다. HTML 이 꼭 필요하면 허용 태그 목록을 지정한 DOMPurify 를 거친다. 순수 JS 는 `textContent` 를 쓰고 `innerHTML`, `document.write` 를 쓰지 않는다. [A]
- 링크와 리다이렉트 대상 URL 은 `javascript:`, `data:` 스킴을 막는다. 리다이렉트 대상은 서버에서 정한 목록으로 매핑하고 사용자 입력을 그대로 쓰지 않는다. [A]
- 응답 헤더에 nonce 기반 CSP, `frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`, HSTS 를 건다. [A][C]
- SQL 은 파라미터 바인딩이나 SQLAlchemy 바인드 파라미터로만 만든다. f-string 이나 `+` 로 SQL 을 조립하지 않는다. [A][C]
- 셸 명령은 `subprocess.run([...], shell=False)` 로 실행하고, 명령은 허용 목록에서 고르고, 사용자 인자 앞에 `--` 를 둔다. [A][C]
- `eval`, `exec`, JS 의 `new Function` 과 문자열 `setTimeout` 을 외부 입력에 쓰지 않는다. [A][C]
- 신뢰하지 않는 데이터에 `pickle.loads`, `yaml.load` 를 쓰지 않는다. `yaml.safe_load`, JSON 을 쓴다. [A]
- 파일 경로를 사용자 입력으로 만들면 기준 디렉토리 아래로 정규화되는지 확인한다(`Path.resolve()` 후 `is_relative_to`). [A]

## 인증과 권한

- 모든 엔드포인트에서 서버가 권한을 검사한다. FastAPI `Depends()` 가드로 기본 거부하고, 리소스마다 소유자를 확인한다(IDOR). 클라이언트가 보낸 사용자 ID 를 믿지 않는다. [A][B]
- JWT 는 `algorithms=[...]` 를 고정하고 `iss`, `aud`, `exp`, `nbf` 를 검증하고 수명을 짧게 둔다. [A]
- 세션 쿠키는 `Secure`, `HttpOnly`, `SameSite=Lax` 이상. 쿠키 인증으로 상태를 바꾸는 요청에는 CSRF 토큰. [A]
- 토큰과 API 키 비교는 `hmac.compare_digest`. 비밀번호는 argon2 나 bcrypt 로 해시한다. [C]
- CORS 에서 `allow_origins=["*"]` 와 `allow_credentials=True` 를 함께 쓰지 않는다. 출처를 명시한다. [A]
- 프론트엔드에서 토큰을 `localStorage` 에 두지 않는다. [A]

## 비밀값과 설정

- 키와 비밀번호를 코드에 쓰지 않는다. `pydantic-settings` 로 환경변수나 비밀 저장소에서 읽고 `SecretStr` 로 타입을 둔다. 필수 값이 없으면 기동 시점에 실패한다. [A][C]
- 저장소에는 `.env.example` 만 올린다. `.env` 는 `.gitignore` 와 `.dockerignore` 둘 다에 넣는다. [A]
- 저장소에서 비밀값을 발견하면 지우는 것과 별개로 이미 노출된 값이니 교체가 필요하다고 보고한다.
- 운영 환경은 `debug=False`. 필요 없으면 `/docs`, `/openapi.json` 을 끈다. 스택 트레이스를 응답으로 내보내지 않는다. [C]

## 로깅

`references/logging.md` 의 로거를 쓰면 아래가 대부분 해결된다. 점검은 여전히 한다.

- 렌더러 앞에 마스킹 프로세서를 둔다. `password`, `token`, `authorization`, `api_key`, `cookie`, `secret` 같은 키를 가린다. [A]
- 요청 헤더 원문, 요청 본문, 프롬프트 전문, 개인정보가 담길 수 있는 LLM 출력을 로그에 남기지 않는다. ID, 해시, 길이를 남긴다. [A][C][D]
- 운영 환경은 JSON 출력으로 둔다. 값 안의 줄바꿈으로 로그 줄을 위조할 수 없다. [A]
- 인증과 권한 실패, 에이전트의 도구 호출(도구 이름, 마스킹된 인자, 사용자 ID)을 로그로 남긴다. [A]
- 비밀값이 렌더링된 로그에 나오지 않는다는 단위 테스트를 하나 둔다. [A]

## 외부 호출: SSRF, 타임아웃

- 사용자나 LLM 이 준 URL 을 서버가 그대로 호출하지 않는다. 호스트 허용 목록, `http`/`https` 만, DNS 를 풀어 사설망, 루프백, 링크 로컬, `169.254.169.254` 를 거부하고, 리다이렉트를 끄거나 매번 다시 검증한다. [A][B]
- httpx, requests 호출마다 타임아웃을 명시한다. requests 는 타임아웃을 주지 않으면 무한히 기다린다. 재시도 횟수와 응답 크기에도 상한을 둔다. [A]
- TLS 검증을 끄지 않는다. `verify=False` 금지. [C]

## 의존성과 공급망

- `uv.lock` 을 커밋하고 CI 와 Docker 에서 `uv sync --locked` 또는 `--frozen` 을 쓴다. [A][C]
- 새 패키지를 추가하기 전에 그 패키지가 실제로 있고 관리되는지 확인한다. 모델이 지어낸 이름이나 오타를 노린 이름이 있다. 표준 라이브러리를 먼저 본다. [C][A]
- CI 에서 `pip-audit`(또는 OSV), Bandit 을 돌리고 심각도 높음에서 실패시킨다. [C]
- GitHub Actions 는 커밋 SHA 로 고정한다. [C][A]

## Docker

- 베이스 이미지를 다이제스트로 고정하고 slim 이미지를 쓴다. 멀티 스테이지 빌드로 uv 와 빌드 도구를 실행 이미지에서 뺀다. [A][C]
- 루트가 아닌 `USER` 로 실행한다. compose 에서 `cap_drop: [ALL]`, `security_opt: [no-new-privileges:true]`, 가능하면 `read_only: true`. [A]
- `/var/run/docker.sock` 을 마운트하지 않는다. `privileged`, 호스트 네트워크를 쓰지 않는다. [A]
- 비밀값을 `ENV`, `ARG`, 이미지 레이어에 넣지 않는다. 빌드 중에 필요하면 BuildKit `--mount=type=secret`. [A]
- `HEALTHCHECK` 를 둔다. [A]

## LLM 과 에이전트

`references/agent.md` 의 구조와 함께 적용한다.

- 검색한 문서, 도구 출력, 웹 페이지, 사용자 파일은 신뢰하지 않는 데이터다. 구분자로 감싼 별도 구역에 넣고 시스템 지시문에 이어 붙이지 않는다. 그 안의 지시는 따르지 않는다. [D][B]
- LLM 출력도 신뢰하지 않는 입력이다. SQL, 셸, HTML, 파일 경로, 도구 인자로 가기 전에 pydantic 스키마로 검증한다. [B][D]
- 도구는 한 가지 일만 하고 범위를 가장 좁게 둔다. "셸 실행", "아무 URL 이나 가져오기" 같은 도구를 만들지 않는다. 도구 인자는 코드에서 검증하고, 권한 판단을 모델에 맡기지 않는다. [A][D]
- 삭제, 결제, 외부 발송처럼 되돌릴 수 없는 도구 호출 앞에는 LangGraph `interrupt()` 로 사람 승인 단계를 둔다. 초안을 먼저 만들고 확정은 승인 뒤에 한다. [A][D]
- 실행마다 `recursion_limit`, 도구 호출 수, 토큰, 경과 시간에 상한을 두고 사용자별 호출 빈도를 제한한다. 비용 폭주를 막는다. [B][D]
- 비밀값과 권한 규칙을 시스템 프롬프트에 넣지 않는다. 프롬프트는 추출될 수 있다고 가정한다. [B]
- 장기 메모리와 checkpointer 에 쓰기 전에 내용을 검증하고, 저장소는 사용자나 테넌트 단위로 나눈다. [D][B]
- LLM 이 만든 코드는 네트워크와 자격 증명이 없는 별도 컨테이너에서만 실행한다. [A][B]
- 모델 버전을 고정한다. MCP 서버는 허용 목록으로 관리한다. [A][B]
- 신뢰하지 않는 콘텐츠가 많으면 도구 없는 LLM 이 그 콘텐츠를 읽어 구조화하고, 도구를 가진 계획 노드는 원문을 보지 않게 나눈다. [D]

## 출처

이 문서는 아래 자료를 이 스택에 맞게 다시 정리한 것이다. CC-BY-SA 자료는 문장을 옮기지 않고 내용만 참고했다.

- [A] Project CodeGuard (CoSAI/OASIS): https://github.com/cosai-oasis/project-codeguard (CC-BY-4.0)
- [B] agamm/claude-code-owasp: https://github.com/agamm/claude-code-owasp (MIT)
- [C] OpenSSF, Security-Focused Guide for AI Code Assistant Instructions: https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions (저장소 Apache-2.0)
- [D] OWASP Cheat Sheet Series (AI Agent Security, LLM Prompt Injection Prevention, Secrets Management, Docker Security): https://github.com/OWASP/CheatSheetSeries (CC-BY-SA-4.0)
- [E] trailofbits/skills: https://github.com/trailofbits/skills (CC-BY-SA-4.0). 공급망 감사 관점 참고
