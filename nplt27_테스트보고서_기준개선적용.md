# nplt27 기준 개선 적용 테스트 보고서

## 1. 적용 범위

- `nplt26.py`를 기준으로 `nplt27.py`를 신규 생성하였다.
- 기존 중복 기능 점검 결과 중 위험도가 낮은 항목을 `nplt27.py`에 우선 적용하였다.
- 실행 기준 문서를 `README.md`에서 `nplt27.py` 기준으로 갱신하였다.

## 2. 적용한 개선 사항

### 2.1 확장자 제외 목록 중복 제거

- `skip_ext_list`에 중복으로 들어 있던 확장자를 제거하였다.
- 리스트 순서를 유지하기 위해 `list(dict.fromkeys(...))` 방식으로 정리하였다.
- 적용 목적: 중복 데이터 정리 및 테스트 가능한 기준 확보.

### 2.2 문자열 포함 검사 함수 중복 정리

- `check_string2()`가 별도 반복 로직을 갖지 않고 `check_string()`을 호출하도록 변경하였다.
- 적용 목적: 동일 기능 함수의 동작 차이 발생 가능성 제거.

### 2.3 도메인/호스트 정규화 공통 함수 추가

- `normalize_domain_host()`를 추가하였다.
- `normalize_sns_host()`와 `normalize_host()`가 공통 정규화 함수를 사용하도록 변경하였다.
- 적용 목적: SNS 링크 판별, Tree Map, 도메인 비교 로직의 기준 통일.

## 3. 테스트 결과

### 3.1 단위 테스트

실행 명령:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

결과:

- 총 56개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 30.472초

### 3.2 실제 URL 실행 테스트

최종 확인 시각: 2026-06-08 20:55:36 KST

실행 명령:

```powershell
python nplt27.py -url http://www.onbranding.co.kr -cost Yes -ca No -db No -robots No -wl 10
```

결과:

- 프로그램 종료 코드: 0
- 대상 사이트 HTTP 응답: 200
- 분석 페이지 수: 17
- 총 스캔 시간: 7.132163초
- `robots.txt`: 존재 확인됨
- `sitemap.xml`: 존재 확인됨
- Domain Information: DNS fallback 경로로 출력됨
- SNS Link Information: 대상 사이트에서 SNS 링크가 발견되지 않음
- Word 보고서 생성: `report\www.onbranding.co.kr.docx`

## 4. 판정

- `nplt27.py`는 현재 GitHub 실행 기준 파일로 사용할 수 있다.
- 이번 단계는 안전한 중복 제거와 기준 파일 분리를 우선 적용한 것이다.
- JS URL 추출 통합, 보고서 출력 API 통합 같은 구조 변경은 영향 범위가 크므로 다음 단계에서 별도 테스트 단위로 진행하는 것이 적합하다.
