# nplt30.py HD PDF Broken Link 최종 수정 테스트 보고서

## 1. 대상
- 파일: `C:\Users\user\Desktop\python\nplt30.py`
- 테스트 URL: `www.hd.com`
- 테스트 일시: 2026-06-28

## 2. 재확인된 문제
- 보고서에 아래 PDF 링크가 Broken Link로 출력되었다.
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_3권(화보 [404]`
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_2권(성장스토리 [404]`
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_1권(통사 [404]`
- 정상 URL은 `).pdf`까지 포함해야 한다.

## 3. 최종 원인
- 이전 수정은 `extract_s_list()`의 URL 추출 문제를 해결했지만, 실제 앵커 링크 처리 경로의 `urlForm()`에도 별도 괄호 절단 로직이 남아 있었다.
- `urlForm()` 마지막 부분에서 `)`가 포함된 URL을 `slice_before_character(returl, ")")`로 처리해 첫 번째 `)` 앞까지만 남겼다.
- 이 때문에 정상 PDF 파일명 내부의 괄호가 URL 종료 문자로 오인되었다.

## 4. 적용한 수정
- `urlForm()`의 무조건 괄호 절단 로직을 제거했다.
- `trim_extracted_url(returl)`을 사용하도록 변경했다.
- 결과적으로 파일명 내부의 균형 잡힌 괄호 `(통사)`, `(성장스토리)`, `(화보)`는 보존하고, 문장 끝에 붙은 불필요한 `)`만 제거한다.

## 5. 테스트 결과

### 5.1 문법 검사
- 명령: `python -m py_compile nplt30.py`
- 결과: 정상 통과

### 5.2 urlForm 회귀 테스트
- 입력:
  - `/common/kr/docs/현대중공업그룹_50년사_1권(통사).pdf`
  - `/common/kr/docs/현대중공업그룹_50년사_2권(성장스토리).pdf`
  - `/common/kr/docs/현대중공업그룹_50년사_3권(화보).pdf`
- 결과:
  - `www.hd.com/common/kr/docs/현대중공업그룹_50년사_1권(통사).pdf`
  - `www.hd.com/common/kr/docs/현대중공업그룹_50년사_2권(성장스토리).pdf`
  - `www.hd.com/common/kr/docs/현대중공업그룹_50년사_3권(화보).pdf`
- 판정: `nplt30 urlForm parenthesized PDF regression OK`

### 5.3 불필요한 닫는 괄호 제거 테스트
- 입력: `http://www.energy-news.co.kr)`
- 결과: `http://www.energy-news.co.kr`
- 입력: `https://x.test/a(1).pdf`
- 결과: `https://x.test/a(1).pdf`
- 판정: `nplt30 trim_extracted_url trailing parenthesis regression OK`

### 5.4 실제 재스캔
- 명령: `python nplt30.py -url www.hd.com -db No`
- 결과: 정상 완료
- 수집 페이지: `184`
- Broken Link 수: `0`
- PDF 링크 처리 확인:
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_3권(화보).pdf`
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_2권(성장스토리).pdf`
  - `https://www.hd.com/common/kr/docs/현대중공업그룹_50년사_1권(통사).pdf`
- 위 PDF는 비용절감 모드에서 파일 다운로드만 `skip` 처리되었고 Broken Link로 기록되지 않았다.

### 5.5 Word 보고서 확인
- 파일: `C:\Users\user\Desktop\python\report\www.hd.com.docx`
- 생성 시각: 2026-06-28 00:13:58
- 확인 결과:
  - `50년사_3권(화보 [404]` 없음
  - `50년사_2권(성장스토리 [404]` 없음
  - `50년사_1권(통사 [404]` 없음
  - Broken Link 섹션의 nplt Index: `0`

## 6. 결론
- 이번 Broken Link는 실제 사이트 링크 문제가 아니라 `urlForm()`의 괄호 처리 버그였다.
- 수정 후 HD의 괄호 포함 PDF 링크는 정상 URL로 유지되며 Broken Link 오탐이 사라졌다.

