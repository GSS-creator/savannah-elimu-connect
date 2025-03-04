from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, abort
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
from werkzeug import urls
from werkzeug.utils import secure_filename
from decimal import Decimal
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

db = SQLAlchemy()

# Association tables
friendships = db.Table('friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

business_connections = db.Table('business_connections',
    db.Column('requester_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('receiver_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('status', db.String(20), default='pending'),  # pending, accepted, rejected
    db.Column('connection_date', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone_number = db.Column(db.String(15), unique=True)
    registration_code = db.Column(db.String(10), unique=True)
    is_verified = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    bio = db.Column(db.Text)
    location = db.Column(db.String(64))
    country = db.Column(db.String(64))
    profile_picture = db.Column(db.String(120))
    terms_accepted = db.Column(db.Boolean, default=False)
    terms_accepted_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    preferred_language = db.Column(db.String(10), default='en')
    
    # Business Profile Fields
    company_name = db.Column(db.String(128))
    job_title = db.Column(db.String(64))
    industry = db.Column(db.String(64))
    company_size = db.Column(db.String(32))
    business_type = db.Column(db.String(32))  # Entrepreneur, Investor, Business Leader
    investment_interests = db.Column(db.Text)
    expertise_areas = db.Column(db.Text)
    looking_for = db.Column(db.Text)  # What the user is looking for in connections
    linkedin_profile = db.Column(db.String(128))
    
    # Relationships
    friends = db.relationship('User', 
                            secondary=friendships,
                            primaryjoin=(friendships.c.user_id == id),
                            secondaryjoin=(friendships.c.friend_id == id),
                            backref=db.backref('friend_of', lazy='dynamic'),
                            lazy='dynamic')
    
    business_network = db.relationship('User',
                                     secondary=business_connections,
                                     primaryjoin=(business_connections.c.requester_id == id),
                                     secondaryjoin=(business_connections.c.receiver_id == id),
                                     backref=db.backref('connected_with', lazy='dynamic'),
                                     lazy='dynamic')
    
    groups = db.relationship('Group', secondary=group_members, backref='group_members')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    opportunities = db.relationship('BusinessOpportunity', backref='creator', lazy='dynamic')
    reviews = db.relationship('Review', 
                            foreign_keys='Review.reviewer_id',
                            backref='reviewer',
                            lazy='dynamic')
    taught_courses = db.relationship('Course',
                                   foreign_keys='Course.instructor_id',
                                   backref=db.backref('instructor', lazy='joined'),
                                   lazy='dynamic')
    enrolled_courses = db.relationship('CourseEnrollment',
                                     foreign_keys='CourseEnrollment.student_id',
                                     backref=db.backref('enrolled_student', lazy='joined'),
                                     lazy='dynamic')
    course_feedback = db.relationship('CourseReview',
                                    foreign_keys='CourseReview.student_id',
                                    back_populates='student',
                                    lazy='dynamic')
    uploaded_resources = db.relationship('Resource',
                                       foreign_keys='Resource.uploader_id',
                                       backref=db.backref('resource_owner', lazy='joined'),
                                       lazy='dynamic')
    organized_events = db.relationship('Event',
                                     foreign_keys='Event.organizer_id',
                                     backref=db.backref('event_creator', lazy='joined'),
                                     lazy='dynamic')
    event_signups = db.relationship('EventRegistration', 
                                  foreign_keys='EventRegistration.participant_id',
                                  lazy='dynamic')
    event_feedback = db.relationship('EventReview',
                                   foreign_keys='EventReview.reviewer_id',
                                   backref=db.backref('feedback_author', lazy='joined'),
                                   lazy='dynamic')
    support_issues = db.relationship('SupportTicket',
                                   foreign_keys='SupportTicket.user_id',
                                   backref=db.backref('ticket_owner', lazy='joined'),
                                   lazy='dynamic')
    ai_conversations = db.relationship('AIChat',
                                     foreign_keys='AIChat.user_id',
                                     backref=db.backref('chat_owner', lazy='joined'),
                                     lazy='dynamic')
    sent_messages = db.relationship('Message',
                                  foreign_keys='Message.sender_id',
                                  backref=db.backref('message_sender', lazy='joined'),
                                  lazy='dynamic')
    received_messages = db.relationship('Message',
                                      foreign_keys='Message.receiver_id',
                                      backref=db.backref('message_receiver', lazy='joined'),
                                      lazy='dynamic')
    saved_locations = db.relationship('UserLocation',
                                    foreign_keys='UserLocation.user_id',
                                    backref=db.backref('location_owner', lazy='joined'),
                                    lazy='dynamic')
    products_listed = db.relationship('Product',
                                    foreign_keys='Product.seller_id',
                                    backref=db.backref('product_owner', lazy='joined'),
                                    lazy='dynamic')
    purchases = db.relationship('Order',
                              foreign_keys='Order.buyer_id',
                              backref=db.backref('order_buyer', lazy='joined'),
                              lazy='dynamic')
    sales = db.relationship('Order',
                          foreign_keys='Order.seller_id',
                          backref=db.backref('order_seller', lazy='joined'),
                          lazy='dynamic')
    
    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
        
    @staticmethod
    def generate_unique_code():
        """Generate a unique 8-character registration code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not User.query.filter_by(registration_code=code).first():
                return code
    
    def add_business_connection(self, user):
        if not self.is_business_connected(user):
            connection = BusinessConnection(requester=self, receiver=user)
            db.session.add(connection)
            return True
        return False
    
    def is_business_connected(self, user):
        return BusinessConnection.query.filter(
            ((BusinessConnection.requester_id == self.id) & (BusinessConnection.receiver_id == user.id)) |
            ((BusinessConnection.requester_id == user.id) & (BusinessConnection.receiver_id == self.id))
        ).first() is not None

    def set_language(self, language_code):
        self.preferred_language = language_code
        db.session.commit()

class BusinessConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')
    connection_date = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.Text)
    
    requester = db.relationship('User', foreign_keys=[requester_id], backref='business_connection_requester')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='business_connection_receiver')

class BusinessOpportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    opportunity_type = db.Column(db.String(32))  # Investment, Partnership, Mentorship, Job
    industry = db.Column(db.String(64))
    location = db.Column(db.String(64))
    investment_range = db.Column(db.String(64))
    requirements = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(32), default='open')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    applications = db.relationship('OpportunityApplication', backref='opportunity', lazy='dynamic')

class OpportunityApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('business_opportunity.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pitch = db.Column(db.Text)
    status = db.Column(db.String(32), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applicant = db.relationship('User', backref='opportunity_applicant')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    posts = db.relationship('Post', backref='group', lazy='dynamic')
    
    def add_member(self, user):
        if user not in self.members:
            self.members.append(user)
            return True
        return False
    
    def remove_member(self, user):
        if user in self.members:
            self.members.remove(user)
            return True
        return False

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    
    comments = db.relationship('Comment', backref='post_comments', lazy='dynamic')
    likes = db.relationship('Like', backref='post_likes', lazy='dynamic')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    images = db.Column(db.Text)
    location = db.Column(db.String(100))
    condition = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)
    
    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['active', 'inactive', 'sold', 'pending_approval']
        if status not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of: {valid_statuses}')
        return status

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref=db.backref('product_orders', lazy='dynamic'))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer)
    price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def get_progress(self, user):
        enrollment = CourseEnrollment.query.filter_by(course_id=self.id, student_id=user.id).first()
        if not enrollment:
            return 0
        completed_lessons = LessonCompletion.query.filter_by(enrollment_id=enrollment.id).count()
        total_lessons = self.lessons.count()
        return (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

    def get_rating(self):
        ratings = [review.rating for review in self.reviews]
        return sum(ratings) / len(ratings) if ratings else 0

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer)
    content_type = db.Column(db.String(20), nullable=False)
    video_url = db.Column(db.String(200))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref=db.backref('course_lessons', order_by='Lesson.order'))

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    lesson = db.relationship('Lesson', backref='lesson_quizzes')
    
    questions = db.relationship('QuizQuestion', backref='quiz_questions', cascade='all, delete-orphan')

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # multiple_choice, true_false, etc
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    points = db.Column(db.Integer, default=1)
    order = db.Column(db.Integer, nullable=False)
    
    options = db.relationship('QuizOption',
                            foreign_keys='QuizOption.question_id',
                            backref=db.backref('question_options', lazy='joined'),
                            lazy='dynamic',
                            order_by='QuizOption.order')

class QuizOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False)

class CourseEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # Payment info
    payment_status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    
    # Relationships
    course = db.relationship('Course', backref='course_enrollments')
    completed_lessons = db.relationship('LessonCompletion', backref='enrollment_lessons')

class LessonCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollment.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    lesson = db.relationship('Lesson', backref='lesson_completions')

class CourseReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    course = db.relationship('Course', backref='course_reviews')
    student = db.relationship('User', 
                            foreign_keys=[student_id],
                            back_populates='course_feedback')

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(200))
    resource_type = db.Column(db.String(50))
    language = db.Column(db.String(50))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref='course_resources')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    max_participants = db.Column(db.Integer)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    registrations = db.relationship('EventRegistration',
                                  foreign_keys='EventRegistration.event_id',
                                  backref=db.backref('event_registrations', lazy='joined'),
                                  lazy='dynamic')
    reviews = db.relationship('EventReview',
                            foreign_keys='EventReview.event_id',
                            backref=db.backref('event_reviews', lazy='joined'),
                            lazy='dynamic')

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, cancelled, attended

class EventReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    speaker = db.Column(db.String(200))
    
    event = db.relationship('Event', backref='event_schedules')

class EventSpeaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(200))
    organization = db.Column(db.String(200))
    role = db.Column(db.String(200))
    social_links = db.Column(db.JSON)
    
    event = db.relationship('Event', backref='event_speakers')

class EventDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(50))
    is_public = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    event = db.relationship('Event', backref='event_documents')

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='normal')
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # For anonymous users
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))

class AIChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    is_ai = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))
    conversation_id = db.Column(db.String(100))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100))
    url = db.Column(db.String(500))
    published_at = db.Column(db.DateTime)
    category = db.Column(db.String(50))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PoliticalEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    category = db.Column(db.String(50))
    source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': self.city,
            'country': self.country,
            'region': self.region,
            'last_updated': self.last_updated.isoformat()
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
