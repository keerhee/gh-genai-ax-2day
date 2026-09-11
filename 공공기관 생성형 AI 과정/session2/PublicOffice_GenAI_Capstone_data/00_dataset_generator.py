# -*- coding: utf-8 -*-
"""캡스톤 — 어린이 보행안전 공백지도 (Track B 오프라인 스냅샷)
   실제 공개데이터(전국CCTV표준데이터·전국어린이보호구역표준데이터·주민등록 인구)의
   컬럼 표기를 모사한 합성 데이터. 실제 파일과 컬럼명이 다를 수 있으므로
   1단계에서 반드시 헤더를 읽고 매핑하는 것을 전제로 한다."""
import csv, random, math, datetime as dt
from collections import defaultdict
random.seed(20260904)
OUT="/home/claude/pub_cap/data/input/"

DONG={  # 중급 과정과 동일한 가상 지명 (한빛구)
 "가온동":dict(pop=38200,kid=3900,hh=17400,area=2.9,lat=37.5520,lon=127.0480),
 "나래동":dict(pop=27600,kid=3100,hh=11800,area=3.4,lat=37.5585,lon=127.0562),
 "다솜동":dict(pop=14900,kid=2050,hh= 7300,area=1.6,lat=37.5462,lon=127.0605),
 "라온동":dict(pop=31500,kid=4400,hh=13900,area=4.1,lat=37.5641,lon=127.0421),
 "마루동":dict(pop= 9800,kid= 610,hh= 5100,area=1.2,lat=37.5498,lon=127.0344),
 "바다동":dict(pop=22400,kid=2600,hh= 9600,area=2.7,lat=37.5610,lon=127.0669),
 "새벽동":dict(pop=18700,kid=1750,hh= 8200,area=2.2,lat=37.5443,lon=127.0512),
}
def jit(v,s): return round(v+random.gauss(0,s),6)

# ── 1) 어린이보호구역 (수요지점) ─────────────────────────────
KIND=["초등학교","유치원","어린이집","학원가"]
ZONE_N={"가온동":6,"나래동":5,"다솜동":6,"라온동":6,"마루동":2,"바다동":4,"새벽동":3}
zones=[]; zi=1
for dg,k in ZONE_N.items():
    d=DONG[dg]
    for _ in range(k):
        kind=random.choices(KIND,[38,24,26,12])[0]
        zones.append({"연번":zi,"시설명":f"한빛{['','제2','제3','새','한','달','별'][zi%7]}{ {'초등학교':'초등학교','유치원':'유치원','어린이집':'어린이집','학원가':'학원가'}[kind] }".replace("한빛한빛","한빛"),
          "시설종류":kind,"소재지도로명주소":f"세종특별자치시 한빛구 {dg} {random.randint(1,40)}로 {random.randint(1,90)}",
          "행정동":dg,"위도":jit(d["lat"],0.0028),"경도":jit(d["lon"],0.0028),
          "관리기관명":"한빛구청","보호구역지정연도":random.choice([2012,2015,2018,2019,2021,2023]),
          "보호구역내CCTV설치대수":0,   # 아래에서 근접 CCTV로 채우지 않는다(의도: 미기입 필드)
          "데이터기준일자":"2026-08-31","제공기관명":"한빛구청"})
        zi+=1
# 사고 다발 지점과 겹치도록 다솜동 3곳을 특정 좌표로 고정
fix=[("다솜동",37.5458,127.0598),("다솜동",37.5469,127.0613),("다솜동",37.5455,127.0589)]
di=[i for i,z in enumerate(zones) if z["행정동"]=="다솜동"][:3]
for i,(dg,la,lo) in zip(di,fix):
    zones[i]["위도"]=la; zones[i]["경도"]=lo

