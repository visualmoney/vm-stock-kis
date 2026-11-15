# 2026-11-16 - P2 와 §13 전략 B 현황

코드는 바꾸지 않았다. 보고서 현황만 붙였다.

## P2

- codegen 은 #21 파일럿과 #100 결정으로 끝난다. 전량 이관은 하지 않는다. 도구는 `scripts/extract_kis_specs.py`, `scripts/generate_endpoint.py`. 파일럿 8개는 `scripts/codegen/pilot/` 이고 휠 밖이다.
- 재시도는 #14. 상한 5, 토큰 재발급 1회. `while True` 는 남는다.
- 이름 충돌은 #15, #164. HTTP 404 만 `KisHTTPNotFoundError` 로 바꿨다. 조회 결과 없음은 `KisNotFoundError` 다. 보고서가 적은 `KisResultNotFoundError` 개명은 하지 않았다.

## §13 전략 B

B-1 의 98.9% 와 B-2 의 54% 는 2026-08-27 표로 두었다. #21 은 그 뒤 272/272, #100 은 접미사 59.9% 를 적었다.

`src/vmkis/endpoints/` 와 파사드, 13.3 의 2~4단계는 시작하지 않았다. 보고서의 전략 B(codegen)와 #100 의 선택(수요 있는 TR 만)은 다른 축이다. codegen 은 유지하고 전량 생성만 하지 않는다.

## 하지 않은 것

§14 결론 문장. 새 이슈. 생성 코드.
