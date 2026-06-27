# nplt28 1차 성능/중복 개선 테스트 보고서

## 1. 작업 목적

`nplt27.py`는 원본으로 보존하고, 신규 파일 `nplt28.py`를 생성하여 저위험 성능 개선과 중복 루틴 정리를 1차 적용했다.

원본 보존:

```text
C:\Users\user\Desktop\python\nplt27.py
```

신규 개선 파일:

```text
C:\Users\user\Desktop\python\nplt28.py
```

## 2. 적용 내용

### 2.1 `nplt28.py` 신규 생성

`nplt27.py`를 복사하여 `nplt28.py`를 생성했다.

### 2.2 BeautifulSoup `find_all()` 반복 호출 완화

페이지 파싱 직후 주요 태그 목록을 한 번에 수집하는 `collect_page_tags()`를 추가했다.

```python
def collect_page_tags(content):
    return {
        "scripts": content.find_all("script"),
        "links": content.find_all("link"),
        "metas": content.find_all("meta"),
        "styles": content.find_all("style"),
        "styled": content.find_all(style=True),
        "colored": content.find_all(color=True),
        "imgs": content.find_all("img"),
        "amp_imgs": content.find_all("amp-img"),
        "frames": content.find_all("frame"),
        "iframes": content.find_all("iframe"),
        "anchors": content.find_all("a"),
        "areas": content.find_all("area"),
        "objects": content.find_all("object"),
        "embeds": content.find_all("embed"),
    }
```

`scanWeb()` 내부의 반복 `content.find_all()` 일부를 `page_tags[...]` 캐시 사용으로 변경했다.

적용된 주요 태그:

- `script`
- `link`
- `meta`
- `style`
- inline `style`
- `color`
- `img`
- `amp-img`
- `frame`
- `iframe`
- `object`
- `embed`
- `a`
- `area`

### 2.3 불필요한 반복 출력 축소

크롤링 루프 안의 디버그성 출력 일부를 `Debug_w()`로 전환했다.

- script tag 원문 출력 축소
- `.load()` 추출 대상 출력 축소
- `.load()` 링크 출력 축소
- `getheadInformation()`의 URL/response 출력 축소

### 2.4 잘못된 style count 수정

기존:

```python
styleCount = styleCount + len(content.find_all('<style'))
```

개선:

```python
styleCount = styleCount + len(page_tags["styles"])
```

`find_all('<style')`는 BeautifulSoup 태그 검색으로 적절하지 않으므로, 캐시된 `style` 태그 목록을 사용하도록 수정했다.

### 2.5 마지막 대량 디버그 덤프 제한

보고서 생성 및 DB 저장 후 이어지는 대량 출력 블록은 일반 실행에서 생략하도록 했다.

```python
if not Debug_mode:
    sys.exit(0)
```

따라서 일반 실행에서는 보고서 작성 후 종료하고, 개발용 상세 덤프는 `-dm Yes`일 때만 진행된다.

## 3. 테스트 결과

### 문법 확인

```text
python -m py_compile nplt28.py
결과: OK
```

### 태그 캐시 함수 검증

```text
nplt28 collect_page_tags OK
```

검증 내용:

- script 1개
- style 1개
- anchor 1개
- image 1개
- iframe 1개

### CLI 도움말 확인

```text
python nplt28.py -h
결과: OK
```

### 기본 함수 import 확인

```text
True
WordPress
```

검증 내용:

- `is_yes_option("yes") == True`
- WordPress generator meta detection 정상

### 원본 보존 확인

`nplt27.py`와 `nplt28.py`의 SHA256 해시가 다름을 확인했다. 즉, `nplt27.py`는 보존되고 `nplt28.py`에만 변경이 적용되었다.

```text
nplt27.py: B0AA0DD45D0897BEFA571B35C70FE78438B3F4A1418284606A639893DBFF7580
nplt28.py: F3A80E5A7D27497672C51D4D3EF26A6BA18EBB6AA2B725A8E5F0A5EFF4C09C16
```

## 4. 아직 남은 개선 포인트

이번 1차 변경은 저위험 개선만 적용했다. 다음 단계에서 아래 항목을 이어서 적용하는 것이 좋다.

1. `HEAD + GET` 중복 요청 제거 또는 조건부화
2. URL 정규화 함수 통합
3. `identify_website_builder_legacy()`의 실행 불가능한 코드 제거
4. 파일 마지막 `if False` 색상 분석 구버전 블록 제거
5. NLTK POS tagging 옵션화
6. 이미지 색상 분석 resize/sampling 적용
7. `scanWeb()` 기능 분리

## 5. 결론

`nplt28.py`는 `nplt27.py` 원본을 보존한 상태에서 생성되었고, `scanWeb()`의 반복 태그 탐색 일부를 캐시화하여 파싱 중복을 줄였다. 또한 일반 실행에서 불필요한 마지막 디버그 덤프를 생략해 체감 실행 속도와 출력량을 줄였다.
