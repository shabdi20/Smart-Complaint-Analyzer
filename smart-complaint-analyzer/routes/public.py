from flask import Blueprint,render_template
bp=Blueprint('public',__name__)
@bp.route('/')
def index(): return render_template('index.html')
@bp.route('/about')
def about(): return render_template('about.html')
@bp.route('/how-it-works')
def how_it_works(): return render_template('how_it_works.html')
