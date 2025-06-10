import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# import py code
import cve_info.filtered_cve as filtered_cve
import news_info.collect_news as collect_news
import poc_info.poc_feed as poc_feed

with open('smtp.json', 'r', encoding='utf-8') as json_file:
    smtp_data = json.load(json_file)
    
# SMTP 서버 설정
SMTP_HOST = ""
SMTP_PORT = ""
USERNAME = ""
PASSWORD = ""

# 메일 기본 정보
FROM_ADDR = ""
TO_ADDRS = ""
SUBJECT = ""


# 1) MIMEMultipart 객체 생성 (본문+첨부)
msg = MIMEMultipart()
msg['From'] = FROM_ADDR
msg['To'] = ', '.join(TO_ADDRS)
msg['Subject'] = SUBJECT

# NEWS HTML

# CVE HTML
cve_result = filtered_cve.filtered_cve()
cve_rows = []
for item in cve_result:
    cve_rows.append(f"""
    <tr>
      <td style="font-size:12px;">{item['id']}</td>
      <td style="font-size:12px;">{item['published']}</td>
      <td style="font-size:12px;">{item['descriptions']}</td>
      <td style="font-size:12px;">
        <a href="{item['references']}" style="font-size:12px;">{item['references']}</a>
      </td>
    </tr>
    """)

# POC HTML
poc_result = poc_feed.poc_main()
poc_rows = []
for item in poc_result:
    poc_rows.append(f"""
    <tr>
      <td style="font-size:12px;">{item['poc_name']}</td>
      <td style="font-size:12px;">{item['poc_updated']}</td>
      <td style="font-size:12px;">{item['poc_descriptions']}</td>
      <td style="font-size:12px;">
        <a href="{item['poc_url']}" style="font-size:12px;">{item['poc_url']}</a>
      </td>
    </tr>
    """)

html_body = f"""
<html>
  <head>
    <meta charset="utf-8">
  </head>
  <body>
    <p style="font-size:15px;">CVE 탐지 결과 목록:</p>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
      <thead>
        <tr>
          <th style="font-size:12px; font-weight:bold;">CVE</th>
          <th style="font-size:12px; font-weight:bold;">날짜</th>
          <th style="font-size:12px; font-weight:bold;">설명</th>
          <th style="font-size:12px; font-weight:bold;">URL</th>
        </tr>
      </thead>
      <tbody>
        {''.join(cve_rows)}
      </tbody>
    </table>

    <br>
    <br>

    <p style="font-size:15px;">보안 뉴스:</p>
    <p style="font-size:15px;">None</p>
    
    <br>
    <br>
    
    <p style="font-size:15px;">PoC 탐지 결과 목록:</p>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
      <thead>
        <tr>
          <th style="font-size:12px; font-weight:bold;">CVE</th>
          <th style="font-size:12px; font-weight:bold;">날짜</th>
          <th style="font-size:12px; font-weight:bold;">설명</th>
          <th style="font-size:12px; font-weight:bold;">URL</th>
        </tr>
      </thead>
      <tbody>
        {''.join(poc_rows)}
      </tbody>
    </table>
  </body>
</html>
"""

html_part = MIMEText(html_body, 'html', _charset='utf-8')
msg.attach(html_part)

# 3) SMTP 서버에 연결해서 메일 발송
with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.ehlo()
    smtp.starttls()               # TLS 암호화 시작
    smtp.login(USERNAME, PASSWORD)
    smtp.send_message(msg)

print("메일을 성공적으로 보냈습니다.")
