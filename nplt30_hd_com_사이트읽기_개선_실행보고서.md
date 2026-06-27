# nplt30.py 사이트 읽기 개선 및 실행 보고서

## 1. 대상
- 파일: `C:\Users\user\Desktop\python\nplt30.py`
- 테스트 명령: `python nplt30.py -url www.hd.com -db y`
- 테스트 일시: 2026-06-27

## 2. 확인된 문제
- `www.hd.com` 접속 시 첫 페이지의 스크립트 리다이렉트 `/kr/main`을 정상 추적하지 못해 1페이지만 수집되는 문제가 있었다.
- `extract_text()`가 전달받은 BeautifulSoup 객체에서 `script/style` 태그를 직접 제거하여, 이후 스크립트 링크/리다이렉트 분석 루틴이 같은 HTML 정보를 재사용하지 못할 수 있었다.
- 절대 URL 리다이렉트 처리 시 `baseUrl`에 전체 URL이 들어갈 수 있어 내부/외부 링크 판정과 후속 수집 기준이 흔들릴 수 있었다.
- HTTPS 전환 후 `http_https` 기준값이 갱신되지 않아 이미지, favicon, 링크 정규화에 영향을 줄 수 있었다.
- favicon URL이 상대경로일 경우 저장 루틴에 부정확한 URL이 전달될 수 있었다.

## 3. 적용한 개선
- `extract_text()`에서 BeautifulSoup 객체를 얕은 복사한 뒤 텍스트 추출용 태그 제거를 수행하도록 변경했다.
- 스크립트 리다이렉트에서 절대 URL이 발견될 때 `baseUrl = urlparse(xurl).netloc` 형식으로 도메인만 저장하도록 수정했다.
- 리다이렉트 후 최종 URL 기준으로 `http_https = getHttp_Https(url)`를 다시 계산하도록 수정했다.
- favicon 저장 전 `FaviconUrl = formatHTTP(FaviconUrl)`를 적용해 상대경로/프로토콜 누락을 보정하도록 수정했다.

## 4. 테스트 결과

### 4.1 문법 검사
- 명령: `python -m py_compile nplt30.py`
- 결과: 정상 통과

### 4.2 extract_text 회귀 테스트
- 내용: `extract_text()` 실행 후 원본 Soup의 `script` 태그가 보존되는지 확인
- 결과: `nplt30 extract_text non-mutating check OK`

### 4.3 짧은 수집 테스트
- 명령: `python nplt30.py -url www.hd.com -db No -sl 2 -ca No -robots No`
- 결과: 정상적으로 리다이렉트 이후 페이지를 수집했다.
- 확인된 주요 URL:
  - `https://www.hd.com/`
  - `https://www.hd.com/kr/main`
  - `https://www.hd.com/kr/site-map/index`

### 4.4 DB 포함 실제 실행
- 명령: `python nplt30.py -url www.hd.com -db y`
- 결과: 정상 완료, exit code 0
- DB next id: `42329`
- 수집 페이지 수: `184`
- 내부 링크 수: `316`
- 외부 링크 수: `205`
- Broken link 수: `3`
- Anchor 수: `17979`
- Image 수: `1107`
- Script 수: `2726`
- Iframe 수: `184`
- Scan time: `98.56096911430359`초
- Average scan time: `0.5356574408386064`초
- favicon 저장 확인:
  - URL: `https://www.hd.com/common/images/favicon.ico`
  - 저장 경로: `C:\Users\user\AppData\Local\Temp\nplt_image\favicon.png`

## 5. 비교
- 개선 전 DB 실행: id `42328`, 수집 페이지 `1`
- 개선 후 DB 실행: id `42329`, 수집 페이지 `184`
- 결론: `www.hd.com`의 스크립트 리다이렉트 및 후속 페이지 수집 문제가 개선되었다.

