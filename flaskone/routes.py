from flask import render_template,redirect,url_for,request
from flaskone import app, db, bcrypt
from flaskone.forms import RegistrationForm,LoginForm,PostForm,SearchForm
from flaskone.models import User,Post
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by(desc(Post.date_posted)).limit(5).all()
    return render_template('home.html', posts=posts)


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registration.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))



# After Login 

# Account show the User Posts only

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(desc(Post.date_posted))
    user = User.query.filter_by(id=current_user.id).first()
    form = SearchForm()
    print('post valid',request.method)
    if request.method == 'POST':
    	if form.validate_on_submit():
    		users = User.query.filter(User.username.like('%'+form.key.data+'%'))
    		if users:
    			return render_template('account.html', title='search',posts=posts,user =user,form=form,users=users)
    else:
    	return render_template('account.html', title='Account',posts=posts,user =user,form=form)


# Post Related process Create new post Update post and Delete post allso 

#Create new post 
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_post.html', title='New Post',
                           form=form, legend='New Post')

@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

# Update Post 
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('new_post.html', title='Update Post',
                           form=form, legend='Update Post')

# Delete Post
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/search", methods=['GET','POST'])
@login_required
def search():
	form = SearchForm()
	if request.method == 'POST':
		if form.validate_on_submit():
		 	posts = Post.query.filter((Post.title.like('%'+form.key.data+'%'))|(Post.content.like('%'+form.key.data+'%')))
		 	users = User.query.filter(User.username.like('%'+form.key.data+'%'))
			if len(posts.all())>0:
				return render_template('search.html',title='author',form=form, posts=posts.all())
			elif users:
				all_post=[]
				for user in users:
					post=[]
					for posts in user.posts:
						post.append(posts)
					all_post.extend(post)
				return render_template('search.html',title='author',form=form, posts=all_post)
	return render_template('search.html',title='get',form=form)


    

@app.route("/user/<int:user_id>")
@login_required
def user(user_id):
	user = User.query.get(user_id)
	friend=''
	for frd in current_user.friends:
		if frd==user:
			friend=frd		
	return render_template('user.html',user=user,posts=user.posts,friend=friend)


@app.route("/add/<int:user_id>")
@login_required
def addfriend(user_id):
	user = User.query.get(user_id)
	user.friendz.append(current_user)
	db.session.commit()
	friend=''
	for frd in current_user.friends:
		if frd==user:
			friend=frd		
	return render_template('user.html',user=user,posts=user.posts,friend=friend)


@app.route("/account/friends", methods=['GET','POST'])
@login_required
def friends():
    user = User.query.filter_by(id=current_user.id).first()
    form = SearchForm()
    if request.method == 'POST':
    	if form.validate_on_submit():
    		users = User.query.filter(User.username.like('%'+form.key.data+'%'))
    		if users:
    			return render_template('friends.html', title='search',user=user,form=form,users=users)
    else:
    	return render_template('friends.html', title='friends',user =user,form=form)

