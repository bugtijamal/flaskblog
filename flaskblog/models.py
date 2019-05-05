from flaskblog import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import event
from slugify import slugify

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200),  nullable=False)
    profile = db.Column(db.String(180),  default="profile.jpg")

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    __searchable__ = ['title', 'body']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(150), nullable=False, default='no-image.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts',lazy=True, passive_deletes=True))
    views = db.Column(db.Integer,default=0)
    comments = db.Column(db.Integer,default=0)
    feature = db.Column(db.String, default=1, nullable=False)
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r' % self.title

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)
db.event.listen(Post.title, 'set',Post.generate_slug, retval=False)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(200), unique=False, nullable=False)
    message = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    post = db.relationship('Post', backref=db.backref('posts',lazy=True, passive_deletes=True))
    feature = db.Column(db.Boolean, default=False, nullable=False)
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r' % self.name
