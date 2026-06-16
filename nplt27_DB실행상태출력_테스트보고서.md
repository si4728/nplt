# nplt27 DB 실행 상태 출력 개선 테스트 보고서

## 1. 개선 배경

사용자가 다음 명령을 실행했을 때 초반 출력에서 DB 사용 여부가 보이지 않았다.

```powershell
python nplt27.py -url http://deokyanggas.com/ -db yes
```

DB 저장은 크롤링과 보고서 생성이 끝난 뒤 마지막 단계에서 수행되므로, 초반 출력만 보면 `-db yes`가 적용되었는지 확인하기 어렵다.

## 2. 적용 내용

- `-db yes`가 활성화되면 실행 초기에 다음 정보를 출력하도록 변경하였다.
  - `Database update: enabled`
  - company id
  - DB 연결 확인 결과
  - next id
- `-db no` 또는 미사용 시 `Database update: disabled`를 출력하도록 변경하였다.
- DB 저장 단계 진입 시 다음 정보를 출력하도록 변경하였다.
  - `Database update: writing report data...`
  - `Database update: completed`
  - `Database update: failed`

## 3. 테스트 결과

### 3.1 nplt27 단위 테스트

```powershell
python -m unittest tests.test_nplt27 -v
```

결과:

- 총 14개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 24.361초

### 3.2 전체 단위 테스트

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

결과:

- 총 65개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 48.994초

### 3.3 로컬 DB 확인

```powershell
python -c "import nplt27; print(nplt27.is_yes_option('yes')); print('next_id=', nplt27.get_lastnumber())"
```

결과:

- `yes` 옵션 인식: `True`
- DB 읽기 연결 성공
- `next_id=42320`

### 3.4 로컬 파일 반영 확인

- `C:\Users\user\Desktop\python\nplt-upload\nplt27.py`
- `C:\Users\user\Desktop\python\nplt27.py`

두 파일의 SHA256 해시가 동일함을 확인하였다.

## 4. 판정

- `-db yes` 옵션은 정상 인식된다.
- 실행 초기에 DB 사용 여부와 연결 확인 결과가 표시되도록 개선되었다.
- 실제 DB 쓰기는 크롤링/보고서 생성 완료 후 마지막 단계에서 실행된다.
