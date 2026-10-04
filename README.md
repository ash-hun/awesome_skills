<div align="center">

# Awesome Skills

A curated collection of Claude Code skills, installable system-wide with a single command.

[![skills](https://img.shields.io/badge/skills-6-8A2BE2?style=flat)](.claude/skills) [![contributors](https://img.shields.io/github/contributors/ash-hun/awesome_skills?style=flat&logo=github&color=blue)](https://github.com/ash-hun/awesome_skills/graphs/contributors) [![forks](https://img.shields.io/github/forks/ash-hun/awesome_skills?style=flat&logo=github&color=blue)](https://github.com/ash-hun/awesome_skills/network/members) [![stars](https://img.shields.io/github/stars/ash-hun/awesome_skills?style=flat&logo=github&color=yellow)](https://github.com/ash-hun/awesome_skills/stargazers) [![issues](https://img.shields.io/github/issues/ash-hun/awesome_skills?style=flat&logo=github&color=red)](https://github.com/ash-hun/awesome_skills/issues) [![last commit](https://img.shields.io/github/last-commit/ash-hun/awesome_skills?style=flat&logo=github)](https://github.com/ash-hun/awesome_skills/commits/main) [![license](https://img.shields.io/github/license/ash-hun/awesome_skills?style=flat&color=green)](LICENSE)

</div>

---

## 무엇인가

[Claude Code](https://claude.com/claude-code)에서 쓰는 **Custom Skill** 을 모아둔 저장소다. 설치하면 어느 디렉토리에서 Claude Code를 열든 모든 스킬이 로드된다.

각 스킬은 `SKILL.md` 를 라우터로 두고 상세 절차를 `references/` 에 둔다. 트리거될 때 읽히는 건 `SKILL.md` 뿐이고 참조 문서는 필요한 때만 읽는다.

**요구사항**: macOS 또는 Linux, `git`, `bash`, 설치된 Claude Code.

---

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/ash-hun/awesome_skills/main/install.sh | bash
```

1. 저장소를 `~/.awesome-skills` 에 클론한다. 이미 있으면 최신 커밋으로 갱신한다.
2. 각 스킬을 `~/.claude/skills/<name>` 으로 심볼릭 링크한다.
3. 관리 명령어를 `~/.local/bin/awesome-skills` 에 설치한다.

설치 후 Claude Code를 재시작해야 스킬이 목록에 잡힌다. 실제 파일은 클론 한 곳에만 있고 `~/.claude/skills` 에는 링크만 놓이므로, 클론에서 고친 내용은 곧바로 전역에 반영된다.

### 관리 명령어

| 명령 | 동작 |
|---|---|
| `awesome-skills link` | 심볼릭 링크를 만들거나 갱신한다 |
| `awesome-skills update` | 최신 커밋을 받아온 뒤 다시 링크한다 |
| `awesome-skills list` | 스킬별 링크 상태를 출력한다 |
| `awesome-skills uninstall [--purge]` | 이 도구가 만든 링크만 제거한다. `--purge` 는 클론까지 지운다 |
| `awesome-skills brief [on\|off\|status]` | `humanism_talk` 의 `brief` 모드를 모든 세션에 적용하거나 해제한다 |

모든 명령은 여러 번 실행해도 결과가 같다.

<details>
<summary>brief 모드 항상 켜기</summary>

```bash
awesome-skills brief on
```

`~/.claude/settings.json` 에 `SessionStart` 와 `PostCompact` 훅을 등록해서, 세션이 시작될 때와 컨텍스트가 압축된 뒤에 `humanism_talk/references/brief.md` 의 규칙을 주입한다. 기존 설정과 다른 훅은 그대로 둔다. `jq` 가 필요하다. 설치 스크립트는 이 명령을 자동으로 실행하지 않는다.

| 끄는 방법 | 범위 |
|---|---|
| `awesome-skills brief off` | 훅 자체를 제거 |
| `<project>/.claude/humanism_talk.off` 파일 생성 | 그 프로젝트에서만 무시 |
| `~/.claude/humanism_talk.off` 파일 생성 | 훅은 두고 전역으로 무시 |
| 세션에서 `"stop caveman"`, `"normal mode"`, `/humanism_talk off` | 그 세션에서만 해제 |

</details>

<details>
<summary>이름이 겹칠 때, 설정 파일, 환경 변수</summary>

**이름이 겹칠 때**: `~/.claude/skills/<name>` 에 실제 디렉토리가 이미 있으면 그 스킬은 건너뛰고 목록을 출력한다. 직접 만든 전역 스킬을 덮어쓰지 않기 위해서다. 저장소 쪽을 쓰려면 그 디렉토리를 옮긴 뒤 `awesome-skills link` 를 다시 실행한다. `uninstall` 도 링크가 `~/.awesome-skills` 안을 가리킬 때만 지운다.

**설정 파일**: 설치 스크립트는 `~/.claude/settings.json` 을 건드리지 않는다. 이 저장소의 `.claude/settings.json` 에 등록된 [obra/superpowers](https://github.com/obra/superpowers) 플러그인을 쓰려면 Claude Code에서 직접 마켓플레이스를 추가한다.

**환경 변수**

| 변수 | 기본값 | 용도 |
|---|---|---|
| `AWESOME_SKILLS_HOME` | `~/.awesome-skills` | 클론 위치 |
| `AWESOME_SKILLS_BRANCH` | `main` | 추적할 브랜치 |
| `AWESOME_SKILLS_BIN` | `~/.local/bin` | CLI 설치 위치 |
| `AWESOME_SKILLS_REPO` | 이 저장소의 GitHub URL | 클론할 원격 (포크에서 쓸 때) |
| `CLAUDE_CONFIG_DIR` | `~/.claude` | Claude Code 설정 디렉토리 |

</details>

---

<!-- skills:start -->
## 설치된 스킬

| 스킬 | 호출 | 한 줄 요약 | 출처 |
|---|---|---|---|
| [`common`](.claude/skills/common/SKILL.md) | `/common [create\|eval\|describe\|docs]` | 스킬 자체를 만들고 검증하고 문서화하는 메타 스킬 | [anthropics/skills](https://github.com/anthropics/skills) + 이 저장소 |
| [`humanism_talk`](.claude/skills/humanism_talk/SKILL.md) | `/humanism_talk [brief\|grill\|off]` | 대화 규율. 응답을 압축하고, 계획을 라운드로 캐묻는다 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) + [mattpocock/skills](https://github.com/mattpocock/skills) |
| [`develop_rule`](.claude/skills/develop_rule/SKILL.md) | `/develop_rule [lite\|full\|ultra\|review\|audit\|debt\|spec\|handoff]` | 재현 가능한 개발. 최소로 짓고, 두 번 돌려도 같게, 문서는 코드에서 유도 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) + [mattpocock/skills](https://github.com/mattpocock/skills) + 이 저장소 |
| [`msg_check`](.claude/skills/msg_check/SKILL.md) | `/msg_check` | 커밋, PR, 진행 보고 문안을 네 기준으로 검수하고 수정안을 낸다 | 이 저장소 |
| [`research_kit`](.claude/skills/research_kit/SKILL.md) | `/research_kit` | AI 연구와 실험 키트. 조사, 설계, 실행과 로깅, 분석과 보고서를 잇는다 | 이 저장소 + Anthropic `deep-research` |
| [`refactoring_service`](.claude/skills/refactoring_service/SKILL.md) | `/refactoring_service [설계문서 경로]` | 기존 서비스를 리팩토링하고 as-is 대비 to-be 변경 문서를 남긴다 | 이 저장소 |

`refactoring_service` 는 명시 호출 전용이다. 나머지는 대화 문맥에서도 자동으로 잡힌다.

## 스킬 상세

<details>
<summary><code>common</code>: 스킬 라이프사이클</summary>

스킬을 만들고, 검증하고, 트리거 문구를 다듬고, 문서에 올리는 네 단계를 한 흐름으로 잡는다. 각 모드는 끝날 때 다음 단계를 제안한다.

| 모드 | 하는 일 |
|---|---|
| `create` | 의도 파악, 인터뷰, `SKILL.md` 초안, 테스트 케이스 작성 |
| `eval` | 테스트 실행, 채점, 브라우저 뷰어로 사람 리뷰, 개선 루프 |
| `describe` | 트리거 평가 쿼리를 만들어 `description` 을 최적화 |
| `docs` | 이 README 의 카탈로그 구간을 갱신 |

범위 밖: 스킬이 아닌 일반 코드와 문서 작성, `.skill` 패키징.

부속: `references/` 5개, `agents/` 3개, `scripts/` 9개, `assets/` 1개, `eval-viewer/`.

</details>

<details>
<summary><code>humanism_talk</code>: 대화 규율</summary>

말은 줄이고, 구조는 드러내고, 추측은 질문으로 바꾸고, 판단은 근거로 한다.

**`brief`** (기본, 지속 모드): 필러, 인사치레, 헤지를 걷어내고, 실질적인 지시문은 실행 전에 세 요소로 분해해 보여준다.

- **목표**: 그 요청이 이루려는 최종 상태
- **인과**: 맥락에서 원인, 원인에서 결과. 확인된 사실과 추정을 구분한다
- **액션**: 동사로 시작하는 행동 목록. 사용자 몫은 `[사용자]` 표시

함께 강제하는 태도는 셋이다. 물은 만큼만 답한다. 근거 없이 동의하지 않는다. 긴 대시, 가운뎃점, 지어낸 항목 번호 같은 말버릇을 쓰지 않는다. 부정어, 숫자, 코드, 사용자의 언어는 압축하지 않는다.

**`grill`** (단발): 계획과 설계를 design tree 로 매핑하고, 지금 물을 수 있는 질문을 한 라운드에 모아 AskUserQuestion 으로 묻는다. 첫 선택지가 추천 답안이다. 사용자가 합의를 확인하기 전까지 실행하지 않는다.

해제: `/humanism_talk off`, `"stop caveman"`, `"normal mode"`.

</details>

<details>
<summary><code>develop_rule</code>: 재현 가능한 개발</summary>

같은 입력이면 같은 결과가 나와야 한다. 세 축으로 강제한다.

- **최소**: 안 지은 코드가 가장 재현 가능하다
- **수렴**: 지은 것은 두 번 실행해도 같은 상태로 간다
- **투영**: 문서는 코드에서 유도한다. 재생성해도 diff 가 없다

지속 모드는 사다리를 탄다. 애초에 필요한가, 이미 코드베이스에 있나, 표준 라이브러리, 플랫폼 네이티브, 이미 설치된 의존성, 한 줄, 최소 구현 순으로 보고 처음 성립하는 칸에서 멈춘다. 강도는 `lite`, `full`(기본), `ultra`.

| 단발 모드 | 하는 일 |
|---|---|
| `review` | 지금의 diff 에서 과잉설계 찾기 |
| `audit` | 저장소 전체의 과잉설계를 삭제량 큰 순으로 |
| `debt` | `ponytail:` 과 `idempotent:` 마커를 장부로 수집 |
| `spec` | `docs/api-spec.md`, `docs/screen-spec.md` 생성과 갱신 |
| `handoff` | 대화를 인수인계 문서로 압축 |

단순화하지 않는 것: 신뢰 경계의 입력 검증, 데이터 손실을 막는 에러 처리, 보안, 접근성 기본, 사용자가 명시적으로 요청한 것. `review` 와 `audit` 은 복잡도만 보며 정확성, 보안, 성능은 범위 밖이다.

처음 켤 때 원칙 카드를 프로젝트의 `CLAUDE.md` 에 마커로 고정한다.

부속: `references/` 9개, `assets/` 3개.

</details>

<details>
<summary><code>msg_check</code>: 작업 메시지 검수</summary>

커밋 메시지, PR 제목과 본문, 진행 보고를 맥락 없이 빠르게 읽는 독자 입장에서 검수한다. 사용자가 쓴 문안이 입력이고 지적 사항과 수정안이 출력이다.

| 기준 | 보는 것 |
|---|---|
| 가시성 | 첫 줄만 읽어도 무엇을 했는지 알 수 있는가 |
| 자연스러운 한국어 | "~를 진행했습니다", "~되어지다" 같은 번역투 |
| 과잉 설명 | 작업 내용, 결과, 특이사항 셋만 남았는가 |
| 지칭 표현 | "그거", "해당 부분"을 독자가 알아볼 이름으로 |

수정안은 원문에 없는 사실을 채우지 않는다. 커밋과 PR 은 AskUserQuestion 으로 승인받은 뒤에만 실행한다.

범위 밖: 초안 작성, 코드 리뷰, 이슈와 릴리스 노트.

부속: `references/` 4개, `evals/`.

</details>

<details>
<summary><code>research_kit</code>: AI 연구와 실험 키트</summary>

LLM 평가, 비교대조 실험, 모델 학습, 새 가설 탐색을 네 단계로 다룬다. 사용자가 있는 단계부터 시작하고 산출물은 `research/<slug>/` 에 모은다.

| 단계 | 산출물 | 핵심 |
|---|---|---|
| 질문과 선행 조사 | `survey.md` | light(기본, 직접 검색) 또는 full(조사 서브에이전트 병렬) |
| 가설과 실험 설계 | `design.md` | 반증 가능한 가설, 한 번에 한 변수, 판정 기준을 실행 전에 숫자로 |
| 실행과 로깅 | `runs/<run-id>/card.md` | config, git hash, seed, 환경을 실험 카드에 기록 |
| 분석과 보고서 | `analysis.md`, `report.md` | 쌍체 bootstrap, McNemar. 지지, 기각, 판정 불가로 판정 |

숫자는 실행 결과나 출처 있는 문헌에서만 나온다.

범위 밖: 연구와 무관한 웹 조사, 논문 원고 조판, 학습 인프라 구축.

부속: `references/` 5개, `assets/` 3개, `scripts/snapshot_env.sh`, `evals/`.

</details>

<details>
<summary><code>refactoring_service</code>: 서비스 리팩토링과 변경 문서</summary>

이미 만들어진 서비스의 구조를 동작 변경 없이 바꾸고, 무엇을 왜 바꿨는지 문서로 남긴다. 설계문서 경로를 인자로 주면 그 문서대로, 주지 않으면 기본 방안(영속성 있는 운영 구조, 확장성을 고려한 구조)으로 간다.

1. 방향 확정
2. as-is 분석. 기존 테스트는 하나씩 읽고 의도를 정리한다
3. 모듈별 계획을 보여주고 승인받는다. 승인 전에는 코드를 고치지 않는다
4. 기존 테스트와 mypy 로 기준선을 잡고, 테스트가 없는 영역은 현재 동작을 고정하는 테스트를 먼저 쓴다
5. 모듈 단위로 리팩토링하고 단위마다 테스트를 돌린다
6. 전체 테스트, mypy, 의존 방향을 기준선과 비교한다
7. 변경 문서를 쓴다

손대는 Python 코드에는 항상 코드 규칙을 적용한다.

| 규칙 | 내용 |
|---|---|
| 호출 계층과 모듈명 | 의존은 한 방향. import 경로만 읽고 역할을 알 수 있게 짓는다 |
| 멱등성과 공통 모듈 | 재사용되는 것은 `common/` 으로. logger 는 반드시 공통 모듈 |
| 타입 힌트 | 모든 함수의 인자와 반환값에 필수 |
| 객체화와 상속 | 기능 관점의 추상화를 적극적으로. 추상 클래스는 가급적 쓰지 않고 상속 깊이 1에서 2 |
| 파일 최상단 주석 | 전체 프로젝트 관점에서 이 모듈이 무엇인지 쓴다 |
| 테스트 | `tests/unit/`(모듈별)과 `tests/integ/`(API 수준 시나리오 e2e). 둘 다 통과 |
| 도구 | uv, pytest, mypy |
| OpenAPI 문서 | FastAPI 기준. 기능 설명, 인자 설명, 사용 예제 |

설계문서와 코드 규칙이 부딪히면 프로젝트 전체에서 해당 모듈까지 위에서 아래로 설명한 뒤 사용자에게 묻는다. 코드 규칙이 다루지 않는 판단은 `develop_rule` 을 따른다.

변경 문서는 대상 서비스의 `docs/refactoring/YYYY-MM-DD-<서비스명>.md` 에 저장하고 구조는 개요, 리팩토링 내용(모듈별 전후 비교), 비고 및 특이사항으로 고정이다.

범위 밖: 새 기능 추가, 버그 수정, 커밋과 푸시.

부속: `references/` 2개, `assets/` 1개, `evals/`.

</details>

## 디렉토리 구조

```
awesome_skills/
├── install.sh                     # 부트스트랩 (클론 또는 갱신 후 링크)
├── bin/awesome-skills             # link / update / list / uninstall / brief
├── hooks/inject-brief.sh          # SessionStart, PostCompact 에 brief 규칙 주입
└── .claude/
    ├── settings.json              # 마켓플레이스, 플러그인 활성화
    └── skills/
        ├── common/                # SKILL.md + references(5) + agents(3) + scripts(9) + assets(1) + eval-viewer
        ├── humanism_talk/         # SKILL.md + references(1) + README.md
        ├── develop_rule/          # SKILL.md + references(9) + assets(3)
        ├── msg_check/             # SKILL.md + references(4) + evals
        ├── research_kit/          # SKILL.md + references(5) + assets(3) + scripts(1) + evals
        └── refactoring_service/   # SKILL.md + references(2) + assets(1) + evals
```

`.claude/settings.json` 에 활성화된 [obra/superpowers](https://github.com/obra/superpowers) 는 로컬 `SKILL.md` 가 아니라 플러그인이라 위 목록과 별개로 관리된다.

## 스킬 추가하기

새 기능은 먼저 기존 스킬의 모드로 붙일 수 있는지 본다. 스킬이 늘어나면 모델이 어느 것을 켤지 헷갈려 트리거 정확도가 떨어진다. 새 스킬이 맞다면 `/common create` 로 시작한다.

- **frontmatter**: `name` 은 디렉토리 이름과 같아야 한다. `description` 은 모델이 언제 켤지 판단하는 근거다.
- **참조 파일**: 스크립트와 템플릿은 스킬 디렉토리 안에 두고 상대 경로로 참조한다.
- **이름 보존**: 기존 스킬을 고칠 때 이름을 바꾸지 않는다.

작업이 끝나면 `/common docs` 로 이 카탈로그를 갱신하고, 커밋과 푸시 후 `awesome-skills update` 로 전역에 반영한다.

## 크레딧

기존 오픈소스 스킬을 실사용 기준으로 재구성했다. 원저작권은 각 원저작자에게 있다.

| 출처 | 라이선스 | 흡수된 곳 |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) `skill-creator` | Apache-2.0 ([전문](.claude/skills/common/LICENSE.txt)) | `common` 의 `create`, `eval`, `describe` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | `develop_rule` 의 최소 축, `review`, `audit`, `debt` |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT | `humanism_talk` 의 `brief` |
| [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | `humanism_talk` 의 `grill`, `develop_rule` 의 `handoff` |
| Anthropic `deep-research` 스킬 (Claude 내장) | 미확인 | `research_kit` 의 full 조사 절차. 원문을 옮기지 않고 다시 씀 |
| 이 저장소 | MIT | `common` 의 `docs`, `develop_rule` 의 수렴과 투영 축, `msg_check`, `research_kit`, `refactoring_service` |

ponytail 의 `ponytail-help` 와 `ponytail-gain` 은 옮기지 않았다. 필요하면 원본 저장소를 쓴다.
<!-- skills:end -->

---

## 기여하기

스킬 추가, 문서 수정, 버그 제보 모두 환영한다.

1. 저장소를 포크하고 위 **스킬 추가하기** 를 따라 작업한다.
2. 외부에서 가져온 스킬이면 원저작자와 라이선스를 PR 본문에 밝힌다. MIT, Apache-2.0 계열이 아니면 먼저 이슈로 논의한다.
3. `awesome-skills link` 실행 후 Claude Code를 재시작해 스킬이 목록에 잡히는지 확인하고 PR 을 연다.

버그 제보와 스킬 제안은 [Issues](https://github.com/ash-hun/awesome_skills/issues)로.

## 라이선스

설치 스크립트와 자체 작성 스킬은 [MIT 라이선스](LICENSE)를 따른다. 외부에서 가져온 스킬의 저작권은 원저작자에게 있으며 출처는 위 **크레딧** 표에 있다.
