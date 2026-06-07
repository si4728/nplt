# nplt26 Phase A 테스트 보고서: Tree Map 내부·외부 링크 분리

> 테스트일: 2026-06-07  
> 변경 대상: `nplt26.py`, `tests/test_nplt26.py`

## 1. 기존 문제

Tree Map 생성 시 그래프의 모든 노드를 사용해 다음 항목이 섞였다.

- 사이트 내부 경로
- 외부 사이트 전체 URL
- 같은 외부 URL의 HTTP/HTTPS 변형
- 빈 경로 노드

따라서 정보구조를 보여주는 Tree Map이 외부 뉴스·지도·SNS URL로 길어지고,
`├──  - 2`와 같은 의미 없는 노드도 출력됐다.

## 2. 변경 내용

- 대상 사이트의 hostname과 동일한 URL만 Tree Map에 포함
- `www` 유무와 HTTP/HTTPS 차이는 같은 내부 사이트로 처리
- query와 fragment를 제거하고 path 기준으로 정규화
- 빈 경로는 `/`로 통합
- 외부 URL은 Tree Map에서 제거
- 외부 링크는 `External Link Domains` 섹션에 도메인별 고유 URL 수로 출력
- 기존 Tree Map 숫자의 의미인 “단순화된 경로별 고유 URL 수” 유지

## 3. 출력 예

```text
Tree Map
/
├── /bbs - 2
└── /data
    └── /data/file
        └── /data/file/notice

External Link Domains
donga.com: 1
map.naver.com: 1
youtube.com: 1
```

## 4. 테스트 결과

- 자동 테스트 42개 전체 통과
- Python 컴파일 성공
- Tree Map 내부 HTTP/HTTPS URL 출력 없음
- `/bbs` 내부 경로 집계 확인
- 빈 경로 노드 없음
- 외부 도메인 별도 집계 확인
- DOCX 생성 성공

생성 보고서:

`temp/treemap_report/treemap_separated.docx`

## 5. 판정

**통과**

Tree Map은 대상 사이트의 내부 디렉터리 구조만 표시하며, 외부 링크는
별도의 도메인 요약으로 분리된다.
