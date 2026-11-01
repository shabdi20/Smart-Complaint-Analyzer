from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user
from extensions import db
from models import User
bp=Blueprint('auth',__name__,url_prefix='/auth')
@bp.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('full_name','').strip();email=request.form.get('email','').strip().lower();password=request.form.get('password','')
        if not 2<=len(name)<=120 or not 5<=len(email)<=254 or '@' not in email or len(password)<10:
            flash('Enter a valid name, email and password (at least 10 characters).','danger')
        elif User.query.filter_by(email=email).first(): flash('Email already registered.','danger')
        else:
            u=User(full_name=name,email=email,role='citizen');u.set_password(password);db.session.add(u);db.session.commit();login_user(u)
            return redirect(url_for('citizen.dashboard'))
    return render_template('auth/register.html')
@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=User.query.filter_by(email=request.form.get('email','').strip().lower()).first()
        if u and u.check_password(request.form.get('password','')):
            login_user(u);return redirect(url_for('admin.dashboard' if u.role=='admin' else 'citizen.dashboard'))
        flash('Invalid email or password.','danger')
    return render_template('auth/login.html')
@bp.route('/logout',methods=['POST'])
@login_required
def logout(): logout_user();return redirect(url_for('public.index'))
