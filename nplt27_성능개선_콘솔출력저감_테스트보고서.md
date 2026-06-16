# nplt27 성능 개선 및 테스트 보고서

## 1. 점검 목적

`nplt27.py` 실행 시 속도가 빠르지 않게 느껴지는 원인을 점검하고, 안전하게 적용 가능한 1차 개선을 반영했다.

## 2. 확인된 주요 병목

- 크롤링 루프가 URL을 1개씩 순차 처리한다.
- 일부 페이지에서 `HEAD` 요청 후 다시 `GET` 요청을 수행하여 네트워크 요청 수가 증가한다.
- HTML 파싱 과정에서 `find_all()` 계열 탐색이 여러 번 반복된다.
- 색상 분석, 워드클라우드, 그래프, Word 보고서 생성은 후처리 시간이 크다.
- 디버그성 `print()` 출력이 많아 터미널 출력량이 증가하고, 실제 처리 속도보다 더 느리게 체감된다.

## 3. 1차 적용 내용

실행 결과에 꼭 필요한 보고서/상태 출력은 유지하고, 반복 크롤링 중 발생하는 디버그성 출력 일부를 `Debug_w()`로 전환했다.

- URL 수집 디버그 출력 축소
- iframe/frame 검사 디버그 출력 축소
- script redirect 검사 출력 축소
- 외부 도메인 skip 출력 축소
- `index` URL 검사 출력 축소
- `npltIndex` 초기값 반복 출력 축소

`Debug_w()`는 `-dm Yes` 옵션으로 디버그 모드가 켜진 경우에만 출력된다.

## 4. 테스트 결과

### 단위 테스트

```text
python -m unittest tests.test_nplt27 -v
결과: OK
실행: 14 tests
소요: 24.618s
```

### 전체 테스트

```text
python -m unittest discover -s tests -p "test_*.py" -v
결과: OK
실행: 65 tests
소요: 45.288s
```

### DB 읽기 확인

```text
python -c "import nplt27; print(nplt27.is_yes_option('yes')); print('next_id=', nplt27.get_lastnumber())"
결과:
True
next_id=42321
```

DB 쓰기 테스트는 실제 운영 DB 데이터 변경 가능성이 있어 수행하지 않았다.

## 5. 추가 개선 권장 사항

다음 항목을 단계적으로 적용하면 실제 실행 시간을 더 크게 줄일 수 있다.

1. `HEAD` + `GET` 중복 요청 제거 또는 조건부 수행
2. 크롤링 URL 동시 처리 적용
   - 권장: worker 3~5개 수준의 제한된 병렬 처리
   - 요청 실패/timeout/robots 정책과 함께 제어 필요
3. URL 정규화 및 중복 제거 강화
   - trailing slash, query, fragment, http/https 변형 정리
4. 색상 분석 범위 축소
   - 첫 페이지 이미지 및 CSS/font color 중심
   - 이미지 다운로드 수 제한
5. 그래프/워드클라우드/색상 분석 옵션화
   - 빠른 점검 모드와 전체 보고서 모드 분리
6. HTML 파싱 결과 캐시
   - 같은 페이지에서 반복 `find_all()` 호출 감소
7. 무거운 라이브러리 lazy import
   - `matplotlib`, `cv2`, `sklearn`, `wordcloud`, `docx`, `mysql` 등은 필요한 기능 실행 시점에 import
   - `-h` 또는 간단 실행의 시작 시간이 짧아질 수 있음

## 6. 결론

이번 변경은 결과 형식을 크게 바꾸지 않는 저위험 성능 개선이다. 실제 전체 수행 시간을 크게 줄이려면 네트워크 요청 구조와 후처리 모듈을 분리하는 2차 개선이 필요하다.
