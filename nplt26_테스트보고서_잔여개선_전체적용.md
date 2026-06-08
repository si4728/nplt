# nplt26 잔여 개선 전체 적용 테스트 보고서

## 적용 일시

- 2026-06-08

## 적용 범위

잔여 개선 포인터 중 실제 결과 오류에 영향을 주는 항목을 코드에 반영했다.

## 적용 내용

### SNS 사용 점검

- `abnormal_url()`의 `find()` 조건 오류를 수정했다.
- `facebook.com`, `m.facebook.com`, `youtube.com`, `youtu.be` 등 서브도메인과 단축 도메인을 플랫폼 단위로 통합하도록 했다.
- `SNS_PLATFORMS` 구조를 추가했다.
- `record_sns_link()`로 플랫폼, 유형, 페이지, 고유 URL을 분리 집계하도록 했다.
- SNS 유형을 `profile`, `content`, `share`, `embed`로 분류하도록 했다.
- SNS 보고서를 Word 표로 출력하도록 했다.
- 대표 URL은 Word 표 안에서 하이퍼링크로 생성되도록 했다.

### ESG 키워드

- ESG 키워드와 본문을 Unicode NFKC, 공백 축약, casefold 기준으로 정규화했다.
- 영어 키워드는 단어 경계 기반으로 검색하도록 했다.
- ESG 보고서 제목을 실제 의미에 맞게 `Pages containing ESG keywords`로 출력하도록 했다.
- DB 저장 시 ESG 결과를 count 내림차순으로 정렬하도록 했다.

### Word 보고서

- 구조화된 표 출력용 `progress_make_table()`을 추가했다.
- Word 표 생성과 하이퍼링크 helper를 추가했다.
- 이미지 파일이 없을 때 `report write error` 대신 `[image unavailable: ...]` 메시지를 보고서에 남기도록 했다.
- `reponsetime_index.JPG` 누락으로 인한 실행 경고를 막기 위해 저장소에 해당 이미지를 추가했다.

### DB 저장

- ESG, 일반 word, SNS 저장 순서를 count 내림차순으로 정렬했다.
- 기존 DB 테이블 구조는 유지했다.

## 추가 테스트

기존 테스트에 다음 검증을 추가했다.

- 정상 query URL이 `abnormal_url()`에서 제거되지 않는지
- SNS host 정규화와 플랫폼 식별
- `youtu.be`와 `youtube.com`의 YouTube 통합
- SNS 유형, 페이지, 고유 URL 집계
- SNS Word 표와 하이퍼링크 생성
- ESG 대소문자 및 공백 정규화 검색
- 누락 이미지 보고서 처리

## 테스트 명령

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python nplt26.py -h
python nplt26.py -url http://www.onbranding.co.kr -cost Yes -ca No -db No -robots No -wl 10
```

## 테스트 결과

- 단위 테스트: 48개 통과
- CLI 도움말: 정상
- 실제 URL 테스트: 정상 종료
- 대상 URL: `http://www.onbranding.co.kr`
- 분석 페이지 수: 18
- robots.txt: HTTP 200 확인
- sitemap.xml: 확인
- Domain Information: DNS fallback으로 출력
- ESG 결과: `소비자 보호 : 1`
- SNS 결과: 대상 사이트에서 SNS 링크 미검출
- Word 보고서 생성: 정상

## 비고

실제 URL 테스트는 외부 네트워크 권한 승인 후 실행했다. `onbranding.co.kr` 테스트에서는 SNS 링크 자체가 발견되지 않았으므로 SNS 표는 생성되지 않고 `No SNS links were found.` 메시지가 출력되는 것이 정상이다.

## 결론

잔여 개선 포인터 중 현재 코드 구조 안에서 적용 가능한 핵심 항목을 반영했고, 회귀 테스트와 실제 URL 실행 테스트를 통과했다.
