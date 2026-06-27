# nplt30.py WordCloud 및 Broken Link 오탐 개선 보고서

## 1. 대상
- 파일: `C:\Users\user\Desktop\python\nplt30.py`
- 확인 대상 사이트: `https://www.hd.com`
- 작성일: 2026-06-27

## 2. 확인된 문제

### 2.1 WordCloud 크기 편차
- 예시 빈도에서 `HYUNDAI: 3461`, `SEAMARQ: 179`로 약 19.34배 차이가 발생했다.
- 기존 WordCloud는 `relative_scaling=1`과 완만한 자동 스케일을 사용해 최빈 단어가 지나치게 커지고 하위 단어가 잘 보이지 않을 수 있었다.

### 2.2 Broken Link 오탐
- 보고서에 아래처럼 괄호 뒤 `.pdf`가 잘린 URL이 Broken Link로 출력되었다.
  - `..._50년사_1권(통사`
  - `..._50년사_2권(성장스토리`
  - `..._50년사_3권(화보`
- 실제 정상 URL은 아래와 같이 `).pdf`까지 포함한다.
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_1권(통사).pdf`
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_2권(성장스토리).pdf`
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_3권(화보).pdf`

## 3. 원인
- `extract_s_list()`가 HTML 문자열에서 URL을 추출할 때 `)`를 URL 종료 문자로 취급했다.
- PDF 파일명 자체에 괄호가 들어간 경우에도 첫 번째 `)`에서 URL을 잘라 잘못된 URL을 scan 대상으로 추가했다.
- 그 결과 실제 파일은 존재하지만 잘린 URL을 요청하면서 404로 오판했다.

## 4. 적용한 개선
- `extract_s_list()`에서 `)`를 무조건 URL 종료 문자로 사용하지 않도록 수정했다.
- `trim_extracted_url()`을 추가해 URL 끝의 불필요한 구두점만 제거하도록 했다.
- 닫는 괄호 `)`는 여는 괄호 `(`보다 많을 때만 끝에서 제거하도록 하여 파일명 내 괄호를 보존했다.
- WordCloud 자동 스케일 기준에 `max/min` 비율을 추가했다.
- 빈도 편차가 큰 경우 `log1p()` 스케일을 더 일찍 적용하도록 조정했다.
- WordCloud 옵션을 `relative_scaling=0.45`, `collocations=False`, `max_words=keyWordList`로 조정했다.

## 5. 테스트 결과

### 5.1 문법 검사
- 명령: `python -m py_compile nplt30.py`
- 결과: 정상 통과

### 5.2 괄호 포함 PDF URL 추출 회귀 테스트
- 테스트 URL: `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_1권(통사).pdf`
- 결과: `.pdf`까지 포함한 전체 URL이 보존됨
- 추가 테스트: `window.open(https://example.com/test.pdf)` 형식의 마지막 `)`는 제거됨
- 결과: `nplt30 parenthesis URL extraction regression OK`

### 5.3 실제 PDF 존재 확인
- `현대중공업그룹_50년사_1권(통사).pdf`: `200 application/pdf`
- `현대중공업그룹_50년사_2권(성장스토리).pdf`: `200 application/pdf`
- `현대중공업그룹_50년사_3권(화보).pdf`: `200 application/pdf`

### 5.4 WordCloud 스케일 테스트
- 원본 빈도 비율: `HYUNDAI / SEAMARQ = 19.34`
- 스케일 후 비율: `1.57`
- 결과: `nplt30 wordcloud scaling regression OK`
- 샘플 이미지 생성: `C:\Users\user\Desktop\python\temp\wc_wordcloud_scale_test.png`

## 6. 결론
- HD PDF Broken Link는 실제 링크 문제가 아니라 코드의 URL 추출 오탐이었다.
- 괄호가 포함된 정상 URL을 보존하도록 수정하여 동일 유형의 PDF 링크 오탐을 줄였다.
- WordCloud는 최빈 단어가 너무 크게 표현되는 문제를 완화했다.

