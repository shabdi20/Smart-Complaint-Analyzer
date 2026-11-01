from services.priority_engine import detect_priority
from services.department_mapper import department_for
from services.duplicate_detector import find_similar
from services.classifier import classify
from types import SimpleNamespace

def test_classifier(app):
    with app.app_context():
        category,confidence=classify('Garbage has not been collected from our street for four days')
        assert category=='Sanitation and Garbage' and 0<=confidence<=1

def test_department(): assert department_for('Water Supply')=='Water Supply Department'
def test_priority():
    assert detect_priority('An exposed electrical wire is hanging')[0]=='High'
    assert detect_priority('Please update the notice board')[0]=='Low'
def test_similarity():
    c=SimpleNamespace(description='Large pothole near the school gate',location='School Road',confirmed_category=None,predicted_category='Roads and Infrastructure')
    assert find_similar('Large pothole near the school gate','Roads and Infrastructure','School Road',[c],.4)
    assert not find_similar('','Roads and Infrastructure','School Road',[c])
