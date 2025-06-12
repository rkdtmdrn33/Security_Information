import nvdlib
from datetime import datetime, time
from dateutil import tz
import csv
import os

from datetime import datetime, timedelta, timezone
### --- 모듈 추가 --- ###
# pip install nvdlib
# pip install datetime
# dateutil, json

def load_keywords_from_csv(): # keywords.csv load
    keywords = []
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일 기준
    filepath = os.path.join(current_dir, 'csv_data\keywords.csv')
    with open(filepath, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # 첫 줄을 header로 인식
        for row in reader:
            keyword = row.get('keyword', '').strip()
            if keyword:
                keywords.append(keyword)
    return keywords

def get_time(): # UTC 시간 변환
    seoul_tz = tz.gettz('Asia/Seoul')
    utc_tz   = tz.gettz('UTC')
    today_seoul = datetime.now(seoul_tz).date() # 금일 날짜 정보
    start_local = datetime.combine(today_seoul, time(0, 0, 0), tzinfo=seoul_tz) # 당일 00:00 
    end_local   = datetime.combine(today_seoul, time(23, 59, 0), tzinfo=seoul_tz) # 당일 23:59
    start_utc = start_local.astimezone(utc_tz) # UTC로 변환
    end_utc   = end_local.astimezone(utc_tz) # UTC로 변환
    return start_utc, end_utc

def get_cve(): # CVE 데이터 수집
    start_time, end_time = get_time() # UTC 시간 데이터
    # cvssV3Severity HIGH 검색
    cves_high = nvdlib.searchCVE( # CVE 검색
        pubStartDate=start_time, # published-start 시간 설정(UTC)
        pubEndDate=end_time, # published-end 시간 설정(UTC)
        keywordSearch='', # keyword
        cvssV3Severity='HIGH',
        limit=50 # 건수 제한
    )
    # cvssV3Severity CRITICAL 검색  
    cves_critical = nvdlib.searchCVE( # CVE 검색
        pubStartDate=start_time, # published-start 시간 설정(UTC)
        pubEndDate=end_time, # published-end 시간 설정(UTC)
        keywordSearch='', # keyword
        cvssV3Severity='CRITICAL',
        limit=50 # 건수 제한
    )
    
    # HIGH, CRITICAL 동시 호출 불가로 인해 각각 호출 후, 결합
    combined_cves = list(cves_high) + list(cves_critical)

    return combined_cves

def filtered_cve(): # Keywords 기반 CVE 정보 Filtering
    keywords = load_keywords_from_csv()
    cves = get_cve()

    filtered_cves = []

    for cve in cves:
        descriptions = cve.descriptions
        matched_keywords = set()
        
        high_cvss_score = False
        base_score = None

        if hasattr(cve.metrics, 'cvssMetricV31') and cve.metrics.cvssMetricV31: # cvssMetricV31 score >= 9
            try:
                base_score = cve.metrics.cvssMetricV31[0].cvssData.baseScore
                if base_score >= 9.0:
                    high_cvss_score = True
                    matched_keywords.add('Over 9.0')
            except (IndexError, AttributeError, TypeError):
                pass

        for desc in descriptions:
            desc_text = desc.value.lower()

            for keyword in keywords: # matching keywords
                keyword = keyword.lower()
                if keyword in desc_text:
                    matched_keywords.add(keyword)

        if matched_keywords or high_cvss_score:
            filtered_cves.append({
                'matched_keywords': list(matched_keywords),
                'id': cve.id,
                'published': cve.published,
                'lastModified': cve.lastModified,
                'descriptions': cve.descriptions[0].value,
                'cvssMetricv31' : cve.metrics.cvssMetricV31[0].cvssData.baseScore,
                'references' : cve.url,
                'cwe' : [cwe.value for cwe in cve.cwe]
            })
    return filtered_cves

    # 결과 출력
    # for item in filtered_cves:
    #     keywords_str = ','.join(k.upper() for k in item['matched_keywords'])
    #     print("\n======================================================\n")
    #     print(f"Filtered by [{keywords_str}]\n")
    #     print(f"{item['id']}\n")
    #     print(f"published: {item['published']}\n")
    #     print(f"lastModified: {item['lastModified']}\n")
    #     print(f"cvssMetricv31: {item['cvssMetricv31']}\n")
    #     print(f"descriptions: {item['descriptions']}\n")
    #     print(f"references: {item['references']}\n")
    #     print(f"CWE: {item['cwe']}")
    # print(f"\n총 {len(filtered_cves)}개의 CVE가 필터링되었습니다.")    
    # return