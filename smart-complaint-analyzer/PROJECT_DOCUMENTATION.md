# Smart Complaint Analyzer — Project Documentation
## Abstract
A local Flask application for reporting civic complaints and using TF-IDF machine learning to suggest categories. Administrators review, assign, and track progress.
## Introduction
Civic complaints vary in type and urgency. An organized reporting workflow improves transparency.
## Problem statement
Manual complaint intake can create inconsistent classification, poor traceability, and delays.
## Existing-system limitations
Paper registers, disconnected messages, and manual sorting lack searchable audit histories.
## Proposed system
A citizen web portal with an ML classifier, rule-based urgency, category-to-department mapping, similarity recommendations, SQLite persistence and an admin dashboard.
## Objectives
Enable easy reporting, automate suggestions, preserve status history, and visualize trends.
## Functional requirements
Registration, login, submission, personal tracking, admin review, status changes, reports and CSV export.
## Nonfunctional requirements
Responsive UI, offline operation after installation, hashed passwords, CSRF, safe image handling, and accessible labels.
## Hardware and software requirements
A laptop with approximately 4 GB RAM or more, Python 3.11+, modern browser, Windows 11 or Linux/macOS, and dependencies from requirements.txt.
## Architecture
Browser → Flask blueprints → services → SQLAlchemy → SQLite. ML training is a separate CLI pipeline writing a joblib artifact used for inference.
## Use cases
Citizen: register, submit, review, track. Admin: authenticate, search, classify/assign, update status, view analytics, export.
## Database design
User 1:N Complaint; Complaint 1:N StatusHistory; StatusHistory N:1 User actor. Primary keys, foreign keys and timestamps support traceability.
## Algorithms
TF-IDF word/bi-gram features + class-balanced Logistic Regression for category; ordered phrase rules for priority; cosine similarity for possible duplicates; mapping dictionary for departments.
## ML methodology
240 synthetic labeled examples, stratified 75/25 split, scikit-learn Pipeline, saved joblib model and evaluation JSON. Closely related samples across splits mean reported metrics are optimistic; an independent dataset is required for trustworthy accuracy.
## Testing strategy
pytest tests for authentication, access control, submission, persistence, administrative status/history, ML services and CSV export. Further manual cross-browser, load and security testing is recommended.
## Expected outcomes
A demonstration of a persistent civic complaint workflow with explainable automated suggestions and admin review.
## Limitations
No government connectivity; no live alerting; synthetic training set; capped duplicate search; offline canvas charts; no migration framework or production hardening.
## Future scope
Multilingual classification, geospatial clustering, SMS/email alerts, better calibrated ML, role-granular notes, stronger rate limiting and independent validation.
## Conclusion
The project illustrates how Python web engineering, databases, and lightweight ML can combine to support structured civic issue management while retaining human oversight.
