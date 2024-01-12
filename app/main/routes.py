from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import EditProfileForm
from app.models import Game, History, Player, User, load_user


@bp.route("/mail/", methods=["GET"])
def mail():
    print(f"mail: {current_user.is_authenticated}")

    if current_user.is_authenticated:
        datalist = (
            Player.query.filter_by(user_id=current_user.id)
            .order_by(Game.last_used_date.desc())
            .limit(20)
            .all()
        )
    else:
        datalist = None

    return render_template("main/index.html", datalist=datalist)


@bp.route("/")
@bp.route("/index/", methods=["GET"])
def index():
    # print(f'index - current_user.is_authenticated: {current_user.is_authenticated}')

    if current_user.is_authenticated:
        # print(f'current_user.id: {current_user.id}')
        datalist = (
            Player.query.filter_by(user_id=current_user.id)
            .order_by(Player.last_used_date.desc())
            .join(Game)
            .add_columns(Game.id, Game.name, Player.last_used_date)
            .filter(Player.game_id == Game.id)
            .limit(20)
            .all()
        )

        # TODO - clear is_playing flag for invited users
        player_single = Player.query.filter_by(
            user_id=current_user.id, game_id=Game.id
        ).one()
        player_single.start_playing()
        db.session.commit()
    else:
        # TODO - if invited user, allow them to create a full user
        datalist = None

    return render_template("main/index.html", datalist=datalist)


# TODO - Security needs to check for a Player record
@bp.route("/game/<int:id>", methods=["GET"])
@login_required
def game(id):
    # print(f'game id: {id}')
    # print(f'game current_user.id: {current_user.id}')

    # TODO - When the user joins a game, need to trigger a playerlist update to all existing players
    player_single = Player.query.filter_by(user_id=current_user.id, game_id=id).one()
    player_single.start_playing()

    data_single = Game.query.filter_by(id=id).first_or_404()
    historylist = History.query.filter_by(game_id=data_single.id).order_by(
        History.add_date.desc()
    )

    playerlist = (
        Player.query.filter_by(game_id=data_single.id)
        .filter(Player.is_playing == True)
        .join(User)
        .add_columns(User.id, User.username)
        .filter(Player.user_id == User.id)
        .all()
    )
    invitedlist = (
        Player.query.filter_by(game_id=data_single.id)
        .join(User, isouter=True)
        .add_columns(User.id, User.username)
        .filter(Player.user_id == User.id)
    )

    print(invitedlist)

    return render_template(
        "main/game.html",
        datasingle=data_single,
        playerlist=playerlist,
        invitedlist=invitedlist,
        historylist=historylist,
    )


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("main/edit_profile.html", title="Edit Profile", form=form)


@bp.route("/inviteduser/<token>", methods=["GET"])
def inviteduser(token):
    print(f"token: {token}")
    # print(f'game current_user.id: {current_user.id}')

    # TODO - When the user joins a game, need to trigger a playerlist update to all existing players
    try:
        player_single = Player.query.filter_by(invite_token=token).one()
        player_single.start_playing()
    except:
        datalist = None
        flash("Your invitation is invalid or has expired.")
        return render_template("main/index.html", datalist=datalist)

    data_single = Game.query.filter_by(id=player_single.game_id).first_or_404()
    historylist = History.query.filter_by(game_id=data_single.id).order_by(
        History.add_date.desc()
    )

    playerlist = (
        Player.query.filter_by(game_id=data_single.id)
        .filter(Player.is_playing == True)
        .join(User)
        .add_columns(User.id, User.username)
        .filter(Player.user_id == User.id)
        .all()
    )
    invitedlist = Player.query.filter_by(game_id=data_single.id).all()

    return render_template(
        "main/game.html",
        datasingle=data_single,
        playerlist=playerlist,
        invitedlist=invitedlist,
        historylist=historylist,
    )
