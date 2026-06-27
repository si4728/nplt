# nplt28 www.hd.com 사이트 읽기 개선 테스트 보고서

## 1. 문제 현상

명령:

```text
python nplt28.py -url www.hd.com -db y
```

문제:

- `www.hd.com`이 제대로 읽히지 않고 1페이지만 분석되는 현상 발생
- 초기 HTML의 script redirect를 따라가지 못함

## 2. 원인

`www.hd.com`의 초기 HTML은 다음과 같이 script redirect만 포함한다.

```html
<script>
    location.href = "/kr/main";
</script>
```

`nplt28.py` 1차 개선에서 `collect_page_tags()`로 script 태그를 캐시했지만, 바로 뒤에서 호출되는 `extract_text(content)`가 원본 BeautifulSoup 객체의 script 태그를 `decompose()`로 제거했다.

그 결과:

- 캐시된 script tag도 `<></>` 형태로 비어 버림
- `location.href="/kr/main"` 정보가 사라짐
- `/kr/main`이 `scanWebList`에 추가되지 않음
- 전체 사이트가 1페이지만 읽힘

## 3. 적용 수정

### 3.1 `extract_text()` 원본 변형 방지

수정 전:

```python
def extract_text(content):
    for script in content.find_all("script"):
        script.decompose()
    text = content.get_text(separator=' ', strip=True)
    return text
```

수정 후:

```python
def extract_text(content):
    content = copy.copy(content)
    for script in content.find_all("script"):
        script.decompose()
    text = content.get_text(separator=' ', strip=True)
    return text
```

텍스트 추출용 복사본만 수정하도록 변경했다.

### 3.2 HTTPS redirect 후 scheme 갱신

`http://www.hd.com`은 `https://www.hd.com/`로 301 redirect된다.

수정 내용:

- Location이 절대 URL일 때 `baseUrl`에는 `urlparse(xurl).netloc`만 저장
- redirect 후 `http_https = getHttp_Https(url)`로 scheme 갱신

결과:

- 내부 링크가 `http://...`가 아니라 `https://...`로 생성됨

### 3.3 콘솔 UnicodeEncodeError 방지

HD현대 페이지 title에 `–` 같은 문자가 포함되어 Windows `cp949` 콘솔 출력 중 오류가 발생했다.

수정:

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

### 3.4 favicon 상대 URL 보정

favicon URL이 `www.hd.com/common/images/favicon.ico`처럼 scheme 없이 저장되는 경우가 있어 저장 직전 `formatHTTP()`로 보정했다.

## 4. 테스트 결과

### 문법 확인

```text
python -m py_compile nplt28.py
결과: OK
```

### script redirect regression 확인

```text
nplt28 hd redirect regression check OK
```

확인 내용:

- `extract_text()` 호출 후에도 원본 script tag가 유지됨
- `location.href = "/kr/main"` 정보가 보존됨

### 실제 사이트 짧은 확인

명령:

```text
python nplt28.py -url www.hd.com -db No -sl 2 -ca No -robots No
```

결과:

```text
1      os: 0     https://www.hd.com/
2      os: 0     https://www.hd.com/kr/main
3      os: 1     https://www.hd.com/kr/site-map/index
```

초기 1페이지만 읽던 문제가 해결되어 `/kr/main`과 후속 페이지를 따라간다.

### 실제 사이트 전체 확인

명령:

```text
python nplt28.py -url www.hd.com -db No -ca No -robots No -wl 10
```

결과:

- 정상 종료
- `UnicodeEncodeError` 재발 없음
- `/kr/main`, `/en/main`, sitemap, business, investors, sustainability 등 다수 페이지 분석
- Tree Map, External Link Domains, ESG keywords, Word Frequency, IP/Domain Information 출력 완료

## 5. 결론

`www.hd.com`을 제대로 읽지 못하던 원인은 `extract_text()`가 원본 HTML Soup에서 script redirect를 제거한 것이었다. 복사본 기반 텍스트 추출로 수정하여 script redirect를 보존했고, HTTPS redirect와 콘솔 인코딩 문제도 함께 보완했다.
