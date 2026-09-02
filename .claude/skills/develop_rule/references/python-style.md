# 모듈 분리와 파이썬 규약

`develop_rule` 스킬의 참조 문서. 파일을 어떻게 나누고 무엇을 어디에 쓰는지.

---

## 모듈을 어떻게 나누는가

기능/목적 단위 분리는 멱등성과 같은 뿌리를 갖는다. **재실행해도 안전한지 판단하려면, 그 단위가 무슨 부수효과를 내는지 한눈에 보여야 한다.** 한 함수가 계산도 하고 파일도 쓰고 API도 호출하면 그 판단이 불가능하다.

**함수 하나 = 결정 하나, 또는 부수효과 하나.** 둘 다 하지 않는다. 계산과 I/O가 섞이면 테스트할 때마다 DB가 필요해지고, "이거 두 번 불러도 되나?"에 답할 수 없다.

```python
# 섞여 있다 — 재실행 안전성 판단 불가, 테스트에 DB 필요
def process_order(order_id):
    order = db.get(Order, order_id)
    total = sum(i.price * i.qty for i in order.items)
    if total > 100_000:
        total *= 0.9
    db.execute(update(Order).where(Order.id == order_id).values(total=total))
    send_email(order.user.email, f"합계 {total}")

# 결정과 부수효과가 분리됐다
def calculate_total(items) -> Decimal:          # 순수 — 몇 번을 불러도 같다
    total = sum(i.price * i.qty for i in items)
    return total * Decimal("0.9") if total > 100_000 else total

def apply_order_total(order_id, total):         # 부수효과 하나, 멱등
    db.execute(update(Order).where(Order.id == order_id).values(total=total))
```

**class를 쓰는 기준:** 유지할 상태가 있거나, 주입할 의존성이 있을 때. 그 둘 다 없으면 함수다. 함수 하나를 담으려고 만든 class, `__init__`이 비어 있는 class, 메서드가 전부 `self`를 안 쓰는 class는 함수로 내려라.

반대로 DB 세션·HTTP 클라이언트·설정을 여러 함수가 공유한다면 그건 class가 맞다.

**파일을 나누는 기준은 목적이지 종류가 아니다.** `models.py` / `services.py` / `utils.py`처럼 종류로 나누면 기능 하나를 고치는 데 파일 다섯 개를 열게 된다. 목적으로 나누면 (`order/`, `payment/`, `notification/`) 그 기능의 멱등성을 한 디렉토리 안에서 검증할 수 있다.

`utils.py`가 커지기 시작하면 경고 신호다. 그 안에 이름 없는 도메인 개념이 숨어 있다는 뜻이다.

---

## 파이썬 파일 규약

### 최상단 설명은 한 줄

그 파일이 무엇을 담고 있는지 한 줄로 지목한다. 배경이나 설계 근거를 문단으로 풀지 않는다 — 코드가 바뀌면 가장 먼저 거짓말이 되는 부분이고, 읽는 사람은 파일 이름만으로 이미 절반을 알고 있다.

```python
"""MDX 텍스트를 PostRecord로 바꾸는 순수 파서."""
```

설명이 한 줄에 안 담기면 파일이 두 가지 일을 하고 있다는 신호다. 문장을 늘리지 말고 파일을 쪼개라.

### import는 두 그룹

외부(표준 라이브러리 + 서드파티)를 위에 모아 **줄 길이 오름차순**, 한 줄 띄고, 로컬 참조를 **줄 길이 내림차순**.

```python
import yaml
from pathlib import Path
from dataclasses import dataclass

from .repository import PostSummary, count_posts, list_posts
from .seed import EmptyContentError, seed
from ..db import session
```

길이순은 취향이 아니라 프로젝트 합의다. 정렬 규칙이 하나로 고정돼 있으면 import 블록의 diff가 의미 있는 변경만 담는다.

### 없어도 되는 import는 넣지 않는다

`from __future__ import annotations`가 대표적이다. 3.10부터 `X | None`이 런타임에서 그냥 동작하므로, 지원 하한이 3.10 이상이면 이 줄은 아무 일도 하지 않는다. 습관으로 붙는 줄은 "이게 왜 여기 있지"를 매번 유발하고, 정말 필요한 곳에서까지 무게를 잃게 만든다.

넣기 전에 물어라 — **이 줄을 지우면 무엇이 깨지는가?** 답이 안 나오면 지운다.

### 상수는 변수와 섞지 않는다

모듈 상수는 import 직후에 모아 선언하고, 함수 안에 리터럴로 흩뿌리지 않는다.

```python
# 나쁨 — 기본값이 호출부에 박혀 있어 유일한지 알 수 없다
def load_settings():
    return Settings(
        content_dir=Path(os.getenv("CONTENT_DIR", "backend/content/posts")),
        allowed_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    )

# 좋음 — 값이 한 곳에 모여 있다
DEFAULT_CONTENT_DIR = BACKEND_ROOT / "content" / "posts"
DEFAULT_ALLOWED_ORIGINS = "http://localhost:3000"

def load_settings():
    return Settings(
        content_dir=Path(os.getenv("CONTENT_DIR", DEFAULT_CONTENT_DIR)),
        allowed_origins=os.getenv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS).split(","),
    )
```

멱등성 관점에서 이게 중요한 이유: 설정 기본값이 여러 곳에 흩어져 있으면 **"같은 설정을 두 번 읽으면 같은 값인가"를 눈으로 확인할 수 없다.** 한 곳에 모여 있으면 확인이 1초에 끝난다.

---

## 코드 위생

**주석은 왜(why)만 남긴다.** 코드가 이미 말하는 것을 한국어로 번역하지 마라. 읽는 사람의 눈만 소모하고, 코드가 바뀌면 거짓말이 된다.

```python
# 나쁨 — 코드를 그대로 반복한다
# 사용자 ID로 사용자를 조회한다
user = db.get(User, user_id)

# 좋음 — 코드에서 읽을 수 없는 이유를 남긴다
# 결제사가 같은 웹훅을 최대 3회 재전송한다. event_id로 걸러야
# 중복 적립이 안 생긴다.
if processed_events.contains(event_id):
    return
```

멱등성 맥락에서 주석이 값을 하는 거의 유일한 경우가 이거다 — **왜 이 코드가 재실행 안전한지(또는 안전하지 않은지)가 코드만 봐서는 안 보일 때.**

**설명이 코드보다 길면 설명을 지운다.** 단순화를 변호하는 문단은 복잡성이 산문으로 돌아온 것이다.

**일부러 멱등하지 않게 둔 곳은 `idempotent:` 마커로 표시한다.** 이유와 멱등하게 만드는 방법을 함께 적는다. 그래야 다음 사람이 버그로 오해하고 "고치지" 않고, 나중에 진짜로 필요해졌을 때 무엇을 해야 하는지 안다.

```python
# idempotent: 감사 로그는 매 시도가 기록돼야 하므로 의도적으로 append다.
# 중복 제거가 필요해지면 (actor, action, request_id)로 유니크 제약을 건다.
audit_log.append(entry)
```

**import는 실제로 쓰는 것만.** 새 의존성 전에 표준 라이브러리로 되는지 먼저 확인해라 — `pathlib`, `dataclasses`, `functools`, `itertools`, `contextlib`, `uuid`, `hashlib`가 대부분을 덮는다. 의존성 하나는 새 환경에서 재현해야 할 상태가 하나 늘어난 것이다.

**타입 힌트는 남기고 설명 주석은 줄여라.** `def apply(o, t):`에 주석을 다는 것보다 `def apply_order_total(order_id: int, total: Decimal) -> None:`이 낫다.

---

