__author__ = 'veydh'

from os import listdir, path
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from config import GMail_account, GMail_pass

def send_email(recipient, subject, body, attachments):
    import smtplib

    gmail_user = GMail_account
    gmail_pwd = GMail_pass

    FROM = gmail_user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    msg = MIMEMultipart('related')
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO[0]

    msg.preamble = 'Multipart massage.\n'
    msg.attach(MIMEText(TEXT, 'html'))

    if attachments:
        for graphpic in listdir('graphs'):
            ImgFileName = 'graphs/'+graphpic
            img_data = open(ImgFileName, 'rb').read()
            image = MIMEImage(img_data, name=path.basename(ImgFileName))
            msg.attach(image)

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()
        print 'Successfully sent mail'
    except:
        print "Failed to send mail"