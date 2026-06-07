# nplt26 Phase A 테스트 보고서: Favicon 보고서 오류

> 테스트일: 2026-06-07  
> 변경 대상: `nplt26.py`, `tests/test_nplt26.py`  
> 실사이트: `http://www.onbranding.co.kr`

## 1. 원인

- favicon URL과 로컬 파일 경로를 `"URL,경로"` 문자열 하나로 저장했다.
- 보고서 작성 시 문자열을 다시 분리하므로 경로 누락·절단에 취약했다.
- PNG 파일도 무조건 다시 PNG로 저장해 `favicon-16x16.png.png`가 생성됐다.
- 로컬 경로가 유효하지 않으면 `run.add_picture()`에서 보고서 오류가 발생했다.

## 2. 변경 내용

- favicon 보고서 항목을 URL, 경로, 라벨이 분리된 dict로 저장
- PNG 입력은 재변환하지 않고 원래 `.png` 파일 사용
- ICO 등 다른 형식만 `.png`로 변환
- URL query를 제외한 안전한 파일명 사용
- 이미지 삽입 실패 시 URL 텍스트는 유지하고 실패 사유를 보고서에 표시
- 기존 문자열 형식도 읽을 수 있도록 호환 유지

## 3. 자동 테스트

실행:

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
```

결과:

- 전체 32개 통과
- 실패 0개
- 오류 0개
- Python 컴파일 성공

추가 테스트:

- PNG favicon이 `.png.png`로 저장되지 않는지 검증
- 구조화된 favicon 데이터가 DOCX에 텍스트와 이미지로 삽입되는지 검증

## 4. 실사이트 회귀 테스트

대상:

```text
http://www.onbranding.co.kr/assets/img/icon/favi/favicon-16x16.png
```

결과:

| 항목 | 결과 |
|---|---|
| 프로세스 종료 코드 | 0 |
| favicon 다운로드 | 성공 |
| 저장 파일 | `temp/favicon_image/favicon-16x16.png` |
| `.png.png` 생성 | 없음 |
| DOCX 생성 | 성공 |
| favicon 텍스트 | 정상 |
| DOCX 삽입 이미지 | 1개 |
| `report write error` | 없음 |
| Traceback | 없음 |

생성 보고서:

`temp/favicon_report/favicon_regression.docx`

## 5. 판정

**통과**

사용자가 제시한 Favicon information 보고서 오류의 원인이 제거됐으며,
실제 onbranding favicon이 단일 PNG 파일과 DOCX 이미지로 정상 처리된다.

## 6. Legacy 경로 추가 보완

사용 환경에서 다음 이전 형식의 항목이 다시 확인됐다.

```text
Favicon information: http://www.onbranding.co.kr/assets/img/icon/favi/favicon-16x16.png,c:\temp\image\favicon-16x16.png.png
```

추가 조치:

- 기존 문자열 report 항목을 계속 지원
- `.png.png` 경로가 들어오면 단일 `.png` 원본을 우선 탐색
- 전달 경로가 없으면 현재 `IMAGE_DIR`에서도 같은 파일명을 탐색
- 복구된 실제 경로만 DOCX 이미지 삽입에 사용

추가 검증:

| 항목 | 결과 |
|---|---|
| `c:\temp\image\favicon-16x16.png.png` 입력 | 정상 인식 |
| 선택된 파일 | `c:\temp\image\favicon-16x16.png` |
| 파일 존재 | 확인 |
| legacy DOCX 이미지 삽입 | 성공 |
| 전체 자동 테스트 | 33개 통과 |
| Python 컴파일 | 성공 |

## 7. 반복 오류 진단

반복 제시된 출력:

```text
report write error.... Favicon information: http://www.onbranding.co.kr/assets/img/icon/favi/favicon-16x16.png,c:\temp\image\favicon-16x16.png.png 7
```

이 출력 형식은 `nplt25.py`의 다음 코드와 일치한다.

```python
print("report write error....", sline, xstyle)
```

현재 `nplt26.py`는 오류 객체까지 출력하므로 형식이 다르다.

```python
print("report write error....", sline, xstyle, error)
```

확인 결과:

- 작업 폴더의 `nplt26.py`는 한 개만 존재
- `nplt26.exe` 또는 `nplt.exe`는 발견되지 않음
- 정확한 legacy 문자열과 `c:\temp\image\favicon-16x16.png.png`로
  현재 `nplt26.py`의 `report_write()` 직접 실행 성공
- 실제 선택 경로: `c:\temp\image\favicon-16x16.png`
- 생성 DOCX inline image: 1개
- `report write error` 재현되지 않음

따라서 반복 오류는 `nplt25.py` 또는 수정 전 코드가 실행된 결과다.
개선본 실행 대상은 `C:\Users\user\Desktop\python\nplt26.py`여야 한다.