# ── 2) CCTV (공급) ────────────────────────────────────────
# 함정: 가온동은 대수가 많지만 설치목적이 '교통단속'·'주정차단속' 위주 → 보호 커버로 세면 안 됨
CCTV_N={"가온동":46,"나래동":22,"라온동":24,"바다동":16,"새벽동":13,"다솜동":9,"마루동":10}
PURPOSE=["생활방범","어린이보호","교통단속","주정차단속","쓰레기단속","재난재해"]
cctv=[]; ci=1
for dg,k in CCTV_N.items():
    d=DONG[dg]
    for _ in range(k):
        if dg=="가온동": p=random.choices(PURPOSE,[16,4,34,30,10,6])[0]
        elif dg in ("다솜동","마루동"): p=random.choices(PURPOSE,[34,8,14,18,18,8])[0]
        else: p=random.choices(PURPOSE,[32,18,18,16,10,6])[0]
        yr=random.choice([2014,2015,2016]) if (dg=="가온동" and random.random()<0.55) else random.choice([2019,2020,2021,2023,2024,2025])
        cctv.append({"연번":ci,"관리기관명":"한빛구청",
          "소재지도로명주소":f"세종특별자치시 한빛구 {dg} {random.randint(1,40)}로 {random.randint(1,90)}",
          "행정동":dg,"설치목적구분":p,"카메라대수":random.choice([1,1,1,2,2,4]),
          "카메라화소수":random.choice([41,41,130]) if yr<2017 else random.choice([200,400,800]),
          "촬영방면정보":random.choice(["도로","교차로","이면도로","공원","주차장","통학로"]),
          "보관일수":30,"설치년월":f"{yr}-{random.randint(1,12):02d}",
          "WGS84위도":jit(d["lat"],0.0030),"WGS84경도":jit(d["lon"],0.0030),
          "데이터기준일자":"2026-08-31","제공기관명":"한빛구청"})
        ci+=1
# 다솜동 3개 보호구역 주변 150m에는 CCTV를 두지 않는다(공백 확정)
def hav(a,b,c,d):
    R=6371000.0; p1,p2=math.radians(a),math.radians(c)
    dp=math.radians(c-a); dl=math.radians(d-b)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))
cctv=[c for c in cctv if not any(hav(c["WGS84위도"],c["WGS84경도"],la,lo)<170 for _,la,lo in fix)]
# 마루동(아동 610명·사고 0건)의 보호구역 옆에 생활방범 CCTV를 붙여 둔다
#  → 수요는 낮은데 시설이 몰린 '⑤ 재배치 검토' 사례를 의도적으로 만든다
mid=max(c["연번"] for c in cctv)
_r2=random.Random(777)          # 주 난수열을 건드리지 않도록 별도 스트림 사용
_maru=[x for x in zones if x["행정동"]=="마루동"]
for z in _maru[:1]:             # 두 곳 중 한 곳에만 붙인다 → 나머지 한 곳은 '④ 관찰'
    for k in range(2):
        mid+=1
        cctv.append({"연번":mid,"관리기관명":"한빛구청",
          "소재지도로명주소":f"세종특별자치시 한빛구 마루동 {_r2.randint(1,40)}로 {_r2.randint(1,90)}",
          "행정동":"마루동","설치목적구분":"생활방범","카메라대수":2,"카메라화소수":_r2.choice([200,400]),
          "촬영방면정보":_r2.choice(["통학로","이면도로"]),"보관일수":30,
          "설치년월":f"{_r2.choice([2022,2023,2024])}-{_r2.randint(1,12):02d}",
          "WGS84위도":round(z["위도"]+_r2.gauss(0,0.0005),6),
          "WGS84경도":round(z["경도"]+_r2.gauss(0,0.0005),6),
          "데이터기준일자":"2026-08-31","제공기관명":"한빛구청"})

# ── 3) 행정동 인구 ────────────────────────────────────────
pop=[{"행정기관":f"세종특별자치시 한빛구 {dg}","행정동":dg,"총인구수":d["pop"],
      "0~12세인구수":d["kid"],"세대수":d["hh"],"면적(km2)":d["area"],
      "중심위도":d["lat"],"중심경도":d["lon"],"기준연월":"2026-08"} for dg,d in DONG.items()]

