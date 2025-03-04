from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit
import logging
import os
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-please-change'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy(app)
login = LoginManager(app)
socketio = SocketIO(app)
login.login_view = 'login'

# Define supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'sw': 'Swahili',
    'ar': 'Arabic'
}

openai.api_key = 'your-openai-api-key'  # You'll need to set this up securely

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    preferred_language = db.Column(db.String(10), default='en')
    auto_translate = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, default='')
    email_notifications = db.Column(db.Boolean, default=True)
    sound_notifications = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    avatar = db.Column(db.String(200))  # Path to avatar file

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    language = db.Column(db.String(10))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(200))  # Path to icon file
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    joined_at = db.Column(db.DateTime, server_default=db.func.now())
    is_admin = db.Column(db.Boolean, default=False)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/chat')
@login_required
def chat():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('chat.html', 
                         users=users, 
                         supported_languages=SUPPORTED_LANGUAGES)

@app.route('/ai_chat')
@login_required
def ai_chat():
    return render_template('ai_chat.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Language preferences
        language = request.form.get('preferred_language')
        auto_translate = request.form.get('auto_translate') == 'on'
        
        # Profile settings
        bio = request.form.get('bio')
        profile_picture = request.files.get('profile_picture')
        
        # Notification settings
        email_notifications = request.form.get('email_notifications') == 'on'
        sound_notifications = request.form.get('sound_notifications') == 'on'
        
        # Update user settings
        if language in SUPPORTED_LANGUAGES:
            current_user.preferred_language = language
        current_user.auto_translate = auto_translate
        current_user.bio = bio
        current_user.email_notifications = email_notifications
        current_user.sound_notifications = sound_notifications
        
        if profile_picture:
            # TODO: Handle profile picture upload
            pass
        
        try:
            db.session.commit()
            flash('Settings updated successfully')
        except Exception as e:
            db.session.rollback()
            flash('Error updating settings: ' + str(e))
        
        return redirect(url_for('settings'))
    
    return render_template('settings.html', supported_languages=SUPPORTED_LANGUAGES)

@app.route('/resources')
@login_required
def resources():
    return render_template('resources.html')

@app.route('/update_language', methods=['POST'])
@login_required
def update_language():
    data = request.get_json()
    language = data.get('language')
    if language in SUPPORTED_LANGUAGES:
        current_user.preferred_language = language
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid language'}), 400

@app.route('/get_messages/<int:user_id>')
@login_required
def get_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp).all()
    
    return jsonify([{
        'sender_id': msg.sender_id,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            logger.debug(f"Registration attempt - Username: {username}, Email: {email}")
            
            if not username or not email or not password:
                flash('Please fill in all fields')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))
            
            user = User(username=username, email=email)
            user.set_password(password)
            logger.debug("Created user object, attempting database commit")
            
            db.session.add(user)
            db.session.commit()
            logger.debug("Database commit successful")
            
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash(f'An error occurred during registration: {str(e)}')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', 
                         user=user, 
                         supported_languages=SUPPORTED_LANGUAGES,
                         title=f"{username}'s Profile")

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form.get('group_name')
        description = request.form.get('group_description')
        members = request.form.getlist('members')
        icon = request.files.get('group_icon')
        
        if not name:
            flash('Group name is required')
            return redirect(url_for('create_group'))
            
        try:
            # Create new group
            group = Group(
                name=name,
                description=description,
                created_by=current_user.id
            )
            
            # Handle icon upload if provided
            if icon:
                filename = secure_filename(icon.filename)
                icon_path = os.path.join('static', 'group_icons', filename)
                icon.save(os.path.join(app.root_path, icon_path))
                group.icon = icon_path
            
            db.session.add(group)
            db.session.flush()  # Get group ID
            
            # Add creator as admin
            creator_member = GroupMember(
                group_id=group.id,
                user_id=current_user.id,
                is_admin=True
            )
            db.session.add(creator_member)
            
            # Add other members
            for member_id in members:
                member = GroupMember(
                    group_id=group.id,
                    user_id=int(member_id)
                )
                db.session.add(member)
            
            db.session.commit()
            flash('Group created successfully!')
            return redirect(url_for('chat'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating group: {str(e)}')
            return redirect(url_for('create_group'))
    
    users = User.query.all()
    return render_template('create_group.html', users=users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@socketio.on('send_message')
def handle_message(data):
    if not current_user.is_authenticated:
        return
    
    message = Message(
        sender_id=current_user.id,
        recipient_id=data['recipient_id'],
        content=data['message'],
        language=data.get('language', 'en')
    )
    db.session.add(message)
    db.session.commit()
    
    emit('receive_message', {
        'sender_id': current_user.id,
        'message': message.content,
        'timestamp': message.timestamp.isoformat(),
        'language': message.language
    }, room=data['recipient_id'])

def get_web_data(query):
    try:
        # Use DuckDuckGo for web search
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Get search results
        for result in soup.find_all('div', class_='result'):
            title = result.find('h2').text if result.find('h2') else ''
            snippet = result.find('div', class_='snippet').text if result.find('div', class_='snippet') else ''
            if title and snippet:
                results.append(f"{title}: {snippet}")
        
        return "\n".join(results[:3])  # Return top 3 results
    except Exception as e:
        return f"Error fetching web data: {str(e)}"

def get_ai_response(query, web_data):
    try:
        # Combine web data with the query for context
        prompt = f"""Based on this web data:
{web_data}

Please answer this question: {query}
Answer in a friendly, helpful way and cite sources when possible."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that provides accurate information based on web data."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating AI response: {str(e)}"

@app.route('/ai_assistant', methods=['POST'])
@login_required
def ai_assistant():
    data = request.get_json()
    query = data.get('query', '')
    
    # Get web data
    web_data = get_web_data(query)
    
    # Get AI response
    ai_response = get_ai_response(query, web_data)
    
    return jsonify({
        'response': ai_response,
        'sources': web_data
    })

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        logger.debug("Dropped all existing tables")
        
        # Create database tables
        db.create_all()
        logger.debug("Database tables created successfully")

if __name__ == '__main__':
    # Initialize the database
    init_db()
    socketio.run(app, debug=True)
