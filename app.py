from flask import (Flask, render_template, flash, g, redirect,
                    url_for, abort, request)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user, 
                        login_required, current_user)
from peewee import *

import forms
import models


app = Flask(__name__)
app.secret_key ="f340jgnvm2495nvm$&"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@app.route('/')
@app.route('/entries')
def index():
    stream = models.Entry.select().limit(20).order_by(models.Entry.date.desc())
    return render_template('toindex.html', stream=stream)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out. See you soon!", "success")
    return redirect(url_for('index'))

@app.route('/register', methods=('GET', 'POST'))
def register():
    form= forms.RegisterForm()
    if form.validate_on_submit():
        flash('Welcome! You registered!', "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)
    
@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new_entry():
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Entry.create(
            user=g.user._get_current_object(),
            title=form.title.data.strip(),
            time_spent=form.time_spent.data,
            content=form.content.data.strip(),
            resources=form.resources.data.strip(),
            date = form.date.data)
        flash("Entry saved!","success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)

@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    try:
        if username and username != current_user.username:
            user = models.User.select().where(models.User.username**username).get()
            stream = user.entries.limit(20)
        else: 
            stream = current_user.get_stream().limit(20)
            user = current_user
        if username:
            template = 'user_stream.html'
        # try:
        #     user = current_user
        #     stream = current_user.get_stream().limit(20)
        #     template = 'user_stream.html'
    except models.DoesNotExist:
        abort(404)
    return render_template(template, stream=stream, user=user)

@app.route('/entries/<int:entry_id>')
def detail(entry_id):
    entries = models.Entry.select().where(models.Entry.id == entry_id)
    if entries.count() == 0:
        abort(404)
    else:
        return render_template('stream.html', stream=entries)

@app.route('/entries/<int:entry_id>/delete', methods=('GET', 'POST'))
@login_required
def delete(entry_id):
    get_entry = models.Entry.get(models.Entry.id==entry_id)
    if current_user == get_entry.user:
        try:
            get_entry.delete_instance()
            flash("Entry deleted!", "success")
            return redirect(url_for('index'))
        except models.DoesNotExist:
            render_template('404.html'), 404
    elif current_user != get_entry.user:
        flash("You can't delete someone else's entry!", "error")
        return render_template("index.html")
    
@app.route('/entries/<int:entry_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_entry(entry_id):
    try:
        entry = models.Entry.get(models.Entry.id == entry_id)
        entries = models.Entry.select().where(
            models.Entry.id==entry_id)
    except models.DoesNotExist:
        render_template('404.html'), 404

    form = forms.EntryForm()
    if current_user == entry.user:
        if request.method == 'GET':
            form.title.data = entry.title
            form.time_spent.data = entry.time_spent
            form.content.data = entry.content
            form.resources.data = entry.resources
            form.date.data = entry.date
        elif form.validate_on_submit():
            entry.title=form.title.data
            entry.time_spent=form.time_spent.data
            entry.content=form.content.data
            entry.resources=form.resources.data
            entry.date=form.date.data
            entry.save()
            flash("Entry updated!", "success")
            return redirect(url_for('detail', entry_id=entry_id))
    elif current_user != entry.user:
        flash("You don't have permission to edit this entry!")
        return redirect(url_for('index', entry_id=entry_id))
    return render_template('edit.html', form=form, entry=entry)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()
    app.run(debug=True, port=8000, host='localhost')