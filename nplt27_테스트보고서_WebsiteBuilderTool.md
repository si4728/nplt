# nplt27 Website Builder Tool 개선 테스트 보고서

## 1. 개선 목적

- 기존 `identify_website_builder()` 루틴은 일부 빌더만 단순 문자열로 확인하였다.
- `googletagmanager.com` preconnect 링크를 Hostinger로 오판할 수 있는 조건이 있었다.
- 알려진 빌더 신호가 없을 때 `Unknown Builder`만 출력되어, 커스텀/정적 사이트인지 구분하기 어려웠다.

## 2. 적용 내용

- `meta generator`, script `src`, link `href`, inline script, 전체 HTML 문자열을 함께 검사하도록 개선하였다.
- 다음 계열의 판별 패턴을 확장하였다.
  - WordPress
  - Wix
  - Shopify
  - Webflow
  - Squarespace
  - Cafe24
  - Gnuboard
  - Rhymix
  - XpressEngine
  - Imweb
  - Sixshop
  - Makeshop
  - Godo Mall
  - Next.js / Nuxt / Vite / Webpack
- `googletagmanager.com` preconnect만으로 Hostinger라고 판정하던 오탐 조건을 제거하였다.
- 빌더/CMS 신호가 없으면 `Custom/Static Site`로 출력하도록 변경하였다.

## 3. 테스트 결과

### 3.1 nplt27 단위 테스트

```powershell
python -m unittest tests.test_nplt27 -v
```

결과:

- 총 8개 테스트 통과
- 실패: 0
- 오류: 0

### 3.2 전체 단위 테스트

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

결과:

- 총 59개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 34.463초

### 3.3 실제 URL 테스트

GitHub 작업 폴더 기준:

```powershell
python nplt27.py -url http://www.onbranding.co.kr -cost Yes -ca No -db No -robots No -wl 10
```

결과:

- 종료 코드: 0
- 분석 페이지 수: 17
- Website builder tool: `Custom/Static Site`
- Word 보고서 생성: `C:\Users\user\Desktop\python\nplt-upload\report\www.onbranding.co.kr.docx`

로컬 실행 파일 기준:

```powershell
python C:\Users\user\Desktop\python\nplt27.py -url http://www.onbranding.co.kr -cost Yes -ca No -db No -robots No -wl 10
```

결과:

- 종료 코드: 0
- 분석 페이지 수: 17
- Website builder tool: `Custom/Static Site`
- Word 보고서 생성: `C:\Users\user\Desktop\python\report\www.onbranding.co.kr.docx`

## 4. 판정

- Website builder tool 루틴 개선이 정상 적용되었다.
- `onbranding.co.kr`은 현재 HTML 기준으로 특정 빌더/CMS 신호가 없어 `Custom/Static Site`로 판정된다.
- 로컬 파일 `C:\Users\user\Desktop\python\nplt27.py`와 GitHub 작업 폴더 파일은 동일 해시로 확인되었다.
