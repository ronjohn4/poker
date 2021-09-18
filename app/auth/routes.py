from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.models import User
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    print(f'is_authenticated: {current_user.is_authenticated}')
    print(f'request.method: {request.method}')

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f'username: {username}')
        print(f'password: {password}')


        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            # flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user) # TODO - add remember me checkbox back  login_user(user, remember=checkbox value)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)


    return render_template('auth/login.html', title='Sign In')


@bp.route('/logout')
def logout():
    # pass
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # pass
#     print('register top')
#     if current_user.is_authenticated:
#         return redirect(url_for('main.list'))
#     form = None
#     if form.validate_on_submit():
    user = User(username="admin", email="admin@domain.com")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('.login'))
#     return render_template('auth/register.html', title='Register', form=form)
    return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    pass
#     if current_user.is_authenticated:
#         return redirect(url_for('main.list'))
#     form = None
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user:
#             send_password_reset_email(user)
#         flash('Check your email for the instructions to reset your password')
#         return redirect(url_for('.login'))
#     return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    pass
#     if current_user.is_authenticated:
#         return redirect(url_for('main.list'))
#     user = User.verify_reset_password_token(token)
#     if not user:
#         return redirect(url_for('main.list'))
#     form = None
#     if form.validate_on_submit():
#         user.set_password(form.password.data)
#         db.session.commit()
#         flash('Your password has been reset.')
#         return redirect(url_for('.login'))
#     return render_template('auth/reset_password.html', form=form)
