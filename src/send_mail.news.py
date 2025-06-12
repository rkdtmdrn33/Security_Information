import smtplib
from datetime import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# import py code
import news_info.collect_news as collect_news
