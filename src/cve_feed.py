import nvdlib
from datetime import datetime, time
from dateutil import tz
import json

### --- 모듈 추가 --- ###
# pip install nvdlib
# pip install datetime
# dateutil, json

### --- URL 관리 --- ###
RSS_CVE_URL = [ # CVE RSS link list
    # CVEFeed.io == https://cvefeed.io/rssfeed/
    "https://cvefeed.io/rssfeed/latest.xml", # Latest CVE Feed
    "https://cvefeed.io/rssfeed/latest.atom", # Latest CVE Feed:
    "https://cvefeed.io/rssfeed/severity/high.xml", # Latest High and Critical Severity CVE Feed:
    "https://cvefeed.io/rssfeed/severity/high.atom", # Latest High and Critical Severity CVE Feed:
    "https://cvefeed.io/rssfeed/newsroom.xml", # Cyber NewsRoom Vulnerability Feed:
    "https://cvefeed.io/rssfeed/newsroom.atom", # Cyber NewsRoom Vulnerability Feed:
]

CVE_API_URL = [ # API 조회만 가능한 site
    # NVD
    "https://nvd.nist.gov/vuln/search"

    # CVE Details
    "https://www.cvedetails.com/documentation/rss-feeds",

    # OpenCVE
    "https://docs.opencve.io/api/cve/",

    # cve-search (CIRCL)
    "https://www.cve-search.org/api/",
]

def get_time(): # UTC 시간 변환
    seoul_tz = tz.gettz('Asia/Seoul')
    utc_tz   = tz.gettz('UTC')
    today_seoul = datetime.now(seoul_tz).date() # 금일 날짜 정보
    start_local = datetime.combine(today_seoul, time(0, 0, 0), tzinfo=seoul_tz) # 당일 00:00 
    end_local   = datetime.combine(today_seoul, time(23, 59, 0), tzinfo=seoul_tz) # 당일 23:59
    start_utc = start_local.astimezone(utc_tz) # UTC로 변환
    end_utc   = end_local.astimezone(utc_tz) # UTC로 변환
    return start_utc, end_utc

def get_cve():
    start_time, end_time = get_time() # UTC 시간 데이터
    # 임시 CVE 검색
    cves = nvdlib.searchCVE( # CVE 검색
        pubStartDate=start_time, # published-start 시간 설정(UTC)
        pubEndDate=end_time, # published-end 시간 설정(UTC)
        keywordSearch='', # keyword

        # CVSS v2: 2007년에 발표된 첫 번째 표준으로
        # CVSS v3.1: : 2019년 6월 발표된 v3.0의 개선판
        # CVSS v4.0: : 2023년 11월에 발표된 최신 버전
        # Low	: 0.0 – 3.9
        # Medium: 4.0 – 6.9
        # High	: 7.0 – 10.0
        cvssV3Severity='HIGH',        
        limit=50 # 건수 제한
    )
    # 임시 결과 출력
    for cve in cves:
        print(f"{cve.id}\n")
        print(f"published: {cve.published}\n")
        print(f"descriptions: {cve.descriptions[0].value}\n")
        print(f"cvssMetricv31: {cve.metrics.cvssMetricV31[0].cvssData.baseScore}")
        print("--------------------------------------------")
    return

def main():
    cve = get_cve()
    return 

if __name__ == "__main__":
    main()