# 공공기관 생성형 AI 트랙 — 중급 (session2)

기초 트랙(`../session1`)의 4단계에 해당한다. 이 세션은 집합 3시간이며, 기초의 산출물이 그대로 입력이 된다.
한 줄 요약: 기초는 파일을 올리고, 중급은 폴더를 맡긴다.

| 순서 | 단계 | 형태·시간 | 덱 | 딸린 파일 |
|---|---|---|---|---|
| 4 | 중급 · 폴더 위임 | 집합 · 프롬프트 12 + 웹앱 5 (41장) | `PublicOffice_GenAI_Intermediate_3H.pptx` / `.pdf` | `PublicOffice_GenAI_Intermediate_3H_data/`, `_Quiz.html` |
| 4-연습 | 중급 연습 과제 | 집합 · 같은 프롬프트 · 새 폴더 (16장) | `PublicOffice_GenAI_Practice_Round.pptx` / `.pdf` | `PublicOffice_GenAI_Practice_Round_data/`, `_Quiz.html` |
| 4-확장 | 중급 캡스톤 | 집합 · 6단계 (29장) | `PublicOffice_GenAI_Capstone.pptx` / `.pdf` | `PublicOffice_GenAI_Capstone_data/` |

연습 과제는 본과정과 캡스톤 사이에 둔다. 본과정에서 배운 흐름을 **새 데이터로 혼자 한 번** 돌려
캡스톤에서 공개데이터를 다룰 준비를 시킨다. 정답 수치는 학습자에게 공개하지 않는다.

캡스톤은 본과정을 일찍 끝낸 팀을 위한 확장 과제다. 시간이 모자라면 4단계까지로 완결된다.

## 중급 · 블록 구성

작업 흐름은 PLAN First → 분석 → 정책 → 보고 → Final Audit. 30분마다 산출물 하나와 웹앱 하나가 나온다.

| 시간 | 블록 | 프롬프트 | 산출물 | 블록 웹앱 |
|---|---|---|---|---|
| 00:00–00:30 | 1 · 계획과 신뢰 | A 계획, B 품질검사, C 안전정제 | PLAN.md · 품질보고서 · 변경로그 | 정제 로그 뷰어 |
| 00:30–01:15 | 2 · 규칙과 분류 | D 분류체계, E 자동분류, F KPI | 분류표 · KPI 표 | 저확신 재검토 큐 |
| 01:15–02:00 | 3 · 지도와 공백 | G 지도, H 시설 대조 | 반복지점 15 · 공백 12 | 점검 후보지 지도 |
| 02:00–02:30 | 4 · 예산 | I 포트폴리오, I-R 레드팀 | 3천만원 3안 + 반박표 | 예산 시뮬레이터 |
| 02:30–03:00 | 5 · 보고와 감사 | J 보고서, K PPT·대시보드, L 최종검산 | 1페이지 보고 · PPT 5장 | 통합 대시보드 + Audit 패널 |

블록 웹앱 다섯 개가 마지막에 하나로 합쳐진 것이 `PublicOffice_GenAI_Intermediate_3H_data/answer/ops_dashboard.html`(덱 p37의 완성본)이다.

## 캡스톤 · 6단계

공개데이터를 스스로 구해 수요와 대응이 어긋난 곳을 찾고, 곳마다 무엇을 할지 정한다.
핵심은 지도 그리기가 아니라 조치 유형 다섯 가지(신설·개선·운영·관찰·재배치)를 숫자 규칙으로 가르는 일이다.

| 단계 | 내용 | 산출물 |
|---|---|---|
| 1 | 데이터 조달과 헤더 매핑 | 매핑표 + 제외 행 목록 |
| 2 | 조치 유형 판정 규칙 | 다섯 유형 규칙표 + 긴급도 식 |
| 3 | 웹앱 PRD | 지도 웹앱 1차 |
| 4 | 개선 | 지도 웹앱 2차 (예산·Audit) |
| 5 | 예산과 레드팀 | 5천만원 3안 + 반박표 |
| 6 | 보고서와 Final Audit | 1페이지 보고서 + 검산표 |

배점 100점은 조치 유형 판정 25, 지도 웹앱 25, 나머지 50으로 나뉜다. 지도의 미관에는 배점이 없다.
모범답안 완성본이 `PublicOffice_GenAI_Capstone_data/answer/gapmap.html`이다. 해설은 같은 폴더의 `answer/model_answer.md`.

## 실습 데이터

| 폴더 | 출처 | 내용 |
|---|---|---|
| `PublicOffice_GenAI_Intermediate_3H_data/` | 공식 키트 | 민원 212행 · CCTV 30 · 지역현황 7 · 사업조건 · CLAUDE.md · 완성본 웹앱 · 강사용 정답 2종 |
| `PublicOffice_GenAI_Practice_Round_data/` | 자체 제작 | 새올구 연습 세트. 파일명은 같고 내용만 다름. 검산기·정답키 포함 |
| `PublicOffice_GenAI_Capstone_data/` | 공식 키트 | 보호구역 32 · CCTV 139 · 인구 7 · 보행사고 24 · 사업조건 · 모범답안 · 진행 가이드 |

완성본 웹앱은 각 키트의 `answer/` 안에 있다. 더블클릭하면 예시 데이터로 바로 돈다.
강사용 파일은 이름에 `instructor`가 붙어 있거나 `강사용_instructor_only/` 안에 있다.
**수강생 배포 시 그 파일들을 뺀다.**

원본 배포용 압축은 `PublicOffice_GenAI_Intermediate_3H_data.zip`과
`PublicOffice_GenAI_Capstone_kit.zip`으로 그대로 남겨 두었다.
