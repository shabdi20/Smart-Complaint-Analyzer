import csv,io
from collections import Counter
from flask import Blueprint,render_template,request,redirect,url_for,flash,abort,Response,current_app
from flask_login import current_user
from sqlalchemy import or_
from extensions import db
from models import Complaint,StatusHistory,User,AuthorityContact,NotificationDelivery,now
from routes import admin_required
from services.department_mapper import CATEGORIES,DEPARTMENTS
bp=Blueprint('admin',__name__,url_prefix='/admin')
STATUSES=['Submitted','Under Review','Assigned','In Progress','Resolved','Rejected']
def filtered():
    q=Complaint.query
    status=request.args.get('status','');category=request.args.get('category','');search=request.args.get('q','').strip()
    if status in STATUSES:q=q.filter_by(status=status)
    if category in CATEGORIES:q=q.filter(or_(Complaint.predicted_category==category,Complaint.confirmed_category==category))
    if search:q=q.filter(or_(Complaint.title.ilike('%'+search+'%'),Complaint.location.ilike('%'+search+'%'),Complaint.city.ilike('%'+search+'%')))
    return q
@bp.route('/')
@admin_required
def dashboard():
    items=Complaint.query.order_by(Complaint.created_at.desc()).limit(8).all()
    all_rows=db.session.query(Complaint.status,Complaint.priority,Complaint.predicted_category,Complaint.location).all()
    count=lambda index:dict(Counter(row[index] for row in all_rows))
    statuses=count(0)
    return render_template('admin/dashboard.html',items=items,total=len(all_rows),pending=sum(statuses.get(x,0) for x in ('Submitted','Assigned')),review=statuses.get('Under Review',0),progress=statuses.get('In Progress',0),resolved=statuses.get('Resolved',0),high=count(1).get('High',0),categories=count(2),priorities=count(1),statuses=statuses,locations=Counter(row[3] for row in all_rows).most_common(5))
@bp.route('/complaints')
@admin_required
def complaints():
    page=request.args.get('page',1,type=int)
    return render_template('admin/complaints.html',items=filtered().order_by(Complaint.created_at.desc()).paginate(page=page,per_page=12,error_out=False),categories=CATEGORIES,statuses=STATUSES)
@bp.route('/complaints/<int:cid>',methods=['GET','POST'])
@admin_required
def detail(cid):
    c=db.get_or_404(Complaint,cid)
    if request.method=='POST':
        status=request.form.get('status');department=request.form.get('department');category=request.form.get('category');note=request.form.get('note','').strip()
        if status not in STATUSES or department not in DEPARTMENTS or category not in CATEGORIES or len(note)>500:
            flash('Invalid update values.','danger');return redirect(url_for('admin.detail',cid=cid))
        if c.status in ('Resolved','Rejected') and status!=c.status:
            flash('Closed complaints cannot be reopened.','danger');return redirect(url_for('admin.detail',cid=cid))
        changed=status!=c.status
        if changed or note or department!=c.assigned_department or category!=(c.confirmed_category or c.predicted_category):
            db.session.add(StatusHistory(complaint_id=c.id,old_status=c.status,new_status=status,changed_by=current_user.id,note=note or 'Administrative review'))
        c.status=status;c.assigned_department=department;c.confirmed_category=category;c.updated_at=now()
        if status=='Resolved' and changed:c.resolved_at=now()
        db.session.commit();flash('Complaint updated.','success');return redirect(url_for('admin.detail',cid=cid))
    return render_template('admin/complaint_detail.html',c=c,statuses=STATUSES,departments=DEPARTMENTS,categories=CATEGORIES)
@bp.route('/users')
@admin_required
def users():
    page=request.args.get('page',1,type=int)
    return render_template('admin/users.html',items=User.query.order_by(User.created_at.desc()).paginate(page=page,per_page=15,error_out=False))
@bp.route('/reports')
@admin_required
def reports(): return render_template('admin/reports.html',total=filtered().count(),categories=CATEGORIES,statuses=STATUSES)
@bp.route('/export.csv')
@admin_required
def export():
    out=io.StringIO();writer=csv.writer(out)
    writer.writerow(['ID','Title','Category','Department','Priority','Status','Location','City','Created'])
    for c in filtered().order_by(Complaint.id).yield_per(200):
        writer.writerow([c.id,c.title,c.confirmed_category or c.predicted_category,c.assigned_department,c.priority,c.status,c.location,c.city,c.created_at.isoformat()])
    return Response(out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=complaints.csv'})


@bp.route('/authorities',methods=['GET','POST'])
@admin_required
def authorities():
    import re
    from services.department_mapper import DEPARTMENTS
    if request.method=='POST':
        name=request.form.get('name','').strip()
        department=request.form.get('department','').strip()
        email=request.form.get('email','').strip().lower()
        phone=request.form.get('phone','').strip()
        channels=set(request.form.getlist('channels'))
        consent=request.form.get('consent')=='yes'
        if (not 2<=len(name)<=120 or department not in DEPARTMENTS or
            (email and (len(email)>254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email))) or
            (phone and not re.fullmatch(r'\+[1-9][0-9]{7,14}',phone)) or
            not channels or not channels<= {'email','sms','whatsapp'} or
            ('email' in channels and not email) or
            (channels & {'sms','whatsapp'} and not phone) or not consent):
            flash('Enter valid contact details, choose channels and confirm consent. Phone must be E.164 (+countrycode...).','danger')
        else:
            db.session.add(AuthorityContact(name=name,department=department,email=email or None,phone=phone or None,email_enabled='email' in channels,sms_enabled='sms' in channels,whatsapp_enabled='whatsapp' in channels,consent_confirmed=True))
            db.session.commit();flash('Authority contact registered.','success')
        return redirect(url_for('admin.authorities'))
    contacts=AuthorityContact.query.order_by(AuthorityContact.id.desc()).all()
    deliveries=NotificationDelivery.query.order_by(NotificationDelivery.id.desc()).limit(50).all()
    return render_template('admin/authorities.html',contacts=contacts,deliveries=deliveries,departments=DEPARTMENTS,notifications_enabled=current_app.config['NOTIFICATIONS_ENABLED'])

@bp.route('/authorities/<int:contact_id>/toggle',methods=['POST'])
@admin_required
def toggle_authority(contact_id):
    contact=db.get_or_404(AuthorityContact,contact_id)
    contact.active=not contact.active
    db.session.commit();flash('Authority notification preference updated.','success')
    return redirect(url_for('admin.authorities'))
