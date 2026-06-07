# nplt26.py 개선 계획 재수립

> 분석 기준일: 2026-06-07  
> 대상: `nplt26.py`, `nplt_whois2.py`, `nplt_forbiddenword.py`, `tests/`  
> 원칙: 현재 CLI와 보고서 결과를 보존하면서 결함 수정, 상태 분리, 모듈화 순서로 진행한다.

## 0. 진행 현황 (2026-06-07)

### Phase 1 1차 적용 완료

- [x] robots.txt를 최초 크롤링 전에 조회하고 `can_fetch()` 정책 적용
- [x] `-robots Yes/No` 옵션 추가, 기본값 `Yes`
- [x] robots/sitemap 반환값을 `str | None`으로 통일
- [x] sitemap 처리의 `.decode()` 및 `3931` 출력 제거
- [x] 응답 charset이 없을 때 `apparent_encoding`을 사용하는 공통 디코딩 함수 적용
- [x] 키워드 끝 숫자 제거 조건을 `isdigit()` 기반으로 수정
- [x] URL 스킴, 사용자 정보, DNS 해석 결과의 공인 IP 여부를 검사
- [x] 사설망 접근은 `NPLT_ALLOW_PRIVATE_NETWORKS=true`일 때만 허용
- [x] DB 커서 컨텍스트 매니저와 보고서 단일 트랜잭션 적용
- [x] 자동 테스트 21개에서 27개로 확대
- [x] `http://www.onbranding.co.kr` 실제 회귀 테스트 및 DOCX 생성 확인

### 다음 적용 항목

- [ ] HTTP 리다이렉트의 각 목적지에 URL/IP 정책 재검사
- [ ] robots.txt의 `crawl-delay` 반영 및 호스트 변경 시 정책 재로딩
- [ ] HTTP fetch와 HTML 분석 분리, fixture 기반 크롤링 테스트 추가
- [ ] DB rollback을 실제 테스트 DB 또는 통합 테스트로 검증
- [ ] 빈 `except`와 숫자 상태 코드를 단계적으로 제거

## 1. 현재 상태

| 항목 | 현재 값 |
|---|---:|
| `nplt26.py` | 5,103행 |
| 함수 | 112개 |
| 클래스 | 0개 |
| 빈 `except:` | 34개 |
| `global` 선언 | 20개 |
| `print()` 호출 | 243개 |
| 최상위 대입 | 117개 |
| 최상위 가변 상태 | 약 60개 |
| `scanWeb()` | 약 992행 |
| `__main__` 실행부 | 약 1,100행 |
| 자동 테스트 | 21개 |

### 완료된 개선

- `nplt25.py`를 보존하고 `nplt26.py`를 개선 대상으로 분리
- DB 접속 정보 환경변수화
- 공용 HTTP 세션과 timeout 적용
- TLS 검증 기본 활성화
- 경로의 `pathlib` 1차 적용
- import 시 후처리 실행 방지
- KISA WHOIS API 및 DNS fallback 적용
- favicon, 차트, 그래프의 DOCX 삽입 경로 수정
- `findAll()`을 `find_all()`로 교체
- Matplotlib 비대화형 백엔드 적용

## 2. 핵심 문제점

### P0. 즉시 수정할 정확성·안전성 문제

#### 2.1 robots.txt를 크롤링 후에 확인

현재 robots.txt 조회는 전체 페이지 수집이 끝난 뒤 보고서 생성 과정에서 수행된다. 따라서 크롤링 허용 여부와 지연 정책을 실제 요청에 반영하지 않는다.

**개선**

- 최초 페이지 요청 전에 `urllib.robotparser.RobotFileParser`로 정책 확인
- User-Agent와 `can_fetch()` 적용
- `crawl-delay`가 있으면 사이트별 요청 간격에 반영
- `--respect-robots Yes/No` 옵션 제공, 기본값은 `Yes`

#### 2.2 사용자 URL에 대한 내부망 접근 제한 없음

입력 URL과 페이지에서 발견한 링크를 직접 요청한다. 로컬 주소나 사설 IP가 입력되는 환경에서는 SSRF 형태의 내부 자원 접근 가능성이 있다.

**개선**

