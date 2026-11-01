from functools import lru_cache
from pathlib import Path
import joblib
from flask import current_app
class ModelUnavailable(RuntimeError): pass
@lru_cache(maxsize=4)
def load_model(path, mtime): return joblib.load(path)
def classify(text):
    path = Path(current_app.config['MODEL_PATH'])
    if not path.is_file(): raise ModelUnavailable('Trained model missing. Run: python -m ml.train_model')
    model = load_model(str(path), path.stat().st_mtime_ns)
    category = str(model.predict([text])[0])
    confidence = float(max(model.predict_proba([text])[0])) if hasattr(model, 'predict_proba') else None
    return category,confidence
