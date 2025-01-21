from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myblogsite.db'
db = SQLAlchemy(app)

# Models for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # Define the relationship with the Friendship table (sent requests)
    friendships_as_user = db.relationship('Friendship', 
                                         foreign_keys='Friendship.user_id', 
                                         back_populates='user',  # Use back_populates instead of backref
                                         lazy='dynamic')
    
    # Define the relationship with the Friendship table (received requests)
    friendships_as_friend = db.relationship('Friendship', 
                                           foreign_keys='Friendship.friend_id', 
                                           back_populates='friend',  # Use back_populates instead of backref
                                           lazy='dynamic')
    
    @property
    def friends(self):
        return [f.friend for f in self.friendships_as_user if f.status == 'accepted'] + \
               [f.user for f in self.friendships_as_friend if f.status == 'accepted']


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # "pending", "accepted", "rejected"

    # Explicitly define the back_populates in both models
    user = db.relationship('User', foreign_keys=[user_id], back_populates='friendships_as_user')  # Link to User (sent requests)
    friend = db.relationship('User', foreign_keys=[friend_id], back_populates='friendships_as_friend')  # Link to User (received requests)



class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route('/')
def home():
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()
        posts = Post.query.all()  # Fetch posts to display
        return render_template('index.html', posts=posts)
    return redirect(url_for('login'))

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = User.query.filter_by(username=session['user']).first().id
        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    
    return render_template('post.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            return redirect(url_for('home'))
        else:
            return "Login Failed"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/send_friend_request/<int:friend_id>')
def send_friend_request(friend_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['user']).first()
    friend = User.query.get(friend_id)
    if user and friend:
        request_exist = Friendship.query.filter_by(user_id=user.id, friend_id=friend.id, status="pending").first()
        if not request_exist:
            friend_request = Friendship(user_id=user.id, friend_id=friend.id, status="pending")
            db.session.add(friend_request)
            db.session.commit()
    return redirect(url_for('home'))

@app.route('/accept_friend_request/<int:friend_request_id>')
def accept_friend_request(friend_request_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    friend_request = Friendship.query.get(friend_request_id)
    if friend_request and friend_request.status == "pending":
        friend_request.status = "accepted"
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['user']).first()
    friend_requests = Friendship.query.filter_by(friend_id=user.id, status="pending").all()
    return render_template('profile.html', user=user, friend_requests=friend_requests)

@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['user']).first()
    post = Post.query.get(post_id)
    if user and post:
        like_exist = Like.query.filter_by(user_id=user.id, post_id=post.id).first()
        if not like_exist:
            like = Like(user_id=user.id, post_id=post.id)
            db.session.add(like)
            db.session.commit()
    return redirect(url_for('home'))

@app.route('/comment_post/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    user = User.query.filter_by(username=session['user']).first()
    post = Post.query.get(post_id)
    if user and post and content:
        comment = Comment(content=content, post_id=post.id, user_id=user.id)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/send_message/<int:receiver_id>', methods=['POST'])
def send_message(receiver_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    user = User.query.filter_by(username=session['user']).first()
    receiver = User.query.get(receiver_id)
    if user and receiver and content:
        message = Message(sender_id=user.id, receiver_id=receiver.id, content=content)
        db.session.add(message)
        db.session.commit()
    return redirect(url_for('profile'))

@app.route('/inbox')
def inbox():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['user']).first()
    received_messages = Message.query.filter_by(receiver_id=user.id).all()
    return render_template('inbox.html', received_messages=received_messages)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
