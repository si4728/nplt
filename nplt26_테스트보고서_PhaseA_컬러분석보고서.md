# nplt26 Phase A 테스트 보고서: 컬러 분석 DOCX 포함

> 테스트일: 2026-06-07  
> 변경 대상: `nplt26.py`, `tests/test_nplt26.py`  
> 기준 사이트: `http://www.onbranding.co.kr`

## 1. 변경 내용

- KMeans 대표 색상 생성을 `make_dominant_color_chart()`로 분리
- 대표 색상을 사용 비율 순으로 정렬
- 차트에 HEX 색상과 픽셀 비율 표시
- RGB 분포 차트와 대표 색상 차트를 `report_write()` 전에 생성
- DOCX에 `Website Color Analysis` 섹션 추가
- 분석 이미지 개수, 대표 색상 차트, RGB/neutral 차트를 보고서에 등록
- 보고서 작성 후 실행되던 중복 KMeans 경로 비활성화

## 2. 자동 테스트

실행:

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
```

결과:

- 전체 34개 통과
- 실패 0개
- 오류 0개
- Python 컴파일 성공

추가 테스트:

- 테스트 이미지에서 RGB 분포 차트 생성
- 테스트 이미지에서 KMeans 대표 색상 차트 생성
- DOCX의 `Website Color Analysis` 텍스트 확인
- DOCX inline image 2개 확인

## 3. onbranding 저장 이미지 회귀 테스트

사용 결과:

```text
C:\Users\user\AppData\Local\Temp\nplt_image\www_onbranding_co_kr_CCAI.jpg
C:\Users\user\AppData\Local\Temp\nplt_image\_barwww_onbranding_co_kr.png
```

검증 결과:

| 항목 | 결과 |
|---|---|
| `Website Color Analysis` | 정상 출력 |
| 분석 이미지 개수 | 48 |
| 대표 색상 차트 | 정상 삽입 |
| RGB/neutral 차트 | 정상 삽입 |
| DOCX inline image | 2개 |
| `report write error` | 없음 |
| Traceback | 없음 |

생성 보고서:

`temp/color_report/onbranding_color_analysis.docx`

## 4. 판정

**통과**

홈페이지 이미지 저장 결과를 이용한 두 컬러 분석 차트가 최종 DOCX 보고서
생성 흐름에 포함된다.

## 5. 잔여 과제

- 전체 픽셀 KMeans의 실행 시간 개선
- 이미지별 균등 샘플링
- query URL, WEBP, AVIF, `srcset` 지원
- favicon/로고 색상과 본문 이미지 색상의 분리 표시
