from datetime import datetime
from flaskone import db, login_manager
from flask_login import UserMixin
from flaskone import app
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey,orm




@login_manager.user_loader
def load_user(user_id):

    return User.query.get(user_id)


friendship = db.Table('friendship',
db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
db.Column('friend_id', db.Integer, db.ForeignKey('user.id')),
)
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    friends = relationship("User", secondary=friendship, 
                           primaryjoin=id==friendship.c.user_id,
                           secondaryjoin=id==friendship.c.friend_id,
                           backref=db.backref('friendz',lazy='dynamic'),
    )
    # def __repr__(self):
    #     return f"User('{self.username}', '{self.email}', '{self.image_file}')"

# class Friend(db.Model):
#     id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
#     friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
#     status = db.Column(db.String(10))
#     request_sent_timestamp = db.Column(db.DateTime)
    # request_response_timestamp = db.Column(db.DateTime)




class Post(db.Model):
    # __searchable__ = ['title', 'content']  # these fields will be indexed by whoosh
     
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref="Posts")

    # def __repr__(self):
    #     return f"Post('{self.title}', '{self.date_posted}')"

