import nvdlib
from datetime import datetime, time
from dateutil import tz
import csv
import json
import os

from datetime import datetime, timedelta, timezone
### --- 모듈 추가 --- ###
# pip install nvdlib
# pip install datetime
# dateutil, json

def load_keywords_from_csv(current_dir):
    keywords = []
    filepath = os.path.join(current_dir, 'keywords.csv')
    with open(filepath, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # 첫 줄을 header로 인식
        for row in reader:
            keyword = row.get('keyword', '').strip()
            if keyword:
                keywords.append(keyword)
    return keywords

def load_excluded_patterns_from_csv(current_dir):
    filepath = os.path.join(current_dir, 'exception.csv')
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row['pattern'].strip().lower() for row in reader if row.get('pattern')]

def load_checked_cves(current_dir):
    """이미 처리된 CVE 번호 로딩"""
    filepath = os.path.join(current_dir, 'cve_check.csv')

    if not os.path.exists(filepath):
        return set()
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return {row['cve_id'] for row in reader if 'cve_id' in row}
    
def append_new_cve(cve_id, current_dir):
    """새로운 CVE 번호를 CSV에 추가"""
    filepath = os.path.join(current_dir, 'cve_check.csv')

    file_exists = os.path.exists(filepath)
    
    with open(filepath, mode='a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['cve_id'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({'cve_id': cve_id})
    
def is_excluded(text, exception):
    """특정 텍스트가 제외 대상 문자열을 포함하는지 확인"""
    return any(pattern in text for pattern in exception)

def get_time(): # UTC 시간 변환
    seoul_tz = tz.gettz('Asia/Seoul')
    utc_tz   = tz.gettz('UTC')
    today_seoul = datetime.now(seoul_tz).date() # 금일 날짜 정보
    start_local = datetime.combine(today_seoul, time(0, 0, 0), tzinfo=seoul_tz) # 당일 00:00 
    end_local   = datetime.combine(today_seoul, time(23, 59, 0), tzinfo=seoul_tz) # 당일 23:59
    start_utc = start_local.astimezone(utc_tz) # UTC로 변환
    end_utc   = end_local.astimezone(utc_tz) # UTC로 변환
    return start_utc, end_utc

    # now = datetime.now(timezone.utc)
    # # 어제 00:00:00 ~ 어제 23:59:59 UTC
    # start_time = datetime(year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc) - timedelta(days=1)
    # end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
    # return start_time, end_time

def get_cve():
    start_time, end_time = get_time() # UTC 시간 데이터
    # 임시 CVE 검색
    cves_high = nvdlib.searchCVE( # CVE 검색
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

    cves_critical = nvdlib.searchCVE( # CVE 검색
        pubStartDate=start_time, # published-start 시간 설정(UTC)
        pubEndDate=end_time, # published-end 시간 설정(UTC)
        keywordSearch='', # keyword
        # CVSS v2: 2007년에 발표된 첫 번째 표준으로
        # CVSS v3.1: : 2019년 6월 발표된 v3.0의 개선판
        # CVSS v4.0: : 2023년 11월에 발표된 최신 버전
        # Low	: 0.0 – 3.9
        # Medium: 4.0 – 6.9
        # High	: 7.0 – 10.0
        cvssV3Severity='CRITICAL',
        limit=50 # 건수 제한
    )
    
    combined_cves = list(cves_high) + list(cves_critical)

    return combined_cves

def filtering(keywords, exception, cve_check):
    cves = get_cve()

    filtered_cves = []

    for cve in cves:
        cve_id = cve.id
        if cve_id in cve_check:
            continue

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

            if is_excluded(desc_text, exception):
                continue

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
                'references' : [reference.url for reference in cve.references],
                'cwe' : [cwe.value for cwe in cve.cwe]
            })

    # 결과 출력
    for item in filtered_cves:
        keywords_str = ','.join(k.upper() for k in item['matched_keywords'])
        print("\n======================================================\n")
        print(f"Filtered by [{keywords_str}]\n")
        print(f"{item['id']}\n")
        print(f"published: {item['published']}\n")
        print(f"lastModified: {item['lastModified']}\n")
        print(f"cvssMetricv31: {item['cvssMetricv31']}\n")
        print(f"descriptions: {item['descriptions']}\n")
        print(f"references: {item['references']}\n")
        print(f"CWE: {item['cwe']}")

    print(f"\n총 {len(filtered_cves)}개의 CVE가 필터링되었습니다.")    

    return [new_cve['id'] for new_cve in filtered_cves]

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일 기준

    # json_filename = os.path.join(current_dir, 'cve_data.json')
    # with open(json_filename, 'r', encoding='utf-8') as f:
    #     cves = json.load(f)

    # txt_filename = os.path.join(current_dir, 'keywords.txt')
    # with open(txt_filename, 'r', encoding='utf-8') as f:
    #     keywords = [line.strip() for line in f if line.strip()]

    keywords = load_keywords_from_csv(current_dir)
    exception = load_excluded_patterns_from_csv(current_dir)
    cve_check = load_checked_cves(current_dir)
    
    new_cves = filtering(keywords, exception, cve_check)

    for i in range(len(new_cves)):
        append_new_cve(new_cves[i], current_dir)

    return 

if __name__ == "__main__":
    main()