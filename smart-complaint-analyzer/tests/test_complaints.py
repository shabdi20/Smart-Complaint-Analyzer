from tests.conftest import login
from models import Complaint
from extensions import db

def create(client):
    return client.post('/citizen/submit',data={'title':'Broken road outside school','description':'The road outside the school has several large potholes.','location':'School Road','city':'Demo City'},follow_redirects=False)
def test_create_persistence(client,app):
    login(client);r=create(client);assert r.status_code==302
    with app.app_context():
        c=Complaint.query.one();assert c.status=='Submitted' and len(c.history)==1
        assert c.assigned_department and c.priority_reason

def test_other_citizen_forbidden(client):
    login(client);create(client)
    client.post('/auth/logout');login(client,'other@example.test')
    assert client.get('/citizen/complaints/1').status_code==403

def test_invalid_and_bad_image(client):
    login(client)
    assert client.post('/citizen/submit',data={'title':'x','description':'short','location':'x','city':'x'}).status_code==200
    from io import BytesIO
    response=client.post('/citizen/submit',data={'title':'Broken road outside school','description':'The road outside the school has several large potholes.','location':'School Road','city':'Demo City','image':(BytesIO(b'not image'),'image.png')},content_type='multipart/form-data')
    assert response.status_code==400

def test_missing_model(client,app):
    login(client);app.config['MODEL_PATH']='/missing/model.joblib'
    assert create(client).status_code==503
