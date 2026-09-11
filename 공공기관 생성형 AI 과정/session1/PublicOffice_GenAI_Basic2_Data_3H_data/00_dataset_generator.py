# -*- coding: utf-8 -*-
"""공공기관 생성형 AI 기초 2 — 실습 데이터 생성기 (재현 가능, seed 고정)"""
import csv, random, datetime as dt
from collections import defaultdict

random.seed(20260902)
OUT = "/home/claude/pub_basic/data/"

DONGS = ["가온동","나래동","다솜동","라온동","마루동","바다동","새벽동"]
DEPTS = ["청소행정과","도로교통과","환경관리과","건축과","복지정책과","주민생활지원과"]
TYPES = ["쓰레기 무단투기","불법주정차","도로파손","소음","악취","가로등 고장","공원 관리","건축 인허가","복지 상담","기타"]
CHANNELS = ["국민신문고","전화","방문","앱","홈페이지"]
AGES = ["20대 이하","30대","40대","50대","60대 이상"]
DEPT_OF = {"쓰레기 무단투기":"청소행정과","악취":"환경관리과","불법주정차":"도로교통과",
           "도로파손":"도로교통과","소음":"환경관리과","가로등 고장":"도로교통과",
           "공원 관리":"환경관리과","건축 인허가":"건축과","복지 상담":"복지정책과","기타":"주민생활지원과"}

START = dt.date(2025,9,1); END = dt.date(2026,8,31)
MONTHS = []
d = START
while d <= END:
    MONTHS.append((d.year,d.month)); 
    d = dt.date(d.year + (d.month==12), (d.month%12)+1, 1)

# 월별 목표 건수: 완만한 증가 + 여름철 쓰레기 급증
BASE = {m:(58+i*1.1) for i,m in enumerate(MONTHS)}

def type_weight(ym):
    y,m = ym
    w = {"쓰레기 무단투기":16,"불법주정차":15,"도로파손":11,"소음":10,"악취":7,
         "가로등 고장":9,"공원 관리":7,"건축 인허가":8,"복지 상담":9,"기타":8}
    if m in (5,6,7,8):                      # 여름철 쓰레기·악취 급증
        w["쓰레기 무단투기"] += 14 + (m-5)*5
        w["악취"] += 5
    return w

rows=[]; nid=1
for ym in MONTHS:
    y,m = ym
    n = int(BASE[ym] * random.uniform(0.93,1.08))
    tw = type_weight(ym); types=list(tw); wts=[tw[t] for t in types]
    dim = (dt.date(y+(m==12),(m%12)+1,1) - dt.date(y,m,1)).days
    for _ in range(n):
        t = random.choices(types, wts)[0]
        recv = dt.date(y,m,random.randint(1,dim))
        # 행정동: 쓰레기 민원은 가온동에 집중
        if t=="쓰레기 무단투기":
            dong = random.choices(DONGS,[34,13,12,11,11,10,9])[0]
        else:
            dong = random.choice(DONGS)
        ch = random.choices(CHANNELS,[34,26,10,20,10])[0]
        age = random.choices(AGES,[14,22,26,21,17])[0]
        dept = DEPT_OF[t]
        # 처리일수: 가온동 지연, 건축 인허가 장기
        base = {"건축 인허가":14,"복지 상담":5,"쓰레기 무단투기":6}.get(t,7)
        if dong=="가온동": base += 5
        if m in (6,7,8) and t=="쓰레기 무단투기": base += 3
        days = max(1, int(random.gauss(base, base*0.42)))
        done = random.random() < 0.90
        proc = recv + dt.timedelta(days=days) if done else None
        status = "완료" if done else random.choice(["처리중","보류"])
        # 만족도: 처리일수 길수록 낮음, 60대+전화는 더 낮음
        sat = None
        if done and random.random() < 0.62:
            s = 5.0 - min(2.6, days*0.13) + random.gauss(0,0.7)
            if age=="60대 이상" and ch=="전화": s -= 0.8
            sat = max(1, min(5, int(round(s))))
        # 재민원: 처리일수·쓰레기 유형에서 높음
        p = 0.07 + min(0.22, days*0.011) + (0.09 if t=="쓰레기 무단투기" else 0)
        rep = "Y" if (done and random.random()<p) else "N"
        rows.append({
            "민원ID": f"C{nid:05d}", "접수일": recv, "부서": dept, "민원유형": t,
            "행정동": dong, "접수채널": ch, "연령대": age, "처리상태": status,
            "처리일": proc, "처리일수": days if done else None,
            "만족도": sat, "재민원여부": rep,
            "민원인연락처": f"010-{random.randint(2000,9999)}-{random.randint(1000,9999)}",
            "민원내용요약": {"쓰레기 무단투기":"상습 투기 지점 방치","불법주정차":"이면도로 상시 주차",
                "도로파손":"포트홀 발생","소음":"야간 공사 소음","악취":"음식물 쓰레기 악취",
                "가로등 고장":"야간 점등 불량","공원 관리":"시설물 파손","건축 인허가":"허가 처리 지연 문의",
                "복지 상담":"지원금 신청 문의","기타":"기타 건의"}[t],
        })
        nid += 1

