# nplt30.py Google Search 결과 표시 개선 테스트 보고서

## 1. 대상
- 파일: `C:\Users\user\Desktop\python\nplt30.py`
- 테스트 URL: `www.hd.com`
- 테스트 일시: 2026-06-28

## 2. 확인된 문제
- 보고서에 아래와 같이 표시되었다.
  - `the Result of google.com search`
  - `- The Average number of link on Google(nplt Index): 0`
- 실제로는 Google 검색 결과가 0이라는 의미가 아니라, 기존 코드가 Google 결과 수를 가져오지 못한 상태였다.

## 3. 원인
- 기존 `googleSearch()`는 Google 검색 HTML에서 `About ... results` 문자열을 직접 찾는 방식이었다.
- Google은 지역, 동의 페이지, 자동화 요청 차단, HTML 구조 변경, 언어별 문구 차이 때문에 해당 문자열을 안정적으로 제공하지 않는다.
- 결과 문자열을 찾지 못하면 빈 문자열을 반환했고, 출력부는 이를 `0`으로 변환했다.
- 또한 `npltIndex[4]`는 현재 기본값 `0`으로 고정되어 있어 기준값 미설정도 실제 0처럼 보였다.

## 4. 적용한 개선
- `parse_google_result_count()`를 추가해 영문/국문 결과 수 문구를 분리 파싱하도록 했다.
- `google_custom_search()`를 추가했다.
  - 환경변수 `GOOGLE_SEARCH_API_KEY` 또는 `GOOGLE_API_KEY`
  - 환경변수 `GOOGLE_SEARCH_ENGINE_ID`, `GOOGLE_CSE_ID`, 또는 `GOOGLE_CX`
  - 위 값이 있으면 Google Custom Search JSON API를 사용한다.
- API 키가 없으면 기존 HTML 요청을 fallback으로 사용하되, 실패 시 `0`이 아니라 `unavailable` 상태와 이유를 반환하도록 했다.
- 출력부에서 성공/실패를 구분하도록 변경했다.
  - 성공: 결과 수와 source 출력
  - 실패: 측정 불가 이유, source, `Google nplt Index: not calculated` 출력
- `npltIndex[4]` 기준값이 0/미설정이면 `not configured`로 표시하도록 했다.

## 5. 테스트 결과

### 5.1 문법 검사
- 명령: `python -m py_compile nplt30.py`
- 결과: 정상 통과

### 5.2 결과 수 파서 회귀 테스트
- `About 1,234 results` -> `1234`
- `검색결과 약 5,678개` -> `5678`
- `no count here` -> `None`
- 판정: `google result count parser regression OK`

### 5.3 API 키 미설정 테스트
- Google Custom Search API 환경변수 미설정 상태에서 `google_custom_search()`는 `None` 반환
- 판정: `google custom search no-key regression OK`

### 5.4 실제 Google 요청 상태 테스트
- 명령: `googleSearch("www.hd.com")`
- 결과:
  - `status`: `unavailable`
  - `count`: `None`
  - `message`: `Google result count was not found in the response`
  - `source`: `Google HTML`
- 판정: `googleSearch live shape regression OK`

### 5.5 실제 보고서 재생성
- 명령: `python nplt30.py -url www.hd.com -db No`
- 결과: 정상 완료
- 생성 보고서: `C:\Users\user\Desktop\python\report\www.hd.com.docx`
- 생성 시각: 2026-06-28 08:33:09
- Google 섹션 확인 결과:
  - `Google result count unavailable: Google result count was not found in the response`
  - `Google search source: Google HTML`
  - `Google nplt Index: not calculated`

## 6. 결론
- 기존 `0` 표시는 실제 검색 결과 0건이 아니라 측정 실패를 잘못 표현한 것이다.
- 개선 후 측정 실패와 실제 결과 수를 분리하여 표시한다.
- 정확한 Google 결과 수가 필요하면 Google Custom Search API 키와 Search Engine ID를 환경변수로 설정해야 한다.

