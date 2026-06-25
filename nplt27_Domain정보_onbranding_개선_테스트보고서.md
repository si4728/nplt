# nplt27 Domain Information 개선 테스트 보고서

## 1. 문제 확인

기존 `www.onbranding.co.kr.docx` 보고서의 마지막 Domain Information에는 아래 두 줄만 출력되었다.

```text
Domain Information
   domain name is www.onbranding.co.kr
   lookup source is whois.com
```

문제점:

- 등록 도메인 기준인 `onbranding.co.kr`이 아니라 서비스 호스트명 `www.onbranding.co.kr`로 조회되었다.
- `whois.com` 응답에서 Registrar, Creation Date, Expiration Date, Updated Date, Name Server가 충분히 채워지지 않았다.
- 그 결과 Domain Information 섹션이 불완전하게 출력되었다.

## 2. 적용 개선

`nplt_whois.py`를 개선했다.

- `normalize_domain()` 보강
  - URL scheme, path, port 제거
  - `www.`, `m.`, `mobile.` 같은 일반 서비스 서브도메인 제거
  - `co.kr`, `or.kr`, `go.kr` 등 한국 2단계 도메인은 등록 도메인 단위로 정규화
- DNS fallback 추가
  - RDAP/whois.com 결과에 `name_servers`가 없으면 Google DNS의 NS 레코드 조회로 보완
  - DNS로 보완된 경우 `source_priority`에 `dns` 추가
- 테스트 추가
  - `tests/test_nplt_whois.py`

## 3. 실제 사이트 확인

대상:

```text
www.onbranding.co.kr
```

실행:

```text
python -c "import nplt_whois, nplt27; print('normalized=', nplt_whois.normalize_domain('www.onbranding.co.kr')); result=nplt27.getdomainInformation('www.onbranding.co.kr'); print(result)"
```

결과:

```text
normalized= onbranding.co.kr
domain name is onbranding.co.kr
lookup source is whois.com, dns
name_servers:
  ns1.cafe24.co.kr
  ns1.cafe24.com
  ns2.cafe24.co.kr
  ns2.cafe24.com
```

개선 후 반환값:

```text
{
  'Domain_Name': 'onbranding.co.kr',
  'Name_Server': [
    'ns1.cafe24.co.kr',
    'ns1.cafe24.com',
    'ns2.cafe24.co.kr',
    'ns2.cafe24.com'
  ],
  'Lookup_Source': 'whois.com, dns'
}
```

## 4. 테스트 결과

### nplt_whois 테스트

```text
python -m unittest tests.test_nplt_whois -v
결과: OK
실행: 4 tests
소요: 0.009s
```

### nplt27 테스트

```text
python -m unittest tests.test_nplt27 -v
결과: OK
실행: 16 tests
소요: 71.747s
```

### 컴파일 확인

```text
python -m py_compile nplt_whois.py nplt27.py
결과: OK
```

## 5. 남은 한계

Registrar, Creation Date, Expiration Date, Updated Date는 `whois.com`이 `onbranding.co.kr`에 대해 충분한 값을 제공하지 않아 아직 비어 있다. 이 항목까지 안정적으로 채우려면 KISA WHOIS OpenAPI 키 기반 조회를 `nplt_whois.py`에 추가하거나, 허용 가능한 다른 공식 WHOIS/RDAP 소스를 추가해야 한다.

## 6. 결론

마지막 Domain Information 문제 중 등록 도메인 정규화와 Name Server 누락 문제는 개선 완료되었다. 보고서에는 이제 `onbranding.co.kr` 기준 도메인명과 DNS fallback 기반 네임서버가 출력된다.
