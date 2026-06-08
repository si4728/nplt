# nplt26 GitHub 실행 파일 재점검 테스트 보고서

## 점검 일시

- 2026-06-08

## 점검 목적

GitHub 저장소 `si4728/nplt`에 업로드된 파일만 기준으로 `nplt26.py` 실행에 필요한 파일이 충분한지 재확인했다.

## 확인 결과

초기 확인 결과, 코드와 테스트는 업로드되어 있었지만 새 환경 실행을 위해 다음 항목이 부족했다.

- `fonts/NanumGothic.ttf`: WordCloud 생성 시 필요한 한글 폰트
- `requirements.txt`: Python 패키지 설치 목록
- `setup_nltk.py`: NLTK 토크나이저와 품사 태거 데이터 설치 안내
- `README.md`: 설치 및 실행 절차

## 적용 사항

1. `fonts/NanumGothic.ttf`를 저장소에 추가했다.
2. `requirements.txt`를 추가했다.
3. `setup_nltk.py`를 추가했다.
4. `README.md`에 설치, 실행, 테스트 명령을 추가했다.
5. `make_word_cloud()`의 폰트 경로를 현재 실행 디렉터리가 아니라 `nplt26.py` 파일 위치 기준으로 변경했다.

## 검증 명령

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python nplt26.py -h
```

## 테스트 결과

- 단위 테스트: 42개 통과
- CLI 도움말 실행: 정상
- 필수 Python 모듈 import: 현재 검증 환경에서 정상
- NLTK 데이터: 현재 검증 환경에서 `punkt`, `punkt_tab`, `averaged_perceptron_tagger`, `averaged_perceptron_tagger_eng` 확인

## 남은 전제 조건

GitHub 파일만 받은 새 PC에서는 다음 설치 명령을 먼저 실행해야 한다.

```powershell
python -m pip install -r requirements.txt
python setup_nltk.py
```

네트워크 스캔 기능은 대상 사이트 접속 가능 여부, 방화벽, robots.txt 설정, TLS 설정에 영향을 받는다.

## 결론

보완 후 저장소 파일 구성은 `nplt26.py` 실행에 필요한 로컬 파일 기준을 충족한다. 단, Python 패키지와 NLTK 데이터는 저장소 파일이 아니라 설치 절차를 통해 준비해야 한다.
