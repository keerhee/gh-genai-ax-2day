# -*- coding: utf-8 -*-
"""공공기관 생성형 AI 중급 — 실습 데이터 생성기 (seed 고정, 재현 가능)
   사례: 쓰레기 무단투기 민원 200건 + 기존 CCTV 30개 + 지역 기초현황 + 예산 3천만원"""
import csv, random, datetime as dt, json
from collections import defaultdict
random.seed(20260903)
OUT = "/home/claude/pub_inter/data/input/"

# ── 행정동 설정 (기초 과정과 동일한 가상 지명) ──────────────
# pop: 인구, hh: 세대, area: 면적(km2), shop: 상가수, oneroom: 원룸비율, old: 노후주택비율, bin: 분리수거함
DONG = {
 "가온동":dict(pop=38200,hh=17400,area=2.9,shop=1240,oneroom=0.46,old=0.31,bins=42,lat=37.5520,lon=127.0480),
 "나래동":dict(pop=27600,hh=11800,area=3.4,shop=610 ,oneroom=0.22,old=0.18,bins=36,lat=37.5585,lon=127.0562),
 "다솜동":dict(pop=14900,hh= 7300,area=1.6,shop=880 ,oneroom=0.58,old=0.44,bins=15,lat=37.5462,lon=127.0605),
 "라온동":dict(pop=31500,hh=13900,area=4.1,shop=520 ,oneroom=0.19,old=0.15,bins=40,lat=37.5641,lon=127.0421),
 "마루동":dict(pop= 9800,hh= 5100,area=1.2,shop=430 ,oneroom=0.62,old=0.51,bins= 9,lat=37.5498,lon=127.0344),
 "바다동":dict(pop=22400,hh= 9600,area=2.7,shop=700 ,oneroom=0.28,old=0.24,bins=29,lat=37.5610,lon=127.0669),
 "새벽동":dict(pop=18700,hh= 8200,area=2.2,shop=560 ,oneroom=0.33,old=0.27,bins=24,lat=37.5443,lon=127.0512),
}
# 민원 배분: 단순 건수 1위=가온동(인구 최다), 인구보정 1위=마루동 → 핵심 함정
SHARE = {"가온동":52,"다솜동":38,"마루동":31,"바다동":26,"새벽동":22,"나래동":18,"라온동":13}
assert sum(SHARE.values())==200

# 반복 발생 지점(핫스팟) — 동별 고정 좌표 클러스터
HOT = {
 "가온동":[("가온로 12길 일대",37.5514,127.0473),("가온시장 뒷골목",37.5527,127.0491)],
 "다솜동":[("다솜로 3길 원룸촌",37.5458,127.0598),("다솜중학교 후문",37.5469,127.0613),("다솜빌라 주차장",37.5455,127.0589)],
 "마루동":[("마루골목 상가 뒤",37.5493,127.0339),("마루경로당 앞",37.5502,127.0350)],
 "바다동":[("바다공원 북측 출입로",37.5615,127.0673)],
 "새벽동":[("새벽역 2번출구 뒤편",37.5447,127.0518)],
 "나래동":[("나래아파트 상가",37.5589,127.0567)],
 "라온동":[("라온천 산책로 입구",37.5645,127.0416)],
}
CH = ["국민신문고","전화","앱","방문","홈페이지"]
DEPT = ["청소행정과","환경관리과","주민생활지원과"]
# 민원 본문 템플릿 — 분류 정답(gt)과 함께
BODY = [
 ("가정용 종량제 봉투가 아닌 일반 비닐에 담아 버려져 있습니다","무단투기(일반생활폐기물)",0.95),
 ("음식물쓰레기를 종량제 용기 없이 그냥 버려 악취가 심합니다","무단투기(음식물)",0.95),
 ("장롱과 매트리스가 버려져 있는데 대형폐기물 스티커가 없습니다","대형폐기물 무단배출",0.95),
 ("상가에서 나온 것으로 보이는 박스와 스티로폼이 산더미입니다","사업장폐기물 혼합배출",0.90),
 ("분리수거함이 넘쳐서 주변에 페트병이 흩어져 있습니다","수거체계 미비(적재초과)",0.85),
 ("수거 차량이 다녀간 뒤에도 쓰레기가 그대로 남아 있습니다","수거 미이행",0.85),
 ("공사장에서 나온 폐자재가 인도에 방치돼 있습니다","건설폐기물 방치",0.90),
 ("담배꽁초와 일회용컵이 계단 아래 쌓여 있습니다","무단투기(일반생활폐기물)",0.75),
 ("여기 좀 봐주세요","분류불가(정보부족)",0.25),
 ("냄새가 너무 심합니다 조치 부탁드립니다","분류불가(정보부족)",0.30),
 ("매번 같은 자리에 또 버립니다 단속 좀 해주세요","무단투기(상습지점)",0.80),
 ("배출 요일이 아닌데 미리 내놓아 길이 지저분합니다","배출요일 위반",0.85),
]
LOWCONF = {"분류불가(정보부족)"}

