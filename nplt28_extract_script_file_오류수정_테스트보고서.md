# nplt28 extract_script_file 오류 수정 테스트 보고서

## 1. 오류 내용

실행 중 다음 오류가 발생했다.

```text
Traceback (most recent call last):
  File "C:\Users\user\Desktop\python\nplt28.py", line 5313, in <module>
    scanWeb(url, url)
  File "C:\Users\user\Desktop\python\nplt28.py", line 3673, in scanWeb
    extract_script_file(slink, url)
  File "C:\Users\user\Desktop\python\nplt28.py", line 1850, in extract_script_file
    filepath = inLink.get("src")
  File "...bs4\element.py", line 2366, in get
    return self.attrs.get(key, default)
AttributeError: 'NoneType' object has no attribute 'get'
```

## 2. 원인

`extract_script_file()`가 script tag 객체를 항상 정상 BeautifulSoup tag로 가정하고 `inLink.get("src")`를 바로 호출했다.

일부 비정상 HTML 또는 BeautifulSoup tag 객체에서는 `attrs`가 `None`일 수 있으며, 이 경우 `Tag.get()` 내부에서 `self.attrs.get()`을 호출하다가 `AttributeError`가 발생한다.

## 3. 적용 수정

파일:

```text
C:\Users\user\Desktop\python\nplt28.py
```

수정 함수:

```python
def extract_script_file(inLink, urls):
    if inLink is None or getattr(inLink, "attrs", None) is None:
        return
    filepath = inLink.get("src")
    if not filepath:
        return
    inpath   = str(filepath)
    if "." in inpath:
        exf = inpath.split('.')[-1].lower()
        if len(exf) < 5:
            add_list_script(inpath, urls, exf)
```

적용 결과:

- `inLink is None`이면 skip
- `inLink.attrs is None`이면 skip
- `src`가 없는 script tag이면 skip
- 정상 `src`가 있는 script tag만 `list_script`에 기록

## 4. 테스트 결과

### 문법 확인

```text
python -m py_compile nplt28.py
결과: OK
```

### 재현/방어 로직 mock 테스트

```text
nplt28 extract_script_file guard OK
```

검증 내용:

- `attrs=None` tag 입력 시 예외 없이 return
- `None` 입력 시 예외 없이 return
- 정상 `src='app.js'` 입력 시 `['app.js', 'http://example.com', 'js']` 기록

## 5. 결론

보고된 traceback은 `extract_script_file()`의 비정상 script tag 방어 누락이 원인이었다. 방어 로직을 추가하여 동일 오류가 다시 발생하지 않도록 수정했다.
