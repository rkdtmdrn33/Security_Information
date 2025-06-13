import smtplib
from datetime import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# import py code
import news_info.collect_news as collect_news

current_time = datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M")

with open('config.json', 'r', encoding='utf-8-sig') as f:
  config = json.load(f)

SMTP_HOST = config['SMTP_HOST']
SMTP_PORT = config['SMTP_PORT']
USERNAME = config['USERNAME']
PASSWORD = config['PASSWORD']
FROM_ADDR = config['FROM_ADDR']
TO_ADDRS = config['TO_ADDRS']
SUBJECT = "[NEWS Announce] NEWS Alert (Last Update)"


msg = MIMEMultipart()
msg['From'] = FROM_ADDR
msg['To'] = ', '.join(TO_ADDRS)
msg['Subject'] = SUBJECT

# NEWS HTML

def news_html():
  news_results = collect_news.get_final_articles()
  news_rows = []
  for item in news_results:
      site_change = item['site'].replace('www.','')
      news_rows.append(f"""
      <tr>
        <td style="border:1px solid #000000;padding:8px;font-size:13px;">{item['title']}</td>
        <td style="border:1px solid #000000;padding:8px;font-size:13px;">
          <span style="color:#333;text-decoration:none;">{site_change}</span>
        </td>
        <td style="border:1px solid #000000;padding:8px;font-size:13px;">
          <a href="{item['url']}">{item['url']}</a>
        </td>
      </tr>
      """)

  html_body = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>PoC</title>
</head>
<body style="margin:0;padding:20px;font-family:Arial, sans-serif;font-size:14px;color:#333;">
  <p style="font-size:20px;">NEWS 기사 확인</p>
  <p style="font-size:13px;">- 총 업데이트 뉴스: {len(news_rows)}건</p>
  <p style="font-size:13px;">- 업데이트 기준: {formatted_time}</p>

  <table style="width:100%;border-collapse:collapse;border:1px solid #000000;">
    <thead>
      <tr>
        <th style="border:1px solid #000000;background:#E7E6E6;padding:8px;text-align:center;">NEWS TITLE</th>
        <th style="border:1px solid #000000;background:#E7E6E6;padding:8px;text-align:center;">SITE</th>
        <th style="border:1px solid #000000;background:#E7E6E6;padding:8px;text-align:center;">URL</th>
      </tr>
    </thead>
    <tbody>
      {''.join(news_rows)}
    </tbody>
  </table>
</body>
</html>
  """
  return html_body


result = news_html()
html_part = MIMEText(result, 'html', _charset='utf-8')
msg.attach(html_part)

# 3) SMTP 서버에 연결해서 메일 발송
with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.ehlo()
    smtp.starttls()               # TLS 암호화 시작
    smtp.login(USERNAME, PASSWORD)
    smtp.send_message(msg)

print("메일을 성공적으로 보냈습니다.")