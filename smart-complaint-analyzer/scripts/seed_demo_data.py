import getpass
from app import create_app
from extensions import db
from models import User,Complaint,StatusHistory
from services.department_mapper import department_for
from services.priority_engine import detect_priority
from services.classifier import classify
app=create_app()
with app.app_context():
    email=input('Demo citizen email: ').strip().lower();password=getpass.getpass('Demo citizen password (min 10 chars): ')
    if len(password)<10 or '@' not in email: raise SystemExit('Invalid credentials')
    if User.query.filter_by(email=email).first(): raise SystemExit('Account already exists')
    u=User(full_name='Demo Citizen',email=email,role='citizen');u.set_password(password);db.session.add(u);db.session.flush()
    samples=[('Potholes by school','The road outside the school has several large potholes.','School Road'),('Garbage pickup missed','Garbage has not been collected from our street for four days.','Market Lane'),('Streetlight fault','The streetlight is not working near the public park.','Park Road'),('Water supply stopped','There is no water supply in our residential area since yesterday.','Station Colony')]
    for title,desc,location in samples:
        cat,conf=classify(title+' '+desc);priority,reason=detect_priority(desc)
        c=Complaint(citizen_id=u.id,title=title,description=desc,location=location,city='Demo City',predicted_category=cat,assigned_department=department_for(cat),priority=priority,priority_reason=reason,model_confidence=conf)
        db.session.add(c);db.session.flush();db.session.add(StatusHistory(complaint_id=c.id,new_status='Submitted',changed_by=u.id))
    db.session.commit();print('Created demo citizen and four complaints.')
