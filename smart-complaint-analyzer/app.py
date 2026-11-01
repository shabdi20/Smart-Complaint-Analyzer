import os
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError
from config import Config
from extensions import db, login_manager, csrf
from models import User

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config: app.config.update(test_config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app); login_manager.init_app(app); csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(uid): return db.session.get(User,int(uid))
    from routes.auth import bp as auth
    from routes.public import bp as public
    from routes.citizen import bp as citizen
    from routes.admin import bp as admin
    for blueprint in (auth,public,citizen,admin): app.register_blueprint(blueprint)
    @app.errorhandler(403)
    def forbidden(e): return render_template('errors/403.html'),403
    @app.errorhandler(404)
    def missing(e): return render_template('errors/404.html'),404
    @app.errorhandler(413)
    def too_large(e): return render_template('errors/413.html'),413
    @app.errorhandler(CSRFError)
    def csrf_error(e): return render_template('errors/403.html',message='Security token invalid or expired. Refresh and retry.'),400
    @app.errorhandler(500)
    def failed(e): db.session.rollback();return render_template('errors/500.html'),500
    return app
app = create_app()
if __name__ == '__main__': app.run(debug=False)
