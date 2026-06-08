# nplt27 Website Tool 추가 패턴 테스트 보고서

## 1. 추가 필요성

기존 개선 후에도 국내 사이트와 글로벌 CMS/프론트엔드 도구에서 자주 발견되는 일부 패턴이 빠져 있었다.
특히 블로그형 서비스, CMS, 쇼핑몰 솔루션, 프론트엔드 프레임워크는 리포트에서 사이트 제작 환경을 설명할 때 유용하다.

## 2. 추가한 Website Tool 패턴

- Joomla
- Drupal
- Magento
- OpenCart
- Tistory
- Naver Modoo
- Bootstrap
- React
- Vue
- Angular
- Svelte
- Gatsby
- Docusaurus
- Hugo
- Jekyll

## 3. 테스트 결과

### 3.1 nplt27 단위 테스트

```powershell
python -m unittest tests.test_nplt27 -v
```

결과:

- 총 8개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 18.920초

### 3.2 전체 단위 테스트

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

결과:

- 총 59개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 37.960초

### 3.3 실제 URL 테스트

```powershell
python nplt27.py -url http://www.onbranding.co.kr -cost Yes -ca No -db No -robots No -wl 10
```

결과:

- 종료 코드: 0
- 분석 페이지 수: 17
- Website builder tool: `Custom/Static Site`
- 기존 출력 결과 유지 확인

### 3.4 로컬 파일 반영 확인

- `C:\Users\user\Desktop\python\nplt-upload\nplt27.py`
- `C:\Users\user\Desktop\python\nplt27.py`

두 파일의 SHA256 해시가 동일함을 확인하였다.

추가 패턴 직접 확인:

- Tistory 판별: 정상
- Joomla 판별: 정상

## 4. 판정

- Website Tool 판별 범위가 국내/글로벌 CMS, 쇼핑몰, 프론트엔드 도구까지 확장되었다.
- 실제 대상 사이트 `onbranding.co.kr`에서는 추가 패턴에 의한 오탐 없이 `Custom/Static Site`로 유지된다.
