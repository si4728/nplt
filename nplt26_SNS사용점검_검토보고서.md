# nplt26 SNS 사용 점검 루틴 검토 보고서

## 1. 검토 범위

- SNS 도메인 목록: `sns_domain_list`
- 링크 수집: HTML의 `a`, `area` 및 일부 스크립트 링크
- 외부 도메인 판별: `relation_domain()`
- SNS 판별 및 집계: `scanWeb()`의 `xUrl in sns_domain_list`
- 보고서 및 DB 출력: `list_sns`

## 2. 현재 처리 흐름

1. HTML에서 링크를 수집한다.
2. `urlForm()`으로 링크를 절대 URL 형태로 변환한다.
3. `addScanList()`가 동일한 전체 URL을 한 번만 스캔 목록에 저장한다.
4. `scanWeb()`가 외부 링크로 판단한 URL의 호스트를 추출한다.
5. 호스트가 `sns_domain_list`와 완전히 일치하면 `list_sns`에 1을 더한다.
6. 보고서에는 도메인별 카운트를 출력하고 DB의 `sns` 테이블에 저장한다.

## 3. 주요 문제점

### 3.1 호스트 완전 일치로 인한 누락

현재 코드는 다음 조건만 사용한다.

```python
if xUrl in sns_domain_list:
    list_sns[xUrl] = list_sns.get(xUrl, 0) + 1
```

`www` 또는 모바일 서브도메인이 다르면 같은 플랫폼이어도 검출되지 않는다.

| URL 예 | 현재 결과 |
|---|---|
| `https://www.facebook.com/acme` | 검출 |
| `https://facebook.com/acme` | 누락 |
| `https://m.facebook.com/acme` | 누락 |
| `https://www.instagram.com/acme` | 검출 |
| `https://instagram.com/acme` | 누락 |
| `https://youtube.com/@acme` | 누락 |
| `https://m.youtube.com/watch?v=...` | 누락 |
| `https://linkedin.com/company/acme` | 누락 |
| `https://m.blog.naver.com/acme` | 누락 |
| `https://X.COM/acme` | 대소문자 때문에 누락 가능 |

### 3.2 주요 플랫폼 누락

현재 65개 도메인이 등록되어 있으나 다음과 같이 실제 사용 빈도가 높은 서비스가 빠져 있다.

- TikTok: `tiktok.com`
- Threads: `threads.net`
- 카카오 오픈채팅: `open.kakao.com`
- 네이버 포스트 및 일부 네이버 커뮤니티 주소
- Instagram, Facebook, YouTube 등의 `www` 없는 기본 도메인과 모바일 도메인

반대로 `vine.co`, `friendster.com`, `stumbleupon.com` 등 종료되었거나 현재 SNS 사용 점검에서 우선순위가 낮은 서비스가 포함되어 있다.

### 3.3 카운트 의미가 불명확함

`addScanList()`는 전체 URL을 `scanWebSet`으로 중복 제거한다. 따라서 현재 SNS 카운트는 다음 중 어느 것도 정확히 나타내지 않는다.

- SNS 링크가 등장한 전체 횟수
- SNS를 사용하는 페이지 수
- 연결된 SNS 계정 수

현재 값은 대체로 **고유 SNS 목적 URL 수**이다. 동일 계정 URL은 여러 페이지에 있어도 1회만 집계되고, 동일 플랫폼의 공유 URL에 쿼리 문자열이 다르면 여러 건으로 집계될 수 있다.

### 3.4 프로필과 공유 기능을 구분하지 않음

다음 링크가 모두 동일한 SNS 사용으로 집계된다.

- 공식 계정: `/company/acme`, `/@acme`
- 게시물·영상: `/posts/...`, `/watch?...`
- 공유 버튼: `/sharer/...`, `/intent/tweet`, `/sharing/share-offsite`
- 임베드 링크: `/embed/...`

홈페이지의 공식 SNS 채널 운영 여부를 확인하려는 목적이라면 공유 버튼이나 임베드 링크를 공식 계정 연결로 계산하면 안 된다.

### 3.5 플랫폼명이 아닌 호스트명으로 출력

보고서와 DB에는 `www.youtube.com`, `youtu.be`가 서로 다른 SNS로 기록된다. 동일 플랫폼의 여러 도메인을 하나의 이름으로 통합하지 못한다.

권장 출력 예:

| 플랫폼 | 프로필 | 콘텐츠 | 공유 | 발견 페이지 |
|---|---:|---:|---:|---:|
| YouTube | 1 | 4 | 0 | 3 |
| Instagram | 1 | 2 | 0 | 2 |
| Facebook | 1 | 0 | 3 | 4 |

### 3.6 정렬과 재실행 안정성

- 보고서는 `list_sns` 삽입 순서로 출력되어 사용량 순위가 아니다.
- `list_sns`와 `scanWebSet`은 전역 객체이며 명시적인 초기화 함수가 없다.
- 같은 Python 프로세스에서 분석을 반복할 경우 이전 결과가 남을 위험이 있다.

