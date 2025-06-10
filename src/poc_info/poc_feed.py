from datetime import datetime, timedelta
import requests
import json
import re

### --- 모듈 추가 --- ###
# pip install requests
# dateutil, json

### --- URL 관리 --- ###
GITHUB_API_URL = "https://api.github.com/search/repositories" # GITHUB_API_URL
# https://github.com/search?q=PoC+CVE-2025&type=repositories # WEB Search

## --- Keywords --- ###
filter_keywords = [
    "apache","F5","Mcafee","Arbor","Sourcefire","Forti","Juniper","Junos","Symantec","Oracle","Mysql","Openvpn","Splunk","Cisco","openssl","router","D-Link","spring","vmware","wi-fi","wifi","bind","PostgreSQL","FreeType","musl libc","curl","GNU","Redis","google","undertow","php","glibc","cups","runc","Jenkins","python","linux","firefox","squid","lighttpd","TLS","Flatpak","pgAdmin","Tenda"
]

def get_poc():
    poc_data = []

    keyword = "PoC CVE-2025-", # 검색 키워드 (name,full_name,description)
    # date_str = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d') # 금일 날짜
    since_date = None, # 날짜(2025-05-30)

    # sort 옵션
    # stars              : 별(즐겨찾기) 기준으로 정렬                            
    # fork               : fork 개수 기준으로 정렬
    # help-wanted-issues : open-issue 중, help-wanted 기준으로 정렬                        
    # updated            : 최근 업데이트 시점 기준으로 정렬
    sort = "updated",

    # order 옵션
    # desc : 내림차순 정렬
    # asc : 오름차순 정렬
    order = "desc", # 정렬 순서

    per_page = 100, # 한번에 가져올 리포지토리 개수
    page = 1, # 페이지 번호
    github_token = None # 깃허브 tokken (무의미)

    # GitHub Search API 검색 쿼리 필수 (query string)
    # query = f"{keyword} in:name,description,readme updated:>={since_date}"
    query = f"{keyword} in:name,description,readme"
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
        "page": page
    }

    headers ={
        "Accept": "aaplication/vnd.github.v3+json"
    }

    response = requests.get(GITHUB_API_URL, headers=headers, params=params)
    if response.status_code != 200:
        print("no data")
        requests.raise_for_status() # 4xx ~ 5xx Error Code 예외처리
    else:
        poc_json = response.json()
        github_items = poc_json.get("items") or "N/A"

        for index in github_items:
            github_name = index.get("name") or "N/A" # NAME
            github_descriptions = index.get("description") or "N/A" # DESCRIPTION
            github_url = index.get("html_url") or "N/A" # URL
            github_updated_at = index.get("updated_at") or "N/A" # UPDATED

            poc_data.append({
                "poc_name": github_name,
                "poc_descriptions": github_descriptions,
                "poc_url": github_url,
                "poc_updated": github_updated_at
            })

        # with open("PoC.json", "w", encoding="utf-8") as f:
        #     json.dump(poc_json, f,  indent=4, ensure_ascii=False)
    return poc_data

def filter_poc(poc_data): # feed 필터링 부분
    cve_pattern = re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.IGNORECASE) # CVE형식 추출
    poc_result = []

    for index in poc_data:
        poc_descriptions = index["poc_descriptions"]
        matches = cve_pattern.findall(poc_descriptions) # CVE 추출
        
        if not matches:
            pass
        else:
            poc_result.append({
                "poc_cve": matches,
                "poc_name": index["poc_name"],
                "poc_descriptions": index["poc_descriptions"],
                "poc_url": index["poc_url"],
                "poc_updated": index["poc_updated"],
            })
            
    return poc_result

def poc_main():
    poc_data = get_poc()
    result = filter_poc(poc_data)
    return result
