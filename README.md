<div align="center">

# Awesome Skills

A curated collection of Claude Code skills, installable system-wide with a single command.

[![skills](https://img.shields.io/badge/skills-3-8A2BE2?style=flat)](.claude/skills) [![contributors](https://img.shields.io/github/contributors/ash-hun/awesome_skills?style=flat&logo=github&color=blue)](https://github.com/ash-hun/awesome_skills/graphs/contributors) [![forks](https://img.shields.io/github/forks/ash-hun/awesome_skills?style=flat&logo=github&color=blue)](https://github.com/ash-hun/awesome_skills/network/members) [![stars](https://img.shields.io/github/stars/ash-hun/awesome_skills?style=flat&logo=github&color=yellow)](https://github.com/ash-hun/awesome_skills/stargazers) [![issues](https://img.shields.io/github/issues/ash-hun/awesome_skills?style=flat&logo=github&color=red)](https://github.com/ash-hun/awesome_skills/issues) [![last commit](https://img.shields.io/github/last-commit/ash-hun/awesome_skills?style=flat&logo=github)](https://github.com/ash-hun/awesome_skills/commits/main) [![license](https://img.shields.io/github/license/ash-hun/awesome_skills?style=flat&color=green)](LICENSE)

</div>

---

## 무엇인가

[Claude Code](https://claude.com/claude-code)에사 유용하게 사용할 수 있는 **Custom Skill** 을 모아둔 저장소다. 설치하면 어느 디렉토리에서 Claude Code를 열든 모든 스킬이 로드된다.

각 스킬은 `SKILL.md` 를 라우터로 두고 상세 절차를 `references/` 에 둔다. 트리거될 때 항상 읽히는 건 `SKILL.md` 뿐이라 컨텍스트를 적게 쓰고, 필요한 참조만 그때 읽는다. 부속 파일은 전부 스킬 디렉토리 안에 있어 저장소 바깥 경로에 의존하지 않는다.

**요구사항** — macOS 또는 Linux, `git`, `bash`. Claude Code가 이미 설치되어 있어야 한다.

---

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/ash-hun/awesome_skills/main/install.sh | bash
```

이 한 줄이 하는 일은 세 가지다.

1. 저장소를 `~/.awesome-skills` 에 클론한다. 이미 있으면 최신 커밋으로 갱신한다.
2. 각 스킬을 `~/.claude/skills/<name>` 으로 심볼릭 링크한다.
3. 관리 명령어를 `~/.local/bin/awesome-skills` 에 설치한다.

설치가 끝나면 Claude Code를 재시작해야 새 스킬이 목록에 잡힌다. `~/.local/bin` 이 `PATH` 에 없으면 설치 스크립트가 추가할 줄을 알려준다.

파이프로 실행하는 스크립트를 그대로 믿기 어렵다면, 먼저 내용을 확인한 뒤 실행해도 된다.

```bash
curl -fsSL https://raw.githubusercontent.com/ash-hun/awesome_skills/main/install.sh -o install.sh
less install.sh
bash install.sh
```

### 설치 후 배치

```
~/.awesome-skills/                       # git clone
├── install.sh
├── bin/awesome-skills
└── .claude/skills/<name>/SKILL.md

~/.claude/skills/<name>      ->  ~/.awesome-skills/.claude/skills/<name>
~/.local/bin/awesome-skills  ->  ~/.awesome-skills/bin/awesome-skills
```

실제 파일은 클론 한 곳에만 존재하고 `~/.claude/skills` 에는 링크만 놓인다. 따라서 `awesome-skills update` 한 번이면 모든 스킬이 함께 갱신되고, 클론에서 스킬을 직접 고치면 그 변경이 곧바로 전역에 반영된다.

### 관리 명령어

| 명령 | 동작 |
|---|---|
| `awesome-skills link` | 심볼릭 링크를 만들거나 갱신한다 |
| `awesome-skills update` | 최신 커밋을 받아온 뒤 다시 링크한다 |
| `awesome-skills list` | 스킬별 링크 상태를 출력한다 |
| `awesome-skills uninstall` | 이 도구가 만든 링크만 제거한다 |
| `awesome-skills uninstall --purge` | 링크와 함께 `~/.awesome-skills` 클론까지 지운다 |
| `awesome-skills brief [on\|off\|status]` | `humanism_talk` 의 압축 응답 모드를 모든 세션에 적용/해제 |

모든 명령은 멱등이다. 여러 번 실행해도 한 번 실행한 것과 결과가 같다.

### brief 모드 항상 켜기

`humanism_talk` 스킬의 `brief` 모드(압축 응답 + 목표·인과·액션 구조)는 매번 부르지 않고 모든 세션에 자동으로 걸 수 있다.

```bash
awesome-skills brief on
```

`~/.claude/settings.json` 에 `SessionStart` 와 `PostCompact` 훅을 등록한다. 새 세션이 시작될 때와 컨텍스트가 압축된 뒤에 `humanism_talk/references/brief.md` 의 규칙이 주입된다. 기존 설정과 다른 훅은 그대로 두고, 여러 번 실행해도 훅은 하나만 남는다. `jq` 가 필요하다.

끄는 방법은 세 가지다.

| 방법 | 범위 |
|---|---|
| `awesome-skills brief off` | 훅 자체를 제거 |
| `<project>/.claude/humanism_talk.off` 파일 생성 | 그 프로젝트에서만 무시 |
| `~/.claude/humanism_talk.off` 파일 생성 | 훅은 두고 전역으로 무시 |

세션 안에서 일시적으로 풀려면 `"stop caveman"`, `"normal mode"`, `/humanism_talk off` 라고 말하면 된다.

이 명령은 설치 스크립트가 자동으로 실행하지 않는다. `~/.claude/settings.json` 은 사용자 개인 설정이라 명시적으로 켤 때만 건드린다.

### 이름이 겹칠 때

`~/.claude/skills/<name>` 에 이미 **실제 디렉토리**가 있으면 그 스킬은 건너뛰고, 설치가 끝날 때 건너뛴 목록을 출력한다. 직접 작성한 전역 스킬을 덮어쓰지 않기 위한 동작이다. 저장소 쪽으로 넘기고 싶다면 그 디렉토리를 옮기거나 지운 뒤 `awesome-skills link` 를 다시 실행한다. 이미 심볼릭 링크인 경우에는 그대로 갱신한다.

`uninstall` 도 같은 원칙을 따른다. 링크 대상이 `~/.awesome-skills` 안을 가리킬 때만 지우므로, 직접 만든 스킬과 다른 곳을 가리키는 링크는 그대로 남는다.

### 설정 파일

설치 스크립트는 `~/.claude/settings.json` 을 건드리지 않는다. 이 저장소의 `.claude/settings.json` 에 등록된 [obra/superpowers](https://github.com/obra/superpowers) 플러그인까지 쓰려면 Claude Code에서 직접 마켓플레이스를 추가해야 한다.

### 환경 변수

| 변수 | 기본값 | 용도 |
|---|---|---|
| `AWESOME_SKILLS_HOME` | `~/.awesome-skills` | 클론 위치 |
| `AWESOME_SKILLS_BRANCH` | `main` | 추적할 브랜치 |
| `AWESOME_SKILLS_BIN` | `~/.local/bin` | CLI 설치 위치 |
| `AWESOME_SKILLS_REPO` | 이 저장소의 GitHub URL | 클론할 원격 (포크에서 쓸 때) |
| `CLAUDE_CONFIG_DIR` | `~/.claude` | Claude Code 설정 디렉토리 |

---

<!-- skills:start -->
## 설치된 스킬

세 개다. 각각이 여러 모드를 가지며, 모드는 인자로 고르거나 대화 문맥에서 자동으로 잡힌다.

| 스킬 | 호출 | 한 줄 요약 | 출처 |
|---|---|---|---|
| [`common`](.claude/skills/common/SKILL.md) | `/common [create\|eval\|describe\|docs]` | 스킬 자체를 만들고 검증하고 문서화하는 메타 스킬 | [anthropics/skills](https://github.com/anthropics/skills) + 이 저장소 |
| [`humanism_talk`](.claude/skills/humanism_talk/SKILL.md) | `/humanism_talk [brief\|grill\|off]` | 대화 규율. 응답을 압축하고, 계획을 라운드로 캐묻는다 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) + [mattpocock/skills](https://github.com/mattpocock/skills) |
| [`develop_rule`](.claude/skills/develop_rule/SKILL.md) | `/develop_rule [lite\|full\|ultra\|review\|audit\|debt\|spec\|handoff]` | 재현 가능한 개발. 최소로 짓고, 두 번 돌려도 같게, 문서는 코드에서 유도 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) + [mattpocock/skills](https://github.com/mattpocock/skills) + 이 저장소 |

세 스킬 모두 `SKILL.md` 를 라우터로 두고 상세 절차는 `references/` 에 둔다. 트리거될 때 항상 읽히는 건 `SKILL.md` 뿐이고, 나머지는 해당 모드에 들어갈 때만 읽는다.

---

## 스킬 상세

### `common` — 스킬 라이프사이클

만들고 → 검증하고 → 이름표를 다듬고 → 문서에 올리는 네 단계를 한 흐름으로 잡는다. 도구가 따로 놀면 만들어놓고 검증을 건너뛰거나, 고쳐놓고 카탈로그를 안 고쳐 문서가 썩기 때문이다.

| 모드 | 하는 일 |
|---|---|
| `create` | 의도 파악 → 인터뷰 → SKILL.md 초안 → 테스트 케이스 작성 |
| `eval` | 테스트 실행 → 채점 → 브라우저 뷰어로 사람 리뷰 → 개선 루프 |
| `describe` | 트리거 eval 쿼리 20개를 만들어 `description` 을 최적화 |
| `docs` | 이 README 의 카탈로그 구간을 갱신 |

각 모드는 끝날 때 다음 단계를 **제안**한다. 강요하지 않는다 — "그냥 대충 만들어줘"라고 하면 그 말을 따른다. 다만 스킬 파일을 건드린 세션에서 README 가 옛날 내용이면 그 사실은 반드시 알린다.

문서를 쓸 때 `description` 을 그대로 베끼지 않는다. 그건 모델용 트리거 문구지 사람용 설명이 아니라서, 카탈로그를 만들 때는 모든 `SKILL.md` 의 **본문까지** 읽는다. 출처·라이선스는 추측하지 않고 LICENSE → frontmatter → GitHub API 순으로 확인하며, 끝내 모르면 빈칸으로 두고 보고한다.

범위 밖: 스킬이 아닌 일반 코드·문서 작성. `.skill` 패키징은 하지 않는다 — 이 저장소는 전역 설치 방식이라 커밋·푸시가 그 역할을 한다.

부속: `references/` 5개, `agents/` 3개(채점·블라인드 비교·분석), `scripts/` 8개, `eval-viewer/`.

### `humanism_talk` — 대화 규율

말할 때와 물을 때를 같은 원칙으로 다룬다. **말은 줄이고, 구조는 드러내고, 추측은 질문으로 바꾼다.**

**`brief`** (기본, 지속 모드) — 관사·필러·인사치레·헤지를 걷어내고, 실질적인 지시문은 실행 *전에* 세 요소로 분해해 보여준다.

- **목표** — 그 요청이 이루려는 최종 상태. 표면 요청을 그대로 베끼지 않는다.
- **인과** — 맥락 → 원인 → 결과. 확인된 사실과 추정을 구분하고, 근거가 없으면 "미확인"이라 쓴다.
- **액션** — 동사로 시작하는 행동 목록. 사용자 몫은 `[사용자]` 표시.

실행이 끝나면 같은 라벨로 닫는다. 인과는 가설에서 실측으로 갱신되고, 액션은 남은 것만 남는다. 한 문장으로 끝나는 질문에는 3요소를 붙이지 않는다 — `"12개."` 로 끝낸다.

압축이 의미를 뒤집을 수 있는 것은 절대 건드리지 않는다: 부정어, 숫자·단위·버전, 코드와 에러 문자열, 사용자의 언어, 한국어 조사. 보안 경고와 비가역 작업 확인에서는 압축을 풀되 3요소는 유지한다. 채팅 밖으로 나가는 텍스트(커밋 메시지, 문서, PR 본문)에는 아예 적용하지 않는다.

**`grill`** (단발) — 계획·설계를 design tree 로 매핑하고, 선행 결정이 끝나 지금 물을 수 있는 질문들(frontier)을 한 라운드에 모아 묻는다. 질문마다 번호와 추천 답안이 붙어 사용자는 뒤집기만 하면 된다. 사실 확인은 서브에이전트가 하고 결정만 사용자에게 남긴다. frontier 가 비고 사용자가 합의를 확인하기 전까지 실행하지 않는다.

두 모드는 이어져 있다. `brief` 의 인과에 "미확인"이 쌓이면 그게 곧 `grill` 의 질문 후보다.

해제: `/humanism_talk off`, `"stop caveman"`, `"normal mode"`. 프로젝트별로 끄려면 `<project>/.claude/humanism_talk.off` 파일을 만든다.

### `develop_rule` — 재현 가능한 개발

**같은 입력이면 같은 결과가 나와야 한다.** 이걸 세 축으로 강제한다.

- **최소** — 안 지은 코드가 가장 재현 가능하다.
- **수렴** — 지은 것은 두 번 실행해도 같은 상태로 간다.
- **투영** — 문서는 코드에서 유도한다. 재생성해도 diff 가 없다.

지속 모드는 사다리를 강제한다. 처음 성립하는 칸에서 멈춘다: ① 애초에 필요한가(YAGNI) → ② 이미 코드베이스에 있나 → ③ 표준 라이브러리 → ④ 플랫폼 네이티브 → ⑤ 이미 설치된 의존성 → ⑥ 한 줄 → ⑦ 최소 구현. 강도는 `lite` / `full`(기본) / `ultra`.

**사다리는 문제를 이해한 다음에 탄다.** 무엇을 건드리는지 모르는 채 고른 최소 변경은 게으른 게 아니라 두 번째 버그다. 버그는 증상이 아니라 근본 원인에서 고친다 — 공유 함수의 가드 하나가 호출자마다 다는 것보다 작은 diff다.

멱등성은 네 가지로 압축된다: 무엇이 "같은 것"인지 먼저 정의하고, 상태를 만들지 말고 맞추고, 어디서 죽어도 재실행이 답이 되게 하고, 확인과 변경 사이의 틈을 없앤다. 층마다 기법이 달라 `references/idempotency-{setup,code,api}.md` 로 갈린다. **층 하나만 처리하고 멱등하다고 선언하지 않는다** — 핸들러에 중복 방지를 넣고 DB 유니크 제약을 빼먹는 게 가장 흔한 실패다.

단발 모드:

| 모드 | 하는 일 | 출력 |
|---|---|---|
| `review` | 지금의 diff 에서 과잉설계 찾기 | `L42: yagni: 구현체 하나뿐인 팩토리. 인라인.` → `net: -N lines possible.` |
| `audit` | 레포 전체, 삭제량 큰 순 | 위와 같은 형식 + `-M deps` |
| `debt` | `ponytail:` / `idempotent:` 마커를 장부로 수집 | 파일별 한 줄 + `no-trigger` 태그 |
| `spec` | `docs/api-spec.md`, `docs/screen-spec.md` 생성·갱신 | 템플릿 두 개를 채운 문서 |
| `handoff` | 대화를 인수인계 문서로 압축 | OS 임시 디렉토리에 저장 |

`review` 와 `audit` 은 **복잡도만** 사냥한다. 정확성 버그, 보안, 성능은 명시적으로 범위 밖이고 일반 리뷰로 넘긴다.

절대 단순화하지 않는 것: 신뢰 경계의 입력 검증, 데이터 손실을 막는 에러 처리, 보안, 접근성 기본, 사용자가 명시적으로 요청한 것.

처음 켤 때 `assets/claude-md-card.md` 를 프로젝트의 `CLAUDE.md` 에 `<!-- develop_rule:start -->` 마커로 고정한다. 대화가 압축돼도 원칙이 살아남게 하기 위해서다. 마커가 이미 있으면 그 구간만 교체하므로 몇 번 실행해도 같은 파일이 된다.

---

## 디렉토리 구조

```
awesome_skills/
├── install.sh                     # 부트스트랩 (clone/pull → link)
├── bin/awesome-skills             # link / update / list / uninstall / brief
├── hooks/inject-brief.sh          # SessionStart·PostCompact 에 brief 규칙 주입
└── .claude/
    ├── settings.json              # 마켓플레이스, 플러그인 활성화
    └── skills/
        ├── common/                # SKILL.md + references(5) + agents(3) + scripts(8) + eval-viewer
        ├── humanism_talk/         # SKILL.md + references/brief.md + README.md
        └── develop_rule/          # SKILL.md + references(9) + assets(3)
```

`.claude/settings.json` 에는 스킬 외에 [obra/superpowers](https://github.com/obra/superpowers) 플러그인이 마켓플레이스 경유로 활성화되어 있다. 로컬 `SKILL.md` 가 아니라 플러그인이므로 위 목록과는 별개로 관리된다.

---

## 스킬 추가하기

이 저장소는 세 개로 수렴하는 것을 목표로 한다. 새 기능은 대개 **새 스킬이 아니라 기존 스킬의 모드**로 붙는 편이 맞다. 스킬이 늘어나면 모델이 어느 것을 켤지 헷갈리고, 그게 곧 트리거 정확도 하락이다.

그래도 새 스킬이 필요하면 `/common create` 로 시작한다. 인터뷰 → 초안 → 테스트 케이스까지 안내한다. 확인할 것:

- **frontmatter** — `name` 은 디렉토리 이름과 같아야 한다. `description` 은 모델이 언제 켤지 판단하는 근거이므로 트리거 문구를 구체적으로 쓴다.
- **참조 파일** — 스크립트·템플릿은 스킬 디렉토리 안에 두고 상대 경로로 참조한다. 저장소 바깥 경로에 의존하면 전역 설치가 깨진다.
- **이름 보존** — 기존 스킬을 고칠 때 이름을 바꾸지 않는다. 이름이 바뀌면 수정이 아니라 새 스킬이고, 전역 설치에서는 둘이 트리거를 두고 경쟁한다.

작업이 끝나면 `/common docs` 로 이 카탈로그를 갱신하고, 커밋·푸시한 뒤 `awesome-skills update` 로 전역에 반영한다.

---

## 라이선스 / 크레딧

이 세 스킬은 기존 오픈소스 스킬들을 실사용 케이스 기준으로 재구성한 것이다. 원저작권은 각 원저작자에게 있다.

| 출처 | 라이선스 | 흡수된 곳 |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) — `skill-creator` | Apache-2.0 ([전문](.claude/skills/common/LICENSE.txt)) | `common` 의 `create` / `eval` / `describe` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | `develop_rule` 의 최소 축, `review` / `audit` / `debt` |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT | `humanism_talk` 의 `brief` |
| [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | `humanism_talk` 의 `grill`, `develop_rule` 의 `handoff` |
| 이 저장소 | MIT | `common` 의 `docs`, `develop_rule` 의 수렴·투영 축 |

업스트림에서 가져오지 않은 것도 밝혀둔다. `ponytail-help`(레퍼런스 카드)과 `ponytail-gain`(벤치마크 스코어보드)은 옮기지 않았다. 전자는 `develop_rule/SKILL.md` 가 같은 역할을 하고 카드에 적힌 설정·업데이트 절차가 이 저장소에서는 동작하지 않기 때문이고, 후자는 업스트림이 측정한 벤치마크 중앙값이라 산출 근거가 여기 없기 때문이다. 두 기능이 필요하면 원본 저장소를 직접 쓰면 된다.
<!-- skills:end -->

---

## 기여하기

스킬 추가, 문서 수정, 버그 제보 모두 환영한다.

1. 저장소를 포크한다.
2. 먼저 기존 세 스킬의 **모드로 붙일 수 있는지** 본다. 스킬이 늘어나면 모델이 어느 것을 켤지 헷갈리고 그게 곧 트리거 정확도 하락이다. 새 스킬이 맞다면 `/common create` 로 시작한다. frontmatter의 `name` 은 디렉토리 이름과 같아야 한다.
3. 외부에서 가져온 스킬이라면 원저작자와 라이선스를 PR 본문에 밝힌다. 라이선스가 MIT/Apache-2.0 계열이 아니면 먼저 이슈로 논의해달라.
4. `awesome-skills link` 를 실행하고 Claude Code를 재시작해 스킬 목록에 잡히는지 확인한 뒤 PR을 연다.
5. README의 스킬 카탈로그는 `/common docs` 로 갱신한다. 카탈로그 마커 사이 구간만 교체되므로 직접 손으로 쓴 부분은 남는다.

버그 제보와 스킬 제안은 [Issues](https://github.com/ash-hun/awesome_skills/issues)로.

## 라이선스

이 저장소의 설치 스크립트와 자체 작성 스킬은 [MIT 라이선스](LICENSE)를 따른다.

외부에서 가져온 스킬의 저작권은 원저작자에게 있다. 출처와 라이선스는 위 카탈로그의 **라이선스 / 크레딧** 항목에 정리되어 있다.
