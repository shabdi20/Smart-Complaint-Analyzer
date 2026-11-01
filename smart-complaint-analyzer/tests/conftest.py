import pytest
from app import create_app
from extensions import db
from models import User
@pytest.fixture
def app(tmp_path):
    a=create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':'sqlite:///'+str(tmp_path/'test.db'),'UPLOAD_FOLDER':str(tmp_path/'uploads'),'WTF_CSRF_ENABLED':False})
    with a.app_context():
        db.create_all()
        for email,role in [('admin@example.test','admin'),('citizen@example.test','citizen'),('other@example.test','citizen')]:
            u=User(full_name='Test User',email=email,role=role);u.set_password('long-test-password');db.session.add(u)
        db.session.commit()
        yield a
        db.session.remove();db.drop_all()
@pytest.fixture
def client(app):return app.test_client()
def login(client,email='citizen@example.test'):
    return client.post('/auth/login',data={'email':email,'password':'long-test-password'},follow_redirects=True)
