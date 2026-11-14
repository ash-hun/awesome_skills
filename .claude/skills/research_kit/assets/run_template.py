"""research_kit 실험 모듈 템플릿.

experiments/<exp-id>/run.py 로 복사해 쓴다. 인자 파싱, seed 고정, 진행바,
항목 단위 jsonl 기록, 실행 폴더 생성과 config 사본까지 갖추고 있다.
비어 있는 곳은 둘이다: load_items() 와 run_one(). 모델 호출과 채점은 거기에 쓴다.

실행:
    python run.py --config configs/prop.yaml --seed 0 --run-dir runs/prop-s0-20260924-a1b2c3d

같은 config 와 seed 로 다시 돌리면 같은 metrics.jsonl 이 나와야 한다.
표준 라이브러리만 쓴다. tqdm 이 없으면 진행바 없이 돈다.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator

try:
    from tqdm import tqdm
except ImportError:  # 진행바 없이도 돌아가게

    def tqdm(it: Iterable[Any], **_: Any) -> Iterable[Any]:  # type: ignore[no-redef]
        return it


def set_seed(seed: int) -> None:
    """실제로 쓰는 모든 난수원의 seed 를 고정한다. 모델 로드와 데이터 셔플보다 먼저 부른다."""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def load_config(path: Path) -> dict[str, Any]:
    """json 또는 yaml 설정을 읽는다. yaml 은 pyyaml 이 있을 때만."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as e:
        raise SystemExit("yaml 설정을 읽으려면 pyyaml 이 필요하다. 또는 json 으로 바꾼다.") from e
    return yaml.safe_load(text)


def load_items(config: dict[str, Any]) -> list[dict[str, Any]]:
    """평가 항목을 읽어 목록으로 돌려준다. 항목마다 "id" 와 "gold" 가 있어야 한다.

    TODO: config["data"] 경로에서 읽는다. 순서를 고정한다(정렬 또는 파일 순서).
    """
    raise NotImplementedError("load_items: 평가셋 읽기를 구현한다")


def run_one(item: dict[str, Any], config: dict[str, Any], seed: int) -> dict[str, Any]:
    """항목 하나를 돌리고 결과 한 줄을 돌려준다.

    돌려주는 dict 에는 최소 다음이 있어야 한다.
      id          항목 ID
      gold        정답
      prediction  산출 규칙으로 뽑은 예측 (뽑지 못하면 None)
      raw         모델의 원 응답 전체. 채점을 다시 해도 API 를 다시 부르지 않게
    평가 기준의 값(correct, score, label)은 design.md 의 산출 규칙대로 여기서 계산하거나,
    4단계의 evaluate.py 에서 raw 로부터 계산한다. 둘 중 하나로 정하고 섞지 않는다.

    TODO: 모델 호출. API 가 seed 파라미터를 받으면 넘긴다.
    """
    raise NotImplementedError("run_one: 모델 호출과 추출을 구현한다")


def iter_results(
    items: list[dict[str, Any]], config: dict[str, Any], seed: int
) -> Iterator[dict[str, Any]]:
    bar = tqdm(items, desc="items", file=sys.stderr, mininterval=10)
    for item in bar:
        try:
            yield run_one(item, config, seed)
        except Exception as e:  # 한 항목이 죽어도 실행은 끝까지 간다. 실패는 기록한다.
            yield {
                "id": item.get("id"),
                "gold": item.get("gold"),
                "prediction": None,
                "raw": None,
                "error": f"{type(e).__name__}: {e}",
            }


def main() -> None:
    parser = argparse.ArgumentParser(description="research_kit 실험 실행")
    parser.add_argument("--config", type=Path, required=True, help="설정 파일 (json 또는 yaml)")
    parser.add_argument("--seed", type=int, required=True, help="design.md 의 seed 목록 중 하나")
    parser.add_argument("--run-dir", type=Path, required=True, help="runs/<run-id>")
    parser.add_argument("--limit", type=int, default=None, help="스모크 테스트용. 앞 N 개만")
    args = parser.parse_args()

    if args.run_dir.exists() and any(args.run_dir.iterdir()):
        raise SystemExit(f"{args.run_dir} 가 이미 있다. 덮어쓰지 않는다. 다시 돌리려면 -r2 를 붙인 새 run-id 를 쓴다.")
    args.run_dir.mkdir(parents=True, exist_ok=True)

    set_seed(args.seed)
    config = load_config(args.config)
    shutil.copy2(args.config, args.run_dir / args.config.name)  # 실행에 쓴 설정 사본

    items = load_items(config)
    if args.limit is not None:
        items = items[: args.limit]

    metrics_path = args.run_dir / "metrics.jsonl"
    n_done = n_err = 0
    with metrics_path.open("w", encoding="utf-8") as f:
        for row in iter_results(items, config, args.seed):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n_done += 1
            n_err += 1 if row.get("error") else 0

    print(f"done: {n_done} items, {n_err} errors -> {metrics_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
