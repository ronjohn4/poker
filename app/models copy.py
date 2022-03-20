# https://flask-migrate.readthedocs.io/
# make sure db is not open in editor
# make sure db is not in use by the bag

# one time creation of the migrations folder
#   flask db init

# commit current changes to the model and build the migration scriptpip in
#   flask db migrate -m "comment"  #double quotes

# execute the migration script
#   flask db upgrade

# Good article on cascade
# https://dev.to/zchtodd/sqlalchemy-cascading-deletes-8hk
# alembic doesn't handle alter on MySQL, need to delete and rebuild


from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import login
from datetime import datetime, timedelta
from hashlib import md5
import jwt
from time import time
import os
# from sqlalchemy.orm import sessionmaker, 
from sqlalchemy.orm import relationship
import base64


# --------------------------------------------------
games_schema = {
        "$schema":"http://json-schema.org/draft-04/schema#",

        "type" : "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "last_used_date": {"type": "string"},
            "is_active": {"type": "boolean"},
            "is_voting": {"type": "boolean"},
            "owner_id": {"type": "integer"},
            "story": {"type": "string"},        
        },
        "required": ["id","name","last_used_date","is_active","is_voting","owner_id"]
    }



# --------------------------------------------------
class Game(db.Model):
    __tablename__ = 'game'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    last_used_date = db.Column(db.DateTime(timezone=True))
    is_active = db.Column(db.Boolean)
    is_voting = db.Column(db.Boolean)
    history = relationship("History", cascade="all, delete", passive_deletes=True)
    players = relationship("User", cascade="all, delete", passive_deletes=True, foreign_keys="[User.current_game_id]", lazy="dynamic")
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    story = db.Column(db.String(64))

    def __repr__(self):
        return '<Game {}>'.format(self.name)

    def to_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
            "last_used_date": self.last_used_date.strftime('%Y-%m-%d %H:%M:%S.%f'),
            "is_active": self.is_active,
            "is_voting": self.is_voting,
            "owner_id": self.owner_id,
            "story": self.story
        }
        # print(f'Game Model to_dict() data: {data}')
        return data


# --------------------------------------------------
class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id', ondelete="cascade"), nullable=False)
    story = db.Column(db.String)
    value = db.Column(db.String)
    add_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<History {}>'.format(self.id)

    def to_dict(self):
        data = {
            "id": self.id,
            "game_id": self.game_id,
            "story": self.story,
            "value": self.value,
            "add_date" : self.add_date.strftime('%Y-%m-%d %H:%M:%S.%f')
        }
        # print(f'History Model to_dict() data: {data}')
        return data


# --------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    vote = db.Column(db.String(10))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    current_game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)

 
    def __repr__(self):
        return '<User {}>'.format(self.username)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


    def get_reset_password_token(self, expires_in=600):
        print(f'self.id={self.id}')
        print(f'expires_in={expires_in}')
        print(f'SECRET_KEY={current_app.config["SECRET_KEY"]}')

        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256')



    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'vote': self.vote,
            'about_me': self.about_me,
            'last_seen': self.last_seen.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'current_game_id': self.current_game_id
        }
        # print(f'User Model to_dict() data: {data}')
        return data


    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token


    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)


    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