CLEAN_N = len(rows)                       # 정제 후 기대 행 수(중복 제거 전)
# ── 의도적 오염 ─────────────────────────────────────────────
dirty = [dict(r) for r in rows]
# 1) 날짜 형식 불일치 3종
for i,r in enumerate(dirty):
    f = i % 7
    def fmt(d):
        if d is None: return ""
        if f in (0,1,2,3): return d.strftime("%Y-%m-%d")
        if f==4: return d.strftime("%Y/%m/%d")
        if f==5: return d.strftime("%Y.%m.%d")
        return d.strftime("%Y년 %m월 %d일")
    r["접수일"] = fmt(r["접수일"]); r["처리일"] = fmt(r["처리일"])
# 2) 결측 (만족도는 이미 결측, 여기선 행정동·부서·처리일수)
for r in random.sample(dirty, 24): r["행정동"] = ""
for r in random.sample(dirty, 11): r["부서"] = ""
for r in random.sample(dirty, 15): r["처리일수"] = ""
# 3) 완전 중복 접수 18건
dup = [dict(r) for r in random.sample(dirty, 18)]
# 4) 민원ID만 다른 실질 중복 12건
dup2 = []
for r in random.sample(dirty, 12):
    r2 = dict(r); r2["민원ID"] = f"C9{random.randint(1000,9999)}"; dup2.append(r2)
# 5) 처리일 < 접수일 오류 9건
for r in random.sample(dirty, 9):
    if r["처리일"]:
        r["처리일"] = "2025-08-15"
# 6) 이상값 처리일수 7건
for r in random.sample(dirty, 7): r["처리일수"] = random.choice(["999","0","-3"])
# 7) 공백·전각·표기 흔들림
for r in random.sample(dirty, 30): r["민원유형"] = " " + r["민원유형"] + " "
for r in random.sample(dirty, 14): r["처리상태"] = r["처리상태"].replace("완료","완 료")
for r in random.sample(dirty, 20): r["접수채널"] = r["접수채널"].replace("국민신문고","국민 신문고")

allrows = dirty + dup + dup2
random.shuffle(allrows)

COLS = ["민원ID","접수일","부서","민원유형","행정동","접수채널","연령대","처리상태",
        "처리일","처리일수","만족도","재민원여부","민원인연락처","민원내용요약"]
