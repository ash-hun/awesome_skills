# 셋업 층: 환경·스키마·배포

uv 프로젝트 구성, Docker 이미지·compose, DB 마이그레이션, 시드 데이터, 배포·CI 스크립트를 다룬다.

이 층에서 멱등성이 가장 중요한 이유는 단순하다. **이 코드는 "새 환경에서 처음 실행"되는 상황을 위해 존재하는데, 정작 그 상황이 가장 검증이 안 된 경로다.** 개발자 로컬은 이미 셋업이 끝난 상태라 아무도 처음부터 돌려보지 않는다. 그래서 신입이 들어오거나 스테이징을 새로 만드는 날 터진다.

---

## uv 프로젝트 구성

의존성은 `pyproject.toml`에 선언하고 `uv.lock`을 커밋한다. lock 파일이 없으면 "같은 환경"이라는 말이 성립하지 않는다 — 어제의 `uv sync`와 오늘의 `uv sync`가 다른 버전을 가져올 수 있기 때문이다.

```toml
[project]
name = "myservice"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
]

[dependency-groups]
dev = ["pytest>=8.0"]

[tool.uv]
package = false          # 애플리케이션이면 빌드하지 않는다
```

| 명령 | 하는 일 | 멱등한가 |
|---|---|---|
| `uv sync` | lock에 적힌 상태로 `.venv`를 맞춘다. 남는 패키지는 지운다 | 예 — 이미 맞으면 아무 일도 안 한다 |
| `uv lock` | pyproject를 풀어 lock을 갱신한다 | 예 — 입력이 같으면 같은 lock |
| `uv run <cmd>` | 필요하면 sync하고 실행한다 | 예 |
| `uv add <pkg>` | pyproject와 lock을 함께 갱신한다 | 아니오 — 의존성을 추가하는 행위 자체 |

`uv sync --frozen`은 lock을 갱신하지 않고 그대로 재현한다. **CI와 Docker 빌드에서는 이걸 쓴다.** 빌드 도중에 lock이 바뀌면 이미지가 재현 불가능해진다.

`requirements.txt`를 만들지 않는다. 유지해야 할 정본이 둘이 되고, 둘은 반드시 갈라진다.

---

## Dockerfile

레이어 순서가 곧 캐시 전략이다. **자주 바뀌는 것을 뒤에 둔다** — 소스 한 줄 고칠 때마다 의존성을 다시 받으면 빌드가 매번 다른 시간을 쓴다.

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# 의존성만 먼저. 소스가 바뀌어도 이 레이어는 캐시된다.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**베이스 이미지 태그를 고정한다.** `python:3.12-slim`은 그나마 낫고 `python:latest`는 재현성이 없다. 엄밀히 하려면 다이제스트(`python:3.12-slim@sha256:...`)를 박는다.

**uv 이미지 버전도 고정한다.** `ghcr.io/astral-sh/uv:latest`를 쓰면 uv가 올라갈 때 빌드 결과가 조용히 바뀐다.

**BuildKit attestation을 끄지 않으면 재빌드가 비결정적이다.** BuildKit은 기본으로 provenance/SBOM attestation을 붙이는데 여기에 빌드 시각이 들어간다. 그래서 입력이 완전히 같아도 이미지 다이제스트가 매번 달라지고, `docker compose up -d --build`가 "이미지가 바뀌었다"고 판단해 컨테이너를 계속 다시 만든다. 상태는 같아지지만 no-op이 아니라서 재시작 churn이 생기고, 다이제스트 고정도 불가능해진다.

```bash
export BUILDX_NO_DEFAULT_ATTESTATIONS=1     # 같은 입력 → 같은 이미지 ID
```

이게 실제로 그런지는 두 번 빌드해서 ID를 비교하면 1분 안에 확인된다. 눈으로 보기 전엔 믿지 마라.

---

## compose

`docker compose up -d`는 선언한 상태로 수렴시키는 명령이다. 몇 번을 실행해도 결과가 같고, 정의가 바뀐 컨테이너만 다시 만든다.

```yaml
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://app:app@db:5432/app
    depends_on:
      db:
        condition: service_healthy      # 뜬 것과 받을 준비가 된 것은 다르다
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
      interval: 10s
      retries: 5

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10

volumes:
  pgdata:
```

**`depends_on`만으로는 부족하다.** 조건 없는 `depends_on`은 "컨테이너가 시작됐다"까지만 보장한다. DB가 연결을 받을 준비가 됐는지는 헬스체크가 판단한다. 이걸 빼면 첫 기동은 실패하고 재실행은 성공하는, 재현이 어려운 실패가 생긴다.

**마이그레이션을 앱 CMD에 붙이지 마라.** 앱을 3개로 스케일하면 마이그레이션이 3번 동시에 돈다. 별도 원샷 서비스나 배포 파이프라인의 한 단계로 분리한다.

**이름 있는 볼륨을 쓴다.** 컨테이너를 지웠다 다시 만들어도 데이터가 남는다. 반대로 파생 상태(캐시, 재생성 가능한 인덱스)는 볼륨에 두지 않는 게 낫다 — 지우고 다시 만드는 게 정상 복구 경로여야 한다.

