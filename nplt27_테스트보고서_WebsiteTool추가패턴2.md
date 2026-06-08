# nplt27 Website Tool 추가 패턴 2차 테스트 보고서

## 1. 추가 적용 내용

Website Tool 판별 범위를 CMS, 랜딩페이지 빌더, 블로그형 도구, 국내 쇼핑몰 솔루션 중심으로 추가 확장하였다.

추가 패턴:

- Elementor
- Ghost
- HubSpot CMS
- Blogger
- Framer
- Tilda
- Carrd
- Readymag
- Notion/Super
- Typedream
- Unbounce
- Instapage
- Landingi
- Shopby
- Gabia Firstmall
- WISA

## 2. 오탐 개선

- 기존 `"/shop"` 패턴은 너무 넓어 Shopby/WISA 같은 다른 쇼핑몰 도구를 Cafe24로 오판할 수 있어 제거하였다.
- Elementor는 WordPress 내부 플러그인이므로 `wp-content`보다 먼저 판별되도록 우선순위를 조정하였다.

## 3. 테스트 결과

### 3.1 nplt27 단위 테스트

```powershell
python -m unittest tests.test_nplt27 -v
```

결과:

- 총 8개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 24.366초

### 3.2 전체 단위 테스트

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

결과:

- 총 59개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 60.005초

### 3.3 실제 URL 테스트

```powershell
python nplt27.py -url http://www.onbranding.co.kr -cost Yes -ca No -db No -robots No -wl 10
```

결과:

- 종료 코드: 0
- 분석 페이지 수: 17
- Website builder tool: `Custom/Static Site`
- 추가 패턴 적용 후에도 대상 사이트 오탐 없음

### 3.4 로컬 파일 반영 확인

- `C:\Users\user\Desktop\python\nplt-upload\nplt27.py`
- `C:\Users\user\Desktop\python\nplt27.py`

두 파일의 SHA256 해시가 동일함을 확인하였다.

로컬 직접 판별:

- HubSpot CMS: 정상
- Framer: 정상
- Shopby: 정상
- Elementor: 정상

## 4. 판정

- Website Tool 판별 범위가 추가 확장되었다.
- 넓은 `"/shop"` 패턴 제거로 쇼핑몰 도구 오탐 가능성을 낮췄다.
- 로컬 실행 파일과 GitHub 작업 폴더 파일 모두 동일하게 적용되었다.
