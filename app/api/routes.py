from app import db, flask_api
from app.api import bp
from app.models import History, Game, User
from flask_restful import Resource, Api, reqparse, inputs
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
import json
# from app.auth.email import send_password_reset_email
# from flask import render_template, redirect, url_for, flash, request
# from flask_login import login_user, logout_user, current_user
# from werkzeug.urls import url_parse

# TODO - move PublishGameState() calls out of base REST endpoints and into special endpoints 

def GameState(id:int):
    # print(f"GameState(id:int): {id}")

    data_single = Game.query.filter_by(id=id).one()
    playerlist = User.query.filter_by(current_game_id=data_single.id).order_by(User.username.asc())
    players = {}
    for p in playerlist:
        players[p.username] = p.to_dict()

    historylist = History.query.filter_by(game_id=data_single.id).order_by(History.add_date.desc())
    history = {}
    for h in historylist:
        history[str(h.add_date)] = h.to_dict()

    game_dict = data_single.to_dict()
    game_dict['players'] = players
    game_dict['history'] = history
    game_json = json.dumps(game_dict)
    
    # print(f"game_json: {game_json}")
    return str(game_json)


def PublishGameState(id:int):
    # print(f'PublishGameState(id:int): {id}')
    import paho.mqtt.client as mqtt

    # def on_connect(mqttc, obj, flags, rc):
    #     print("rc: " + str(rc))

    # def on_publish(mqttc, obj, mid):
    #     print("mid: " + str(mid))

    mqttc = mqtt.Client()
    # mqttc.on_connect = on_connect
    # mqttc.on_publish = on_publish
    # Uncomment to enable debug messages
    # mqttc.on_log = on_log
    mqttc.connect("broker.hivemq.com", 1883, 60)
    infot = mqttc.publish(f"poker/view/{id}", GameState(id) , qos=2)
    infot.wait_for_publish()
    
    print(f'PublishGameState-end: channel=poker/{id}')
    return


