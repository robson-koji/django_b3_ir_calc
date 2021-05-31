from django.shortcuts import render

# Create your views here.
def send_email(title, html):
    import smtplib

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.header import Header


    print(title)
    print(html)

    smtp = smtplib.SMTP()
    smtp.connect('localhost')

    msgRoot = MIMEMultipart("alternative")
    msgRoot['Subject'] = Header(title, "utf-8")
    msgRoot['From'] = "robson_scripts@contabo.com"
    msgRoot['To'] = "robson.koji@gmail.com"

    html_email = MIMEText(html, 'html', "utf-8")

    msgRoot.attach(html_email)
    smtp.sendmail("sf@b3ircalc.online", "robson.koji@gmail.com", msgRoot.as_string())
