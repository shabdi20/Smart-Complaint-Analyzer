from pathlib import Path
from uuid import uuid4
from PIL import Image,UnidentifiedImageError
from flask import Blueprint,render_template,request,redirect,url_for,flash,abort,current_app,send_from_directory
from flask_login import login_required,current_user
from sqlalchemy import or_
from extensions import db
from models import Complaint,StatusHistory
from services.classifier import classify,ModelUnavailable
from services.department_mapper import CATEGORIES,department_for
from services.priority_engine import detect_priority
from services.duplicate_detector import find_similar
bp=Blueprint('citizen',__name__,url_prefix='/citizen')

def owned(cid):
    c=db.get_or_404(Complaint,cid)
    if c.citizen_id!=current_user.id and current_user.role!='admin': abort(403)
    return c
@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role=='admin': return redirect(url_for('admin.dashboard'))
    q=Complaint.query.filter_by(citizen_id=current_user.id)
    items=q.order_by(Complaint.created_at.desc()).limit(6).all()
    return render_template('citizen/dashboard.html',items=items,total=q.count(),pending=q.filter(Complaint.status.in_(['Submitted','Under Review','Assigned'])).count(),progress=q.filter_by(status='In Progress').count(),resolved=q.filter_by(status='Resolved').count())
@bp.route('/complaints')
@login_required
def complaints():
    q=Complaint.query.filter_by(citizen_id=current_user.id)
    status=request.args.get('status','');category=request.args.get('category','')
    if status:q=q.filter_by(status=status)
    if category:q=q.filter(or_(Complaint.confirmed_category==category,Complaint.predicted_category==category))
    page=request.args.get('page',1,type=int)
    return render_template('citizen/complaints.html',items=q.order_by(Complaint.created_at.desc()).paginate(page=page,per_page=10,error_out=False),categories=CATEGORIES)
@bp.route('/submit',methods=['GET','POST'])
@login_required
def submit():
    if request.method=='POST':
        fields={k:request.form.get(k,'').strip() for k in ('title','description','location','city','landmark','category')}
        if not 5<=len(fields['title'])<=150 or not 15<=len(fields['description'])<=3000 or not 2<=len(fields['location'])<=150 or not 2<=len(fields['city'])<=100 or len(fields['landmark'])>150:
            flash('Check title (5–150), description (15–3000), location and city.','danger');return render_template('citizen/submit_complaint.html',categories=CATEGORIES)
        if fields['category'] not in ['','Auto Detect']+CATEGORIES: abort(400)
        try: predicted,confidence=classify(fields['title']+' '+fields['description'])
        except ModelUnavailable as e:
            flash(str(e),'danger');return render_template('citizen/submit_complaint.html',categories=CATEGORIES),503
        category=fields['category'] if fields['category'] in CATEGORIES else predicted
        filename=None;upload=request.files.get('image')
        if upload and upload.filename:
            ext=Path(upload.filename).suffix.lower()
            if ext not in ('.png','.jpg','.jpeg','.webp'):
                flash('Only PNG, JPEG or WebP images are accepted.','danger');return render_template('citizen/submit_complaint.html',categories=CATEGORIES),400
            try:
                img=Image.open(upload.stream);img.verify();upload.stream.seek(0)
                img=Image.open(upload.stream)
                if img.width*img.height>16000000: raise ValueError('Image too large')
                img=img.convert('RGB');filename=uuid4().hex+'.jpg';img.save(Path(current_app.config['UPLOAD_FOLDER'])/filename,format='JPEG',quality=85)
            except (UnidentifiedImageError,OSError,ValueError):
                flash('Image is invalid or too large.','danger');return render_template('citizen/submit_complaint.html',categories=CATEGORIES),400
        priority,reason=detect_priority(fields['title']+' '+fields['description'])
        candidates=Complaint.query.filter_by(predicted_category=category).order_by(Complaint.id.desc()).limit(500).all()
        matches=find_similar(fields['description'],category,fields['location'],candidates,current_app.config['SIMILARITY_THRESHOLD'])
        c=Complaint(citizen_id=current_user.id,title=fields['title'],description=fields['description'],location=fields['location'],city=fields['city'],landmark=fields['landmark'],predicted_category=predicted,confirmed_category=category if category!=predicted else None,assigned_department=department_for(category),priority=priority,priority_reason=reason,model_confidence=confidence,image_filename=filename,possible_duplicate=bool(matches))
        db.session.add(c);db.session.flush();db.session.add(StatusHistory(complaint_id=c.id,new_status='Submitted',changed_by=current_user.id,note='Complaint submitted'));db.session.commit()
        from services.notifications import notify_new_complaint
        notify_new_complaint(c.id)
        flash('Complaint submitted successfully.','success');return redirect(url_for('citizen.detail',cid=c.id))
    return render_template('citizen/submit_complaint.html',categories=CATEGORIES)
@bp.route('/complaints/<int:cid>')
@login_required
def detail(cid):
    c=owned(cid)
    candidates=Complaint.query.filter(Complaint.id!=cid,Complaint.predicted_category==c.predicted_category).order_by(Complaint.id.desc()).limit(500).all()
    matches=find_similar(c.description,c.confirmed_category or c.predicted_category,c.location,candidates,current_app.config['SIMILARITY_THRESHOLD'])
    return render_template('citizen/complaint_detail.html',c=c,matches=matches)
@bp.route('/uploads/<filename>')
@login_required
def upload(filename):
    c=Complaint.query.filter_by(image_filename=filename).first_or_404();owned(c.id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],filename)
@bp.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        name=request.form.get('full_name','').strip()
        if 2<=len(name)<=120:current_user.full_name=name;db.session.commit();flash('Profile updated.','success')
        else:flash('Name must be 2–120 characters.','danger')
    return render_template('citizen/profile.html')
