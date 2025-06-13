import smtplib
import os
from datetime import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# import py code
import cve_info.filtered_cve as filtered_cve

current_time = datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M")

current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일 기준
filepath = os.path.join(current_dir, 'config.json')

with open(filepath, 'r', encoding='utf-8-sig') as f:
  config = json.load(f)

SMTP_HOST = config['SMTP_HOST']
SMTP_PORT = config['SMTP_PORT']
USERNAME = config['USERNAME']
PASSWORD = config['PASSWORD']
FROM_ADDR = config['FROM_ADDR']
TO_ADDRS = config['TO_ADDRS']
SUBJECT = "[NVD Announce] CVE Alert (Last Update)"

# 1) MIMEMultipart 객체 생성 (본문+첨부)
msg = MIMEMultipart()
msg['From'] = FROM_ADDR
msg['To'] = ', '.join(TO_ADDRS)
msg['Subject'] = SUBJECT

# NEWS HTML

def cve_html(): # CVE HTML  
  cve_result = filtered_cve.filtered_cve()

  if not cve_result: # Exception handling
     return 0
  else:
    cve_rows = []
    for item in cve_result:
        cve_rows.append(f"""
        <tr>
          <td style="border:1px solid #000000;padding:8px;font-size:13px;">{item['id']}</td>
          <td style="border:1px solid #000000;padding:8px;font-size:13px;">{item['published']}</td>
          <td style="border:1px solid #000000;padding:8px;font-size:13px;">{item['descriptions']}</td>
          <td style="border:1px solid #000000;padding:8px;font-size:13px;">
            <a href="{item['references']}">{item['references']}</a>
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
    <p style="font-size:20px;">NVD 신규 업데이트 CVE 보고서</p>
    <p style="font-size:13px;">- 총 업데이트 CVE: {len(cve_rows)}건</p>
    <p style="font-size:13px;">- 업데이트 기준: {formatted_time}</p>
    <p style="margin-bottom:20px; font-size:13px;">
      <a href="https://nvd.nist.gov/vuln/search" target="_blank" style="color:#0066cc;text-decoration:none;">
        - NVD: https://nvd.nist.gov/vuln/search
      </a>
    </p>
  
    <table style="width:100%;border-collapse:collapse;border:1px solid #000000;">
      <thead>
        <tr>
          <th style="border:1px solid #000000;background:#E7E6E6;padding:8px;text-align:center;">NVD</th>
          <th style="border:1px solid #000000;background:#E7E6E6;padding:8px;text-align:center;">DATE</th>
          <th style="border:1px solid #000000;background:#E7E6E6;padding:8px;text-align:center;">Descriptions</th>
          <th style="border:1px solid #000000;background:#E7E6E6;padding:8px;text-align:center;">link</th>
        </tr>
      </thead>
      <tbody>
        {''.join(cve_rows)}
      </tbody>
    </table>
  </body>
  </html>
    """
    return html_body

def send_mail_cve():
  result = cve_html()
  html_part = MIMEText(result, 'html', _charset='utf-8')
  msg.attach(html_part)

  # 3) SMTP 서버에 연결해서 메일 발송
  with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
      smtp.ehlo()
      smtp.starttls()               # TLS 암호화 시작
      smtp.login(USERNAME, PASSWORD)
      smtp.send_message(msg)

  print("CVE 메일을 성공적으로 보냈습니다.")