# ── 4) 어린이 보행사고 (수요 신호) ────────────────────────
acc=[]; ai=1
ACC_N={"다솜동":7,"가온동":6,"라온동":4,"나래동":3,"새벽동":2,"바다동":2,"마루동":0}
for dg,k in ACC_N.items():
    d=DONG[dg]
    for _ in range(k):
        if dg=="다솜동" and ai%2==1:
            _,la,lo=random.choice(fix); la=jit(la,0.0004); lo=jit(lo,0.0004)
        else:
            la=jit(d["lat"],0.0025); lo=jit(d["lon"],0.0025)
        acc.append({"연번":ai,"사고유형":"어린이 보행자 사고","행정동":dg,
          "발생연도":random.choice([2023,2024,2025]),"사상자수":random.choice([1,1,1,2]),
          "심각도":random.choices(["경상","중상","사망"],[76,22,2])[0],
          "위도":la,"경도":lo,"시간대":random.choice(["07-09","13-15","15-17","17-19"])})
        ai+=1

def w(name,rows):
    with open(OUT+name,"w",newline="",encoding="utf-8-sig") as f:
        wr=csv.DictWriter(f,list(rows[0])); wr.writeheader(); wr.writerows(rows)
w("child_safety_zones.csv",zones)
w("cctv.csv",cctv)
w("population_by_dong.csv",pop)
w("pedestrian_accidents.csv",acc)

# ── 사업조건 ──────────────────────────────────────────────
open(OUT+"project_conditions.txt","w",encoding="utf-8").write("""[사업 개요]
사업명 : 어린이 보행안전 취약지점 개선 시범사업
예산   : 50,000,000원 (총액 초과 불가, 당해연도 집행)
기간   : 2026년 10월 ~ 12월
소관   : 안전총괄과 (협조: 교통행정과, 도시재생과)

[집행 단가]
생활방범 CCTV 신설(어린이보호구역용)   3,500,000원 / 대
기존 CCTV 화소 개선·방향 조정          1,200,000원 / 대
음성안내 보행신호기                     2,500,000원 / 개소
옐로카펫(대기공간 표시)                   800,000원 / 개소
과속방지턱 설치                         1,200,000원 / 개소
보도 조명(LED) 개선                     2,000,000원 / 개소
무인 교통단속 장비                     18,000,000원 / 대
등하교 안전지도 인력                    1,800,000원 / 인·월

[제약 조건]
1. CCTV 신설은 개인정보 영향평가와 주민 의견수렴에 6주가 걸린다. 연내 최대 5대.
2. 무인 교통단속 장비는 경찰청 협의가 필요하며 연내 설치는 최대 1대.
3. 등하교 안전지도 인력은 최소 2개월 연속 배치해야 효과 측정이 가능하다.
4. 한 개소에 세 가지 이상의 조치를 중복 배정하지 않는다.
5. 한 개 행정동에 예산의 40%를 초과 배정하지 않는다.
6. 시설 신설만으로 구성된 안은 제출할 수 없다. 운영·인력 대안을 1개 이상 포함한다.

[의사결정 요청]
- 5천만원 범위에서 성격이 다른 포트폴리오 3안
- 각 안의 비용·기대효과 가능성·부작용·추가 확인정보
- 최우선 개선 지점 상위 5곳과 그 근거
""")

# ── 정답키 ────────────────────────────────────────────────
PROTECT={"생활방범","어린이보호"}
def cover(z, r, only_protect):
    n=0
    for c in cctv:
        if only_protect and c["설치목적구분"] not in PROTECT: continue
        if hav(z["위도"],z["경도"],c["WGS84위도"],c["WGS84경도"])<=r: n+=c["카메라대수"]
    return n
