# {서비스명} 기능 정의서

| 항목 | 값 |
|---|---|
| Last Updated | YYYY-MM-DD |

> `Last Updated` 는 문서 내용이 실제로 바뀐 날만 적는다. 시각은 적지 않는다.

---

## 서비스 개요

이 서비스가 누구를 위해 무엇을 하는지 두세 줄. 범위 밖인 것도 한 줄.

---

## 기능 목록

기능 ID 알파벳순.

| 기능 ID | 기능 | 진입점 | 상태 |
|---|---|---|---|
| `feature_id` | 한 줄 설명 | `METHOD /path` | 구현됨 |

---

## 기능별 상세

### feature_id: 기능 이름

**설명**: 이 기능이 사용자에게 주는 결과 한두 줄.

**입력과 결과**

| 입력 | 결과 |
|---|---|
| — | — |

**처리 흐름**: `xxx_router` 에서 `xxx_service.method` 로, `atomic_module_a`, `atomic_module_b` 순.

**구현 파일**

| 파일 | 층 | 역할 |
|---|---|---|
| `app/api/xxx_router.py` | api | 한 줄 |
| `app/service/xxx_service.py` | service | 한 줄 |

**테스트**

| 종류 | 파일 |
|---|---|
| 단위 | `tests/unit/test_feature_id_module.py` |
| 통합 | `tests/integ/test_feature_id.py` |

**제약과 미구현**: 없음.

---

## 공통 모듈

여러 기능이 함께 쓰는 파일.

| 파일 | 역할 | 쓰는 기능 |
|---|---|---|
| `app/common/logger.py` | structlog 로거 설정 | 전체 |
| `app/common/settings.py` | 환경변수 설정 | 전체 |
