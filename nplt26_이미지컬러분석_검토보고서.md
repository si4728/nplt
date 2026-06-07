# nplt26 이미지 저장 및 홈페이지 컬러 분석 검토 보고서

> 검토일: 2026-06-07  
> 대상: `nplt26.py`  
> 기준 사이트: `http://www.onbranding.co.kr`

## 1. 결론

이미지를 저장하는 목적은 코드에 **부분적으로 반영되어 있다**.

현재 코드는 홈페이지에서 발견한 일부 JPG/PNG 이미지를 로컬에 저장한 뒤:

1. RGB 우세 픽셀 비율 계산
2. KMeans 기반 대표 색상 5개 추출

을 수행한다.

2026-06-07 후속 변경으로 RGB 분포 차트와 KMeans 대표 색상 차트가
`Website Color Analysis` 섹션으로 DOCX에 포함된다. favicon은 컬러 분석
입력이 아닌 보고서 표시용으로 유지된다.

## 2. 현재 처리 흐름

```text
HTML <img> 탐색
  ↓
첫 3개 크롤링 페이지에서 JPG/PNG URL 수집
  ↓
list_img_analysis에 URL 저장
  ↓
image_copy()
  ↓
save_url2image()로 IMAGE_DIR에 파일 저장
  ↓
저장된 로컬 파일 경로로 list_img_analysis 교체
  ├─ make_image_analysis_bar()
  │    └─ R/G/B/기타 우세 픽셀 비율 이미지 생성
  └─ 실행 종료부 KMeans
       └─ 대표 색상 5개 차트 생성
```

실제 저장 파일 예:

```text
www_onbranding_co_kr_main_2.jpg
www_onbranding_co_kr_ONB-B3642_.png
www_onbranding_co_kr_inquiry_bg.jpg
```

## 3. 정상 반영된 내용

### 3.1 이미지 URL 수집

`scanWeb()`은 `<img>` 태그의 `src`를 확인하고 JPG/PNG인 경우
`list_img_analysis`에 URL을 저장한다.

- 적용 조건: `webPageColorAnalysis == True`
- 수집 범위: `counter < 4`, 즉 최초 3페이지
- 중복 방지: `set` 사용

### 3.2 로컬 이미지 저장

`image_copy()`가 URL 목록을 순회하고 `save_url2image()`가 이미지를
`IMAGE_DIR`에 저장한다.

저장 후 `list_img_analysis`는 URL 집합에서 실제 로컬 파일 경로 집합으로
교체된다. 이후 컬러 분석은 원격 URL이 아니라 저장된 파일을 사용한다.

### 3.3 RGB 비율 분석

`get_rgb_space()`는 저장 이미지의 각 픽셀을 RGB로 변환하고 다음 기준으로
분류한다.

- R 값이 가장 크면 Red
- G 값이 가장 크면 Green
- B 값이 가장 크면 Blue
- 동일하거나 어느 한 채널이 명확히 크지 않으면 Neutral

`make_image_analysis_bar()`는 전체 이미지의 결과를 합산해 다음 파일을 만든다.

```text
_barwww_onbranding_co_kr.png
```

### 3.4 KMeans 대표 색상

실행 종료부는 저장된 모든 이미지 픽셀을 합친 뒤 KMeans를 수행해 최대
5개의 중심 색상을 구하고 다음 파일을 생성한다.

```text
www_onbranding_co_kr_CCAI.jpg
```

### 3.5 실제 파일 확인

onbranding 테스트에서 확인된 결과:

| 항목 | 결과 |
|---|---:|
| 컬러 분석 대상 저장 이미지 | 48개 |
| 저장 이미지 총용량 | 약 5.7MB |
| RGB 비율 차트 | 생성 성공 |
| KMeans 대표 색상 차트 | 생성 성공 |
| RGB 차트 크기 | 500 × 100 |
| KMeans 차트 크기 | 600 × 400 |

## 4. 문제점

### 완료. 컬러 분석 결과 DOCX 포함

RGB 차트와 KMeans 차트를 보고서 작성 전에 생성하고 다음 항목으로 등록했다.

- `Website Color Analysis`
- 분석 이미지 개수
- `Dominant color palette`
- `RGB and neutral distribution`

실제 onbranding 저장 결과로 생성한 DOCX에서 이미지 2개 삽입을 확인했다.

### P1. Favicon은 컬러 분석 대상이 아님

`save_Favicon()`의 반환 파일은 `add_favicon_report()`로 DOCX에 삽입될 뿐,
`list_img_analysis`에는 추가되지 않는다.

favicon은 사이트 브랜드 색상을 대표할 수 있지만 크기가 작고 투명 배경이
많으므로 본문 이미지와 동일한 가중치로 섞는 것도 적절하지 않다.

**권장**

- favicon은 별도 `Brand Icon Colors` 항목으로 분석
- 본문 이미지 대표 색상과 분리해 표시

### 완료. 전체 픽셀 KMeans 성능 개선

모든 이미지의 모든 픽셀을 `reshape(-1, 3)` 후 `np.vstack()`하고 KMeans에
전달한다. 큰 배경 이미지 하나가 수백만 픽셀을 제공해 메모리와 CPU를
과도하게 사용한다.

실제 onbranding 전체 실행은 크롤링 표시 시간 약 3.6초에 비해 전체 실행이
약 563.7초였다. 대부분이 이미지 후처리에 사용된 것으로 판단된다.