# GAMES ---------------------------------------------
class GamesHistory(Resource):
    def post(self,id):
        parser = reqparse.RequestParser()
        parser.add_argument('story', type=str, required=True, help='Story problem (not required)')
        parser.add_argument('value', type=str, required=True, help='Value problem (not required)')
        parser.add_argument('add_date', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f'), required=False, help='add_date problem')
        args = parser.parse_args()
        # print(f'GamesAddHistory-post args: {args}')

        if args['add_date'] is None:
            args['add_date'] = datetime.now()

        data_single = History(
            game_id = id,
            story = args['story'],
            value = args['value'],
            add_date = args['add_date'],
        )
        
        try:
            db.session.add(data_single)
            db.session.flush()  # flush() so the id is populated after add
            db.session.commit()
        except:
            return {'msg':'Unknown error when trying to GamesAddHistory'}, 500  

        # print(f'GamesAddHistory-post return: {data_single.to_dict()}')
        PublishGameState(id)
        return data_single.to_dict(), 200

class GamesToggleVote(Resource):
    def put(self, id):
        try:
            data_single = Game.query.filter_by(id=id).one()
        except NoResultFound:
            return {'msg':f'No records found for id:{id}'}, 404
        except:
            return {'msg':f'Unknown error when trying to put Games id:{id}'}, 500   

        data_single.is_voting = not data_single.is_voting

        db.session.commit()
        # print(f'GamesToggleVote-put return: {data_single.to_dict()}')

        PublishGameState(id)
        return data_single.to_dict(), 200


class Games(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='name cannot be blank')
        parser.add_argument('last_used_date', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f'), required=False, help='last_used_date problem')
        parser.add_argument('is_active', type=bool, required=False,help='is_active problem (not required)')
        parser.add_argument('is_voting', type=bool, required=False, help='is_voting problem (not required)')
        parser.add_argument('owner_id', type=int, required=True, help='owner_id cannot be blank')
        parser.add_argument('story', type=str, required=False, help='story problem (not required)')
                
        args = parser.parse_args()
        # print(f'Games-post args: {args}')

        if args['last_used_date'] is None:
            args['last_used_date'] = datetime.now()
        if args['is_active'] is None:
            args['is_active'] = True
        if args['is_voting'] is None:
            args['is_voting'] = False

        data_single = Game(
            name = args['name'],
            last_used_date = args['last_used_date'],
            is_active = args['is_active'],
            is_voting = args['is_voting'],
            owner_id = args['owner_id'],
            story = args['story'],
        )

        try:
            db.session.add(data_single)
            db.session.flush()  # flush() so the id is populated after add
            db.session.commit()
        except:
            return {'msg':'Unknown error when trying to post Games'}, 500  

        # print(f'Games-post return: {data_single.to_dict()}')
        return data_single.to_dict(), 200

class GamesID(Resource):
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False, help='name problem (not required)')
        parser.add_argument('last_used_date', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f'), required=False, help='last_used_date problem (not required)')
        parser.add_argument('is_active', type=bool, required=False, help='is_active problem (not required)')
        parser.add_argument('is_voting', type=bool, required=False, help='is_voting problem (not required)')
        parser.add_argument('owner_id', type=int, required=False, help='owner_id problem (not required)')
        parser.add_argument('story', type=str, required=False, help='story problem (not required)')
        args = parser.parse_args()
        # print(f'Games-put args: {args}')

        try:
            data_single = Game.query.filter_by(id=id).one()
        except NoResultFound:
            return {'msg':f'No records found for id:{id}'}, 404
        except:
            return {'msg':f'Unknown error when trying to put Games id:{id}'}, 500   

        if args['name'] is not None:
            data_single.name = args['name']
        if args['last_used_date'] is not None:
            data_single.last_used_date = args['last_used_date']
        if args['is_active'] is not None:
            print(f'is_active setting to: {args["is_active"]}')
            data_single.is_active = args['is_active']
        if args['is_voting'] is not None:
            data_single.is_voting = args['is_voting']
        if args['owner_id'] is not None:
            data_single.owner_id = args['owner_id']
        if args['story'] is not None:
            data_single.story = args['story']

        db.session.commit()
        # print(f'Games-put return: {data_single.to_dict()}')
        return data_single.to_dict(), 200

    def get(self, id):
        try:
            data_single = Game.query.filter_by(id=id).one()
        except NoResultFound:
            return {'msg':f'No records found for id:{id}'}, 404
        except:
            return {'msg':f'Unknown error when trying to get Games id:{id}'}, 500   

        # print(f'Games-get return: {data_single.to_dict()}')
        return data_single.to_dict(), 200

    def delete(self, id):
        try:
            Game.query.filter_by(id=id).delete()
            db.session.commit()
        except:
            return {'msg':f'Unknown error when trying to delete Games id:{id}'}, 500   

        # print(f'Games-delete return: {data_single.to_dict()}')
        return {'msg':f'Game deleted id:{id}'}, 200



class GamesSetStory(Resource):
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('story', type=str, required=True, help='story problem (required)')
        args = parser.parse_args()
        # print(f'GamesSetStory-put args: {args}')

        try:
            data_single = Game.query.filter_by(id=id).one()
        except NoResultFound:
            return {'msg':f'No records found for id:{id}'}, 404
        except:
            return {'msg':f'Unknown error when trying to put Games id:{id}'}, 500   

        if args['story'] is not None:
            data_single.story = args['story']

        db.session.commit()
        # print(f'GamesSetStory-put return: {data_single.to_dict()}')

        PublishGameState(id)
        return data_single.to_dict(), 200


flask_api.add_resource(GamesToggleVote, '/games/<int:id>/togglevote')  # Put
flask_api.add_resource(GamesSetStory, '/games/<int:id>/setstory')  # Put
flask_api.add_resource(GamesHistory, '/games/<int:id>/history') # Task Specific Post
flask_api.add_resource(Games, '/games') # Post
flask_api.add_resource(GamesID, '/games/<int:id>')  # Put, Get, Delete


# USERS ---------------------------------------------
class UsersID(Resource):
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=False, help='username problem (not required)')
        parser.add_argument('email', type=str, required=False, help='email problem (not required)')
        parser.add_argument('vote', type=str, required=False, help='vote problem (not required)')
        parser.add_argument('about_me', type=str, required=False, help='about_me problem (not required)')
        parser.add_argument('last_seen', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f'), required=False, help='last_seen problem (not required)')
        parser.add_argument('current_game_id', type=int, required=False, help='current_game_id problem (not required)')
        args = parser.parse_args()
        # print(f'Users-put args: {args}')

        try:
            data_single = User.query.filter_by(id=id).one()
        except NoResultFound:
            return {'msg':f'No records found for id:{id}'}, 404
        except:
            return {'msg':f'Unknown error when trying to put Users id:{id}'}, 500   

        if args['username'] is not None:
            data_single.username = args['username']
        if args['email'] is not None:
            data_single.email = args['email']
        if args['vote'] is not None:
            data_single.vote = args['vote']
        if args['about_me'] is not None:
            data_single.about_me = args['about_me']
        if args['last_seen'] is not None:
            data_single.last_seen = args['last_seen']
        if args['current_game_id'] is not None:
            data_single.current_game_id = args['current_game_id']

        db.session.commit()
        # print(f'Users-put return: {data_single.to_dict()}')
        return data_single.to_dict(), 200

    def get(self, id):
        try:
            data_single = User.query.filter_by(id=id).one()
        except NoResultFound:
            return {'msg':f'No records found for id:{id}'}, 404
        except:
            return {'msg':f'Unknown error when trying to get Users id:{id}'}, 500   

        # print(f'User-get return: {data_single.to_dict()}')
        return data_single.to_dict(), 200

    def delete(self, id):
        try:
            User.query.filter_by(id=id).delete()
            db.session.commit()
        except:
            return {'msg':f'Unknown error when trying to delete Users id:{id}'}, 500   

        # print(f'Users-delete return: {data_single.to_dict()}')
        return {'msg':f'User deleted id:{id}'}, 200


class Users(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='username problem')
        parser.add_argument('email', type=str, required=True, help='email problem')
        parser.add_argument('vote', type=str, required=False, help='vote problem (not required)')
        parser.add_argument('about_me', type=str, required=False, help='about_me problem (not required)')
        parser.add_argument('last_seen', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f'), required=False, help='last_seen problem (not required)')
        parser.add_argument('current_game_id', type=int, required=False, help='current_game_id problem (not required)')
        args = parser.parse_args()

        # print(f'Users-post args: {args}')

        if args['last_seen'] is None:
            args['last_seen'] = datetime.now()
        if args['vote'] is None:
            args['vote'] = ""
        if args['about_me'] is None:
            args['about_me'] = ""
        if args['current_game_id'] is None:
            args['current_game_id'] = None

        data_single = User(
            username = args['username'],
            email = args['email'],
            vote = args['vote'],
            about_me = args['about_me'],
            last_seen = args['last_seen'],
            current_game_id = args['current_game_id'],
        )
        data_single.set_password('test')

        try:
            db.session.add(data_single)
            db.session.flush()  # flush() so the id is populated after add
            db.session.commit()
        except:
            return {'msg':'Unknown error when trying to post Users'}, 500  

        # print(f'Users-post return: {data_single.to_dict()}')
        return data_single.to_dict(), 200

class UsersVote(Resource):
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('vote', type=str, required=True, help='vote problem (required)')
        parser.add_argument('current_game_id', type=int, required=True, help='current_game_id problem (required)')
        args = parser.parse_args()
        # print(f'UsersVote-put args: {args}')

        try:
            data_single = User.query.filter_by(id=id).one()
        except NoResultFound:
            return {'msg':f'No records found for id:{id}'}, 404
        except:
            return {'msg':f'Unknown error when trying to put Users id:{id}'}, 500   

        if args['vote'] is not None:
            data_single.vote = args['vote']
        if args['current_game_id'] is not None:
            data_single.current_game_id = args['current_game_id']

        db.session.commit()
        # print(f'Users-put return: {data_single.to_dict()}')

        PublishGameState(data_single.current_game_id)
        return data_single.to_dict(), 200

flask_api.add_resource(UsersID, '/users/<int:id>') # Put, Get, Delete
flask_api.add_resource(Users, '/users')  # Post
flask_api.add_resource(UsersVote, '/users/<int:id>/vote')  # Put

# ---------------------------------------------
# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.list'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('.login'))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get('next')
#         if not next_page or url_parse(next_page).netloc != '':
#             next_page = url_for('main.list')
#         return redirect(next_page)
#     return render_template('auth/login.html', title='Sign In', form=form)


# @bp.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('main.list'))


# @bp.route('/register', methods=['GET', 'POST'])
# def register():
#     print('register top')
#     if current_user.is_authenticated:
#         return redirect(url_for('main.list'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('.login'))
#     return render_template('auth/register.html', title='Register', form=form)


# @bp.route('/reset_password_request', methods=['GET', 'POST'])
# def reset_password_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.list'))
#     form = ResetPasswordRequestForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user:
#             send_password_reset_email(user)
#         flash('Check your email for the instructions to reset your password')
#         return redirect(url_for('.login'))
#     return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


# @bp.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('main.list'))
#     user = User.verify_reset_password_token(token)
#     if not user:
#         return redirect(url_for('main.list'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         user.set_password(form.password.data)
#         db.session.commit()
#         flash('Your password has been reset.')
#         return redirect(url_for('.login'))
#     return render_template('auth/reset_password.html', form=form)


# # ---------------------------------------------------------
# @bp.route('/edit/<int:id>', methods=["GET", "POST"])
# # @login_required
# def edit(id):
#     form = SessionForm()
#     if request.method == "POST" and form.validate_on_submit():
#         data_single = Session.query.filter_by(id=id).first_or_404()
#         # before = str(data_single.to_dict())
#         data_single.name = request.form['name']
#         data_single.is_active = 'is_active' in request.form

#         # after = str(data_single.to_dict())
#         # writeaudit(data_single.id, before, after)
#         db.session.commit()
#         return redirect(url_for('.view', id=data_single.id))

#     if request.method == 'GET':
#         data_single = Session.query.filter_by(id=id).first_or_404()
#         form.load(data_single)
#     return render_template('main/edit.html', form=form)
