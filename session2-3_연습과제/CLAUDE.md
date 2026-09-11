# 새올구 무단투기 대응 프로젝트 — 상시 규칙

이 파일은 폴더 루트에 둔다. Claude Code는 매 명령마다 이 파일을 먼저 읽는다.

## 원본 보존
input/ 아래 원본은 수정하지 않는다. 정제 결과는 output/에 새 파일로 만든다.

## 개인정보
연락처·생년·상세주소는 분석용 데이터에서 마스킹하고, 지도·보고서·대시보드에 노출하지 않는다.

## 추정 표시
추정한 값은 "추정"이라고 쓴다. 데이터에 없는 숫자를 만들지 않는다.
상관관계를 인과관계로 서술하지 않는다.

## 변경 로그
모든 변경은 working/cleaning_log.md에 건수·행번호·이유를 남긴다.

## 사람 승인
분류체계 확정 · 정책대안 선정 · 최종 보고서 배포 세 지점에서는 진행을 멈추고 확인을 요청한다.

## 산출물
문서는 한국어 마크다운, 숫자에는 (원천파일 · 계산식)을 병기한다.
웹 산출물은 단일 HTML 파일로 만들고 데이터를 외부로 보내지 않는다.

---

## 폴더 구조
```
input/     읽기 전용 원본 — complaints_200.csv · cctv_existing_30.csv · district_profile.csv · project_conditions.txt
working/   판단의 흔적 — PLAN.md · classification_rule.md · cleaning_log.md · red_team.md · final_audit.md
output/    남는 결과 — 01_데이터품질보고서.md · 02_정제민원.xlsx · 04_민원분류.xlsx · 06_핵심KPI.xlsx
           07_민원지도.html · 08_정책대안.md · 09_기관장보고.docx · 11_dashboard.html
```
