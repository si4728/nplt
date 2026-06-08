# nplt26 기능별 개선 포인터

## 1. 실행 환경 및 설정

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| 경로 설정 | `nplt26.py:113` | `BASE_DIR`, `REPORT_DIR`, `TEMP_DIR`, `IMAGE_DIR` 기준은 유지한다. 새 산출물은 반드시 이 경로 상수를 사용한다. |
| 디렉터리 생성 | `nplt26.py:126` | `ensure_output_directories()`를 분석 시작과 테스트 시작 전에 호출한다. |
| DB 설정 | `nplt26.py:130` | 비밀번호 하드코딩은 제거된 상태다. DB 연결 실패 시 분석 자체는 계속 진행되도록 유지한다. |
| 의존성 안내 | `requirements.txt`, `setup_nltk.py`, `README.md` | 새 패키지를 추가하면 `requirements.txt`와 README 설치 절차도 같이 갱신한다. |

테스트 포인트:

- `python nplt26.py -h`
- `python -m unittest discover -s tests -p "test_*.py" -v`

## 2. URL 검증, HTTP, robots.txt

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| 사이트 루트 정규화 | `nplt26.py:260` | `normalize_site_root()`는 robots, sitemap, favicon 기본 URL 계산에 사용한다. |
| 사설망 차단 | `nplt26.py:268` | `validate_public_url()` 정책은 SSRF 방어와 직접 관련된다. 예외 허용은 `NPLT_ALLOW_PRIVATE_NETWORKS`로만 처리한다. |
| 응답 디코딩 | `nplt26.py:294` | `decode_response_text()`에서 charset, apparent encoding, fallback 순서를 유지한다. |
| robots 상태 확인 | `nplt26.py:306`, `nplt26.py:347`, `nplt26.py:359` | `fetch_text_status()`, `robots_status_message()`, `configure_robots()`가 존재 여부와 접근 정책을 분리한다. |
| 보고서 출력 | `nplt26.py:5018` | robots.txt는 파일 유무와 HTTP 상태를 표시한다. 차단 규칙 목록 출력으로 바꾸지 않는다. |

테스트 포인트:

- `test_fetch_text_status_treats_empty_200_as_available`
- `test_robots_status_message_reports_file_availability`
- `test_configure_robots_blocks_disallowed_path`

## 3. Favicon 처리

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| favicon 저장 | `nplt26.py:1069` | `save_Favicon()`은 실제 이미지 형식을 검증하고 PNG가 아닌 경우 PNG로 변환한다. |
| 보고서 항목 추가 | `nplt26.py:4184` | `add_favicon_report()`는 URL과 로컬 경로를 구조화된 dict로 저장한다. |
| 경로 복구 | `nplt26.py:4198` | `resolve_favicon_path()`는 legacy `.png.png` 경로를 복구한다. |
| Word 삽입 | `nplt26.py:4258` | `report_write()`의 `xstyle == 7` 분기에서 0.25 inch 이하로 삽입한다. |

개선 포인터:

- favicon 다운로드 실패 시 URL만 남기는 fallback 메시지를 더 명확히 한다.
- favicon 후보 탐색을 `<link rel>` 우선순위 기반으로 정리한다.

테스트 포인트:

- `test_save_favicon_keeps_single_png_extension`
- `test_report_write_uses_structured_favicon_data`
- `test_report_write_repairs_legacy_double_png_path`

## 4. 이미지 및 컬러 분석

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| 이미지 저장 | `nplt26.py:1095` | `save_url2image()`는 홈페이지 컬러 분석용 이미지 저장 함수다. |
| RGB 분포 | `nplt26.py:1145` | `get_rgb_space()`는 R/G/B/Neutral 픽셀 비율을 계산한다. |
| RGB 막대 | `nplt26.py:1169` | `make_image_analysis_bar()`는 Word 보고서용 차트를 만든다. |
| 대표 색상 | `nplt26.py:1241` | `make_dominant_color_chart()`는 샘플링과 KMeans로 dominant color를 만든다. |
| CSS 폰트 색상 | `nplt26.py:1312`, `nplt26.py:1334`, `nplt26.py:1354` | CSS color 정규화, 집계, 차트 생성이 분리되어 있다. |
| 보고서 출력 | `nplt26.py:5353` | `Website Color Analysis` 섹션에서 대표색, RGB 분포, 폰트 색상을 함께 출력한다. |

개선 포인터:

- 첫 페이지 이미지 우선 정책은 유지한다.
- 다운로드 실패 이미지는 조용히 제외하되 제외 개수를 보고서에 표시한다.
- KMeans cluster 수가 실제 색상 수보다 많을 때 warning을 줄이는 방어 로직을 추가한다.

테스트 포인트:

- `test_get_rgb_space_counts_dominant_channels`
- `test_get_rgb_space_handles_missing_file`
- `test_extract_font_colors_normalizes_css_values`
- `test_color_analysis_charts_are_included_in_report`
- `test_font_color_chart_is_included_in_report`

