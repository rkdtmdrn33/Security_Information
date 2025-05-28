import feedparser
from bs4 import BeautifulSoup
import json

### --- 모듈 추가 --- ###
# pip install feedparser
# pip install beautifulsoup4
# json

### --- URL 관리 --- ###
RSS_INFO_URL = [ # SK EYES RSS LINK LIST                
    # FeedBurner 관련
    "http://feeds.feedburner.com/2-spyware/XBaU",
    "http://feeds.feedburner.com/Snort",
    "http://feeds.feedburner.com/darknethackers",
    "http://feeds.feedburner.com/tripwire-state-of-security",
    
    # 구글
    "http://googleprojectzero.blogspot.com/feeds/posts/default",

    # 보안 뉴스
    "http://www.boannews.com/media/news_rss.xml",
    "http://www.boannews.com/media/news_rss.xml?skind=5",

    # 보안 리서치/DB
    "http://www.exploit-db.com/rss.xml",
    "http://www.schneier.com/blog/index.rdf",

    # 안티바이러스 업체 블로그
    "https://antivirussoftwareforpc.blogspot.com/feeds/posts/default?alt=rss",
    "https://asec.ahnlab.com/ko/feed/",
    "https://blog.avast.com/rss.xml",
    "https://blog.avira.com/feed",
    "https://blog.zonealarm.com/feed",
    "https://blogs.quickheal.com/feed/",
    "https://pandasecurity.com/mediacenter/feed",
    "https://webroot.com/blog/feed",

    # 보안 미디어/포럼
    "https://feeds.feedburner.com/securityweek",
    "https://grahamcluley.com/feed/",
    "https://isarc.tachyonlab.com/rss",
    "https://isc.sans.edu/rssfeed_full.xml",
    "https://kaspersky.co.uk/blog/feed", 
    "https://threatpost.com/feed/",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.dailysecu.com/rss/allArticle.xml",
    "https://www.darkreading.com/rss.xml",
    "http://krebsonsecurity.com/feed/",

    # NIST
    "https://www.nist.gov/blogs/cybersecurity-insights/rss.xml",
    "https://www.nist.gov/news-events/news/rss.xml",

    # Reddit
    "https://reddit.com/r/antivirus/.rss",

    # Malware.news
    "https://malware.news/c/forensics.rss",
    "https://malware.news/c/malwareanalysis.rss",
    "https://malware.news/c/news.rss",
]

RSS_INFO_KR_URL = [ # 국내 보안 사이트
    "https://www.dailysecu.com/rss/allArticle.xml", # 데일리시큐
    "https://knvd.krcert.or.kr/rss/securityInfo.do", # KNVD
    "https://knvd.krcert.or.kr/rss/securityNotice.do", # KNVD
    "https://www.boho.or.kr/kr/rss.do?bbsId=B0000133", # KISA 인터넷 보호나라
    "http://www.boannews.com/media/news_rss.xml?mkind=1", # 보안뉴스
    "http://www.boannews.com/media/news_rss.xml?mkind=2", # 보안뉴스
]


def print_feed(): # feed 출력 부분
    return

def filter_feed(): # feed 필터링 부분
    return 

def get_feed(): # feed 요청 부분
    get_feed_data = [] # 결과값 
    for index, link in enumerate(RSS_INFO_URL): # RSS links 순회
        feed_data = feedparser.parse(link)
        if not feed_data.entries: # feed 0건일 경우
            print(f"index:{index+1} : {link} is No Entries")
        else:
            for entry in feed_data.entries: # feed entries 순회
                # "Column" 값이 없으면 "N/A" 반환 (예외처리), JSON 데이터 참고
                feed_title = entry.get("title", "N/A") 
                feed_link = entry.get("link", "N/A")
                feed_update = entry.get("updated", "N/A")
                feed_summary = entry.get("summary", "N/A")

                if feed_summary != "N/A": # summary가 HTML 형식으로 받아올 경우, 문자열 추출
                    soup = BeautifulSoup(feed_summary, "html.parser") 
                    feed_summary = soup.get_text(separator=" ", strip=True)
                
                get_feed_data.append({ # 딕셔너리 형태로 저장
                    "feed_title": feed_title,
                    "feed_link": feed_link,
                    "feed_update": feed_update,
                    "feed_summary": feed_summary
                })

                # 임시 출력
                print(f"feed_title : {feed_title}")
                print(f"feed_link : {feed_link}")
                print(f"feed_update : {feed_update}")
                print(f"feed_summary: {feed_summary}")
                print(f"===================================================")
    return get_feed_data

def main():
    example = get_feed()
    return 

if __name__ == "__main__":
    main()