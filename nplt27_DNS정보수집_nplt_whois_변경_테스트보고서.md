# nplt27 DNS/Domain 정보 수집 변경 테스트 보고서

## 1. 변경 목적

`nplt27.py`의 Domain/DNS 정보 수집 루틴을 기존 `nplt_whois2.py` 호출 방식에서 새 `nplt_whois.py`의 `get_domain_registration_info()` 호출 방식으로 변경했다.

## 2. 적용 내용

- `nplt27.py` import 변경
  - 기존: `import nplt_whois2`
  - 변경: `import nplt_whois`
- `getdomainInformation()`에서 `nplt_whois.get_domain_registration_info()`를 호출하도록 변경
- 새 모듈 결과 키를 기존 보고서/DB 흐름에서 사용하던 키로 변환하는 어댑터 추가
  - `domain` -> `Domain_Name`
  - `registrar` -> `Registrar`
  - `creation_date` -> `Creation_Date`
  - `expiration_date` -> `Expiration_Date`
  - `updated_date` -> `Updated_Date`
  - `name_servers` -> `Name_Server`
  - `source_priority` -> `Lookup_Source`
- 도메인 만료일까지 남은 일수 계산 기능 유지
  - `Expiration_Date` 기반으로 `NoDRfexpire` 계산

## 3. 단위 테스트 결과

### nplt27 테스트

```text
python -m unittest tests.test_nplt27 -v
결과: OK
실행: 16 tests
소요: 24.688s
```

추가된 테스트:

- `adapt_domain_registration_info()`가 새 `nplt_whois.py` 결과를 기존 키 구조로 변환하는지 확인
- `getdomainInformation()`이 `nplt_whois.get_domain_registration_info()`를 호출하는지 확인

### 기존 whois2 테스트

```text
python -m unittest tests.test_nplt_whois2 -v
결과: OK
실행: 4 tests
소요: 0.008s
```

기존 모듈 파일은 삭제하지 않았고, 기존 테스트 영향도 없음이 확인되었다.

## 4. 실제 도메인 조회 테스트

테스트 대상:

```text
http://deokyanggas.com/
```

실행:

```text
python -c "import nplt27; result=nplt27.getdomainInformation('http://deokyanggas.com/'); print(result)"
```

결과 요약:

```text
Domain_Name: DEOKYANGGAS.COM
Lookup_Source: rdap, whois.com
Registrar: Gabia, Inc.
Creation_Date: 2018-01-17T06:16:22Z
Expiration_Date: 2028-07-21T11:59:59Z
Updated_Date: 2025-07-04T06:05:01Z
Name_Server:
  NS.GABIA.CO.KR
  NS.GABIA.NET
  NS1.GABIA.CO.KR
NoDRfexpire: 764
```

## 5. 전체 테스트 참고

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

전체 테스트는 `nplt26`의 오래 걸리는 색상 분석/서브프로세스 테스트 진행 중 180초 제한에 도달하여 중단되었다. 중단 전 실행된 항목들은 통과했으며, 이번 변경 대상인 `nplt27` 및 WHOIS 연동 테스트는 별도로 정상 통과했다.

## 6. 결론

`nplt27.py`의 DNS/Domain 정보 수집 루틴은 새 `nplt_whois.py` 기반으로 변경 완료되었다. 보고서 출력에 필요한 기존 필드명은 어댑터로 유지했으므로, 기존 Domain Information 출력과 DB 저장 흐름의 호환성도 유지된다.