## 5. Font List

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| CSS 폰트 파싱 | `nplt26.py:1921` | `parsing_fontlist()`가 `font-family`, `font` shorthand, `@font-face`를 처리한다. |
| 폰트 선택 | `nplt26.py:1965` | `select_font()`에서 중복 제거와 출력 대상 선별을 담당한다. |
| 보고서 출력 | `nplt26.py:5140` | 5개 단위로 줄바꿈해 Word 보고서에 출력한다. |

개선 포인터:

- CSS 파서 기반으로 교체하면 quoted family, fallback, `var()` 처리 안정성이 좋아진다.
- 폰트명과 폰트 컬러 분석 결과를 같은 섹션 또는 인접 섹션으로 묶는 것을 검토한다.

테스트 포인트:

- `test_parsing_fontlist_handles_css_shorthand_and_face`

## 6. SNS 사용 점검

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| SNS 도메인 목록 | `nplt26.py:531` | `sns_domain_list`는 평면 host 목록이다. 플랫폼별 구조로 바꾸는 것이 1순위다. |
| 비정상 URL 필터 | `nplt26.py:2791` | `abnormal_url()`의 `find()` 조건 오류가 SNS 누락의 직접 원인이다. 먼저 수정한다. |
| 스캔 큐 | `nplt26.py:2935` | `addScanList()`가 전체 URL 기준 중복 제거를 수행한다. |
| SNS 판별 | `nplt26.py:3044` | 현재 `xUrl in sns_domain_list` 완전 일치 방식이다. `identify_sns_platform()`으로 교체한다. |
| DB 저장 | `nplt26.py:1013` | `sns_url`, `sns_cnt`만 저장한다. 플랫폼, 유형, 페이지 수, 고유 URL 수를 분리한다. |
| Word 출력 | `nplt26.py:5230` | 삽입 순서 텍스트 출력이다. 표, 정렬, 링크 유형, 하이퍼링크를 적용한다. |

우선순위:

1. `abnormal_url()`을 `"LOGIN" in s[0].upper()` 형태로 수정한다.
2. `normalize_sns_host()`와 `identify_sns_platform()`을 추가한다.
3. `www`, `m`, 기본 도메인을 같은 플랫폼으로 통합한다.
4. profile/content/share/embed를 분류한다.
5. Word 보고서를 표로 바꾼다.

테스트 포인트:

- YouTube `watch?v=...`가 제거되지 않는지
- `facebook.com`, `www.facebook.com`, `m.facebook.com` 통합
- `fakefacebook.com` 오검출 방지
- `youtu.be`, `youtube.com`, `www.youtube.com` 통합
- 공유 URL과 공식 프로필 URL 분리

참조 문서:

- `nplt26_SNS사용점검_검토보고서.md`
- `nplt26_SNS_link_information_루틴_검토보고서.md`

## 7. ESG 키워드

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| 키워드 목록 | `nplt26.py:391` | `nplt_esg_word`는 471개 평면 배열이다. CSV/JSON 구조화 후보이다. |
| 문자열 검색 | `nplt26.py:1513` | `check_stringAll()`은 단순 부분 문자열 검색이다. |
| 집계 | `nplt26.py:1520` | `counting_esg_word()`는 한 페이지 내 중복을 1회로 처리한다. |
| 본문 호출 | `nplt26.py:3879` | `word_html_string` 대상으로 ESG 집계를 수행한다. |
| DB 저장 | `nplt26.py:958` | 정렬 전 dict 순서로 제한 저장한다. |
| 보고서 출력 | `nplt26.py:5297` | 보고서에는 집계 수 기준 정렬 후 출력한다. |

우선순위:

1. 키워드와 본문에 Unicode NFKC, 공백 축약, casefold 적용.
2. 영어 단일어는 word boundary 기반 검색.
3. `Frequency ESG word list`를 `Pages containing ESG keywords`로 변경.
4. DB 저장도 집계 수 기준으로 정렬.
5. 중복, 앞 공백, 오탈자 정리.

테스트 포인트:

- 영어 대소문자 혼합 검출
- `SOCIAL IMPACT ASSESSMENT` 중첩 정책
- 페이지 수와 실제 출현 횟수 분리
- 중복 키워드 1회 집계

참조 문서:

- `nplt26_ESG키워드_검토보고서.md`

## 8. Tree Map 및 외부 도메인

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| host 정규화 | `nplt26.py:1751` | `normalize_host()`에서 `www.` 제거와 소문자 처리를 한다. |
| 내부 경로 변환 | `nplt26.py:1756` | `tree_path_for_url()`이 내부 URL만 경로로 변환한다. |
| 트리 데이터 생성 | `nplt26.py:1777` | `build_tree_map_data()`가 내부 경로와 외부 도메인을 분리한다. |
| 보고서 출력 | `nplt26.py:5253` | Tree Map 출력 후 `External Link Domains`를 별도 출력한다. |

개선 포인터:

