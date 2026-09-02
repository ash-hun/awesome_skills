<div align="center">

# Awesome Skills

A curated collection of Claude Code skills, installable system-wide with a single command.

[![skills](https://img.shields.io/badge/skills-14-8A2BE2?style=flat)](.claude/skills) [![contributors](https://img.shields.io/github/contributors/ash-hun/awesome_skills?style=flat&logo=github&color=blue)](https://github.com/ash-hun/awesome_skills/graphs/contributors) [![forks](https://img.shields.io/github/forks/ash-hun/awesome_skills?style=flat&logo=github&color=blue)](https://github.com/ash-hun/awesome_skills/network/members) [![stars](https://img.shields.io/github/stars/ash-hun/awesome_skills?style=flat&logo=github&color=yellow)](https://github.com/ash-hun/awesome_skills/stargazers) [![issues](https://img.shields.io/github/issues/ash-hun/awesome_skills?style=flat&logo=github&color=red)](https://github.com/ash-hun/awesome_skills/issues) [![last commit](https://img.shields.io/github/last-commit/ash-hun/awesome_skills?style=flat&logo=github)](https://github.com/ash-hun/awesome_skills/commits/main) [![license](https://img.shields.io/github/license/ash-hun/awesome_skills?style=flat&color=green)](LICENSE)

</div>

---

## 무엇인가

[Claude Code](https://claude.com/claude-code)에사 유용하게 사용할 수 있는 **Custom Skill** 을 모아둔 저장소다. 설치하면 어느 디렉토리에서 Claude Code를 열든 모든 스킬이 로드된다.

모든 스킬은 `.claude/skills/<name>/SKILL.md` 단일 파일로 self-contained 하게 작성되어 있다. 추가 스크립트, 훅, 런타임 의존성 없음.

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

모든 명령은 멱등이다. 여러 번 실행해도 한 번 실행한 것과 결과가 같다.

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

| 스킬 | 호출 | 한 줄 요약 | 출처 |
|---|---|---|---|
| [`skills-readme`](.claude/skills/skills-readme/SKILL.md) | `/skills-readme [README 경로]` | 설치된 스킬을 읽어 이 README의 카탈로그 구간을 갱신 | 이 저장소 |
| [`ponytail`](.claude/skills/ponytail/SKILL.md) | `/ponytail [lite\|full\|ultra]` | 게으른 시니어 개발자 모드. 동작하는 가장 단순한 해법을 강제 | [ponytail](https://github.com/DietrichGebert/ponytail) |
| [`ponytail-review`](.claude/skills/ponytail-review/SKILL.md) | `/ponytail-review` | diff 대상 과잉설계 리뷰. 지울 것만 찾는다 | ↑ |
| [`ponytail-audit`](.claude/skills/ponytail-audit/SKILL.md) | `/ponytail-audit` | 레포 전체 과잉설계 감사. 큰 삭제부터 랭킹 | ↑ |
| [`ponytail-debt`](.claude/skills/ponytail-debt/SKILL.md) | `/ponytail-debt` | `ponytail:` 주석을 부채 장부로 수집 | ↑ |
| [`ponytail-gain`](.claude/skills/ponytail-gain/SKILL.md) | `/ponytail-gain` | 벤치마크 기반 효과 스코어보드 | ↑ |
| [`ponytail-help`](.claude/skills/ponytail-help/SKILL.md) | `/ponytail-help` | ponytail 전체 레퍼런스 카드 | ↑ |
| [`grilling`](.claude/skills/grilling/SKILL.md) | 트리거 문구 / `/grilling` | 계획·설계를 라운드 단위 질문으로 압박 검증 | [mattpocock/skills](https://github.com/mattpocock/skills) |
| [`grill-me`](.claude/skills/grill-me/SKILL.md) | `/grill-me` | `grilling` 세션을 여는 얇은 래퍼 | ↑ |
| [`handoff`](.claude/skills/handoff/SKILL.md) | `/handoff [다음 세션 목적]` | 현재 대화를 인수인계 문서로 압축 | ↑ |

---

## 스킬 상세

### 저장소 관리

#### `skills-readme`
`.claude/skills/*/SKILL.md`를 **본문까지** 읽어 이 README의 카탈로그 구간을 다시 쓴다. frontmatter의 `description`은 모델용 트리거 문구지 사람용 설명이 아니므로 그대로 베끼지 않는다.

교체 범위는 `<!-- skills:start -->` ~ `<!-- skills:end -->` 사이뿐이라, 바깥의 손으로 쓴 부분은 반복 실행해도 살아남는다. 출처·라이선스는 LICENSE → settings.json의 curl 이력 → GitHub API 순으로 확인하고, 끝내 모르면 추측 대신 빈칸으로 두고 보고한다. 훅/플러그인 런타임을 전제로 쓰인 스킬 문서는 부속 파일 설치 여부를 확인해 안 되는 기능에 경고를 붙인다.

### ponytail 계열 — 과잉설계 방지

#### `ponytail`
"게으름 = 비효율이 아니라 효율"이라는 전제의 상시 모드. 아래 **사다리**를 위에서부터 타고 내려가다 처음 성립하는 칸에서 멈춘다.

1. 애초에 필요한가? (YAGNI)
2. 이 코드베이스에 이미 있나? → 재사용
3. 표준 라이브러리가 하나?
4. 플랫폼 네이티브 기능으로 되나?
5. 이미 설치된 의존성으로 되나?
6. 한 줄로 되나?
7. 그때서야 최소 구현

강도는 3단계 — `lite`(대안만 제시), `full`(기본, 사다리 강제), `ultra`(YAGNI 극단주의).

명시적 안전장치도 있다: 입력 검증·에러 처리·보안·접근성·사용자가 명시 요청한 것은 절대 단순화하지 않고, **"문제 이해"에는 게으르지 않는다**(작은 diff를 위해 파악을 건너뛰는 건 금지). 의도적으로 감수한 한계는 `ponytail:` 주석으로 한계와 업그레이드 조건을 남긴다 — 이게 `ponytail-debt`의 입력이 된다.

비활성화: `"stop ponytail"` 또는 `"normal mode"`.

#### `ponytail-review`
diff 한정 리뷰. 정확성·보안·성능은 **범위 밖**(일반 리뷰로 라우팅)이고 복잡도만 사냥한다.

발견 1건 = 1줄, `L<line>: <tag> <무엇>. <대체안>.` 형식. 태그는 `delete:` / `stdlib:` / `native:` / `yagni:` / `shrink:`. 마지막에 `net: -N lines possible.`로 마감하고, 자를 게 없으면 `Lean already. Ship.`

#### `ponytail-audit`
`ponytail-review`의 레포 전체 버전. diff 대신 트리 전체를 훑고 삭제량 큰 순으로 랭킹. 단발 리포트이며 수정은 적용하지 않는다.

#### `ponytail-debt`
`grep -rnE '(#|//) ?ponytail:' .`로 남겨둔 shortcut 주석을 수집해 파일별 장부로 정리. 업그레이드 트리거가 없는 항목은 `no-trigger`로 표시 — 조용히 썩는 부채를 드러내는 게 목적. 요청하면 `PONYTAIL-DEBT.md`로 저장한다.

#### `ponytail-gain`
공개 벤치마크 중앙값(5개 태스크 × 3개 모델) 스코어보드. **레포별 절감치는 절대 출력하지 않는다** — 안 쓴 코드에는 비교 기준선이 없기 때문. 실제 레포 수치가 필요하면 `ponytail-debt`/`ponytail-audit`로 유도한다.

#### `ponytail-help`
모드·스킬·명령 요약 카드. ⚠️ 이 카드 안의 **"Configure Default Mode"(`PONYTAIL_DEFAULT_MODE`, `~/.config/ponytail/config.json`)와 "Update"(`/plugin` 마켓플레이스) 섹션은 이 저장소에 적용되지 않는다.** 해당 기능은 업스트림의 훅/플러그인 런타임이 필요한데, 여기는 SKILL.md만 설치한 구성이다. 세션 자동 활성화도 없으니 `/ponytail`로 직접 켜야 한다.

### 사고 정리 / 세션 관리

#### `grilling`
계획·결정·아이디어를 **design tree**로 매핑해 라운드 단위로 심문한다. 선행 결정이 끝나 지금 물을 수 있는 질문들(= frontier)을 한 라운드에 모아 번호 + 추천 답안과 함께 제시하고 답을 기다린다. 답이 트리를 갱신하면 frontier를 다시 계산해 다음 라운드로. **사실 확인은 에이전트 몫**(서브에이전트로 조회), **결정은 사용자 몫**. frontier가 비면 종료하며, 사용자가 합의를 확인하기 전엔 실행하지 않는다.

#### `grill-me`
`/grilling`을 실행하는 한 줄짜리 래퍼. `disable-model-invocation: true`라 명시 호출 전용.

#### `handoff`
현재 대화를 새 에이전트가 이어받을 수 있는 인수인계 문서로 압축한다. **OS 임시 디렉토리에 저장**(워크스페이스 오염 방지), "suggested skills" 섹션 포함, 스펙·플랜·커밋·diff 등 기존 산출물은 중복 서술 대신 경로/URL로 참조, API 키·비밀번호·PII는 마스킹. 인자를 주면 다음 세션의 목적에 맞춰 문서를 조정한다. 역시 명시 호출 전용.

---

## 디렉토리 구조

```
awesome_skills/
├── README.md
└── .claude/
    ├── settings.json          # 권한 allowlist, 마켓플레이스, 플러그인 활성화
    └── skills/
        ├── skills-readme/SKILL.md
        ├── ponytail/SKILL.md
        ├── ponytail-review/SKILL.md
        ├── ponytail-audit/SKILL.md
        ├── ponytail-debt/SKILL.md
        ├── ponytail-gain/SKILL.md
        ├── ponytail-help/SKILL.md
        ├── grilling/SKILL.md
        ├── grill-me/SKILL.md
        └── handoff/SKILL.md
```

`.claude/settings.json`에는 스킬 외에 [obra/superpowers](https://github.com/obra/superpowers) 플러그인이 마켓플레이스 경유로 활성화되어 있다. 이건 로컬 SKILL.md가 아니라 플러그인이라 위 목록과는 별개로 관리된다.

---

## 스킬 추가하기

원격 저장소의 SKILL.md 하나만 가져오면 끝이다.

```bash
mkdir -p .claude/skills/<name>
curl -sfL "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<name>/SKILL.md" \
  -o .claude/skills/<name>/SKILL.md
```

체크 포인트:

- **frontmatter** — `name`(디렉토리명과 일치), `description`(모델이 언제 쓸지 판단하는 근거이므로 트리거 문구를 구체적으로), 선택적으로 `argument-hint`, `disable-model-invocation`.
- **참조 파일** — SKILL.md가 같은 디렉토리의 스크립트·템플릿을 참조하면 그 파일들도 함께 받아야 한다. 현재 설치된 10개는 전부 참조 없는 self-contained.
- **훅 의존성** — 업스트림이 세션 자동 활성화나 상태줄을 훅으로 구현했다면, SKILL.md만 복사한 구성에서는 동작하지 않는다(위 `ponytail-help` 주의사항 참고).

설치 후 새 세션에서 스킬 목록에 잡히는지 확인한다.

---

## 라이선스 / 크레딧

외부 스킬의 저작권은 원저작자에게 있다. 두 출처 모두 MIT.

- [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) — MIT — ponytail 6종
- [mattpocock/skills](https://github.com/mattpocock/skills) — MIT — `grilling`, `grill-me`, `handoff`
- 이 저장소 — `skills-readme`
<!-- skills:end -->

---

## 기여하기

스킬 추가, 문서 수정, 버그 제보 모두 환영한다.

1. 저장소를 포크한다.
2. `.claude/skills/<name>/SKILL.md` 를 추가한다. frontmatter의 `name` 은 디렉토리 이름과 같아야 한다.
3. 외부에서 가져온 스킬이라면 원저작자와 라이선스를 PR 본문에 밝힌다. 라이선스가 MIT/Apache-2.0 계열이 아니면 먼저 이슈로 논의해달라.
4. `awesome-skills link` 를 실행하고 Claude Code를 재시작해 스킬 목록에 잡히는지 확인한 뒤 PR을 연다.
5. README의 스킬 카탈로그는 `/skills-readme` 로 갱신한다. 카탈로그 마커 사이 구간만 교체되므로 직접 손으로 쓴 부분은 남는다.

버그 제보와 스킬 제안은 [Issues](https://github.com/ash-hun/awesome_skills/issues)로.

## 라이선스

이 저장소의 설치 스크립트와 자체 작성 스킬은 [MIT 라이선스](LICENSE)를 따른다.

외부에서 가져온 스킬의 저작권은 원저작자에게 있다. 출처와 라이선스는 위 카탈로그의 **라이선스 / 크레딧** 항목에 정리되어 있다.
