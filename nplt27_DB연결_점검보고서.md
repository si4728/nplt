# nplt27 DB 연결 점검 및 개선 보고서

## 1. 점검 대상

- 파일: `nplt27.py`
- 점검 범위:
  - DB 설정
  - DB 옵션 파싱
  - DB cursor/transaction 처리
  - report DB 저장 흐름

## 2. 발견한 문제점

### 2.1 로컬 파일의 `DB_CONFIG` 중복 정의

로컬 `C:\Users\user\Desktop\python\nplt27.py`에는 `DB_CONFIG`가 두 번 정의되어 있었다.

- 첫 번째: 환경변수 기반 설정
- 두 번째: 하드코딩 설정

결과적으로 `NPLT_DB_HOST`, `NPLT_DB_USER`, `NPLT_DB_PASSWORD` 같은 환경변수 설정이 무시될 수 있었다.

### 2.2 `-db Yes` 옵션 파싱 오류

기존 코드:

```python
if args.db.upper() in ["Yes", "Y", "1"]:
```

`args.db.upper()`는 `"YES"`를 반환하지만 비교 목록에는 `"Yes"`가 들어 있어 `-db Yes`가 DB 연결을 켜지 못하는 문제가 있었다.

### 2.3 트랜잭션 rollback 범위 부족

`get_db_cursor()`는 `mysql.connector.Error`만 rollback 처리했다.
DB cursor 블록 내부에서 일반 예외가 발생하면 rollback이 명확히 수행되지 않을 수 있었다.

### 2.4 DB id 할당 실패 후 insert 진행 가능성

`get_lastnumber()`가 실패해 `0`을 반환하는 경우에도 `_report_to_db()`가 계속 insert를 진행할 수 있는 구조였다.
이 경우 `id=0` 또는 잘못된 데이터 저장 가능성이 있었다.

## 3. 적용한 개선

- `DB_CONFIG`를 환경변수 기반 단일 설정으로 정리
- 기존 로컬 기본 비밀번호 동작을 보존하기 위해 `NPLT_DB_PASSWORD` 미설정 시 기본값은 기존과 동일하게 유지
- `is_yes_option()` 추가
- `-db Yes`, `-db YES`, `-db yes`, `-db Y`, `-db 1`, `-db true` 모두 DB 사용으로 인식
- `get_db_cursor()`가 일반 예외에서도 rollback 후 close 수행
- `_report_to_db()`에서 next id 할당 실패 시 insert 중단

## 4. 테스트 결과

### 4.1 nplt27 단위 테스트

```powershell
python -m unittest tests.test_nplt27 -v
```

결과:

- 총 13개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 24.308초

### 4.2 전체 단위 테스트

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

결과:

- 총 64개 테스트 통과
- 실패: 0
- 오류: 0
- 실행 시간: 44.492초

### 4.3 로컬 DB 읽기 연결 테스트

```powershell
python -c "import nplt27; print('next_id=', nplt27.get_lastnumber())"
```

결과:

- DB 접속 성공
- `basic` 테이블 조회 성공
- 반환값: `next_id=42319`

### 4.4 로컬 파일 반영 확인

- `C:\Users\user\Desktop\python\nplt-upload\nplt27.py`
- `C:\Users\user\Desktop\python\nplt27.py`

두 파일의 SHA256 해시가 동일함을 확인하였다.

## 5. 주의 사항

- 실제 `-db Yes` 전체 실행은 DB에 `basic`, `head`, `domain`, `word`, `esg`, `sns`, `js_css` 등 데이터를 insert하므로 이번 테스트에서는 수행하지 않았다.
- 실제 저장 테스트가 필요하면 별도 테스트 DB 또는 백업 후 실행하는 것이 안전하다.
- 현재 id 생성은 `SELECT MAX(id) + 1` 방식이므로 동시 실행 시 id 충돌 가능성이 있다. 장기적으로는 DB의 `AUTO_INCREMENT` 또는 별도 sequence/lock 방식으로 바꾸는 것이 좋다.

## 6. 판정

- DB 연결 설정, 옵션 파싱, transaction rollback, id 실패 방어가 개선되었다.
- 로컬 DB 읽기 연결은 정상이다.
- 실제 쓰기 테스트는 데이터 오염 방지를 위해 생략했다.
