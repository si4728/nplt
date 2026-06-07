# nplt26.py 모듈별 재점검 및 개선 계획

> 점검일: 2026-06-07  
> 대상: `nplt26.py`, `nplt_whois2.py`, `nplt_forbiddenword.py`, `tests/`  
> 기준 사이트: `http://www.onbranding.co.kr`  
> 제외 범위: DB 비밀번호 교체 및 운영 자격 증명 변경

## 0. 단계별 진행 현황

### 2026-06-07: Phase A-1 HTML 인코딩 경로 완료

- [x] UTF-8, CP949, charset 미지정 응답 테스트 추가
- [x] 디코딩 문자열을 실제 BeautifulSoup 분석에 사용
- [x] 자동 테스트 30개 통과
- [x] `onbranding.co.kr` 17페이지 회귀 테스트 통과
- [x] DOCX 한글, Domain Information, robots, sitemap 확인
- [ ] Phase A fixture/snapshot 확대
- [ ] Phase B 리다이렉트별 URL/IP 재검증

테스트 결과는 `nplt26_테스트보고서_PhaseA_인코딩.md`에 기록한다.

### 2026-06-07: Phase A-2 Favicon 보고서 오류 완료

- [x] favicon URL과 로컬 경로를 구조화된 데이터로 분리
- [x] `.png.png` 이중 확장자 제거
- [x] 기존 `.png.png` report 경로 자동 복구
- [x] DOCX favicon 삽입 실패 fallback 추가
- [x] 자동 테스트 33개 통과
- [x] onbranding 실제 favicon 및 DOCX 삽입 테스트 통과

테스트 결과는 `nplt26_테스트보고서_PhaseA_Favicon.md`에 기록한다.

### 2026-06-07: Phase A-3 컬러 분석 DOCX 포함 완료

- [x] RGB/neutral 분포 차트를 DOCX에 삽입
- [x] KMeans 대표 색상 차트를 DOCX에 삽입
- [x] 대표 색상 HEX와 픽셀 비율 표시
- [x] 자동 테스트 34개 통과
- [x] onbranding 저장 이미지 기반 DOCX 이미지 2개 확인

테스트 결과는 `nplt26_테스트보고서_PhaseA_컬러분석보고서.md`에 기록한다.

### 2026-06-07: Phase A-4 첫 페이지·폰트 컬러 최적화 완료

- [x] 이미지 컬러 분석을 첫 페이지로 제한
- [x] 첫 페이지 CSS의 폰트/텍스트 색상 8종 분석
- [x] 폰트 색상 차트를 DOCX에 삽입
- [x] RGB 분석 벡터화
- [x] KMeans 리사이즈 및 최대 100,000픽셀 샘플링
- [x] 전체 실행시간 563.7초에서 26.44초로 단축
- [x] 자동 테스트 37개 통과

테스트 결과는 `nplt26_테스트보고서_PhaseA_첫페이지_폰트컬러.md`에 기록한다.

### 2026-06-07: Phase A-5 Word 이미지·Font List 개선 완료

- [x] 모든 일반 이미지를 Word 본문 폭 6인치 이하로 자동 축소
- [x] favicon 최대 0.25인치 제한
- [x] 이미지 종횡비 유지
- [x] `font-family`, `font` shorthand, `<font face>` 파싱
- [x] 첫 페이지 외부 CSS의 Font List 반영
- [x] `!important`와 CSS 제어값 제거
- [x] 자동 테스트 39개 통과

테스트 결과는 `nplt26_테스트보고서_PhaseA_Word이미지_FontList.md`에 기록한다.

### 2026-06-07: Phase A-6 robots.txt 존재 확인 완료

- [x] robots.txt 본문 보고서 출력 제거
- [x] HTTP 200, 404, 확인 실패 상태 구분
- [x] 빈 HTTP 200 응답도 파일 존재로 판정
- [x] 크롤링 allow/disallow 정책 적용은 유지
- [x] 자동 테스트 41개 통과
- [x] onbranding HTTP 200 및 DOCX 상태 메시지 확인

테스트 결과는 `nplt26_테스트보고서_PhaseA_Robots존재확인.md`에 기록한다.

### 2026-06-07: Phase A-7 Tree Map 내부·외부 링크 분리 완료

