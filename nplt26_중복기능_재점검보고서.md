# nplt26 중복 기능 재점검 보고서

## 1. 요약

정적 점검 결과, 동일한 이름의 함수가 중복 정의된 문제는 없다. 다만 같은 목적을 비슷한 방식으로 처리하는 유사 기능과 legacy 데이터가 남아 있다.

가장 중요한 중복/유사 항목은 다음이다.

- SNS legacy 목록 `sns_domain_list`와 신규 `SNS_PLATFORMS`
- host/domain 정규화 함수군
- URL 단순화 함수군
- JavaScript/link 추출 함수군
- 문자열 포함 검사 함수군
- report 출력 함수군
- 확장자 skip 목록의 데이터 중복

## 2. 자동 점검 결과

| 항목 | 결과 |
|---|---:|
| top-level 함수 수 | 150 |
| 동일 이름 함수 중복 | 0 |
| top-level 변수 중복 할당 | 없음 |
| `sns_domain_list` 항목 | 65 |
| `sns_domain_list` 중복 | 0 |
| `SNS_PLATFORMS` 플랫폼 | 28 |
| `SNS_PLATFORMS` 도메인 | 39 |
| `SNS_PLATFORMS` 내부 도메인 중복 | 0 |
| `skip_ext_list` 항목 | 140 |
| `skip_ext_list` 고유 항목 | 132 |

`skip_ext_list` 중복 항목:

- `zip`
- `bin`
- `dot`
- `psd`
- `mp4`
- `avi`
- `mov`
- `ai`

## 3. 중복/유사 기능 상세

### 3.1 SNS 목록 중복

| 항목 | 코드 위치 | 상태 |
|---|---|---|
| legacy host 목록 | `nplt26.py:533` | `sns_domain_list` |
| 신규 플랫폼 매핑 | `nplt26.py:545` | `SNS_PLATFORMS` |
| 플랫폼 식별 | `nplt26.py:1606` | `identify_sns_platform()` |

현재 `identify_sns_platform()`은 먼저 `SNS_PLATFORMS`를 보고, 이후 fallback으로 `sns_domain_list`를 본다. 즉 기능상 중복이지만 호환성 때문에 유지 중이다.

권장:

1. `sns_domain_list`에만 있고 `SNS_PLATFORMS`에 없는 도메인을 선별한다.
2. 필요한 도메인은 `SNS_PLATFORMS`로 이동한다.
3. fallback 사용 빈도를 로그 또는 테스트로 확인한다.
4. 1~2회 릴리스 뒤 `sns_domain_list`를 제거한다.

위험도: 중간. 바로 제거하면 오래된 SNS 도메인 검출이 사라질 수 있다.

### 3.2 host/domain 정규화 중복

| 함수 | 코드 위치 | 용도 |
|---|---|---|
| `get_domain()` | `nplt26.py:1761` | 기존 URL 문자열에서 host 추출 |
| `relation_domain()` | `nplt26.py:1776` | 내부/외부 도메인 판단 |
| `cmp_domain()` | `nplt26.py:1468` | 도메인 비교용 기존 함수 |
| `normalize_host()` | `nplt26.py:1924` | Tree Map용 host 정규화 |
| `normalize_sns_host()` | `nplt26.py:1590` | SNS용 host 정규화 |

중복 성격:

- `normalize_host()`와 `normalize_sns_host()`는 둘 다 host 소문자화와 `www.` 제거를 한다.
- `get_domain()`은 직접 문자열 slicing을 사용하고, `normalize_sns_host()`는 `urlparse()`를 사용한다.
- `cmp_domain()`은 현재 `scanWeb()`의 early return 조건에 쓰이지만, host 문자열에 `//`가 없으면 항상 `3`을 반환해 실효성이 낮다.

권장:

1. 공통 함수 `normalize_domain_host()`를 만들고 Tree/SNS가 공유하게 한다.
2. `get_domain()`은 호환 wrapper로 남기되 내부 구현을 `urlparse()` 기반으로 바꾼다.
3. `cmp_domain()` 사용 의미를 재검토한다. 실효성이 없다면 테스트 추가 후 제거한다.

위험도: 높음. 스캔 범위와 외부 링크 분류에 직접 영향.

### 3.3 URL 단순화 함수 중복

| 함수 | 코드 위치 | 용도 |
|---|---|---|
| `simpleUrl()` | `nplt26.py:2166` | URL path 축약 |
| `simpleUrl2()` | `nplt26.py:2188` | `simpleUrl()` 후 추가 축약 |
| `get_parentPath()` | `nplt26.py:1732` | depth 기반 parent path |
| `get_parent_path()` | `nplt26.py:1912` | Tree Node parent path |

중복 성격:

- Tree Map과 URL 요약에서 비슷한 path 축약을 각각 구현한다.
- `get_parentPath()`와 `get_parent_path()`는 이름도 유사해 혼동 가능성이 크다.

권장:

- `path_parent_for_tree()`와 `collapse_path_for_display()`처럼 목적 중심 이름으로 교체한다.
- 기존 함수명은 테스트 통과 후 wrapper로 일정 기간 유지한다.

위험도: 중간. Tree Map 출력이 바뀔 수 있다.

### 3.4 JavaScript/link 추출 함수 중복

