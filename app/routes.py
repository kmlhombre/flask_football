from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddFootballerForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Footballer
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
def index():
    users = User.query.all()
    footballers = Footballer.query.all()
    return render_template('index.html', footballers=footballers, users=users, title='Homepage')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/add_footballer', methods=['GET', 'POST'])
@login_required
def add_footballer():
    form = AddFootballerForm()
    if form.validate_on_submit():
        footballer = Footballer(name=form.name.data, surname=form.surname.data, team=form.team.data, country=form.country.data, added_by=current_user.id)
        db.session.add(footballer)
        db.session.commit()
        flash('The footballer was successfully added to the database.')
        return redirect(url_for('index'))
    return render_template('add_footballer.html', title='Add footballer', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    footballers = Footballer.query.filter_by(added_by=user.id)
    return render_template('user.html', user=user, footballers=footballers)