with open(OUT+"01_complaints_raw.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,COLS); w.writeheader()
    for r in allrows:
        w.writerow({k:("" if r[k] is None else r[k]) for k in COLS})

# ── 02 세그먼트 (정제본 기준, long format) ─────────────────
def summarize(rs):
    n=len(rs); days=[r["처리일수"] for r in rs if r["처리일수"] is not None]
    sat=[r["만족도"] for r in rs if r["만족도"] is not None]
    rep=sum(1 for r in rs if r["재민원여부"]=="Y")
    return {"건수":n,
            "평균처리일수": round(sum(days)/len(days),1) if days else "",
            "평균만족도": round(sum(sat)/len(sat),2) if sat else "",
            "만족도응답수": len(sat),
            "재민원건수": rep, "재민원율(%)": round(rep/n*100,1)}

seg=[]
for dim,key in [("민원유형","민원유형"),("행정동","행정동"),("접수채널","접수채널"),
                ("연령대","연령대"),("부서","부서"),("처리상태","처리상태")]:
    g=defaultdict(list)
    for r in rows: g[r[key]].append(r)
    for k,v in sorted(g.items(), key=lambda x:-len(x[1])):
        seg.append({"세그먼트구분":dim,"세그먼트":k, **summarize(v)})
# 교차: 민원유형 × 행정동 (건수 8건 이상만)
g=defaultdict(list)
for r in rows: g[(r["민원유형"],r["행정동"])].append(r)
for (t,dg),v in sorted(g.items(), key=lambda x:-len(x[1])):
    if len(v)>=8:
        seg.append({"세그먼트구분":"민원유형×행정동","세그먼트":f"{t} / {dg}", **summarize(v)})
with open(OUT+"02_complaints_segments.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,list(seg[0])); w.writeheader(); w.writerows(seg)

# ── 03 월별 요약 ────────────────────────────────────────────
mon=defaultdict(lambda: {"n":0,"trash":0,"days":[],"open":0,"sat":[],"rep":0})
for r in rows:
    k = r["접수일"].strftime("%Y-%m"); m=mon[k]
    m["n"]+=1
    if r["민원유형"]=="쓰레기 무단투기": m["trash"]+=1
    if r["처리일수"] is not None: m["days"].append(r["처리일수"])
    else: m["open"]+=1
    if r["만족도"] is not None: m["sat"].append(r["만족도"])
    if r["재민원여부"]=="Y": m["rep"]+=1
mrows=[{"월":k,"총민원건수":v["n"],"쓰레기민원건수":v["trash"],
        "평균처리일수":round(sum(v["days"])/len(v["days"]),1),
        "미처리건수":v["open"],
        "평균만족도":round(sum(v["sat"])/len(v["sat"]),2),
        "재민원율(%)":round(v["rep"]/v["n"]*100,1)} for k,v in sorted(mon.items())]
with open(OUT+"03_complaints_monthly.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,list(mrows[0])); w.writeheader(); w.writerows(mrows)

# ── 04 재사용 프롬프트 템플릿 ───────────────────────────────
tmpl=[
 ("B1","데이터 품질검사","공공기관 데이터 분석 보조자","{파일명}","전체 행 수·결측·중복·날짜오류·형식 불일치·이상값 점검","품질 보고서 표 → 수정 원칙 → 사람 확인 3개","원본 삭제 금지, 수정 행은 행번호와 이유 명시"),
 ("B2","현황 KPI 요약","부서장 보고용 KPI 분석가","{정제본}, {세그먼트}","규모·구성·추이 순 KPI 요약, 유형·행정동·채널·상태별 비교","KPI 표 → TOP3 변화 → 세그먼트 비교표 → 결론 3줄","계산 근거 없는 원인 단정 금지"),
 ("B3","원인 후보 TOP3","민원 재발 방지 정책분석 담당자","{세그먼트}","재민원율·평균처리일수 높은 유형·집단과 원인 후보 3개","원인/근거지표/확실성/추가확인 데이터 표","상관관계를 인과관계로 쓰지 말 것"),
 ("B4","3개 시나리오 예측","간부회의용 추세·예측 분석가","{월별요약}","최근 6개월 추세 분석 + 다음 달 보수/기준/낙관 예측","추세 요약 → 예측표 → 차트 2개 기획 → 과장 점검","단일 예측값 금지, 가정과 불확실성 명시"),
 ("B5","기관장 1페이지 보고서","기관장 보고서 작성 기획 담당자","{앞 단계 산출물 전부}","핵심결론·핵심숫자·발견·원인·전망·제안 순 작성","제목 → 요약 3줄 → 지표표 → 원인/전망/제안 → 의사결정 요청 1문장","모든 숫자에 원천파일·계산방법 표시"),
 ("W1","실습별 미니 웹앱","사내 웹앱을 만드는 프론트엔드 파트너","{해당 단계 산출물}","단일 HTML 웹앱 생성, CSV 업로드 → 화면 구성","한국어 UI·단일 파일·반응형","외부 전송 금지, 규칙 임계값 변경 금지"),
 ("W2","통합 대시보드 PRD","사내 업무 도구 프로덕트 오너","{정제본}+{월별요약}","화면 4영역·기능·성공기준·범위 제외 정의","항목별 소제목+불릿, 한 페이지","한 문장 하나의 요구, 모호어 금지"),
]
with open(OUT+"04_prompt_templates.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["코드","단계","[역할]","[데이터]","[지시]","[형식]","[제약]"]); w.writerows(tmpl)

# ── 05 정답키 ──────────────────────────────────────────────
tot=len(rows)
trash_last4 = sum(v["trash"] for k,v in sorted(mon.items())[-4:])
trash_prev4 = sum(v["trash"] for k,v in sorted(mon.items())[-8:-4])
gaon = [r for r in rows if r["행정동"]=="가온동" and r["처리일수"] is not None]
oth  = [r for r in rows if r["행정동"]!="가온동" and r["처리일수"] is not None]
rep_by_type=defaultdict(lambda:[0,0])
for r in rows:
    rep_by_type[r["민원유형"]][1]+=1
    if r["재민원여부"]=="Y": rep_by_type[r["민원유형"]][0]+=1
ans=[
 ("원본 행 수(오염본)", len(allrows)),
 ("중복 제거 후 행 수", tot),
 ("완전 중복", 18), ("ID만 다른 실질 중복", 12),
 ("처리일<접수일 오류", 9), ("처리일수 이상값(999/0/-3)", 7),
 ("행정동 결측", 24), ("부서 결측", 11), ("처리일수 결측(형식)", 15),
 ("날짜 형식 종류", "YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD / YYYY년 MM월 DD일"),
 ("최근 4개월 쓰레기민원", trash_last4), ("직전 4개월 쓰레기민원", trash_prev4),
 ("쓰레기민원 증가율(%)", round((trash_last4/trash_prev4-1)*100,1)),
 ("가온동 평균처리일수", round(sum(r["처리일수"] for r in gaon)/len(gaon),1)),
 ("그 외 평균처리일수", round(sum(r["처리일수"] for r in oth)/len(oth),1)),
 ("재민원율 TOP3 유형", " > ".join(f"{k}({v[0]/v[1]*100:.1f}%)" for k,v in sorted(rep_by_type.items(), key=lambda x:-x[1][0]/x[1][1])[:3])),
 ("함정1", "만족도 결측 38% — 부서별 만족도 비교는 응답수 함께 봐야 함"),
 ("함정2", "온라인 채널 재민원율이 높아 보이나, 쓰레기 민원이 그 채널에 몰린 구성 효과"),
 ("함정3", "민원인연락처 컬럼 — 보고서·대시보드에 절대 노출 금지"),
]
with open(OUT+"05_answer_key_instructor.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["항목","값"]); w.writerows(ans)

print("raw(dirty)", len(allrows), "clean", tot, "seg", len(seg), "months", len(mrows))
for k,v in ans[:17]: print(" ",k,v)
