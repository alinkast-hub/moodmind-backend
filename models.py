
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    subscription_type = db.Column(db.String(20), default='free')  # 'free' or 'premium'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'subscription_type': self.subscription_type,
            'created_at': self.created_at.isoformat()
        }

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)  # 1-10 scale
    emotions = db.Column(db.Text)  # JSON string of detected emotions
    ai_response = db.Column(db.Text)  # AI-generated supportive response
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_emotions(self, emotions_dict):
        self.emotions = json.dumps(emotions_dict)

    def get_emotions(self):
        return json.loads(self.emotions) if self.emotions else {}

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'mood_score': self.mood_score,
            'emotions': self.get_emotions(),
            'ai_response': self.ai_response,
            'created_at': self.created_at.isoformat()
        }

class DailyUsage(db.Model):
    __tablename__ = 'daily_usage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    entry_count = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'entry_count': self.entry_count
        }
