# nplt26 Phase A 테스트 보고서: robots.txt 존재 확인

> 테스트일: 2026-06-07  
> 변경 대상: `nplt26.py`, `tests/test_nplt26.py`  
> 기준 사이트: `http://www.onbranding.co.kr`

## 1. 기존 코드 점검

기존 보고서는 `ROBOTS_TEXT` 본문 전체를 출력했다.

```text
User-agent: *
Disallow: ...
```

또한 `fetch_text()`는 404, 네트워크 오류, 권한 오류를 모두 `None`으로
반환해 robots.txt가 없는 경우와 확인에 실패한 경우를 구분하지 못했다.

이는 `robots.txt Information`의 목적이 파일 존재 여부 확인이라는 요구와
일치하지 않았다.

## 2. 변경 내용

- `fetch_text_status()` 추가
- HTTP 상태와 본문을 분리해 저장
- robots 정책 파싱용 본문은 내부적으로 유지
- 보고서에는 본문을 출력하지 않음
- 다음 세 상태를 구분

```text
robots.txt is available. [HTTP 200]
robots.txt was not found. [HTTP 404]
robots.txt availability check failed: <오류>
```

HTTP 200 응답은 본문이 비어 있어도 파일이 존재하는 것으로 판정한다.

## 3. 자동 테스트

- 전체 41개 통과
- 실패 0개
- 오류 0개
- Python 컴파일 성공

추가 테스트:

- robots allow/disallow 정책 유지
- HTTP 200 존재 판정
- 빈 HTTP 200 응답도 존재로 판정
- HTTP 404 미존재 메시지

## 4. 실사이트 검증

대상:

```text
http://www.onbranding.co.kr/robots.txt
```

결과:

| 항목 | 결과 |
|---|---|
| 상태 | `available` |
| HTTP 상태 | 200 |
| 내부 본문 길이 | 117자 |
| 보고서 본문 출력 | 안 함 |
| `User-agent` 출력 | 없음 |
| `Disallow` 출력 | 없음 |
| 보고서 메시지 | `robots.txt is available. [HTTP 200]` |
| Traceback | 없음 |
| `report write error` | 없음 |

생성 보고서:

`temp/robots_status_report/robots_status.docx`

## 5. 판정

**통과**

robots.txt 정책 적용에는 파일 내용을 사용하지만, 보고서의
`robots.txt Information`은 파일 존재 여부와 확인 실패 여부만 표시한다.
