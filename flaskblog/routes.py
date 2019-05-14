from flask import  render_template, redirect, url_for, request, flash,current_app,abort
from flask_login import login_user, login_required,logout_user,current_user
from flaskblog import app, bcrypt,db,search
from .forms import SignUpForm,LoginForm,PostForm
from .models import User, Post,Comments
import os 
import secrets


def save_photo(photo):
    rand_hex  = secrets.token_hex(10)
    _, file_extention = os.path.splitext(photo.filename)
    file_name = rand_hex + file_extention
    file_path = os.path.join(current_app.root_path, 'static/images', file_name)
    photo.save(file_path)
    return file_name


@app.route('/')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    popularpost = Post.query.order_by(Post.views.desc()).limit(3)
    return render_template('post/index.html', posts=posts, popularpost=popularpost)


@app.route('/news/<string:slug>', methods=['POST','GET'])
def news(slug):
    post = Post.query.filter_by(slug=slug).first()
    popularpost = Post.query.order_by(Post.views.desc()).limit(3)
    comment = Comments.query.filter_by(post_id=post.id).filter_by(feature=True).all()
    post.views = post.views + 1
    db.session.commit()
    
    if request.method =="POST":
        post_id = post.id
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        comment = Comments(name=name,email=email,message=message,post_id=post_id)
        db.session.add(comment)
        post.comments = post.comments + 1
        db.session.commit()
        flash('Your comment has been submited  submitted will be published after aproval of admin', 'success')
        return redirect(request.url)

    return render_template('post/news-details.html', post=post, comment=comment, popularpost=popularpost)


@app.route('/search')
def search():
    keyword = request.args.get('q')
    posts = Post.query.msearch(keyword,fields=['title'],limit=6)
    return render_template('post/search.html', posts=posts)
    

@app.route('/admin')
@login_required
def admin():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('admin/home.html',posts = posts)


@app.route('/comments/', methods=['POST','GET'])
def comments():
    comments =Comments.query.order_by(Comments.id.desc()).all()
    return render_template('admin/comment.html',comments=comments)


@app.route('/check/<int:id>', methods=['POST','GET'])
@login_required
def check(id):
    comment = Comments.query.get_or_404(id)
    if (comment.feature == True):
        comment.feature = False
        db.session.commit()
    else:
        comment.feature = True
        db.session.commit()
        return redirect(url_for('comments')) 
    return redirect(url_for('comments'))


@app.route('/addpost',methods=['POST','GET'])
@login_required
def addpost():
    form = PostForm(request.form)
    if request.method =="POST" and form.validate():
        photo = save_photo(request.files.get('photo'))
        post = Post(title=form.title.data, body=form.content.data,category=request.form.get('category'),image=photo,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added ','success')
        return redirect(url_for('admin'))
    return render_template('admin/addpost.html', form=form)


@app.route('/update/<int:id>',methods=['POST','GET'])
@login_required
def update(id):
    form = PostForm(request.form)
    post = Post.query.get_or_404(id)
    form.title.data = post.title 
    form.content.data = post.body
    if request.method=='POST' and form.validate():
        if request.files.get('photo'):     
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/'+ post.image))
                post.image = save_photo(request.files.get('photo'))
            except:
                post.image = save_photo(request.files.get('photo'))
        post.title = form.title.data
        post.body = form.content.data
        post.category = request.form.get('category')
        flash('Post has been updated', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('admin/addpost.html', form=form, post=post)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    try:
        os.unlink(os.path.join(current_app.root_path,'static/images/'+ post.image))
        db.session.delete(post)
    except:
        db.session.delete(post)
    flash('Post has deleted ','success')
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delcomment/<int:id>')
@login_required
def delcomment(id):
    comment = Comments.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has deleted ','success')
    return redirect(url_for('admin'))


@app.route('/signup', methods=['POST','GET'])
def signup():
    form = SignUpForm(request.form)
    if request.method == 'POST' and form.validate():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data,username=form.username.data, email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering, you able to login now','success')
        return redirect(url_for('login'))
    return render_template('admin/signup.html', form=form)



@app.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        next = request.args.get('next')
        return redirect(next or url_for('admin'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash('This user not exists','warning')
            return redirect(url_for('login'))
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.','success')
            next = request.args.get('next')
            return redirect(next or url_for('admin'))
        flash('Invalid password','danger')
    return render_template('admin/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you are logout','success')
    return redirect(url_for('login'))
    