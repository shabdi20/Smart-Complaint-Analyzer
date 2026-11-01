import json
from pathlib import Path
p=Path(__file__).resolve().parent/'saved_model'/'evaluation.json'
if __name__=='__main__':
    if not p.exists(): raise SystemExit('Run python -m ml.train_model first')
    data=json.loads(p.read_text(encoding='utf-8'))
    print(json.dumps({k:v for k,v in data.items() if k!='classification_report'},indent=2));print(data['classification_report'])