- [x] Tree Map에서 외부 전체 URL 제거
- [x] 내부 URL을 path 기준으로 정규화
- [x] HTTP/HTTPS와 `www` 변형 통합
- [x] 빈 경로 노드 제거
- [x] 외부 링크를 도메인별 고유 URL 수로 별도 출력
- [x] 자동 테스트 42개 통과

테스트 결과는 `nplt26_테스트보고서_PhaseA_TreeMap.md`에 기록한다.

## 1. 재점검 요약

| 항목 | 측정 결과 |
|---|---:|
| `nplt26.py` | 5,169행 |
| 함수 | 120개 |
| `scanWeb()` | 996행 |
| `__main__` 실행부 | 1,106행 |
| 전역 변수 쓰기 선언 | 26개 |
| 예외 처리 | 62개 |
| 빈 `except:` | 29개 |
| 자동 테스트 | 27개 |
| `nplt_forbiddenword.py` 목록 | 1,950개, 중복 89개 |

현재 코드는 기능상 실행되지만, `nplt26.py` 하나가 설정, HTTP, URL 정규화,
크롤링, HTML 분석, 이미지 처리, 집계, DB, DOCX, CLI를 모두 담당한다.
따라서 기능 추가보다 먼저 요청 계층과 실행 상태를 분리해야 한다.

## 2. 최우선 결함

### P0-1. 리다이렉트 목적지 URL/IP 검증 누락

- 최초 URL만 `validate_public_url()`로 검사한다.
- `requests`의 자동 리다이렉트와 HEAD 응답의 `Location`은 재검사하지 않는다.
- `save_Favicon()`, `save_url2image()`, `getheadInformation()`,
  `check_iframe_location()`도 공통 안전 정책을 우회한다.

**조치**

- 모든 HTTP 요청을 `SafeHttpClient` 하나로 통합한다.
- 자동 리다이렉트를 끄고 각 `Location`을 `urljoin()`한 뒤 재검사한다.
- 최대 리다이렉트 횟수, 최대 응답 크기, 허용 Content-Type을 설정한다.
- DNS 재해석 결과도 실제 연결 직전에 다시 확인한다.

### P0-2. 응답 인코딩 개선이 실제 HTML 파싱에 반영되지 않음

- `decode_response_text(page)`를 호출하지만 BeautifulSoup은 다시
  `page.content`와 `from_encoding="utf-8"`로 파싱한다.
- EUC-KR/CP949 페이지에서 제목, 본문, 키워드가 손상될 수 있다.

**조치**

- HTTP 계층에서 최종 디코딩 문자열을 결정한다.
- 분석기는 `response.text`가 아닌 `FetchedPage.text`만 사용한다.
- UTF-8, EUC-KR, CP949 fixture 테스트를 추가한다.

### P0-3. `scanWeb()`의 전역 상태 결합

- 996행에서 내부 함수 44개와 다수 전역 컬렉션을 직접 사용한다.
- 21개 전역 값을 쓰며, 한 번의 프로세스에서 두 사이트를 연속 실행하면
  이전 결과가 섞일 가능성이 있다.
- 부분 실패 시 어느 분석 항목이 실패했는지 구분하기 어렵다.

**조치**

- `CrawlConfig`, `CrawlState`, `PageResult`, `CrawlResult` 데이터 클래스를 만든다.
- 페이지 fetch, 링크 추출, 분석, 집계를 별도 단계로 나눈다.
- `scanWeb()` 재귀적 역할을 `Crawler.run()`의 명시적 큐 처리로 교체한다.

### P0-4. 오류 은폐

- 빈 `except:` 29개가 프로그래밍 오류까지 정상 흐름처럼 처리한다.
- 일부 네트워크 예외 분기는 상위 `Exception` 뒤에 있어 도달할 수 없다.
- 오류 번호 문자열과 대량 `print()` 때문에 원인 추적이 어렵다.

**조치**

- `requests.RequestException`, `ValueError`, 파서 오류 등으로 범위를 좁힌다.
- `logging`에 URL, 단계, 예외 유형을 구조화해 기록한다.
- 페이지별 `AnalysisIssue`를 결과에 포함하고 보고서에도 실패 항목을 표시한다.

## 3. 목표 모듈 구조

