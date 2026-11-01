"""Opt-in authority notifications; no external sends unless explicitly enabled."""
import base64
import json
import logging
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import current_app
from extensions import db
from models import AuthorityContact, NotificationDelivery

logger = logging.getLogger(__name__)

def send_email(contact, subject, body, cfg):
    if not (cfg['SMTP_HOST'] and cfg['SMTP_FROM']):
        raise RuntimeError('SMTP not configured')
    msg = EmailMessage()
    msg['From'] = cfg['SMTP_FROM']; msg['To'] = contact.email; msg['Subject'] = subject
    msg.set_content(body)
    if cfg['SMTP_USE_SSL']:
        connection = smtplib.SMTP_SSL(cfg['SMTP_HOST'], cfg['SMTP_PORT'], timeout=8, context=ssl.create_default_context())
    else:
        connection = smtplib.SMTP(cfg['SMTP_HOST'], cfg['SMTP_PORT'], timeout=8)
    with connection as smtp:
        if not cfg['SMTP_USE_SSL']:
            smtp.starttls(context=ssl.create_default_context())
        if cfg['SMTP_USER']:
            smtp.login(cfg['SMTP_USER'], cfg['SMTP_PASSWORD'])
        smtp.send_message(msg)

def send_twilio(destination, channel, body, cfg):
    sid=cfg['TWILIO_ACCOUNT_SID']; token=cfg['TWILIO_AUTH_TOKEN']
    sender=cfg['TWILIO_SMS_FROM'] if channel=='sms' else cfg['TWILIO_WHATSAPP_FROM']
    if not (sid and token and sender):
        raise RuntimeError('Twilio credentials or sender not configured')
    data={'To':destination if channel=='sms' else 'whatsapp:'+destination,
          'From':sender if channel=='sms' else 'whatsapp:'+sender.removeprefix('whatsapp:')}
    if channel=='whatsapp':
        template=cfg['TWILIO_WHATSAPP_CONTENT_SID']
        if not template:
            raise RuntimeError('Approved WhatsApp Content Template SID required')
        data['ContentSid']=template
        # Template should use {{1}} for complaint ID and {{2}} for category.
        data['ContentVariables']=json.dumps({'1':body['id'],'2':body['category']})
    else:
        data['Body']=body['text']
    url=f'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json'
    auth=base64.b64encode(f'{sid}:{token}'.encode()).decode()
    req=Request(url,data=urlencode(data).encode(),headers={'Authorization':'Basic '+auth,'Content-Type':'application/x-www-form-urlencoded'},method='POST')
    with urlopen(req,timeout=8) as response:
        if response.status not in (200,201,202):
            raise RuntimeError('Provider rejected notification')

def notify_new_complaint(complaint_id):
    """Call after commit. Never block a saved complaint on delivery failure."""
    cfg=current_app.config
    if not cfg['NOTIFICATIONS_ENABLED']:
        return
    from models import Complaint
    complaint=db.session.get(Complaint,complaint_id)
    if complaint is None:return
    q=AuthorityContact.query.filter_by(active=True,consent_confirmed=True)
    if not cfg['NOTIFY_ALL_AUTHORITIES']:
        q=q.filter_by(department=complaint.assigned_department)
    contacts=q.all()
    subject=f'[Smart Complaint Analyzer] New complaint #{complaint.id} ({complaint.priority})'
    body=(f'New civic complaint #{complaint.id}\nTitle: {complaint.title}\n'
          f'Category: {complaint.confirmed_category or complaint.predicted_category}\n'
          f'Department: {complaint.assigned_department}\nPriority: {complaint.priority}\n'
          f'City: {complaint.city}\nLocation: {complaint.location}\n'
          'Log into the authorized admin dashboard to review the complaint.\n'
          'Automated priority is advisory; this is an academic prototype.')
    # Do not include citizen identity or uploaded image in notifications.
    for contact in contacts:
        for channel,enabled,address in [('email',contact.email_enabled,contact.email),('sms',contact.sms_enabled,contact.phone),('whatsapp',contact.whatsapp_enabled,contact.phone)]:
            if not enabled or not address:continue
            status='sent';detail='Accepted by provider (delivery not guaranteed)'
            try:
                if channel=='email':send_email(contact,subject,body,cfg)
                else:send_twilio(address,channel,{'text':body[:1400],'id':str(complaint.id),'category':complaint.confirmed_category or complaint.predicted_category},cfg)
            except Exception as exc:
                status='failed';detail='Provider configuration or delivery request failed'
                logger.warning('Notification failed for complaint %s contact %s channel %s: %s',complaint.id,contact.id,channel,type(exc).__name__)
            db.session.add(NotificationDelivery(complaint_id=complaint.id,authority_id=contact.id,channel=channel,status=status,detail=detail))
            try:db.session.commit()
            except Exception:
                db.session.rollback();logger.exception('Could not record notification delivery')
