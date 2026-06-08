# nplt27 Header Security 개선 테스트 보고서

## 1. 개선 배경

`deokyanggas.com` 헤더 분석 결과 다음 보안 헤더가 누락되어 있었다.

- `X-XSS-Protection`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Content-Security-Policy`
- `Strict-Transport-Security`
- `Referrer-Policy`
- `Permissions-Policy`

또한 `Cache-Control: pre-check=0, post-check=0, max-age=0` 및 `Expires: 0`은 캐시 만료를 지시하지만 저장 방지까지 보장하지 않아 민감 페이지에는 명확한 `no-store` 권고가 필요하다.

## 2. 적용 내용

- `collect_security_header_recommendations()` 함수 추가
- `get_header_value()` 함수 추가
- Header Information 출력 뒤에 `Security Header Recommendations` 섹션 추가
- 누락 또는 약한 보안 헤더에 대해 구체적인 개선 권고 출력

## 3. 추가 권고 항목

- `X-XSS-Protection`: CSP 중심 적용 및 legacy 정책 검토
- `X-Content-Type-Options`: `nosniff` 권장
- `X-Frame-Options`: `DENY` 또는 `SAMEORIGIN` 권장
- `Content-Security-Policy`: `default-src`, `frame-ancestors` 권장
- `Strict-Transport-Security`: HTTPS 안정화 후 HSTS 권장
- `Referrer-Policy`: `strict-origin-when-cross-origin` 이상 권장
- `Permissions-Policy`: camera, microphone, geolocation 등 미사용 기능 제한 권장
- `Cache-Control`: 민감 페이지는 `no-store, no-cache, must-revalidate` 권장
- `Expires: 0`: 명시적 Cache-Control 사용 권장

## 4. 테스트 결과

### 4.1 nplt27 단위 테스트

```powershell
python -m unittest tests.test_nplt27 -v
```

결과:

- 총 10개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 20.741초

### 4.2 전체 단위 테스트

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

결과:

- 총 61개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 32.042초

### 4.3 실제 URL 테스트

```powershell
python nplt27.py -url http://deokyanggas.com -cost Yes -ca No -db No -robots No -wl 10
```

결과:

- 종료 코드: 0
- 분석 페이지 수: 213
- Website builder tool: `Gnuboard`
- `Security Header Recommendations` 섹션 생성 확인
- Word 보고서에 `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy` 권고 문구 포함 확인
- Word 보고서 생성: `C:\Users\user\Desktop\python\nplt-upload\report\deokyanggas.com.docx`

### 4.4 로컬 파일 반영 확인

- `C:\Users\user\Desktop\python\nplt-upload\nplt27.py`
- `C:\Users\user\Desktop\python\nplt27.py`

두 파일의 SHA256 해시가 동일함을 확인하였다.

로컬 직접 확인:

- 누락/약한 헤더 샘플 입력 시 권고 9개 생성
- `X-XSS-Protection`, `X-Content-Type-Options`, `X-Frame-Options` 권고 정상 생성

## 5. 판정

- Header Information 보안 헤더 점검 결과가 단순 누락 표시에서 구체적 개선 권고까지 확장되었다.
- DB 저장 필드는 기존 호환성을 유지했고, 보고서 출력만 강화하였다.
- 로컬 실행 파일과 GitHub 작업 폴더 파일 모두 동일하게 적용되었다.