- 허용 스킴을 `http`, `https`로 제한
- `localhost`, loopback, link-local, private, reserved IP 차단
- DNS 재해석 후에도 목적지 IP 검증
- 리다이렉트 목적지도 동일하게 검증
- 내부망 검사가 필요한 운영 환경에는 명시적 허용 목록 제공

#### 2.3 sitemap 반환 타입 불일치

`getsitemapInformation()`은 실패 시 `None`을 반환하지만 호출부에서 바로 `.decode()`한다. 실제 실행에서 출력된 `3931`은 이 오류가 빈 예외 처리에 가려진 결과다.

**개선**

- robots/sitemap 함수 반환값을 `str | None`으로 통일
- 각 함수 내부에서 HTTP 상태, 문자 인코딩, 예외를 처리
- 호출부에서 `.decode()` 제거
- `3931` 같은 위치 번호 출력 대신 원인 로그 기록

#### 2.4 응답 인코딩을 UTF-8로 강제

모든 페이지에 `page.encoding = "utf-8"`을 적용하여 EUC-KR, CP949 등 다른 인코딩 페이지의 텍스트가 손상될 수 있다.

**개선**

- HTTP `Content-Type` charset 우선
- 없으면 `response.apparent_encoding` 또는 BeautifulSoup 감지 사용
- 원본 bytes와 해석된 text의 책임을 HTTP 계층에서 통일

#### 2.5 DB 함수의 자원 해제 오류 가능성

연결 전에 예외가 발생하면 `connection`과 `cursor`가 정의되지 않은 상태에서 `finally`가 실행될 수 있다. `insertImage()`는 성공 여부를 반환하지 않으며, `report_to_db()`는 여러 테이블을 부분 커밋한다.

**개선**

- DB 연결 컨텍스트 매니저 도입
- 전체 보고서 저장을 하나의 트랜잭션으로 처리
- 오류 시 rollback
- 함수 반환 타입과 실패 정책 명시
- 동적 컬럼명은 허용 목록으로 검증

#### 2.6 키워드 숫자 제거 오류 잔존

`kw[-1:]` 문자열을 정수 목록 `[0, 1, ...]`과 비교하므로 조건이 항상 거짓이다.

**개선**

```python
if kw and kw[-1].isdigit():
    kw = remove_right_number(kw)
```

#### 2.7 외부 부가 서비스가 핵심 실행을 지연

공인 IP 조회, Google 검색 결과 스크래핑, Naver/Google 속도 비교가 기본 실행에 포함된다. 분석 대상과 무관한 외부 장애가 전체 실행 시간과 결과 안정성에 영향을 준다.

**개선**

- 부가 조회를 `ExternalEnrichment` 단계로 분리
- 기본 비활성화 또는 개별 CLI 옵션 제공
- Google HTML 스크래핑 제거 또는 공식 API 사용
- 공인 IP 조회는 HTTPS 서비스로 교체

## 3. 구조적 문제

### 3.1 `scanWeb()`가 너무 많은 책임을 보유

약 992행 안에서 URL 정규화, 중복 제어, HTTP 요청, HTML 파싱, SEO 분석, 이미지 수집, 키워드 분석, 그래프 갱신을 모두 수행한다.

**목표 분리**

```text
fetch_page()
normalize_and_validate_url()
extract_links()
analyze_metadata()
analyze_images()
analyze_scripts_and_styles()
analyze_keywords()
record_page_result()
```

각 함수는 `PageResult`를 반환하고 공유 전역 변수를 직접 수정하지 않게 한다.

### 3.2 실행부가 1,100행

CLI 해석, 초기화, 크롤링, 통계 계산, 보고서 생성, 디버그 출력, KMeans 분석이 `if __name__ == "__main__"` 아래에 연결되어 있다.

**목표 구조**

```python
def parse_args() -> CrawlConfig: ...
def run(config: CrawlConfig) -> CrawlResult: ...
def build_report(result: CrawlResult) -> Path: ...
def main() -> int: ...
```

### 3.3 전역 상태와 세션 간 오염

최상위 가변 상태가 약 60개이며 새 크롤링 실행 전에 일부만 초기화된다. 같은 프로세스에서 두 사이트를 연속 분석하면 이전 결과가 섞일 수 있다.

**개선**

- `CrawlConfig`: 실행 설정
- `CrawlState`: 수집 중 가변 상태
- `PageResult`: 페이지별 분석 결과
- `CrawlResult`: 최종 불변 결과
- 크롤링마다 새 객체 생성

