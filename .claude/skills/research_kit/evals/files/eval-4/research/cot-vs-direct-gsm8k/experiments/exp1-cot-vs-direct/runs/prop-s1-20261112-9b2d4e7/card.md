# 실행 카드: prop-s1-20261112-9b2d4e7

- 설계: [design.md](../../../../design.md)
- 실험: exp1-cot-vs-direct
- 조건 ID: prop
- seed: 1
- 상태: 완료
- 구분: 확증

## 실행 명령

```bash
python experiments/exp1-cot-vs-direct/run.py --config configs/prop.json --seed 1 --run-dir experiments/exp1-cot-vs-direct/runs/prop-s1-20261112-9b2d4e7
```

## 설정

- config 파일: [config](./config.json) (실행에 쓴 사본)
- design.md 와 다른 점: 없음

## 데이터

- 평가셋 / 학습셋: data/gsm8k_test_500.jsonl (GSM8K test 앞 500문항)
- 버전 (해시 또는 날짜): sha256 3c1e9f…b2a7 (2026-11-02)
- 항목 수: 500

## 환경

- 기록 시각: 2026-11-12T09:12:00Z
- git commit: `9b2d4e7` (main)
- 작업 트리 변경: no
- OS: Linux 6.8.0 x86_64
- Python: Python 3.11.9
- 주요 패키지: torch==2.4.1, transformers==4.45.2, vllm==0.6.3, numpy==2.1.2
- GPU: 1 NVIDIA A100-SXM4-80GB,550.90.07
- CUDA (torch): 12.4

## 모델

- 모델 / 스냅샷 또는 체크포인트 경로: Qwen/Qwen2.5-7B-Instruct
- 디코딩 설정 (해당 시): temperature 0.7, top_p 0.9, max_tokens 512, seed 1

## 결과

- 원 지표 파일: [metrics](./metrics.jsonl)
- 그림: 없음 (평가 단계에서 생성)
- 주 기준: 정확도 73.4% (추출 실패 4개는 오답 처리)
- 보조 기준: 추출 실패율 0.8%
- 추출 실패 수 / 비율: 4 / 0.8%
- 소요 시간 / 비용: 약 6분, A100 1장

## 메모

- 이상 없음