적용 내용:

- 첫 페이지 이미지만 분석
- 이미지당 최대 256×256으로 축소
- 이미지당 최대 5,000픽셀
- 전체 최대 100,000픽셀
- RGB 분류 NumPy 벡터화

전체 실행시간은 563.7초에서 26.44초로 단축됐다.

### P1. 이미지 크기에 따라 색상 가중치가 왜곡됨

현재 방식은 이미지 개수가 아니라 픽셀 수로 합산한다. 3MB 배경 이미지 하나가
작은 로고·아이콘 수십 개보다 훨씬 큰 영향력을 가진다.

**권장**

- `pixel_weighted`: 실제 화면 면적 중심
- `image_balanced`: 이미지별 동일 가중치
- `brand_assets`: 로고/favicon 중심

분석 목적에 따라 세 결과를 구분해야 한다.

### P2. query가 포함된 이미지 URL을 전부 제외

`image_copy()`는 URL에 `?`가 있으면 다운로드하지 않는다.

```python
if "?" in x:
    continue
```

CDN 버전 문자열이나 이미지 리사이즈 파라미터가 있는 정상 URL도 누락된다.

**권장**

- query를 제거하지 말고 다운로드에는 유지
- 저장 파일명만 URL path 또는 URL hash로 생성

### P2. 지원 확장자가 JPG/PNG로 제한됨

WEBP, JPEG, SVG, AVIF가 컬러 분석 대상에서 제외된다.

**권장**

- Content-Type 기준으로 JPEG/PNG/WEBP/AVIF 지원
- SVG는 안전 파싱 또는 래스터 변환 후 별도 처리

### P2. `srcset` 처리가 불완전함

`src`가 없을 때 `srcset` 전체 문자열을 하나의 URL처럼 처리한다.
`image-480.jpg 480w, image-960.jpg 960w` 형식에서 실제 URL을 선택하지 못한다.

**권장**

- `srcset` 파서로 후보를 분리
- 중간 크기 또는 최대 1개 후보만 선택

### P2. 저장 파일명 충돌 가능성

현재 파일명은 도메인과 URL 마지막 경로만 조합한다. 서로 다른 경로에서
같은 파일명을 사용하면 덮어쓸 수 있다.

**권장**

- 정규화 URL의 SHA-256 앞 12자를 파일명에 포함
- MIME 타입으로 확장자 결정

### P2. 투명 픽셀과 배경색 처리 없음

PNG의 alpha 채널을 고려하지 않고 OpenCV BGR 이미지로 읽는다. 완전 투명
픽셀의 RGB 값이 대표 색상에 포함될 수 있다.

**권장**

- alpha가 낮은 픽셀 제외
- 흰색/검정 배경 합성 여부를 설정으로 선택

### P3. RGB 비율 분류가 브랜드 색상 분석으로는 단순함

R/G/B 중 어느 채널이 가장 큰지만 비교하므로 주황, 보라, 청록, 회색 등의
의미 있는 색상군을 표현하지 못한다.

**권장**

- HSV 또는 CIELAB 공간 사용
- 색상명, HEX, 비율을 함께 제공
- KMeans cluster별 픽셀 비율을 계산

### P3. 자동 테스트 부족

현재 이미지 관련 테스트는:

- 없는 파일의 `get_rgb_space()` 처리
- favicon 저장 및 DOCX 삽입

정도다. 실제 컬러 비율과 KMeans 결과는 검증되지 않는다.

## 5. Favicon 저장과 컬러 분석의 관계

| 저장 대상 | 현재 목적 | 컬러 분석 사용 |
|---|---|---|
| favicon | DOCX에 아이콘 표시 | 사용 안 함 |
| 본문 JPG/PNG | 홈페이지 컬러 분석 | 사용 |
| RGB bar | 분석 결과 파일 | DOCX 포함 |
| KMeans CCAI | 대표 색상 결과 파일 | DOCX 포함 |

따라서 favicon 오류 수정은 보고서 이미지 삽입 안정화 작업이며,
홈페이지 컬러 추출의 핵심 입력은 `save_url2image()`로 저장한 본문 이미지다.

## 6. 개선 우선순위

1. [완료] RGB bar와 KMeans 차트를 DOCX의 `Website Color Analysis` 항목에 삽입
2. KMeans 입력 이미지 리사이즈와 픽셀 샘플링 적용
3. 대표 색상의 HEX 값과 비율 계산
4. query URL, WEBP/JPEG, `srcset` 지원
5. URL hash 기반 파일명으로 충돌 방지
6. alpha 픽셀 제외
7. favicon/로고 색상과 본문 이미지 색상을 분리 표시
8. fixture 기반 컬러 분석 자동 테스트 추가

## 7. 권장 보고서 출력

```text
Website Color Analysis

Analyzed images: 48
Sampling mode: image-balanced

Dominant colors:
1. #1F4E79  31.2%
2. #FFFFFF  24.8%
3. #D9E2F3  18.1%
4. #333333  15.5%
5. #E67E22  10.4%

[Dominant color palette image]
[RGB/neutral distribution image]
```

## 8. 판정

**보고서 연결 완료, 분석 품질 개선 필요**

이미지 저장 파일은 실제 홈페이지 컬러 계산에 사용되고 결과 차트도 최종
DOCX에 포함된다. 처리 성능과 표본 대표성 개선은 후속 과제로 남아 있다.
