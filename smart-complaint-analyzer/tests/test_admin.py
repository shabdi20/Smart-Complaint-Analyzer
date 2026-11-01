from tests.conftest import login
from tests.test_complaints import create
from models import Complaint

def test_admin_review_and_export(client,app):
    login(client);create(client)
    client.post('/auth/logout');login(client,'admin@example.test')
    assert client.get('/admin/').status_code==200
    assert client.get('/admin/export.csv').status_code==200
    r=client.post('/admin/complaints/1',data={'status':'Under Review','category':'Roads and Infrastructure','department':'Public Works Department','note':'Inspection scheduled'},follow_redirects=True)
    assert r.status_code==200
    with app.app_context():
        c=Complaint.query.first();assert c.status=='Under Review' and len(c.history)==2

def test_citizen_cannot_export(client):
    login(client);assert client.get('/admin/export.csv').status_code==403
