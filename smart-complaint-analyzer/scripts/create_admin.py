import getpass
from app import create_app
from extensions import db
from models import User
app=create_app()
with app.app_context():
    email=input('Admin email: ').strip().lower()
    if User.query.filter_by(email=email).first(): raise SystemExit('Account already exists')
    name=input('Full name: ').strip()
    password=getpass.getpass('Strong password (min 12 characters): ')
    if len(password)<12 or len(name)<2 or '@' not in email: raise SystemExit('Invalid details')
    u=User(full_name=name,email=email,role='admin');u.set_password(password);db.session.add(u);db.session.commit();print('Administrator created.')
