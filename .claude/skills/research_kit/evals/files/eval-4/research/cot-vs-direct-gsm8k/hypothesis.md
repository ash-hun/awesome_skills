# 가설: Qwen2.5-7B-Instruct 에서 few-shot CoT 는 direct answer 보다 GSM8K 정확도를 3%p 이상 올린다

- 작성일: 2026-11-05
- 연구 주제: 사내 수학 문제 풀이 보조 기능의 프롬프트 선택
- 본 연구에서 이 실험이 맡는 역할: 맞으면 서비스 프롬프트를 CoT 로 바꾸고 지연 시간 증가를 감수한다. 틀리면 direct 를 유지한다.

## 가설

Qwen2.5-7B-Instruct, GSM8K test 500문항, sampling(temperature 0.7) seed 3개 평균에서 8-shot CoT 의 정확도가 8-shot direct 보다 3%p 이상 높다.

## 왜 이렇게 생각하는가

CoT 계열 보고가 7B 급에서 수 %p 이득을 보고함. 3%p 는 지연 시간 증가(약 4배)를 정당화하는 최소 폭으로 서비스 팀과 합의한 값.

## 쓸 수 있는 자원

- 모델: 오픈 웨이트, 추론만
- 계산: A100 1장
- 데이터: GSM8K test 앞 500문항
- 기한: 없음

## 변경 이력

없음
