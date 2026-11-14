# 실행 카드: base-s0-20261110-f3a9c1e

- 설계: [design.md](../../../../design.md)
- 실험: exp1-prop-vs-base
- 조건 ID: base
- seed: 0
- 상태: 완료
- 구분: 확증

## 실행 명령

```bash
python experiments/exp1-prop-vs-base/run.py --config configs/base.json --seed 0 --run-dir experiments/exp1-prop-vs-base/runs/base-s0-20261110-f3a9c1e
```

## 설정

- config 파일: [config](./config.json) (실행에 쓴 사본)
- design.md 와 다른 점: 없음

## 데이터

- 평가셋 / 학습셋: data/gsm8k_test_500.jsonl (GSM8K test 앞 500문항)
- 버전 (해시 또는 날짜): sha256 3c1e9f…b2a7 (2026-11-00)
- 항목 수: 500

## 환경

- 기록 시각: 2026-11-10T09:12:00Z
- git commit: `f3a9c1e` (main)
- 작업 트리 변경: no
- OS: Linux 6.8.0 x86_64
- Python: Python 3.11.9
- 주요 패키지: torch==2.4.1, transformers==4.45.2, vllm==0.6.3, numpy==2.1.2
- GPU: 1 NVIDIA A100-SXM4-80GB,550.90.07
- CUDA (torch): 12.4

## 모델

- 모델 / 스냅샷 또는 체크포인트 경로: Qwen/Qwen2.5-7B-Instruct
- 디코딩 설정 (해당 시): temperature 0, top_p 1.0, max_tokens 512

## 결과

- 원 지표 파일: [metrics](./metrics.jsonl)
- 그림: 없음 (평가 단계에서 생성)
- 주 기준: 미산출 (평가 단계에서 채점)
- 보조 기준: 없음
- 추출 실패 수 / 비율: 3 / 0.6%
- 소요 시간 / 비용: 약 6분, A100 1장

## 메모

- 추출 실패 3개. 원 응답은 metrics.jsonl 의 raw 에 전부 저장됨
