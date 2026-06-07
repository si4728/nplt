# nplt26 SNS link information 루틴 검토 보고서

## 1. 결론

현재 `SNS link information`은 정상적인 SNS 링크를 누락할 수 있다. 실제 생성된 `deokyanggas.com.docx`에서는 Tree Map의 외부 도메인에 `youtube.com: 1`이 존재하지만 SNS 섹션에는 다음과 같이 출력된다.

```text
SNS link information
 - Can not found SNS link information
```

직접 원인은 SNS 판별 전에 호출되는 `abnormal_url()`의 조건 오류이다.

## 2. 직접 원인

현재 코드:

```python
def abnormal_url(u):
    s = u.split("?")
    if len(s)==2:
        if s[0].upper().find("LOGIN"):
            if s[1].find("&")==-1:
                return True
    return False
```

Python의 `str.find()`는 문자열을 찾지 못하면 `-1`을 반환한다. `-1`은 조건문에서 참으로 평가되므로 `LOGIN`이 없는 정상 URL도 비정상 URL로 처리된다.

영향 예:

| URL | 현재 `abnormal_url()` 결과 |
|---|---|
| `https://www.youtube.com/watch?v=1` | `True` |
| `https://youtube.com/watch?v=1` | `True` |
| `https://twitter.com/intent/tweet?url=x` | `True` |
| `https://www.facebook.com/sharer.php?u=x` | `True` |
| `https://youtu.be/abc` | `False` |

따라서 쿼리 파라미터가 하나인 YouTube 영상, SNS 공유 링크 등은 `scanWeb()`의 SNS 판별부에 도달하지 못한다.

의도대로 로그인 URL만 차단하려면 최소한 다음처럼 명시적으로 비교해야 한다.

```python
if "LOGIN" in s[0].upper():
```

하지만 로그인 URL 제외 정책 자체도 SNS 탐지와 페이지 스캔에서 분리하는 것이 안전하다.

## 3. SNS 결과 생성 경로

1. HTML의 링크가 `addScanList()`에 저장된다.
2. `scanWeb()`가 URL을 처리한다.
3. `abnormal_url()`이 비정상 URL 여부를 판단한다.
4. 외부 도메인이면 호스트가 `sns_domain_list`에 있는지 확인한다.
5. 검출 결과를 `list_sns`에 누적한다.
6. 보고서 생성부가 `list_sns`를 Word 문서에 출력한다.
7. DB 사용 시 `sns` 테이블에도 같은 값을 저장한다.

즉 Word 출력부만의 문제가 아니라, 출력 데이터가 만들어지기 전에 정상 링크가 제거되는 구조적 문제이다.

## 4. 출력부 문제

### 4.1 카운트 의미가 표시되지 않음

현재 출력 예:

```text
 1   12   www.youtube.com
```

숫자 `1`과 `12`의 의미를 설명하는 열 제목이 없다. `12`는 전체 링크 출현 횟수나 페이지 수가 아니라 현재 구조상 고유 목적 URL의 수에 가깝다.

### 4.2 정렬되지 않음

`list_sns.items()` 삽입 순서대로 출력한다. 많이 사용된 플랫폼 순위 또는 플랫폼명 순서가 아니다.

### 4.3 동일 플랫폼 분리

다음 값은 동일 플랫폼이지만 별도 행으로 출력된다.

- `www.youtube.com`
- `youtube.com`
- `youtu.be`

플랫폼명을 기준으로 `YouTube` 하나로 통합해야 한다.

### 4.4 클릭 가능한 링크가 아님

Word 보고서에는 호스트명이 일반 텍스트로 추가된다. 실제 계정 URL이 저장되지 않으며 하이퍼링크도 생성되지 않는다.

### 4.5 표 형식이 아님

모든 보고서 내용이 사실상 하나의 큰 Word 문단에 연속 추가된다. SNS 목록도 고정 폭 공백으로 열을 흉내 내므로 글꼴, 줄바꿈, 페이지 폭에 따라 정렬이 깨질 수 있다.

### 4.6 영문 메시지 오류

현재:

```text
Can not found SNS link information
```

권장:

```text
No SNS links were found.
```

단, 공식 계정과 공유 링크를 구분하게 되면 다음처럼 표시하는 것이 더 정확하다.

- `No SNS links were found.`
- `Only SNS sharing links were found.`
- `Official SNS profile links were found.`

## 5. DB 저장 문제

현재 DB에는 다음 값만 저장한다.

- `id`
- `sns_url`: 호스트명
- `sns_cnt`: 모호한 카운트

문제점:

- 플랫폼명이 없다.
- 실제 프로필 URL이 없다.
- 프로필, 게시물, 공유, 임베드 유형을 구분하지 않는다.
- 페이지 수와 링크 수를 구분하지 않는다.
- Word 보고서와 마찬가지로 탐지 누락의 영향을 그대로 받는다.

## 6. 우선 개선 순서

### Phase 1: 정상 링크 누락 수정

1. `abnormal_url()`의 `find()` 조건 오류를 수정한다.
2. 정상 쿼리 URL과 로그인 URL 테스트를 추가한다.
3. SNS 판별을 일반 페이지 스캔 제외 로직보다 먼저 수행한다.
4. YouTube 영상 URL이 SNS 결과에 포함되는지 통합 테스트한다.

### Phase 2: SNS 결과 구조화

1. 호스트를 정규화하고 플랫폼명으로 통합한다.
2. 프로필·콘텐츠·공유·임베드 유형을 구분한다.
3. 전체 링크 수, 발견 페이지 수, 고유 URL 수를 별도로 집계한다.
4. 공식 계정 URL을 결과에 보존한다.

### Phase 3: Word 및 DB 출력 개선

Word 표 권장 열:

| 플랫폼 | 유형 | 발견 페이지 | 링크 수 | 대표 URL |
|---|---|---:|---:|---|
| YouTube | Profile | 2 | 3 | 채널 URL |

추가 개선:

- 플랫폼 또는 사용량 기준 정렬
- 대표 URL에 Word 하이퍼링크 적용
- 빈 결과 메시지 교정
- DB에 플랫폼, 유형, 페이지 수, 고유 URL 수 저장

## 7. 필수 테스트

- `watch?v=...` YouTube URL이 `abnormal_url()`에서 제외되지 않는지 확인
- 로그인 URL만 정책에 따라 제외되는지 확인
- `youtu.be`와 `youtube.com`을 YouTube로 통합
- 공유 URL과 공식 프로필 URL 구분
- Tree Map 외부 SNS 도메인과 SNS 섹션 결과 일관성 확인
- SNS 결과의 카운트 정렬 확인
- Word 표와 하이퍼링크 생성 확인
- DB 저장 값과 Word 출력 값 일치 확인

## 8. 판정

현재 `SNS link information` 결과는 신뢰하기 어렵다. 특히 쿼리 문자열을 가진 정상 SNS URL이 사전 필터에서 제거되므로 “SNS 연결정보가 없습니다”라는 결과가 실제 사이트 상태와 다를 수 있다.

가장 먼저 `abnormal_url()`을 수정하고 테스트한 뒤, SNS 판별과 보고서 표현을 단계적으로 개선해야 한다.
