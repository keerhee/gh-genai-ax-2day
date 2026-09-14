# 보충교재

본 과정(session0~session2-4)과 별개로, **수업 전에 스스로 준비할 것**을 다루는 자료입니다.
세션 순서에 끼지 않으므로 폴더 번호를 붙이지 않았습니다.

```
보충교재/
├── 설치/           Claude Desktop · VS Code · Claude Code 설치 (윈도우/맥)
└── 한글문서_HWP/    한컴오피스 없이 한글 문서를 다루는 법 + 예제 양식 3개
```

## 설치 안내 — Claude Desktop · VS Code · Claude Code

윈도우·맥 양쪽 설치 절차를 한 곳에 모았습니다. 사전 배포용입니다.

| 파일 | 용도 |
|---|---|
| `설치/설치안내.md` | 원고(원본). 고칠 때는 이 파일을 고칩니다 |
| `설치/설치안내.pdf` | 수강생 배포용 문서 (A4 15쪽) |
| `설치/설치안내.docx` | 기관 양식에 맞춰 다시 편집할 때 |
| `설치/설치교안.pptx` | 강의용 덱 원본 (PPTX는 깃허브에 올리지 않습니다) |
| `설치/설치교안.pdf` | 덱 배포용 (25장) |
| `설치/_reference_ko.docx` | 문서 변환용 서식 원본 — A4·여백·표·코드블록 서식이 여기 들어 있습니다 |
| `설치/문서_후처리.py` | 변환 후 표 머리행을 쪽마다 반복시키는 후처리 |

### 내용 구성

문서는 **세 갈래 중 하나만 고르게** 되어 있습니다. 셋을 다 설치하지 않습니다.

| 갈래 | 설치할 것 | 터미널 | 대상 |
|---|---|---|---|
| A | Claude Desktop | 필요 없음 | 대부분의 수강생 |
| B | VS Code + Claude Code 확장 | 필요 없음 | 편집기를 함께 쓰는 경우 |
| C | Claude Code CLI | 필요함 | 명령창 작업이 익숙한 경우 |

Claude Desktop 안에 Claude Code가 함께 들어 있어, 갈래 A만으로 중급 실습까지 됩니다.

### 사전 안내에 반드시 넣을 것

**Claude Code는 유료 요금제(Pro·Max·Team·Enterprise) 또는 Console 계정에서만 동작합니다.**
무료 요금제로는 앱이 설치되고 Chat 탭까지만 열리며, 실습에 쓰는 Code 탭은 열리지 않습니다.
수강 신청 안내에 이 한 줄을 같이 보내면 당일 혼선이 줄어듭니다.

두 번째 원인은 기관 방화벽입니다. 허용을 요청할 주소는 문서 1.3과 부록 B에 그대로 적어 두었으니
정보화 담당 부서에 미리 보내도록 안내하십시오. **`claude.ai`만 허용하고
`assets-proxy.anthropic.com` · `*.claudeusercontent.com`을 막으면 오류 없이 빈 화면이 떠서
원인을 찾는 데 가장 오래 걸립니다.**

## 고칠 때

원고는 `설치/설치안내.md`, 덱은 빌드 스크립트로 다시 만듭니다. 덱은 다른 교안과 같은
`zeroone-pitch-deck` 템플릿을 씁니다.

```bash
# 문서 DOCX·PDF 재생성 — 세 단계를 모두 거쳐야 서식이 맞습니다
pandoc 설치안내.md -o 설치안내.docx --reference-doc=_reference_ko.docx
python3 문서_후처리.py 설치안내.docx
soffice --headless --convert-to pdf 설치안내.docx --outdir .

# 덱 재생성 후 반드시 검수
NODE_PATH=$(npm root -g) node 설치교안_빌드.js
python3 ~/Project/.claude/skills/zeroone-pitch-deck/scripts/qa_overflow.py 설치교안.pptx  # 0건이어야 함
soffice --headless --convert-to pdf 설치교안.pptx --outdir .
pdftoppm -r 80 -png 설치교안.pdf /tmp/deck   # 눈으로 확인까지 해야 끝입니다
```

### 문서 서식에서 한 번 겪은 것

