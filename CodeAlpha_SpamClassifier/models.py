from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Classification(db.Model):
    """
    Store all email classifications made by the system
    """
    __tablename__ = 'classifications'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_spam = db.Column(db.Boolean, nullable=False)
    spam_confidence = db.Column(db.Float, nullable=False)
    not_spam_confidence = db.Column(db.Float, nullable=False)
    message_length = db.Column(db.Integer)
    processed_length = db.Column(db.Integer)
    ip_address = db.Column(db.String(45), default='127.0.0.1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    feedbacks = db.relationship('Feedback', backref='classification', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'message': self.message,
            'is_spam': self.is_spam,
            'spam_confidence': self.spam_confidence,
            'not_spam_confidence': self.not_spam_confidence,
            'message_length': self.message_length,
            'processed_length': self.processed_length,
            'created_at': self.created_at.isoformat(),
            'feedback_count': len(self.feedbacks),
            'has_feedback': len(self.feedbacks) > 0
        }
    
    def __repr__(self):
        return f'<Classification {self.id}: {self.is_spam}>'


class Feedback(db.Model):
    """
    Store user feedback on classification results
    """
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    classification_id = db.Column(db.Integer, db.ForeignKey('classifications.id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)  # True if model predicted correctly
    user_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'classification_id': self.classification_id,
            'is_correct': self.is_correct,
            'user_comment': self.user_comment,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Feedback {self.id}: {self.is_correct}>'


class Statistics(db.Model):
    """
    Store aggregated statistics for analytics
    """
    __tablename__ = 'statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    total_classified = db.Column(db.Integer, default=0)
    spam_count = db.Column(db.Integer, default=0)
    legitimate_count = db.Column(db.Integer, default=0)
    accuracy_from_feedback = db.Column(db.Float, default=0.0)
    date = db.Column(db.Date, default=datetime.utcnow, unique=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'total_classified': self.total_classified,
            'spam_count': self.spam_count,
            'legitimate_count': self.legitimate_count,
            'spam_percentage': round((self.spam_count / self.total_classified * 100) if self.total_classified > 0 else 0, 2),
            'accuracy_from_feedback': round(self.accuracy_from_feedback, 2),
            'date': self.date.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    def __repr__(self):
        return f'<Statistics {self.date}>'