```text
nplt/
├── __main__.py
├── cli.py
├── config.py
├── models.py
├── logging_config.py
├── crawler/
│   ├── engine.py
│   ├── http_client.py
│   ├── url_policy.py
│   ├── robots.py
│   └── frontier.py
├── analyzers/
│   ├── html.py
│   ├── links.py
│   ├── seo.py
│   ├── keywords.py
│   ├── assets.py
│   ├── builder.py
│   └── performance.py
├── enrichment/
│   ├── whois.py
│   ├── dns.py
│   └── external.py
├── media/
│   ├── downloader.py
│   ├── colors.py
│   └── charts.py
├── reporting/
│   ├── model.py
│   ├── console.py
│   └── docx.py
└── persistence/
    └── mysql.py
```

기존 `nplt26.py`는 전환 기간에 호환 실행기 역할을 유지하고, 새 모듈의
`main()`을 호출하도록 단계적으로 축소한다.

## 4. 모듈별 점검 및 개선

### 4.1 설정·CLI

**문제**

- argparse 파싱과 1,100행 실행 흐름이 같은 블록에 있다.
- Yes/No 해석이 옵션마다 다르고 잘못된 값도 조용히 기본값이 된다.
- 실행마다 전역 컬렉션을 완전히 초기화한다는 보장이 없다.

**개선**

- `parse_args(argv) -> CrawlConfig`와 `run(config) -> CrawlResult` 분리
- 공통 `parse_bool()`과 argparse `choices` 적용
- `max_pages`, `max_depth`, `max_response_bytes`, `crawl_delay` 옵션 추가
- 출력 경로와 외부 부가 조회 옵션을 설정 객체로 이동

**완료 기준**

- `__main__` 10행 이하
- CLI 단위 테스트와 잘못된 옵션 테스트 통과
- 한 프로세스에서 서로 다른 사이트를 연속 실행해 상태가 섞이지 않음

### 4.2 HTTP·URL 정책

**문제**

- GET/HEAD 코드가 여러 함수에 중복된다.
- 자동 리다이렉트, 이미지 다운로드, 외부 조회 정책이 일관되지 않다.
- retry/backoff, 응답 크기 제한, Content-Type 검증이 없다.
- `getipInformation()`은 평문 HTTP 외부 API를 사용한다.

**개선**

- `SafeHttpClient.fetch()`와 `FetchedPage` 도입
- URL 정규화, 공인 IP 검사, 리다이렉트 검사를 요청마다 적용
- 스트리밍 다운로드와 최대 바이트 제한 적용
- 외부 부가 조회를 기본 크롤링과 분리하고 실패를 비치명적으로 처리
- HTTPS 지원 IP 정보 제공자로 교체하거나 기능을 선택 옵션으로 전환

**완료 기준**

- 네트워크 요청 경로가 공통 클라이언트 하나만 사용
- private/link-local/loopback 및 리다이렉트 우회 테스트 통과
- timeout, 404, 500, 비HTML, 대용량 응답 테스트 통과

### 4.3 robots·sitemap

**문제**

- 최초 호스트의 robots 정책 하나만 보관한다.
- 호스트가 변경되면 정책이 갱신되지 않는다.
- `crawl-delay`를 실제 요청 간격에 반영하지 않는다.
- sitemap은 존재 여부만 확인하고 URL 수집에는 사용하지 않는다.

**개선**

- 호스트별 `RobotsPolicy` 캐시 도입
- `can_fetch`, `crawl_delay`, sitemap URL을 구조화
- host별 요청 시각을 관리해 지연 적용
- sitemap XML 파싱은 별도 선택 기능으로 추가

**완료 기준**

- 호스트별 allow/disallow와 crawl-delay 테스트 통과
- robots 조회 실패 정책을 설정으로 명시

### 4.4 크롤링 엔진·URL 큐

**문제**

- LIFO `pop()`으로 실제 탐색 순서가 명확하지 않다.
- URL 중복 기준이 함수별로 다르고 수작업 문자열 결합이 많다.
- `sys.exit()`가 라이브러리 내부에서 호출될 수 있다.
- 페이지 수와 깊이의 명시적 상한이 없다.

**개선**

- `deque` 기반 BFS와 `CrawlTask(url, parent, depth)` 도입
- canonical URL 함수 하나로 fragment, 기본 포트, hostname case 정규화
- 방문/대기/실패 상태를 `CrawlState`가 소유
- 종료는 결과 상태로 반환하고 CLI만 exit code를 결정

**완료 기준**

