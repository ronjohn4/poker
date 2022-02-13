from flask import flash, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Game, User, History, load_user
from datetime import datetime
from app.main.forms import EditProfileForm


@bp.route('/mail/', methods=["GET"])
def mail():
    print(f'mail: {current_user.is_authenticated}')



    if (current_user.is_authenticated):
        datalist = Game.query.filter_by(owner_id=current_user.id).order_by(Game.last_used_date.desc()).limit(20).all()
    else:
        datalist = None

    return render_template('main/index.html', datalist=datalist)


@bp.route('/')
@bp.route('/index/', methods=["GET"])
def index():
    # print(f'index - current_user.is_authenticated: {current_user.is_authenticated}')

    if (current_user.is_authenticated):
        # print(f'current_user.id: {current_user.id}')
        datalist = Game.query.filter_by(owner_id=current_user.id).order_by(Game.last_used_date.desc()).limit(20).all()
    else:
        datalist = None

    return render_template('main/index.html', datalist=datalist)


@bp.route('/game/<int:id>', methods=["GET"])
@login_required
def game(id):
    # print(f'game id: {id}')
    # print(f'game current_user.id: {current_user.id}')

    # TODO - When the user joins a game, need to trigger a playerlist update to all existing players
    currentplayer = User.query.filter_by(id=current_user.id).one()
    currentplayer.current_game_id = id
    db.session.commit()

    data_single = Game.query.filter_by(id=id).first_or_404()
    playerlist = User.query.filter_by(current_game_id=data_single.id).order_by(User.username.asc())
    historylist = History.query.filter_by(game_id=data_single.id).order_by(History.add_date.desc())

    return render_template('main/game.html', datasingle=data_single, 
        playerlist=playerlist, historylist=historylist)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', title='Edit Profile', form=form)
