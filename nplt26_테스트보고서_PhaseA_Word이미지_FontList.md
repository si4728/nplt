# nplt26 Phase A 테스트 보고서: Word 이미지 크기와 Font List

> 테스트일: 2026-06-07  
> 변경 대상: `nplt26.py`, `tests/test_nplt26.py`  
> 기준 사이트: `http://www.onbranding.co.kr`

## 1. Word 이미지 크기 개선

- Word 페이지의 실제 본문 폭을 계산
- 일반 보고서 이미지는 본문 폭과 본문 높이 72% 이내로 축소
- 원본 종횡비 유지
- 작은 이미지는 불필요하게 확대하지 않음
- favicon은 최대 0.25 × 0.25인치로 제한

onbranding 최종 DOCX:

| 항목 | 결과 |
|---|---:|
| 페이지 본문 폭 | 6.0인치 |
| 삽입 이미지 | 8개 |
| 최대 이미지 폭 | 6.0인치 |
| 본문 폭 초과 이미지 | 0개 |

## 2. Font List 재점검

기존 문제:

- 문자열 위치 탐색 방식으로 일부 선언 누락 가능
- `font` shorthand에서 크기·스타일이 폰트명으로 섞일 수 있음
- 외부 stylesheet의 font-family를 Font List에 반영하지 않음
- `!important`가 폰트명에 남음

개선:

- CSS `font-family` 선언 파싱
- CSS `font` shorthand에서 font-size 이후 family 부분 추출
- HTML `<font face="">` 지원
- 인용부호와 쉼표 기반 family 분리
- 첫 페이지 외부 stylesheet 최대 10개 반영
- `inherit`, `initial`, `unset`, `revert` 제외
- `!important` 제거
- 알파벳 순 정렬

onbranding에서 확인된 Font List:

```text
-apple-system
Apple Color Emoji
Apple SD Gothic Neo
BlinkMacSystemFont
Helvetica Neue
Malgun Gothic
Noto Sans KR
Poppins
Pretendard
Pretendard Variable
proxima-nova
proxima-nova-condensed
proxima-nova-extra-condensed
proxima-nova-extra-wide
proxima-nova-wide
Roboto
sans-serif
Segoe UI
Segoe UI Emoji
Segoe UI Symbol
swiper-icons
system-ui
```

## 3. 테스트 결과

- 자동 테스트 39개 전체 통과
- Python 컴파일 성공
- 실사이트 17페이지 분석 성공
- DOCX 생성 성공
- `report write error` 없음
- Traceback 없음
- `sans-serif !important` 제거 확인

추가 테스트:

- 넓은 이미지가 Word 본문 폭 이하로 축소되는지 검증
- `font-family`, `font` shorthand, `<font face>` 복합 파싱
- `!important` 정규화

## 4. 생성 보고서

`temp/wordfit_final_report/www.onbranding.co.kr.docx`

## 5. 판정

**통과**

보고서 이미지가 Word 페이지 안에 종횡비를 유지하며 배치되고, Font List가
HTML과 첫 페이지 외부 CSS를 포함해 정규화된 폰트명으로 출력된다.
