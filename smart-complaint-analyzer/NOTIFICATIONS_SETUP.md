# Authority SMS, WhatsApp and email notifications

This feature **does not send messages until you configure providers and enable it**. A phone number alone is not enough to send SMS or WhatsApp. Provider accounts, verified senders, costs, recipient consent and (for WhatsApp) approved templates may be required.

## Register recipients
1. Run `python -m scripts.init_db` to add the new tables to an existing database (do not delete your existing SQLite database).
2. Start the app and sign in as an administrator.
3. Open **Authority alerts** in the sidebar and register each authority's name, department, email and/or E.164 phone number (`+919876543210`). Select desired channels and confirm recipient consent.
4. Contacts can be disabled and re-enabled from this page. Only active, consent-confirmed contacts receive notifications.

## Email setup
Configure `.env`: `SMTP_HOST`, `SMTP_PORT` (usually 587 for STARTTLS or 465 for SSL), `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`; set `SMTP_USE_SSL=1` for port 465. Use your mail provider's SMTP/app-password instructions. Never commit `.env`.

## SMS and WhatsApp
Create a Twilio account, acquire an SMS-capable sender, and configure `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_SMS_FROM` (E.164). For WhatsApp, set `TWILIO_WHATSAPP_FROM` to an approved WhatsApp-enabled sender and `TWILIO_WHATSAPP_CONTENT_SID` to a provider-approved template SID. The template should contain `{{1}}` for complaint ID and `{{2}}` for category. WhatsApp business-initiated messages require an approved template and proper recipient opt-in. Sandbox/trial accounts have recipient restrictions; real delivery is not guaranteed. India may have additional SMS sender registration requirements.

Finally set `NOTIFICATIONS_ENABLED=1` and restart Flask. Default `NOTIFY_ALL_AUTHORITIES=1` notifies all registered, active, consenting authorities on each new complaint; set `0` to notify only authorities in the assigned department.

## Behavior and privacy
Alerts are sent only **after** a complaint is saved. Failed provider requests do not cancel the complaint. Each attempted channel is logged as `sent` (accepted by provider, not proof of delivery) or `failed` in **Authority alerts**. A saved complaint does not guarantee message delivery. The synchronous implementation may delay the complaint response when many authorities are registered or providers are slow; a queue/retry worker is a recommended production enhancement. Notifications contain complaint title, category, priority, city, location and ID but no citizen email or name. Register recipients only with authorization and consent. This is an academic prototype, not a government emergency alerting service.

## Run on Windows PowerShell
From the project folder, with the virtual environment activated:
```powershell
python -m pip install -r requirements.txt
python -m scripts.init_db
python app.py
```
Your existing `.env` is preserved; copy new settings from `.env.example` into it. Do not overwrite existing secrets.
