# Smart Complaint Analyzer
**AI-Powered Smart City Complaint Management System — academic prototype, not a government service.**

## Problem, motivation and objectives
Citizens need a clear way to report civic issues, while reviewers need structured queues and transparent status histories. This project demonstrates how a local NLP model can suggest categories, rule-based logic can recommend priorities, and a relational database can track progress. It does not contact any real government department.

## Implemented features
Citizen registration/login, profile editing, complaint submission with optional image, local ML categorization with confidence estimate, configurable category-to-department mapping, explained priority, cosine-similarity suggestions, personal tracking/history and filters. Admin login, protected review routes, status updates and notes, category/department correction, user directory, live statistics, canvas-based offline charts, search/pagination and CSV export. CSRF, password hashing and server-side role checks included.

## Stack and architecture
Python 3.11+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, SQLite, scikit-learn, Pillow, vanilla JS, CSS. All assets are local; no CDN is required. The UI is custom CSS rather than Bootstrap; charts use native HTML Canvas rather than Chart.js to remain fully offline.

`app.py` builds the Flask application. `models/` defines the database schema. `routes/` separates public, authentication, citizen and admin endpoints. `services/` contains ML inference, department mapping, priority rules and duplicate similarity. `ml/` contains labeled data, training and evaluation. `templates/` and `static/` contain the UI. `scripts/` contains setup commands. `tests/` contains pytest tests.

## Database schema
`User` (one-to-many `Complaint`), `Complaint` (one-to-many `StatusHistory`), and `StatusHistory` (many-to-one `User` via `changed_by`). Foreign keys, uniqueness and status indexes are included. Timestamps use UTC. `db.create_all()` is suitable for initial setup, not schema migration of existing databases.

## Windows 11 PowerShell installation
Open PowerShell in the extracted project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; from pathlib import Path; p=Path('.env'); t=p.read_text(); p.write_text(t.replace('replace-with-a-long-random-secret', secrets.token_hex(32)))"
python -m scripts.init_db
python -m ml.train_model
python -m scripts.create_admin
python app.py
```

Visit **http://127.0.0.1:5000/**. Use the credentials you entered when running `create_admin`. For a sample citizen and four complaints, optionally run `python -m scripts.seed_demo_data` after model training. You choose the demo password; no public password is embedded.

If PowerShell refuses activation, run `Set-ExecutionPolicy -Scope Process Bypass` then retry activation. You may also run `.venv\Scripts\python.exe` without activation.

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; from pathlib import Path; p=Path('.env');p.write_text(p.read_text().replace('replace-with-a-long-random-secret',secrets.token_hex(32)))"
python -m scripts.init_db
python -m ml.train_model
python -m scripts.create_admin
python app.py
```

## Machine learning and NLP
`python -m ml.train_model` loads 240 labeled synthetic sentences in eight classes, performs a stratified 75/25 split, fits a scikit-learn pipeline (TF-IDF with English stop words and 1–2-grams; class-balanced logistic regression), evaluates predictions and writes `classifier.joblib` and `evaluation.json`. Run `python -m ml.evaluate_model` to inspect measured metrics. Prediction loads the saved pipeline without retraining on user complaints. A missing model displays setup instructions. The probability is an estimate, not calibrated real-world certainty. The synthetic examples include paraphrases of identical base sentences across train/test; evaluation accuracy is likely inflated and **must not be claimed as generalization performance**. Collect independent real-world labels and group examples before a production evaluation.

## Priority and duplicate detection
`services/priority_engine.py` checks configurable high-risk phrases first, then medium-priority service indicators, then defaults to Low. It returns an explanation. The priority is **not** an emergency assessment. `services/duplicate_detector.py` compares TF-IDF vectors with cosine similarity for complaints in the same category, adding location terms. The default similarity threshold is `0.48`, configurable in `.env`. At most the latest 500 same-category complaints are considered. Similarity never blocks submission and does not establish a duplicate.

## Security
Passwords are hashed using Werkzeug. Flask-Login protects sessions and server-side role checks protect administrator endpoints. Flask-WTF provides CSRF tokens. Image uploads are checked by Pillow, limited to 5 MB request size and 16 million pixels, converted to JPEG, given random filenames and stored in the private instance directory. Image retrieval checks ownership. No real secrets or databases should be committed. Set `SESSION_COOKIE_SECURE=1` behind HTTPS for production. The default development secret is **unsafe** if `.env` is not configured. Use HTTPS, rate limiting, account recovery and a production WSGI server before any public deployment.

## Tests
Run `python -m pytest -q` after installing requirements and training. Tests use a temporary SQLite database and separate fixture accounts. Some tests require the saved classifier. For first-run problems, check that the virtual environment is activated, run `python -m ml.train_model`, and verify your `.env` secret and writable `instance/` directory.

## Demo workflow
Register a citizen, submit a pothole complaint, review category/department/priority, then sign out. Sign in as the admin, change status to Under Review and add a note. Sign back in as citizen and verify the timeline. Show admin charts and export CSV. A second similar complaint demonstrates similarity suggestions.

## Limitations and future work
This is a local educational prototype, not municipal integration. No notifications, email verification, password reset, geocoding, audit-grade access logging, migrations, or government API integrations. Similarity scans only a capped recent set. Categories are trained on small synthetic examples. No image understanding is performed. Admin notes appear in the status history and are therefore visible to the complaint owner; do not enter sensitive internal-only notes. Admin updates do not enforce a full transition graph beyond preventing reopening closed cases. Future improvements include independently evaluated datasets, a robust migration strategy, notifications, human-verified labels, multilingual NLP, stricter transitions, and production deployment security.


## Authority notifications (new)
Administrators can register consenting authority contacts under **Authority alerts**. On each new complaint, the application can attempt email via SMTP and SMS/WhatsApp via Twilio. Outbound notifications are **off by default** and require provider credentials and (for WhatsApp) an approved template. See [NOTIFICATIONS_SETUP.md](NOTIFICATIONS_SETUP.md) for complete setup, limitations, and Windows commands. Run `python -m scripts.init_db` after updating an existing installation to create the new tables.