gap_all=[z for z in zones if cover(z,150,False)==0]
gap_pro=[z for z in zones if cover(z,150,True)==0]
accnear=lambda z,r=200: sum(1 for a in acc if hav(z["위도"],z["경도"],a["위도"],a["경도"])<=r)
prio=sorted(zones,key=lambda z:(-(0 if cover(z,150,True) else 1)*1000 - accnear(z)*100 - DONG[z["행정동"]]["kid"]/100))
gap_by_dong=defaultdict(int)
for z in gap_pro: gap_by_dong[z["행정동"]]+=1
# 조치 유형 5분류 (웹앱과 동일한 규칙: 반경150m · 목적 생활방범/어린이보호 · 2017년 이후 · 130만화소 이상 · 수요 아동지수 0.30)
kidmax=max(d["kid"] for d in DONG.values())
def classify(z):
    near=[c for c in cctv if hav(z["위도"],z["경도"],c["WGS84위도"],c["WGS84경도"])<=150]
    ok=[c for c in near if c["설치목적구분"] in PROTECT]
    usable=[c for c in ok if int(c["설치년월"][:4])>=2017 and c["카메라화소수"]>=130]
    ev=accnear(z)
    kid=DONG[z["행정동"]]["kid"]/kidmax
    demand = ev>0 or kid>=0.30
    if demand:
        if not usable and not near: a="① 신설"
        elif not usable:            a="② 개선"
        elif ev>0:                  a="③ 운영·인력"
        else:                       a="적정"
    else:
        a="⑤ 재배치 검토" if len(usable)>=2 else "④ 관찰"
    return a, ev, round(kid,2), len(usable), len(near)
cls=defaultdict(int); rows_cls=[]
for z in zones:
    a,ev,kid,u,nn=classify(z); cls[a]+=1
    rows_cls.append((z["시설명"],z["행정동"],a,ev,kid,u,nn, round(ev*20+kid*40,1) if a.startswith(("①","②","③")) else ""))
rows_cls.sort(key=lambda r:-(r[7] if r[7]!="" else -1))
with open("/home/claude/pub_cap/data/action_type_answer_instructor.csv","w",newline="",encoding="utf-8-sig") as f:
    wr=csv.writer(f); wr.writerow(["시설명","행정동","조치유형","반경200m사건","아동지수","쓸수있는시설","전체시설","긴급도"]); wr.writerows(rows_cls)

ans=[
 ("어린이보호구역 수",len(zones)),
 ("조치유형 ① 신설",cls["① 신설"]),("조치유형 ② 개선",cls["② 개선"]),
 ("조치유형 ③ 운영·인력",cls["③ 운영·인력"]),("적정",cls["적정"]),
 ("조치유형 ④ 관찰",cls["④ 관찰"]),("조치유형 ⑤ 재배치 검토",cls["⑤ 재배치 검토"]),
 ("긴급도 상위 5", " > ".join(f"{r[0]}({r[1]}·{r[2]})" for r in rows_cls[:5])),("CCTV 수",len(cctv)),("보행사고 수",len(acc)),
 ("미커버(반경150m, 목적 무관)",len(gap_all)),
 ("미커버(반경150m, 생활방범·어린이보호만)",len(gap_pro)),
 ("함정 1 — 설치목적 필터","가온동 CCTV 46대 중 다수가 교통·주정차 단속. 목적을 안 거르면 가온동이 '충분'으로 보인다"),
 ("목적 필터 전후 미커버 차이",f"{len(gap_all)}곳 → {len(gap_pro)}곳"),
 ("동별 미커버(목적필터)", " · ".join(f"{k} {v}" for k,v in sorted(gap_by_dong.items(),key=lambda x:-x[1]))),
 ("함정 2 — 인구 가중","마루동은 0~12세 610명뿐. 미커버 수만 보면 상위, 아동 가중 시 하위"),
 ("함정 3 — 사고 이력 결합","다솜동 3개 보호구역은 반경 200m 내 보행사고와 겹침 → 최우선"),
 ("최우선 후보 상위 5", " > ".join(f"{z['시설명']}({z['행정동']})" for z in prio[:5])),
 ("예산 함정","CCTV 신설은 연내 최대 5대(1,750만원). 5천만원 전액 CCTV 배정 불가. 운영·인력 대안 1개 이상 필수"),
 ("좌표 주의","가상 좌표. 실제 지도 타일 위에 올리면 위치가 맞지 않는다. Track A에서는 실제 데이터로 교체"),
]
with open("/home/claude/pub_cap/data/answer_key_instructor.csv","w",newline="",encoding="utf-8-sig") as f:
    wr=csv.writer(f); wr.writerow(["항목","값"]); wr.writerows(ans)
for k,v in ans: print(" ",k,"=",v)
