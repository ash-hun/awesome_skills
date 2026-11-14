# Qwen2.5-7B-Instruct 에서 few-shot CoT 는 direct answer 보다 GSM8K 정확도를 3%p 이상 올린다

CoT 가 7B 급 모델의 GSM8K 정확도를 높인다는 보고는 많지만, instruct 모델에서 direct 조건을 어떻게 정의하느냐에 따라 차이가 1%p 에서 60%p 까지 벌어진다. 공식 Qwen2.5-7B-Instruct 수치(91.6)는 평가 설정이 공개되지 않아 재현 목표로 쓸 수 없다. 이 실험은 같은 8-shot 예시에서 풀이 유무만 바꿔 차이를 잰다.

**가정**: direct 는 8-shot 예시에서 풀이를 뺀 것. 답 형식은 두 조건 모두 `#### <number>`  **조사 깊이**: light

## 지지하는 보고
- 7B 급에서 CoT 가 GSM8K 를 수 %p 올림 ([Wei et al. 2022](https://arxiv.org/abs/2201.11903))

## 반박하거나 조건을 다는 보고
- instruct 모델은 direct 지시에도 풀이를 쓰는 경향이 있어 차이가 1%p 안팎으로 줄 수 있음 ([Short-Path Prompting, 2025](https://arxiv.org/abs/2504.09586))
- 추출 규칙(strict / flexible)만으로 수 %p 가 달라짐 ([arXiv 2506.14641](https://arxiv.org/abs/2506.14641))

## 가져다 쓸 자원
| 종류 | 이름 | 비고 (설정, 버전, 라이선스) | 출처 |
|---|---|---|---|
| 베이스라인 | Qwen2.5-7B-Instruct 공식 91.6 | 평가 설정 미공개, 재현 목표로 부적합 | [Qwen blog](https://qwenlm.github.io/blog/qwen2.5/) |
| 데이터셋 | GSM8K test | 1,319문항, MIT | [HF](https://huggingface.co/datasets/openai/gsm8k) |
| 평가 기준 | `####` 정확 일치 | lm-eval-harness gsm8k_cot strict-match | [lm-eval](https://github.com/EleutherAI/lm-evaluation-harness) |

## 알려진 함정
- 공개 벤치마크 오염 가능성 ([GSM1k](https://arxiv.org/abs/2405.00332))

## 방향 제안
- **유지**: 가설 그대로. 선택됨 (2026-11-06)
