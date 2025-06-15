# main 함수
import send_mail_cve
import send_mail_poc
import send_mail_news

try:
    send_mail_cve.send_mail_cve()
except ValueError as ve:
    print(f"[SKIP] 메일 전송 생략: {ve}")

send_mail_poc.send_mail_poc()
send_mail_news.send_mail_news()