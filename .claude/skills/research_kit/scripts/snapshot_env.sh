#!/usr/bin/env bash
# 실험 카드의 "환경" 절에 붙일 스냅샷을 마크다운으로 출력한다.
# 읽기만 하고 아무것도 바꾸지 않으므로 몇 번 실행해도 안전하다.
# 사용: bash snapshot_env.sh [저장소 경로]   (기본: 현재 디렉토리)

repo="${1:-.}"

echo "- 기록 시각: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  commit="$(git -C "$repo" rev-parse HEAD)"
  branch="$(git -C "$repo" rev-parse --abbrev-ref HEAD)"
  if [ -n "$(git -C "$repo" status --porcelain --untracked-files=no)" ]; then
    dirty="yes — 커밋되지 않은 변경 있음, 이 실행은 재현 불가"
  else
    dirty="no"
  fi
  echo "- git commit: \`$commit\` ($branch)"
  echo "- 작업 트리 변경: $dirty"
else
  echo "- git commit: 저장소 아님 — 이 실행은 재현 불가"
fi

echo "- OS: $(uname -srm)"

if command -v python >/dev/null 2>&1; then
  py=python
elif command -v python3 >/dev/null 2>&1; then
  py=python3
else
  py=""
fi

if [ -n "$py" ]; then
  echo "- Python: $($py --version 2>&1)"
  "$py" - <<'EOF' 2>/dev/null
import importlib.metadata as md
pkgs = ["torch", "transformers", "datasets", "accelerate", "peft", "trl",
        "vllm", "numpy", "scipy", "scikit-learn", "openai", "anthropic"]
found = []
for p in pkgs:
    try:
        found.append(f"{p}=={md.version(p)}")
    except md.PackageNotFoundError:
        pass
if found:
    print("- 주요 패키지: " + ", ".join(found))
EOF
fi

if command -v nvidia-smi >/dev/null 2>&1; then
  gpus="$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | sort | uniq -c | sed 's/^ *//' | paste -sd ';' -)"
  echo "- GPU: $gpus"
  if [ -n "$py" ]; then
    cuda="$("$py" -c 'import torch; print(torch.version.cuda)' 2>/dev/null)"
    [ -n "$cuda" ] && echo "- CUDA (torch): $cuda"
  fi
else
  echo "- GPU: 없음 또는 nvidia-smi 미설치"
fi