---

## 스키마 마이그레이션

**직접 SQL을 쓴다면:**

```sql
CREATE TABLE IF NOT EXISTS users (
    id         BIGSERIAL PRIMARY KEY,
    email      TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;

-- 인덱스에 이름을 주면 IF NOT EXISTS가 의미를 갖는다
CREATE UNIQUE INDEX IF NOT EXISTS users_email_uniq ON users (lower(email));
```

**마이그레이션 도구(Alembic 등)를 쓴다면** 도구가 버전 테이블로 멱등성을 관리하므로 같은 리비전을 두 번 적용하지 않는다. 다만 **한 리비전 안의 내용은 여전히 직접 멱등하게 써야 한다.** 리비전 중간에 실패하면 버전 테이블은 갱신되지 않은 채 일부 DDL만 적용된 상태로 남는다.

```python
def upgrade():
    # DDL과 데이터 백필을 한 트랜잭션에 묶는다 — 중간 실패 시 전부 롤백
    op.add_column("users", sa.Column("display_name", sa.Text()))
    op.execute("UPDATE users SET display_name = email WHERE display_name IS NULL")
    op.alter_column("users", "display_name", nullable=False)
```

주의: PostgreSQL은 DDL이 트랜잭션 안에서 동작하지만 MySQL은 대부분의 DDL이 암묵적 커밋을 일으킨다. MySQL이라면 리비전을 더 잘게 쪼개라.

**되돌릴 수 없는 마이그레이션(컬럼 삭제, 타입 축소)은 재실행 안전성과 별개로 위험하다.** 가능하면 삭제를 다음 릴리스로 미루는 2단계 방식(먼저 안 쓰게 만들고, 나중에 지운다)을 택하고, 그 판단을 보고에 남겨라.

---

## 시드 데이터

시드는 "이 데이터가 존재하는 상태로 만든다"이지 "이 데이터를 넣는다"가 아니다. upsert가 기본이다.

```python
DEFAULT_ROLES = [
    {"code": "admin",  "name": "관리자"},
    {"code": "member", "name": "일반 사용자"},
]

def seed_roles(session):
    for role in DEFAULT_ROLES:
        session.execute(
            insert(Role)
            .values(**role)
            .on_conflict_do_update(index_elements=["code"], set_={"name": role["name"]})
        )
    session.commit()
```

`code`가 자연 키다. 자동 증가 `id`를 기준으로 삼으면 재실행마다 새 행이 쌓인다.

`on_conflict_do_update`와 `on_conflict_do_nothing` 중 무엇을 쓸지는 **누가 그 값의 주인인가**로 갈린다. 코드가 정본이면 update(코드 변경이 반영된다), 운영자가 UI에서 수정할 수 있으면 do_nothing(사람의 수정을 덮지 않는다).

**빈 목록으로 동기화하지 마라.** "전부 삭제"가 정당한 목표 상태가 되어버리는데, 실제로는 경로 오설정일 확률이 훨씬 높다. 소스가 비면 멈추고 알린다.

---

## 배포·CI

배포는 재시도가 일상이다 — 네트워크 실패, 타임아웃, 승인 대기. 재시도가 안전하지 않으면 사람이 매번 "지금 다시 눌러도 되나?"를 판단해야 한다.

- **이미지 태그는 커밋 SHA.** 같은 태그가 다른 내용을 가리키면 "같은 배포를 두 번"이 성립하지 않는다.
- **선언형 도구를 선호해라.** `kubectl apply` / `terraform apply`는 수렴하고, `kubectl create`는 두 번째 실행에서 터진다.
- **마이그레이션과 앱 배포가 한 스크립트에 있다면** 각각 개별적으로 재실행 가능해야 한다. 앱 배포가 실패해서 전체를 다시 돌릴 때 마이그레이션이 또 돌기 때문이다.
- **CI 캐시 키에 내용 해시를 써라.** 브랜치명 같은 가변 키를 쓰면 같은 커밋이 다른 결과를 낸다.

---

## 이 층의 체크리스트

- [ ] 깨끗한 환경에서 처음부터 실행해봤나? (컨테이너나 임시 디렉토리에서)
- [ ] **연속 두 번** 실행해봤나? 두 번째가 첫 번째와 같은 상태로 끝나는가?
- [ ] 중간에 `Ctrl+C`로 끊고 다시 실행하면 이어서 완성되는가?
- [ ] `uv.lock`을 커밋했나? Docker 빌드가 `--frozen`인가?
- [ ] 베이스 이미지와 도구 이미지 태그가 고정돼 있나?
- [ ] 사용자 소유 파일(`.env`, 로컬 설정)을 덮어쓰지 않는가?
- [ ] 실패했을 때 조용히 넘어가는 곳이 없는가? (`set -e`, 예외 삼키기)

두 번 실행 체크는 스크립트 한 줄이면 되고, CI에 넣어두면 매번 값을 한다:

```bash
./setup.sh && ./setup.sh
docker compose up -d && docker compose up -d
```
