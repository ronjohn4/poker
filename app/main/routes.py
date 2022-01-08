from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Game, User, History, load_user
from datetime import datetime


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


@bp.route('/view/<int:id>', methods=["GET"])
def view(id):
    # print(f'view id: {id}')
    # print(f'view current_user.id: {current_user.id}')

    # TODO - When the user joins a game, need to trigger a playerlist update to all existing players
    currentplayer = User.query.filter_by(id=current_user.id).one()
    currentplayer.current_game_id = id
    db.session.commit()

    data_single = Game.query.filter_by(id=id).first_or_404()
    playerlist = User.query.filter_by(current_game_id=data_single.id).order_by(User.username.asc())
    historylist = History.query.filter_by(game_id=data_single.id).order_by(History.add_date.desc())

    return render_template('main/view.html', datasingle=data_single, 
        playerlist=playerlist, historylist=historylist)