| 함수 | 코드 위치 | 용도 |
|---|---|---|
| `get_locationhref()` | `nplt26.py:2234` | `location.href` 추출 |
| `get_location()` | `nplt26.py:2279` | `document.location` 추출 |
| `get_location2()` | `nplt26.py:2295` | 다른 location 패턴 추출 |
| `get_windowlocationhref()` | `nplt26.py:2369` | `window.location.href` 추출 |
| `get_href2()` | `nplt26.py:2316` | legacy href 추출 |
| `get_href()` | `nplt26.py:2340` | regex 기반 href 추출 |

중복 성격:

- location 계열 함수가 문자열 slicing 기반으로 여러 개 존재한다.
- `get_href2()`는 현재 직접 호출되지 않는 것으로 보이며 `get_href()`가 사용 중이다.

권장:

1. `extract_navigation_url(script_text)` 하나로 통합한다.
2. `get_href2()`는 호출이 없으면 제거 후보로 표시한다.
3. JavaScript URL 추출 테스트를 추가한 뒤 통합한다.

위험도: 중간~높음. JS 기반 이동 링크 수집에 영향.

### 3.5 문자열 포함 검사 함수 중복

| 함수 | 코드 위치 | 용도 |
|---|---|---|
| `check_string()` | `nplt26.py:1515` | list 중 하나라도 포함 |
| `check_string2()` | `nplt26.py:1523` | `find()` 기반 포함 |
| `check_stringAll()` | `nplt26.py:1547` | 포함된 항목 목록 반환 |
| `check_string_Length()` | `nplt26.py:1539` | 길이 또는 포함 검사 |

중복 성격:

- `check_string()`과 `check_string2()`는 거의 같은 기능이다.
- `check_stringAll()`은 반환 타입이 다르므로 유지 가치가 있다.

권장:

- `contains_any()`와 `find_all_contains()`로 이름을 명확히 한다.
- `check_string2()`는 `check_string()`으로 대체 가능하다.

위험도: 낮음~중간. 호출 지점이 많아 일괄 치환 테스트 필요.

### 3.6 report 출력 함수군

| 함수 | 코드 위치 | 용도 |
|---|---|---|
| `progress_make()` | `nplt26.py:4350` | 기본 보고서 라인 |
| `improved_progress_make()` | `nplt26.py:4324` | 출력 + DB record 저장 |
| `progress_make2()` | `nplt26.py:4412` | 두 값 조합 |
| `progress_make3()` | `nplt26.py:4416` | 숫자 + 단위 |
| `progress_make33()` | `nplt26.py:4423` | 숫자 2개 + 단위 |
| `progress_make_table()` | `nplt26.py:4436` | 구조화 표 |

중복 성격:

- `progress_make2/3/33`은 문자열 포맷 편의 함수다.
- `improved_progress_make()`는 DB 저장까지 포함해 역할이 섞여 있다.

권장:

1. `report_add_line()`, `report_add_metric()`, `report_add_table()`로 새 API를 만든다.
2. DB record 저장은 `record_metric()`으로 분리한다.
3. 기존 함수는 wrapper로 유지하다가 점진 제거한다.

위험도: 중간. 보고서와 DB 출력 모두 영향.

### 3.7 확장자 skip 목록 데이터 중복

| 데이터 | 코드 위치 | 문제 |
|---|---|---|
| `skip_ext_list` | `nplt26.py:471` | 140개 중 8개 중복 |

권장:

- list 대신 tuple 또는 set literal로 정리한다.
- 출력 순서가 필요하면 `dict.fromkeys(skip_ext_list)`로 중복만 제거한다.

위험도: 낮음.

## 4. 즉시 제거 가능 후보

아래는 비교적 안전한 후보지만, 삭제 전 테스트 추가가 좋다.

| 후보 | 이유 | 권장 조치 |
|---|---|---|
| `skip_ext_list` 중복 값 | 데이터 중복 | 중복 제거 |
| `check_string2()` | `check_string()`과 거의 동일 | 호출부 1곳 대체 |
| `get_href2()` | 직접 호출 없음으로 보임 | 한 번 더 grep 후 제거 |

## 5. 보수적으로 유지할 후보

| 후보 | 유지 이유 |
|---|---|
| `sns_domain_list` | `SNS_PLATFORMS` fallback으로 legacy 도메인 보존 |
| `get_domain()` | 코드 전반에서 많이 사용 |
| `relation_domain()` | 내부/외부 도메인 판단 핵심 |
| `progress_make*()` | 보고서 전체에 광범위 사용 |
| location 추출 함수군 | JS 링크 수집 회귀 위험 |

## 6. 권장 정리 순서

1. `skip_ext_list` 중복 제거.
2. `check_string2()`를 `check_string()`으로 대체하고 테스트.
3. `get_href2()` 미사용 확인 후 제거.
4. `normalize_domain_host()` 공통 함수 도입.
5. `get_domain()` 내부 구현을 공통 함수 기반으로 변경.
6. `progress_make*()`는 새 report API 도입 후 wrapper화.
7. JS navigation 추출 함수군은 충분한 샘플 테스트 작성 후 통합.

## 7. 결론

현재 코드는 동일 이름 함수 중복은 없지만, legacy 구현과 신규 개선 함수가 함께 존재하는 과도기 상태다. 지금 바로 큰 폭으로 삭제하기보다는 낮은 위험도 항목부터 제거하고, URL/보고서/JS 링크 추출처럼 영향 범위가 큰 부분은 테스트를 먼저 늘린 뒤 단계적으로 통합하는 것이 안전하다.