- 동일 URL 변형의 중복 제거 테스트 통과
- `max_pages`, `max_depth`가 정확히 적용됨
- fixture 사이트의 방문 순서와 그래프 snapshot 일치

### 4.5 HTML·링크 분석

**문제**

- 링크, frame, meta refresh, JavaScript 문자열, 이미지, SEO 분석이
  `scanWeb()`에 혼합되어 있다.
- 정규식과 수작업 문자열 파싱이 많아 오탐과 예외 가능성이 높다.
- `abnormal_url()`의 `find()` 조건처럼 참/거짓 판정이 잘못될 수 있는
  레거시 코드가 남아 있다.

**개선**

- `analyze_page(page) -> PageResult` 순수 함수 구성
- `extract_links`, `analyze_head`, `analyze_images`,
  `analyze_embeds`, `detect_builder`로 분리
- URL 결합은 모두 `urljoin()` 사용
- JavaScript 링크 추출은 제한된 패턴만 지원하고 출처를 결과에 기록

**완료 기준**

- 분석 함수 80% 이상 단위 테스트
- 함수당 100행 이하
- 대표 HTML fixture 10종 결과 snapshot 통과

### 4.6 키워드·금칙어

**문제**

- NLTK 자원이 없으면 페이지 분석 전체가 실패할 수 있다.
- 금칙어 모듈은 1,950개 목록 중 89개가 중복된다.
- 현재 금칙어 발견 결과는 URL과 단어의 구조가 일관되지 않다.
- 목록 포함 여부를 list에서 선형 검색한다.

**개선**

- 금칙어 데이터를 UTF-8 텍스트/JSON 리소스로 분리하고 로드 시 정규화
- `frozenset`으로 중복 제거 및 O(1) 조회
- 대소문자, 공백, Unicode 정규화 정책 명시
- `ForbiddenMatch(url, word, normalized_word)` 구조 사용
- NLTK 자원 사전 점검과 명확한 대체 동작 추가

**완료 기준**

- 중복 0개, 빈 문자열 0개
- 한글/영문/공백 변형 테스트 통과
- NLTK 자원 부재 시 전체 크롤링은 계속되고 경고가 결과에 남음

### 4.7 이미지·차트

**문제**

- 이미지 요청도 안전 URL 정책을 우회한다.
- 전체 픽셀을 Python 이중 루프로 순회해 느리다.
- 모든 이미지 픽셀을 `vstack()`한 뒤 KMeans를 수행해 메모리 사용이 크다.
- 파일명 충돌, 확장자 없는 URL, 잘못된 이미지 처리 정책이 약하다.

**개선**

- 안전 HTTP 클라이언트와 콘텐츠 크기 제한 사용
- NumPy 벡터 연산으로 RGB 분류
- 이미지별 리사이즈/샘플링 후 제한된 픽셀만 KMeans에 입력
- URL 해시 기반 파일명과 MIME 기반 확장자 결정
- 차트 함수는 입력 데이터와 출력 경로만 받도록 순수화

**완료 기준**

- 기존 결과 대비 허용 오차 내 색상 비율 유지
- 동일 샘플에서 처리 시간 70% 이상 단축
- 손상 이미지와 대용량 이미지 테스트 통과

### 4.8 WHOIS·외부 부가 조회

**현재 평가**

- `nplt_whois2.py`는 204행, 전역 쓰기와 빈 `except`가 없고 테스트 4개가 있다.
- KISA 실패 시 DNS fallback이 동작하는 구조는 유지할 가치가 있다.

**개선**

- 반환 dict를 `DomainInfo` 데이터 클래스로 교체
- API 응답 fixture를 확대하고 JSON 형식 오류 테스트 추가
- `.co.kr` 외 도메인에 대한 KISA 적용 범위와 fallback 정책 명시
- Google 검색 HTML 스크래핑과 비교 사이트 조회는 기본 비활성화

**완료 기준**

- WHOIS 모듈 테스트 10개 이상
- API 키 없음, timeout, malformed JSON, 빈 DNS 결과 검증

### 4.9 DB 저장

**문제**

- 연결 관리는 개선됐지만 `_report_to_db()`가 전역 결과를 직접 읽는다.
- 동적 컬럼 문자열 생성이 스키마와 강하게 결합되어 있다.
- SQL과 전체 인자를 콘솔에 출력해 운영 데이터가 노출될 수 있다.
- 실제 rollback 통합 검증이 없다.