### 3.7 테스트 부재

현재 테스트에는 SNS 도메인 정규화, 서브도메인 처리, 플랫폼 통합, 공유 링크 구분, 카운트 의미를 검증하는 항목이 없다.

## 4. 개선 권장 구조

### 4.1 플랫폼별 도메인 매핑

단순 문자열 목록 대신 플랫폼 정보를 구조화한다.

```python
SNS_PLATFORMS = {
    "facebook": {"domains": {"facebook.com"}},
    "instagram": {"domains": {"instagram.com"}},
    "youtube": {"domains": {"youtube.com", "youtu.be"}},
    "x": {"domains": {"x.com", "twitter.com"}},
    "linkedin": {"domains": {"linkedin.com"}},
    "naver_blog": {"domains": {"blog.naver.com"}},
}
```

호스트는 소문자로 변환하고 포트와 끝의 점을 제거한다. `www`, `m`, `mobile` 같은 허용 서브도메인은 기준 도메인에 포함되는지 안전하게 비교한다.

문자열의 단순 `endswith("facebook.com")`는 `fakefacebook.com`도 허용할 수 있으므로 다음 형태로 비교해야 한다.

```python
host == domain or host.endswith("." + domain)
```

### 4.2 링크 유형 분류

플랫폼과 URL 경로를 기준으로 최소한 다음 유형을 구분한다.

- `profile`: 공식 계정 또는 채널
- `content`: 게시물, 영상, 쇼츠 등
- `share`: 공유 버튼 URL
- `embed`: 임베드 URL
- `unknown`: 분류할 수 없는 SNS URL

### 4.3 집계 지표 분리

- `link_count`: HTML에 나타난 전체 링크 수
- `page_count`: 해당 SNS가 발견된 페이지 수
- `unique_url_count`: 고유 목적 URL 수
- `profile_count`: 고유 계정 또는 채널 수

기존 DB 호환성이 필요하면 현재 `sns_cnt`에는 `unique_url_count`를 유지하고 새 필드를 추가하는 방식이 적절하다.

### 4.4 보고서 개선

- 도메인 대신 플랫폼명으로 통합한다.
- 사용량 기준으로 정렬한다.
- 공식 채널과 단순 공유 기능을 구분한다.
- `SNS 연결정보가 없습니다` 대신 다음을 구분한다.
  - SNS 링크 없음
  - 공유 링크만 발견
  - 공식 SNS 채널 발견

## 5. 단계별 개선 계획

### Phase SNS-1: 검출 누락 보정

1. `normalize_sns_host()`를 추가한다.
2. `identify_sns_platform()`을 추가한다.
3. 기본·`www`·모바일 서브도메인을 동일 플랫폼으로 통합한다.
4. TikTok, Threads, 카카오 등 주요 누락 플랫폼을 보완한다.
5. 플랫폼 식별 단위 테스트를 추가한다.

### Phase SNS-2: 링크 유형 및 집계 개선

1. 프로필·콘텐츠·공유·임베드 링크를 분류한다.
2. 페이지별 중복과 전체 URL 중복을 각각 관리한다.
3. 전체 링크 수, 발견 페이지 수, 고유 URL 수를 분리한다.
4. 동일 계정 URL의 쿼리 및 추적 파라미터를 정규화한다.

### Phase SNS-3: 보고서와 DB 개선

1. 플랫폼명과 링크 유형별 결과를 Word 보고서에 출력한다.
2. 카운트 내림차순으로 정렬한다.
3. 기존 `sns` 테이블과의 호환 방식을 결정한다.
4. 분석 시작 시 SNS 전역 상태를 초기화한다.

## 6. 필수 테스트 항목

- `facebook.com`, `www.facebook.com`, `m.facebook.com` 통합
- 호스트 대소문자 정규화
- `fakefacebook.com` 오검출 방지
- `youtube.com`, `www.youtube.com`, `m.youtube.com`, `youtu.be` 통합
- `x.com`과 `twitter.com` 통합
- 프로필과 공유 URL 분류
- 같은 SNS 링크가 여러 페이지에 있을 때 `link_count`와 `page_count` 분리
- 쿼리 문자열만 다른 동일 공유 URL 처리
- 분석을 두 번 실행했을 때 이전 결과가 남지 않는지 확인
- 보고서 정렬 및 SNS 미검출 메시지 확인

## 7. 결론

현재 루틴은 등록된 특정 호스트의 외부 링크 존재 여부를 단순 확인하는 수준이다. 일반적인 SNS URL 변형을 많이 놓치고, 공식 계정 연결과 공유 버튼을 구분하지 않으며, 출력 카운트도 사용 횟수나 페이지 수로 해석하기 어렵다.

우선 Phase SNS-1에서 도메인 정규화와 플랫폼 통합을 적용한 뒤, Phase SNS-2에서 링크 유형과 집계 지표를 분리하는 순서가 적절하다.