### 3.4 보고서 이벤트가 숫자 코드에 의존

`progress_make(1|2|4|5|...)`의 숫자가 텍스트, 제목, 경고, 이미지 의미를 동시에 표현한다.

**개선**

- `ReportItemKind` 열거형 도입
- `ReportItem(kind, text, image_path)` 데이터클래스 사용
- 콘솔 출력과 DOCX 생성을 동일 데이터에서 독립 처리

### 3.5 데이터와 로직 혼재

ESG 사전, 메시지, 필터 목록, HTML 태그 목록이 실행 코드와 같은 파일에 있다. `nplt_forbiddenword.py`도 1,958행의 데이터 중심 파일이다.

**개선**

- `constants.py`: 고정 상수
- JSON/TXT: ESG 및 금칙어 데이터
- 로딩 시 중복 제거와 정규화
- 데이터 변경이 코드 변경을 요구하지 않도록 분리

## 4. 성능 및 자원 문제

### 4.1 이미지 픽셀 Python 반복

`get_rgb_space()`가 모든 픽셀을 이중 반복한다.

**개선**

- NumPy boolean mask로 벡터화
- 분석 전 최대 해상도로 축소
- 벤치마크와 결과 동일성 테스트 추가

### 4.2 KMeans에 전체 이미지 픽셀 적재

모든 이미지를 `reshape()` 후 `np.vstack()`하여 메모리에 적재한다. 고해상도 이미지가 많으면 메모리가 급증한다.

**개선**

- 이미지당 고정 수 픽셀 무작위 샘플링
- 총 샘플 상한 설정
- `MiniBatchKMeans` 검토
- 기존 RGB 바 분석과 KMeans 분석의 중복 목적 정리

### 4.3 큐를 LIFO로 처리

`scanWebList.pop()`을 사용해 깊이 우선 방식으로 처리한다. 크롤링 깊이와 우선순위 제어가 어렵다.

**개선**

- `collections.deque.popleft()` 기반 BFS
- URL과 함께 depth 저장
- `max_pages`, `max_depth` 설정 추가

### 4.4 요청 재시도와 응답 크기 제한 부재

timeout은 적용됐지만 일시적 429/5xx 재시도, backoff, 최대 다운로드 크기가 없다.

**개선**

- `HTTPAdapter`와 `Retry` 적용
- 429, 500, 502, 503, 504만 제한적으로 재시도
- `Retry-After` 준수
- HTML과 이미지의 최대 응답 크기 설정
- 파일 다운로드는 streaming 처리

## 5. 테스트 공백

현재 테스트는 유틸리티와 WHOIS 파서 중심의 21개다. 핵심 크롤링, 보고서, DB는 자동 검증되지 않는다.

### 추가할 테스트

1. HTML fixture 3종
   - 상대·절대 URL과 redirect
   - EUC-KR 또는 CP949 페이지
   - 이미지, iframe, script, meta 태그 포함 페이지
2. HTTP mock 테스트
   - timeout, 404, 429, redirect loop
   - robots 차단
   - sitemap 없음
3. 크롤링 통합 테스트
   - 방문 URL 수
   - 내부/외부 링크 수
   - broken link 결과
4. 보고서 테스트
   - DOCX 생성
   - 필수 제목과 이미지 존재
5. DB 테스트
   - mock connection의 commit/rollback
   - 연결 실패 시 미정의 변수 오류 없음
6. 반복 실행 테스트
   - 한 프로세스에서 두 사이트 결과가 섞이지 않음

## 6. 실행 로드맵

### Phase 0. 기준선 갱신

**기간:** 2~3일

- 현재 `onbranding.co.kr` 결과를 JSON snapshot으로 저장
- HTML fixture 3종 작성
- 핵심 통계와 DOCX 산출물 테스트 추가
- `pytest`, coverage 구성

**완료 기준**

- [ ] 네트워크 없는 통합 테스트 가능
- [ ] 핵심 결과 snapshot 작성
- [ ] 테스트 40개 이상

### Phase 1. 정확성·안전성 수정

**기간:** 4~6일

- robots 정책을 크롤링 전에 적용
- URL/IP 안전 검사 추가
- sitemap/robots 반환 타입 통일
- 인코딩 자동 감지
- 숫자 접미사 버그 수정
- 34개 빈 `except:`를 구체적 예외로 교체
- 외부 부가 조회를 선택 옵션으로 전환

