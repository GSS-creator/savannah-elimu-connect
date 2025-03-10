from app import app, db
from models import User, Group, Post, Comment, Like, Product, Order, Review, Message, NewsArticle, PoliticalEvent, WeatherData, UserLocation, Resource

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 