- 외부 도메인 결과를 SNS 판별과 공유해서 중복 로직을 줄인다.
- Tree Map은 내부 구조 전용으로 유지한다.
- 외부 도메인은 정렬과 상위 N 제한을 추가할 수 있다.

테스트 포인트:

- `test_tree_map_separates_internal_paths_and_external_domains`

## 9. Word 보고서 생성

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| 진행 데이터 누적 | `nplt26.py:4172` | `progress_make()`가 `report_list`에 스타일 코드와 문자열을 저장한다. |
| 이미지 크기 조정 | `nplt26.py:4219` | `add_picture_fitted()`가 Word 본문 폭과 높이에 맞게 조정한다. |
| Word 생성 | `nplt26.py:4258` | `report_write()`에서 모든 섹션을 하나의 문단에 붙인다. |
| 이미지 삽입 | `nplt26.py:4302` | `xstyle == 5`에서 이미지 크기를 본문 폭에 맞춘다. |
| favicon 삽입 | `nplt26.py:4315` | `xstyle == 7`에서 favicon을 작은 크기로 삽입한다. |

우선순위:

1. 큰 섹션은 Word 표로 전환한다. 특히 SNS, External Domains, ESG, word frequency.
2. `report_list`를 문자열 중심에서 구조화 항목 중심으로 확장한다.
3. 하이퍼링크 helper를 추가한다.
4. report write error 로그에 섹션명과 원본 타입을 포함한다.

테스트 포인트:

- `test_report_images_fit_word_content_width`
- `test_report_write_uses_structured_favicon_data`

## 10. DB 저장

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| DB 연결 | `nplt26.py:845` | `get_db_cursor()`는 contextmanager로 commit/rollback/close를 처리한다. |
| report DB 저장 | `nplt26.py:907`, `nplt26.py:917` | `_report_to_db()`가 basic, esg, word, head, sns, domain 등을 저장한다. |
| 마지막 ID 조회 | `nplt26.py:864` | 실패 시 0을 반환한다. |

개선 포인터:

- `_report_to_db()`가 너무 크므로 table별 insert 함수로 분리한다.
- ESG/word/SNS 저장 전 정렬 기준을 보고서와 일치시킨다.
- 긴 키워드 49자 truncation은 충돌 가능성이 있으므로 원문 컬럼 확장 또는 hash를 추가한다.

테스트 포인트:

- `test_db_cursor_commits_and_closes`
- `test_get_lastnumber_handles_connection_failure`

## 11. 도메인 및 WHOIS

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| 도메인 정보 출력 | `nplt26.py:4078` | `getdomainInformation()`에서 `nplt_whois2.get_domain_info()` 결과를 보고서에 출력한다. |
| 보고서 위치 | `nplt26.py:5391` | `Domain Information` 섹션에서 호출한다. |
| WHOIS 구현 | `nplt_whois2.py` | KISA API key가 없으면 DNS fallback을 사용한다. |

개선 포인터:

- API key 없음, DNS fallback, 네트워크 실패를 보고서에서 구분한다.
- 도메인 정규화 결과를 함께 출력한다.

테스트 포인트:

- `tests/test_nplt_whois2.py`

## 12. 링크 수집 및 스캔 루프

| 기능 | 코드 위치 | 개선 포인터 |
|---|---|---|
| URL 정규화 | `nplt26.py:2260` | `urlForm()`이 상대 URL, protocol-relative URL, 비정상 path를 처리한다. |
| 그래프 노드 | `nplt26.py:2828` | `addgraphNode()`가 node graph와 외부 링크 관계에 영향을 준다. |
| 스캔 큐 추가 | `nplt26.py:2935` | 중복 제거 기준은 전체 URL이다. |
| 메인 스캔 | `nplt26.py:2947` | `scanWeb()`가 대부분의 분석을 수행하는 핵심 함수다. |
| 앵커 수집 | `nplt26.py:3764` | `<a href>`를 수집하고 `addScanList()`로 보낸다. |

개선 포인터:

- `scanWeb()`를 수집, 필터링, 다운로드, 분석, 보고 데이터 생성 단계로 나눈다.
- URL 필터 정책과 SNS/외부 도메인 집계를 분리한다.
- 쿼리 파라미터 정규화 정책을 명시한다.

테스트 포인트:

- `test_should_skip_href_rejects_javascript_this_reference`
- `test_validate_public_url_accepts_public_address`
- `test_validate_public_url_blocks_private_address`

## 13. 다음 작업 추천 순서

1. SNS 누락 수정: `abnormal_url()` 및 플랫폼 식별 함수 추가.
2. SNS Word 표 출력: `list_sns` 구조화와 `report_write()` 표 출력.
3. ESG 검색 정확도: 정규화, 대소문자, 단어 경계.
4. DB 저장 정렬: ESG/word/SNS 상위 결과 일치.
5. Word 보고서 구조화: 표와 하이퍼링크 helper 도입.
6. `scanWeb()` 단계별 분리: 장기 유지보수용 리팩터링.