START = dt.date(2026,5,1); END = dt.date(2026,8,20)
SPAN = (END-START).days

rows=[]; nid=1
for dg,cnt in SHARE.items():
    for _ in range(cnt):
        # 핫스팟 집중도: 다솜·마루는 반복지점 비중 높음
        p_hot = 0.72 if dg in ("다솜동","마루동") else 0.45
        if random.random() < p_hot and HOT[dg]:
            name,la,lo = random.choice(HOT[dg])
            lat = round(la + random.gauss(0,0.00035),6); lon = round(lo + random.gauss(0,0.00035),6)
            spot = name; repeat="Y"
        else:
            d=DONG[dg]
            lat = round(d["lat"] + random.gauss(0,0.0035),6); lon = round(d["lon"] + random.gauss(0,0.0035),6)
            spot = ""; repeat="N"
        recv = START + dt.timedelta(days=random.randint(0,SPAN))
        # 여름 후반으로 갈수록 증가
        if random.random() < 0.30: recv = START + dt.timedelta(days=random.randint(int(SPAN*0.55),SPAN))
        body,gt,conf = random.choice(BODY)
        done = random.random() < 0.82
        days = max(1,int(random.gauss(9 if dg in("가온동","다솜동") else 6, 3.2)))
        proc = recv + dt.timedelta(days=days) if done else None
        # 주소 표기 불일치 3종
        style = random.choice(["도로명","지번","혼합"])
        base = spot if spot else f"{dg} 일원"
        if style=="도로명": addr = f"세종특별자치시 한빛구 {dg} {random.randint(1,40)}로 {random.randint(1,90)}"
        elif style=="지번": addr = f"한빛구 {dg} {random.randint(100,899)}-{random.randint(1,60)}"
        else: addr = f"{dg} {base}".strip()
        rows.append({
          "민원ID":f"M{nid:04d}","접수일":recv,"접수채널":random.choice(CH),
          "행정동":dg,"주소":addr,"위도":lat,"경도":lon,"반복지점":spot,"반복여부":repeat,
          "민원내용":body,"처리상태":"완료" if done else random.choice(["처리중","보류"]),
          "처리일":proc,"처리기간":days if done else None,"담당부서":random.choice(DEPT),
          "신고자연락처":f"010-{random.randint(2000,9999)}-{random.randint(1000,9999)}",
          "신고자생년":f"{random.randint(1955,2004)}{random.randint(1,12):02d}{random.randint(1,28):02d}-{random.randint(1,2)}******",
          "_gt_민원유형":gt,"_gt_확신도":conf})
        nid+=1
random.shuffle(rows)

# ── 의도적 오염 ────────────────────────────────────────────
dirty=[dict(r) for r in rows]
def fmt(d,f):
    if d is None: return ""
    return [d.strftime("%Y-%m-%d"),d.strftime("%Y-%m-%d"),d.strftime("%Y/%m/%d"),d.strftime("%Y.%m.%d"),d.strftime("%y%m%d")][f]
for i,r in enumerate(dirty):
    f=i%5; r["접수일"]=fmt(r["접수일"],f); r["처리일"]=fmt(r["처리일"],f)
for r in random.sample(dirty,9):  r["행정동"]=""
for r in random.sample(dirty,7):  r["위도"]=""; r["경도"]=""      # 좌표 변환 실패 상황
for r in random.sample(dirty,6):  r["처리기간"]=""
for r in random.sample(dirty,4):  r["주소"]=""
dup=[dict(r) for r in random.sample(dirty,7)]                     # 완전 중복
dup2=[]
for r in random.sample(dirty,5):                                  # ID만 다른 실질 중복
    r2=dict(r); r2["민원ID"]=f"M9{random.randint(100,999)}"; dup2.append(r2)
for r in random.sample(dirty,6):                                  # 처리일 < 접수일
    if r["처리일"]: r["처리일"]="2026-04-02"
for r in random.sample(dirty,4): r["처리기간"]=random.choice(["-2","0","365"])
allrows = dirty+dup+dup2
random.shuffle(allrows)

COLS=["민원ID","접수일","접수채널","행정동","주소","위도","경도","반복지점","반복여부",
      "민원내용","처리상태","처리일","처리기간","담당부서","신고자연락처","신고자생년"]
