import feedparser
import csv
import os
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone

def get_csv_path(filename):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(BASE_DIR, 'csv_data', filename)

def read_feed_urls():
    csv_path = get_csv_path('news_url.csv')
    urls=[]
    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                urls.append(row['url'])
    return urls

def read_keywords():
    csv_path = get_csv_path('news_word.csv')
    keywords = []
    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader=csv.DictReader(csvfile)
            for row in reader:
                keywords.append(row['keyword'])
    return keywords

def read_sent_articles():
    csv_path = get_csv_path('sent_articles.csv')
    sent = set()
    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sent.add((row['site'], row['url']))
    return sent

def save_sent_articles(site_url_list):
    csv_path = get_csv_path('sent_articles.csv')
    file_exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['sites', 'url'])
        if not file_exists:
            writer.writeheader()
        for site, url in site_url_list:
            writer.writerow({'site': site, 'url': url})

def get_site_from_url(url):
    return urlparse(url).netloc

def fetch_all_feeds():
    feed_urls = read_feed_urls()
    all_entries = []
    for feed_url in feed_urls:
        feed = feedparser.parse(feed_url)
        all_entries.extend(feed.entries)
    return all_entries

def filter_by_keywords(entries):
    keywords = read_keywords()
    filtered = []
    for entry in entries:
        title = entry.title
        summary = entry.summary if 'summary' in entry else ''
        content = f"{title} {summary}".lower()
        if any(keyword.lower() in content for keyword in keywords) :
            filtered.append(entry)
    return filtered


def filter_new_articles(entries):
    sent = read_sent_articles()
    new_articles = []
    new_sent = []
    for entry in entries:
        url = entry.link
        site = get_site_from_url(url)
        if (site, url) not in sent:
            new_articles.append({'title': entry.title, 'url': url, 'site': site})
            new_sent.append((site, url))
    return new_articles, new_sent


def is_today_kst(entry):
    KST = timezone(timedelta(hours=9))
    now_kst = datetime.now(KST)
    today_kst = now_kst.date()
    time_struct = None
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        time_struct = entry.updated_parsed
    elif hasattr(entry, 'published_parsed') and entry.published_parsed:
        time_struct = entry.published.parsed
    else:
        time_struct = None
    
    if time_struct:
        entry_dt = datetime(*time_struct[:6], tzinfo=timezone.utc).astimezone(KST)
        return entry_dt.date() == today_kst
    else:
        return False
    
def fetch_all_feeds_today():
    feed_urls = read_feed_urls()
    all_entries = []
    for feed_url in feed_urls:
        feed = feedparser.parse(feed_url)
        today_entries = [entry for entry in feed.entries if is_today_kst(entry)]
        all_entries.extend(today_entries)
    return all_entries
    
def get_final_articles():
    all_entries = fetch_all_feeds_today()
    filtered_entries = filter_by_keywords(all_entries)
    new_articles, new_sent = filter_new_articles(filtered_entries)
    save_sent_articles(new_sent)
    return new_articles


if __name__ == '__main__':
    print("오늘 기사 리스트")
    today_entres = fetch_all_feeds_today()
    for entry in today_entres:
        print(f"{entry.title} ({entry.link})")

    
    print("\n키워드 포함 기사 리스트")
    filtered = filter_by_keywords(today_entres)
    for entry in filtered:
        print(f"{entry.title} ({entry.link})")
    

    print ("\n 중복 아닌 새 기사 리스트")
    new_articles, new_sent = filter_new_articles(filtered)
    for article in new_articles:
        print(f"{article['title']} ({article['url']})")