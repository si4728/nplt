# nplt26 Phase A 테스트 보고서: HTML 인코딩 경로

> 테스트일: 2026-06-07  
> 변경 대상: `nplt26.py`, `tests/test_nplt26.py`  
> 기준 사이트: `http://www.onbranding.co.kr`

## 1. 변경 내용

- `parse_html_response(response)` 공통 함수 추가
- HTTP 헤더 charset 또는 `apparent_encoding`으로 디코딩한 문자열을
  BeautifulSoup에 전달하도록 변경
- `scanWeb()`의 UTF-8 강제 파싱 제거
- iframe 확인과 Google HTML 파싱도 동일한 디코딩 경로 사용
- 태그 검증이 `page.text`를 다시 읽지 않고 확정된 `page_text`를 사용

## 2. 자동 테스트

실행 명령:

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
```

결과:

- 전체 30개 통과
- 실패 0개
- 오류 0개
- 기존 27개에서 인코딩 테스트 3개 추가

추가된 검증:

- UTF-8 charset 헤더가 있는 한글 HTML
- CP949 charset 헤더가 있는 한글 HTML
- charset이 없을 때 `apparent_encoding` 적용

## 3. 정적 검증

실행 명령:

```powershell
python -m py_compile nplt26.py nplt_whois2.py nplt_forbiddenword.py
```

결과:

- 컴파일 성공
- 디코딩 대상 HTML에 남아 있는 실제 `from_encoding="utf-8"` 사용 0개

## 4. 실사이트 회귀 테스트

실행 옵션:

```powershell
python nplt26.py -url http://www.onbranding.co.kr -db No -cost Yes -dm No -robots Yes
```

결과:

| 항목 | 결과 |
|---|---|
| 프로세스 종료 코드 | 0 |
| 분석 페이지 | 17 |
| 크롤링 표시 시간 | 3.609초 |
| 페이지 평균 표시 시간 | 0.212초 |
| 전체 실행 시간 | 약 563.7초 |
| DOCX 생성 | 성공 |
| Node graph 생성 | 성공 |
| 한글 `온브랜딩` | 정상 |
| Unicode 대체문자 `�` | 없음 |
| Domain Information | 정상 출력 |
| robots.txt | 정상 출력 |
| sitemap | 정상 출력 |
| Traceback | 없음 |
| report write error | 없음 |

생성 파일:

- `temp/phaseA_report/www.onbranding.co.kr.docx`
- `temp/phaseA_report/www.onbranding.co.kr.png`
- `temp/onbranding_phaseA_encoding_test.log`

## 5. 테스트 중 확인된 환경 사항

첫 실행은 기존 `report/www.onbranding.co.kr.docx`가 다른 프로그램에서 열려
있어 `PermissionError`가 발생했다. 코드 회귀와 분리하기 위해 별도 테스트
출력 폴더로 재실행했고 정상 완료했다.

샌드박스 내부 실행에서는 외부 DNS 접속이 차단되어 WHOIS DNS fallback이
실패했다. 외부 접속 승인 후 재실행에서는 Domain Information이 정상 출력됐다.

## 6. 판정

**통과**

HTML 디코딩 결과가 실제 분석기에 전달되며, 기존 사이트 분석 결과와 DOCX
출력이 유지된다.

## 7. 잔여 위험

- HTTP 리다이렉트 목적지 URL/IP 재검증은 아직 적용되지 않았다.
- 전체 실행 시간 대부분이 이미지 수집 및 KMeans 후처리에 사용된다.
- 빈 `except:` 29개는 후속 모듈 분리 단계에서 제거해야 한다.