with open(OUT+"complaints_200.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,COLS); w.writeheader()
    for r in allrows: w.writerow({k:("" if r[k] is None else r[k]) for k in COLS})

# ── CCTV 30개 ─────────────────────────────────────────────
# 함정: 가온동에 CCTV가 많지만 노후·저화소·방향불일치 / 다솜동·마루동은 0~1대
CCTV_PLAN={"가온동":9,"나래동":6,"라온동":6,"바다동":4,"새벽동":3,"다솜동":1,"마루동":1}
cc=[];cid=1
for dg,k in CCTV_PLAN.items():
    d=DONG[dg]
    for _ in range(k):
        old = dg=="가온동" and random.random()<0.7
        yr = random.choice([2014,2015,2016]) if old else random.choice([2019,2020,2022,2023,2024])
        px = random.choice(["41만","41만","100만"]) if yr<2017 else random.choice(["200만","400만"])
        cc.append({"CCTV_ID":f"CV{cid:03d}","행정동":dg,
          "설치주소":f"한빛구 {dg} {random.randint(1,40)}로 {random.randint(1,90)}",
          "위도":round(d["lat"]+random.gauss(0,0.0030),6),"경도":round(d["lon"]+random.gauss(0,0.0030),6),
          "설치연도":yr,"화소":px,"촬영방향":random.choice(["도로","교차로","주차장","공원","골목"]),
          "야간성능":"미흡" if yr<2017 else random.choice(["보통","양호"]),
          "설치목적":random.choice(["방범","교통","쓰레기단속","어린이보호"])})
        cid+=1
with open(OUT+"cctv_existing_30.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,list(cc[0])); w.writeheader(); w.writerows(cc)

# ── 지역별 기초현황 ────────────────────────────────────────
base=[]
for dg,d in DONG.items():
    base.append({"행정동":dg,"인구":d["pop"],"세대수":d["hh"],"면적(km2)":d["area"],
      "상가수":d["shop"],"원룸비율(%)":round(d["oneroom"]*100,1),"노후주택비율(%)":round(d["old"]*100,1),
      "분리수거함수":d["bins"],"기존CCTV수":CCTV_PLAN[dg],
      "청소차수거주기(주/회)":3 if dg in("가온동","라온동","나래동") else 2,
      "중심좌표_위도":d["lat"],"중심좌표_경도":d["lon"]})
with open(OUT+"district_profile.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,list(base[0])); w.writeheader(); w.writerows(base)

# ── project_conditions.txt ──────────────────────────────────────────
cond = """[사업 개요]
사업명 : 생활폐기물 무단투기 저감 시범사업
예산   : 30,000,000원 (총액 초과 불가, 당해연도 내 집행)
기간   : 2026년 9월 ~ 12월 (4개월)
소관   : 청소행정과 (협조: 환경관리과, 주민생활지원과)

[집행 단가]
고정형 방범·단속 CCTV 설치        3,500,000원 / 대   (전기·통신 인입 포함)
이동형(태양광) 감시카메라 임차     1,200,000원 / 대·4개월
스마트 분리수거함 설치              800,000원 / 개
LED 보안등·조명 개선                2,000,000원 / 개소
경고·안내 표지판 제작·설치           150,000원 / 개
계도요원 인건비                     1,800,000원 / 인·월
현수막·주민 홍보물                   400,000원 / 회
클린하우스(수거거점) 정비           2,600,000원 / 개소
현장 실태조사 용역                  3,000,000원 / 회

[제약 조건]
1. 고정형 CCTV는 개인정보 영향평가와 주민 의견수렴이 선행되어야 하며, 최소 6주가 소요된다.
   → 9월 착수 기준으로 연내 설치는 최대 4대까지만 현실적이다.
2. 이동형 감시카메라는 영향평가 대상이 아니나 야간 인식률이 낮다.
3. 계도요원은 최소 2개월 이상 연속 배치해야 효과 측정이 가능하다.
4. 분리수거함·클린하우스는 주민 동의가 필요한 부지에 한해 설치한다.
5. 예산의 10% 이상을 홍보에만 쓰지 않는다.
6. 단속 위주 대안은 민원 재발과 주민 반발 가능성을 함께 검토해야 한다.

[의사결정 요청 사항]
- 3천만원 범위에서 서로 다른 성격의 정책 포트폴리오 3안을 제시할 것
- 각 안의 비용, 기대효과 가능성, 부작용, 추가 확인이 필요한 정보를 명시할 것
- 총액이 30,000,000원을 넘는 안은 제출 불가
"""
open(OUT+"project_conditions.txt","w",encoding="utf-8").write(cond)

# ── CLAUDE.md (프로젝트 규칙) ─────────────────────────────
claude_md = """# 프로젝트 규칙 — 무단투기 민원 분석

## 원칙
1. input/ 아래 원본 파일은 절대 수정하지 않는다. 정제 결과는 output/ 에 새 파일로 만든다.
2. 개인정보(연락처·생년·주소 상세)는 분석용 데이터에서 마스킹한다. 지도·보고서·대시보드에 노출하지 않는다.
3. 추정한 값은 반드시 "추정"이라고 표시한다. 데이터에 없는 숫자를 만들지 않는다.
4. 상관관계를 인과관계로 서술하지 않는다.
5. 모든 변경은 working/cleaning_log.md 에 건수·행번호·이유를 남긴다.
6. 최종 보고 전 모든 숫자를 원본에서 다시 계산한다(Final Audit).

## 산출물 규칙
- 문서는 한국어, 표는 마크다운. 숫자에는 (원천파일 · 계산식)을 병기한다.
- 웹 산출물은 외부 라이브러리 없이 단일 HTML 파일로 만들고 데이터를 외부로 전송하지 않는다.

## 사람 승인 지점
- 분류체계 확정 · 정책대안 선정 · 최종 보고서 배포. 이 세 곳에서는 진행을 멈추고 확인을 요청한다.
"""
open("/home/claude/pub_inter/data/CLAUDE.md","w",encoding="utf-8").write(claude_md)

# ── 정답키 (강사용) ───────────────────────────────────────
clean = rows
cnt_by = defaultdict(int); done_days=defaultdict(list); repeat_by=defaultdict(int)
for r in clean:
    cnt_by[r["행정동"]]+=1
    if r["처리기간"] is not None: done_days[r["행정동"]].append(r["처리기간"])
    if r["반복여부"]=="Y": repeat_by[r["행정동"]]+=1
per10k = {d: round(cnt_by[d]/DONG[d]["pop"]*10000,1) for d in DONG}
gtcnt=defaultdict(int); low=0
for r in clean:
    gtcnt[r["_gt_민원유형"]]+=1
    if r["_gt_확신도"]<0.5: low+=1
hot_rank = sorted(((r["반복지점"] for r in clean if r["반복지점"])), key=lambda x:x)
hotcnt=defaultdict(int)
for r in clean:
    if r["반복지점"]: hotcnt[r["반복지점"]]+=1

ans=[("원본 행 수(오염본)",len(allrows)),("중복 제거 후",len(clean)),
 ("완전 중복",7),("ID만 다른 실질 중복",5),("처리일<접수일 오류",6),("처리기간 이상값(-2/0/365)",4),
 ("행정동 결측",9),("좌표 결측(지오코딩 실패)",7),("주소 결측",4),("처리기간 결측",6),
 ("날짜 형식 종류","YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD / YYMMDD"),
 ("개인정보 컬럼","신고자연락처 · 신고자생년(주민번호 앞자리) · 주소 상세"),
 ("민원 건수 1위(단순)",f"가온동 {cnt_by['가온동']}건"),
 ("인구 1만명당 1위",f"마루동 {per10k['마루동']}건 (가온동 {per10k['가온동']}건)"),
 ("인구보정 순위", " > ".join(f"{d}({per10k[d]})" for d in sorted(per10k,key=lambda x:-per10k[x])[:4])),
 ("CCTV 공백 hotspot","다솜동(CCTV 1대, 민원 38건) · 마루동(CCTV 1대, 민원 31건)"),
 ("CCTV 있어도 민원 많음","가온동 — CCTV 9대 중 다수가 2014~2016년 41만 화소·야간 미흡"),
 ("반복지점 TOP3", " > ".join(f"{k}({v})" for k,v in sorted(hotcnt.items(),key=lambda x:-x[1])[:3])),
 ("저확신 분류 대상(정보부족)",f"{low}건"),
 ("분류 정답 카테고리 수",len(gtcnt)),
 ("예산 함정","고정형 CCTV는 영향평가 6주 → 연내 최대 4대. 3천만원 전액 CCTV 배정은 집행 불가"),
 ("Red Team 포인트","단속 강화안은 인접 동으로 투기 이전(풍선효과) 가능성 — 데이터로 확인 불가, 추가 조사 필요"),
]
with open("/home/claude/pub_inter/data/answer_key_instructor.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["항목","값"]); w.writerows(ans)
with open("/home/claude/pub_inter/data/classification_answer_instructor.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["민원ID","정답_민원유형","정답_확신도"])
    for r in clean: w.writerow([r["민원ID"],r["_gt_민원유형"],r["_gt_확신도"]])

print("rows(dirty)",len(allrows),"clean",len(clean))
for k,v in ans: print(" ",k,"=",v)