**완료 기준**

- [ ] 빈 `except:` 0개
- [ ] `3931` 위치 번호 오류 출력 제거
- [ ] private/loopback URL 차단 테스트
- [ ] CP949 fixture 정상 분석

### Phase 2. 실행 흐름과 상태 분리

**기간:** 1~2주

- `parse_args()`, `run()`, `main()` 분리
- `CrawlConfig`, `CrawlState`, `PageResult`, `CrawlResult` 작성
- 전역 상태를 기능 단위로 완전 이전
- BFS 큐, `max_pages`, `max_depth` 도입

**완료 기준**

- [ ] `__main__` 30행 이하
- [ ] 전역 가변 상태 10개 이하
- [ ] 연속 두 사이트 실행 테스트 통과

### Phase 3. `scanWeb()` 분해

**기간:** 2~3주

- HTTP fetch와 HTML 분석 분리
- 링크, SEO, 이미지, 스크립트, 키워드 분석기 분리
- 함수별 명시적 입력/출력과 타입 힌트 적용
- NLTK 리소스 누락 오류를 사전 검사

**완료 기준**

- [ ] 단일 함수 150행 이하
- [ ] 핵심 분석 함수 80% 이상 커버리지
- [ ] 기존 snapshot과 결과 일치

### Phase 4. DB·보고서 경계 정리

**기간:** 1주

- DB 컨텍스트 매니저와 단일 트랜잭션
- `ReportItem` 구조 도입
- 콘솔 렌더러와 DOCX 렌더러 분리
- 보고서 작성 실패 항목을 결과에 기록

**완료 기준**

- [ ] DB 연결 코드 1개
- [ ] rollback 테스트 통과
- [ ] 숫자 스타일 코드 제거
- [ ] DOCX 회귀 테스트 통과

### Phase 5. 모듈화

**기간:** 2~3주

```text
nplt/
├── __main__.py
├── config.py
├── models.py
├── crawler/
│   ├── engine.py
│   ├── http_client.py
│   ├── robots.py
│   └── url_policy.py
├── analyzers/
│   ├── seo.py
│   ├── links.py
│   ├── keywords.py
│   └── images.py
├── reporting/
│   ├── model.py
│   ├── console.py
│   └── docx.py
└── persistence/
    └── mysql.py
```

**완료 기준**

- [ ] `python -m nplt` 실행
- [ ] 기존 CLI 호환
- [ ] 순환 import 없음
- [ ] 전체 테스트 통과

### Phase 6. 측정 기반 성능 개선

**기간:** 1~2주

- 이미지 RGB 분석 벡터화
- KMeans 픽셀 샘플링
- HTTP retry/backoff
- 크롤링 구간별 프로파일링
- 동기 구조에서 먼저 최적화

**완료 기준**

- [ ] 메모리 상한 측정
- [ ] 이미지 분석 10배 이상 개선
- [ ] 대표 사이트 처리 시간 30% 이상 개선

### Phase 7. 선택적 병렬 처리와 배포

**기간:** 2~3주

- 상태 분리 완료 후 제한된 동시 요청 실험
- 사이트별 concurrency와 delay 적용
- `pyproject.toml`, ruff, mypy, CI 구성
- 비동기화는 실측 효과가 있을 때만 채택

## 7. 즉시 착수 순서

1. sitemap/robots 함수 반환 타입 통일과 `3931` 오류 제거
2. `kw[-1].isdigit()` 버그 수정
3. DB 연결 실패 시 `finally` 오류 제거
4. URL/IP 안전 검사와 robots 사전 확인
5. HTML fixture 및 HTTP mock 테스트 추가
6. `parse_args()`와 `main()` 분리
7. `CrawlState` 도입
8. `scanWeb()` 기능별 분해

## 8. 일정 재산정

| 단계 | 예상 기간 |
|---|---:|
| Phase 0~1 | 1~2주 |
| Phase 2~4 | 4~6주 |
| Phase 5~6 | 3~5주 |
| Phase 7 | 2~3주 |

안정적인 1차 구조 개선까지 약 2개월, 성능·배포 자동화까지 포함하면 약 3개월을 예상한다. 비동기 크롤링은 필수 목표가 아니라 측정 후 결정하는 선택 항목으로 둔다.