- pandoc 기본 reference.docx는 **`sectPr`가 비어 있어 Letter 용지로 떨어집니다.** A4·여백·쪽번호를
  `설치/_reference_ko.docx`에 넣어 두었으니 이 파일을 지우거나 새로 받아 덮어쓰지 마십시오.
- 표의 열 폭은 **마크다운 구분선의 대시 개수 비율**로 정해집니다. 열이 흐트러져 보이면 원고에서
  `|------|---|`처럼 폭을 다시 잡습니다.
- 카드 표의 라벨 칸은 폭이 고정입니다. 덱에서 `rows`의 라벨은 **네 글자 이내**로 씁니다.

### VS Code 쪽에서 빠지기 쉬운 것

수강생이 가장 많이 막히는 지점이라 문서 3.4·3.6과 덱 14·16장에 따로 넣어 두었습니다.

- 확장은 **`code --install-extension anthropic.claude-code`** 로도 설치됩니다. 여러 대를 깔 때 씁니다.
  확인은 `code --list-extensions --show-versions`.
- **맥은 `code` 명령이 기본으로 없습니다.** `Cmd+Shift+P → Shell Command: Install 'code' command in PATH`를
  한 번 실행해야 합니다. 윈도우는 User Installer가 자동 등록합니다.
- **확장은 `claude`를 PATH에 넣지 않습니다.** 확장만 깔고 통합 터미널에서 `claude`를 치면 "없는 명령"이
  나오는데 이게 정상입니다. 터미널에서 쓰려면 길 C(CLI)를 따로 설치해야 합니다.

### 덱에서 명령을 보여 주는 방식

설치 명령은 화면에서 **그대로 옮겨 칠 수 있어야** 하므로, 빌드 스크립트 안에 `codeBlock()`을 두고
다크 카드 + 등폭 글꼴(Consolas)로 찍습니다. 프롬프트 표시(`PS C:\>` · `$`)를 앞에 흐린 색으로
붙여 두었으므로, 수강생이 프롬프트까지 따라 치는 사고가 줄어듭니다. 높이는 내용에서 계산하므로
항목을 늘리면 자동으로 늘어나지만, 콘텐츠 하한(5.9in)을 넘으면 빌드 로그가 경고합니다.

## 기준일

2026년 9월. 설치 절차는 공식 문서(<https://code.claude.com/docs/>)에서 다시 확인한 내용입니다.
이번 판에서 확인·반영한 것: 내려받기 주소가 `claude.com/download`로 바뀐 점, winget·Homebrew·npm
설치 경로, VS Code 확장 식별자(`anthropic.claude-code`), 권한 모드 네 가지와 **유료 요금제의
기본값이 Auto**라는 점, 방화벽 허용 도메인 목록입니다.
화면과 메뉴 이름은 버전에 따라 달라지므로, 기수가 바뀌면 명령과 화면 순서를 다시 확인하십시오.

---

## 한글 문서(HWP·HWPX) — kordoc

한컴오피스 없이 한글 문서를 읽고·만들고·채우는 오픈소스 도구를 다룹니다.
공무원이 쓰는 양식 그대로 연습할 수 있게 예제 세 개를 함께 넣었습니다.

| 파일 | 용도 |
|---|---|
| `한글문서_HWP/kordoc_설치와_사용.md` | 설치 세 가지 방법 · 읽기 · 마크다운→HWPX 생성 · 양식 채우기 |
| `한글문서_HWP/예제/*.hwpx` | 업무보고·보고서 양식 3종 (이름·번호는 전부 가짜 값) |
| `한글문서_HWP/예제/서울시_공무원_생성형_AI_활용_교육_계획서_gemini.pdf` | PDF→마크다운 연습용. **AI가 만든 가상 문서** |

마크다운으로 쓴 보고서를 공문서 HWPX로 바꾸면서 **행정업무운영 편람 표기법까지
검수**해 줍니다. 쌍점·물결표 띄어쓰기 같은 것을 잡아 줍니다.

```bash
npx kordoc generate 보고서.md -o 보고서.hwpx   # 만들면서 표기법 검수
npx kordoc validate 보고서.hwpx                 # 한컴독스에서 열리는 구조인지
```

저장소는 <https://github.com/chrisryugj/kordoc> (MIT). Node.js 18 이상이 필요합니다.
