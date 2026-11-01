import csv,json
from pathlib import Path
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,precision_recall_fscore_support,classification_report
ROOT=Path(__file__).resolve().parent

def train():
    with (ROOT/'dataset'/'complaints.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    texts=[r['text'] for r in rows];labels=[r['category'] for r in rows]
    x_train,x_test,y_train,y_test=train_test_split(texts,labels,test_size=.25,random_state=42,stratify=labels)
    model=Pipeline([('tfidf',TfidfVectorizer(lowercase=True,stop_words='english',ngram_range=(1,2),sublinear_tf=True)),('clf',LogisticRegression(max_iter=1200,class_weight='balanced'))])
    model.fit(x_train,y_train);pred=model.predict(x_test)
    precision,recall,f1,_=precision_recall_fscore_support(y_test,pred,average='macro',zero_division=0)
    report={'samples':len(rows),'test_samples':len(y_test),'accuracy':accuracy_score(y_test,pred),'macro_precision':precision,'macro_recall':recall,'macro_f1':f1,'classification_report':classification_report(y_test,pred,zero_division=0)}
    output=ROOT/'saved_model';output.mkdir(exist_ok=True)
    (output/'evaluation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    joblib.dump(model,output/'classifier.joblib')
    print(json.dumps({k:v for k,v in report.items() if k!='classification_report'},indent=2));print(report['classification_report'])
    return report
if __name__=='__main__':train()
