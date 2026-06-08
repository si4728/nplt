# nplt27 실행 안내

## 설치

```powershell
python -m pip install -r requirements.txt
python setup_nltk.py
```

## 실행 예시

```powershell
python nplt27.py -url http://www.onbranding.co.kr -cost Yes -ca No -db No
```

보고서는 `report` 폴더에 생성되고, 임시 파일은 `temp` 폴더에 생성됩니다.

## 테스트

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## 기준 파일

- `nplt27.py`: 현재 개선 적용 기준 실행 파일
- `nplt26.py`: 이전 기준 파일