**개선**

- `ReportRecord`를 입력으로 받는 `MySqlReportRepository` 도입
- 허용 컬럼 매핑을 상수로 고정
- SQL 디버그 출력 제거, 행 수와 오류 코드만 로깅
- DB 미사용 실행에서는 connector 초기화도 하지 않도록 지연 import 검토

**완료 기준**

- 저장 함수가 전역 변수를 읽지 않음
- commit/rollback/부분 실패 테스트 통과
- DB 비활성 실행과 보고서 생성이 DB 패키지 상태에 영향받지 않음

### 4.10 보고서

**문제**

- 분석 중 `progress_make()`가 콘솔 출력, 보고서 모델, DB 레코드를 동시에 변경한다.
- 숫자 style code가 의미를 숨긴다.
- DOCX 작성 실패 시 항목을 건너뛰어 보고서가 불완전해도 성공처럼 끝난다.
- 그래프 함수가 입력 그래프를 직접 수정한다.

**개선**

- `ReportSection`, `ReportItem`, `Severity` 모델 도입
- 분석 결과에서 보고서 모델을 생성한 뒤 Console/DOCX/DB 렌더러가 소비
- 이미지 누락과 XML 비호환 문자를 사전 검증
- 그래프는 복사본을 렌더링

**완료 기준**

- 보고서 생성이 전역 `report_list`를 사용하지 않음
- DOCX 구조/텍스트/이미지 fixture 테스트 통과
- 누락 항목이 있으면 결과 상태가 `partial_success`로 표시됨

## 5. 단계별 실행 순서

### Phase A. 회귀 기준 고정

- 현재 `onbranding.co.kr` 실행 결과를 JSON snapshot으로 저장
- UTF-8/EUC-KR, redirect, robots, broken link fixture 작성
- 테스트를 27개에서 최소 45개로 확대

### Phase B. 안전 HTTP 계층

- `url_policy.py`, `http_client.py`, `robots.py` 분리
- 모든 요청 경로를 공통 클라이언트로 전환
- 인코딩과 리다이렉트 결함 수정

### Phase C. 실행 상태와 크롤러

- 설정/상태/결과 데이터 클래스 도입
- BFS frontier와 방문 정책 구현
- `scanWeb()`에서 fetch와 큐 관리를 제거

### Phase D. 분석기 분해

- 링크, SEO, 이미지, 키워드, builder 분석 순서로 이동
- 각 분석기는 `PageResult`만 수정하거나 새 결과를 반환
- 빈 `except`를 모듈 이동 시 함께 제거

### Phase E. 보고서·DB 분리

- 중립적인 보고서 모델 작성
- Console, DOCX, MySQL 어댑터 분리
- 기존 DOCX 결과와 비교 검증

### Phase F. 레거시 축소와 성능

- `nplt26.py`를 호환 실행기로 축소
- 이미지 벡터화와 샘플링 적용
- lint, type check, CI 도입

## 6. 우선 작업 백로그

1. [완료] HTML 파싱을 디코딩된 문자열로 변경하고 인코딩 fixture 추가
2. 리다이렉트별 URL/IP 재검증이 포함된 `SafeHttpClient` 작성
3. 이미지·favicon·HEAD·iframe 요청을 공통 클라이언트로 이동
4. `parse_args()`와 `run()` 분리
5. `CrawlConfig`, `CrawlState`, `PageResult` 도입
6. URL frontier와 canonical URL 분리
7. `scanWeb()`에서 링크 추출기 분리
8. 키워드/금칙어 분석기 분리 및 목록 중복 제거
9. 보고서 모델과 DOCX 렌더러 분리
10. DB repository 분리와 rollback 통합 테스트

## 7. 전체 완료 기준

- 자동 테스트 80개 이상, 핵심 모듈 커버리지 80% 이상
- 빈 `except:` 0개
- `scanWeb()` 제거 또는 100행 이하 orchestration 함수로 축소
- `__main__` 10행 이하
- 크롤링 모듈의 전역 가변 상태 0개
- 모든 HTTP 요청이 동일한 URL/IP/timeout/redirect 정책 사용
- `onbranding.co.kr`의 Domain Information, robots, sitemap, 한글, DOCX 결과 유지
- 기존 CLI 옵션 호환 및 종료 코드 문서화
