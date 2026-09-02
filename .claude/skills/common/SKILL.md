---
name: common
description: >
  이 저장소의 스킬 자체를 만들고, 검증하고, 문서화하는 메타 스킬. SKILL.md 를 새로
  쓰거나, 기존 스킬의 본문이나 description 을 고치거나, 테스트 케이스로 스킬 성능을
  측정하거나, README 의 스킬 카탈로그를 갱신할 때 사용한다. 다루는 대상이
  `.claude/skills/<name>/SKILL.md` 일 때만 해당한다 — 일반 코드 작성, 일반 문서 작성,
  리서치에는 쓰지 않는다. Use when the user says "스킬 만들어줘", "스킬 고쳐줘",
  "스킬 평가해줘", "트리거가 잘 안 잡혀", "README 최신화", "스킬 목록 정리해줘",
  "create a skill", "improve this skill", "run evals on this skill", "optimize the
  skill description", "update the skills README", or invokes /common.
argument-hint: "[create|eval|describe|docs]"
license: MIT
---

# Common — 스킬 라이프사이클

스킬은 한 번 쓰고 끝나는 파일이 아니다. **만들고 → 검증하고 → 이름표를 다듬고 → 문서에 올린다.** 이 네 단계가 한 흐름인데, 도구가 따로 놀면 만들어놓고 검증을 건너뛰거나, 고쳐놓고 카탈로그를 안 고쳐서 문서가 썩는다. `common` 은 그 흐름 전체를 한 자리에서 잡는다.

## 모드

인자가 있으면 그 모드로, 없으면 대화 맥락을 보고 판단한다. 사용자가 이미 어느 단계에 있는지 파악해서 그 지점부터 이어가는 게 핵심이다 — 초안이 이미 있는데 인터뷰부터 다시 하면 시간만 버린다.

| 인자 | 단계 | 읽을 참조 |
|---|---|---|
| `create` | 의도 파악 → 인터뷰 → SKILL.md 초안 → 테스트 케이스 | `references/authoring.md` |
| `eval` | 테스트 실행 → 채점 → 사람 리뷰 → 개선 루프 | `references/evaluation.md` |
| `describe` | description 을 트리거 정확도 기준으로 최적화 | `references/description.md` |
| `docs` | README 스킬 카탈로그 갱신 | `references/catalog.md` |

참조 문서는 **해당 모드에 들어갈 때 읽는다.** 네 개를 미리 다 읽지 않는다.

트리거 문구로도 들어온다. "스킬 만들어줘"는 `create`, "이 스킬 평가해줘"는 `eval`, "트리거가 엉뚱한 데서 잡혀"는 `describe`, "README 최신화"는 `docs`.

## 단계를 잇기

각 모드가 끝나면 다음 단계를 **제안한다**. 강요하지 말고, 사용자가 "그냥 대충 만들어줘" 라고 하면 그 말을 따른다.

- `create` 가 끝나면 → 테스트 케이스를 방금 만들었으니 `eval` 을 돌려보자고 제안
- `eval` 루프가 끝나면 → description 도 손볼지 물어보고 `describe` 로
- 스킬이 추가·삭제·이름 변경·수정된 뒤에는 → `docs` 로 카탈로그를 맞춘다

마지막 항목이 특히 중요하다. 스킬을 건드린 세션에서 카탈로그를 안 고치면 그 다음 사람은 문서를 못 믿게 된다. 스킬 파일을 수정하고 대화를 끝내려 할 때, README 가 아직 옛날 내용이면 그 사실을 알린다.

## 사용자와 대화할 때

이 스킬을 부르는 사람의 배경은 넓다. 터미널을 이제 막 연 사람일 수도 있고, 평소 평가 파이프라인을 짜는 사람일 수도 있다. 맥락 단서를 보고 표현 수위를 맞춘다.

- "평가", "벤치마크" 정도는 대체로 통한다
- "JSON", "assertion" 은 사용자가 그 말을 먼저 쓰거나 알아듣는 신호가 보일 때만 설명 없이 쓴다

애매하면 한 줄로 짧게 풀어 쓴다. 용어를 아는 사람에게 설명을 붙이는 손해가, 모르는 사람이 막히는 손해보다 작다.

## 저장소 규약

- 스킬은 `.claude/skills/<name>/SKILL.md` 에 둔다. frontmatter 의 `name` 은 디렉토리 이름과 같아야 한다.
- 스크립트·템플릿·참조 문서를 같이 쓰면 스킬 디렉토리 안에 두고 상대 경로로 참조한다. 저장소 바깥 경로에 의존하면 전역 설치가 깨진다.
- 외부에서 가져온 스킬은 원저작자와 라이선스를 남긴다. `LICENSE.txt` 를 함께 받았으면 그대로 둔다.
- **기존 스킬을 고칠 때는 이름을 보존한다.** 디렉토리 이름과 frontmatter 의 `name` 을 그대로 쓴다. `research-helper` 를 고쳐서 `research-helper-v2` 를 만들지 않는다 — 이름이 바뀌면 그건 수정이 아니라 새 스킬이고, 전역 설치에서는 둘이 같이 트리거를 두고 경쟁한다.
- 이 저장소는 전역 설치의 원본이다. `~/.claude/skills/<name>` 은 여기를 가리키는 심볼릭 링크이므로, 여기서 고치면 전역에 바로 반영된다.

## 참조 파일

모드에 들어갈 때 읽는다.

- `references/authoring.md` — 의도 파악, 인터뷰, 작성 가이드, 문체, 테스트 케이스 작성
- `references/evaluation.md` — 실행·채점·집계·리뷰어·개선 루프·블라인드 비교
- `references/description.md` — 트리거 eval 쿼리 생성과 description 최적화 루프
- `references/catalog.md` — 수집, 출처·라이선스 확인, README 마커 구간 갱신 규칙
- `references/schemas.md` — `evals.json`, `grading.json` 등의 JSON 구조

서브에이전트를 띄울 때 읽는 지시문:

- `agents/grader.md` — 출력이 assertion 을 만족하는지 채점
- `agents/comparator.md` — 두 출력의 블라인드 A/B 비교
- `agents/analyzer.md` — 왜 한쪽이 이겼는지 분석

실행 스크립트는 `scripts/`, 사람이 결과를 보는 뷰어는 `eval-viewer/` 에 있다.

## 범위 밖

- 스킬이 아닌 일반 코드·문서 작성. `common` 이 다루는 대상은 `SKILL.md` 와 그 부속 파일이다.
- `.skill` 패키징과 `present_files` 기반 전달. 이 저장소는 Claude Code 전역 설치 방식이라 `install.sh` 와 `awesome-skills` CLI 가 그 역할을 한다. 스킬을 추가했으면 커밋·푸시하면 끝이다.
