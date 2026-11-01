from models import User
from tests.conftest import login

def test_home(client): assert client.get('/').status_code==200
def test_registration(client,app):
    response=client.post('/auth/register',data={'full_name':'New Person','email':'new@example.test','password':'strongpass123'})
    assert response.status_code==302
    with app.app_context():
        user=User.query.filter_by(email='new@example.test').one()
        assert user.password_hash!='strongpass123' and user.check_password('strongpass123')
def test_invalid_registration(client):
    client.post('/auth/register',data={'full_name':'N','email':'bad','password':'short'})
    assert client.get('/auth/login').status_code==200
def test_login_logout(client):
    assert login(client).status_code==200
    assert client.post('/auth/logout').status_code==302
def test_admin_only(client):
    login(client)
    assert client.get('/admin/').status_code==403
