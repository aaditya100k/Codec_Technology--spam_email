import os
from datetime import datetime, date
from models import db, Classification, Feedback, Statistics

def init_db(app):
    """
    Initialize the database with Flask app
    """
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database initialized successfully")

def save_classification(message, is_spam, spam_confidence, not_spam_confidence, 
                       message_length, processed_length, ip_address='127.0.0.1'):
    """
    Save a classification result to the database
    """
    try:
        classification = Classification(
            message=message,
            is_spam=is_spam,
            spam_confidence=spam_confidence,
            not_spam_confidence=not_spam_confidence,
            message_length=message_length,
            processed_length=processed_length,
            ip_address=ip_address
        )
        db.session.add(classification)
        db.session.commit()
        
        # Update statistics
        update_statistics()
        
        return classification.to_dict()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving classification: {e}")
        return None

def get_classification_history(limit=50):
    """
    Get recent classification history
    """
    try:
        classifications = Classification.query.order_by(
            Classification.created_at.desc()
        ).limit(limit).all()
        
        return [c.to_dict() for c in classifications]
    except Exception as e:
        print(f"Error retrieving history: {e}")
        return []

def save_feedback(classification_id, is_correct, user_comment=None):
    """
    Save user feedback for a classification
    """
    try:
        # Check if classification exists
        classification = Classification.query.get(classification_id)
        if not classification:
            return None
        
        feedback = Feedback(
            classification_id=classification_id,
            is_correct=is_correct,
            user_comment=user_comment
        )
        db.session.add(feedback)
        db.session.commit()
        
        # Update statistics
        update_statistics()
        
        return feedback.to_dict()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving feedback: {e}")
        return None

def get_feedback_for_classification(classification_id):
    """
    Get all feedback for a specific classification
    """
    try:
        feedbacks = Feedback.query.filter_by(
            classification_id=classification_id
        ).all()
        
        return [f.to_dict() for f in feedbacks]
    except Exception as e:
        print(f"Error retrieving feedback: {e}")
        return []

def update_statistics():
    """
    Update daily statistics
    """
    try:
        today = date.today()
        stats = Statistics.query.filter_by(date=today).first()
        
        if not stats:
            stats = Statistics(date=today)
            db.session.add(stats)
        
        # Count classifications
        all_classifications = Classification.query.all()
        today_classifications = Classification.query.filter(
            db.func.date(Classification.created_at) == today
        ).all()
        
        stats.total_classified = len(today_classifications)
        stats.spam_count = len([c for c in today_classifications if c.is_spam])
        stats.legitimate_count = len([c for c in today_classifications if not c.is_spam])
        
        # Calculate accuracy from feedback
        feedbacks = Feedback.query.all()
        if feedbacks:
            correct_feedbacks = len([f for f in feedbacks if f.is_correct])
            stats.accuracy_from_feedback = (correct_feedbacks / len(feedbacks)) * 100
        
        stats.last_updated = datetime.utcnow()
        db.session.commit()
        
        return stats.to_dict()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating statistics: {e}")
        return None

def get_statistics():
    """
    Get today's statistics
    """
    try:
        today = date.today()
        stats = Statistics.query.filter_by(date=today).first()
        
        if stats:
            return stats.to_dict()
        
        return {
            'total_classified': 0,
            'spam_count': 0,
            'legitimate_count': 0,
            'spam_percentage': 0,
            'accuracy_from_feedback': 0
        }
    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        return None

def get_all_time_statistics():
    """
    Get all-time statistics across all dates
    """
    try:
        all_classifications = Classification.query.all()
        all_feedbacks = Feedback.query.all()
        
        total = len(all_classifications)
        spam_count = len([c for c in all_classifications if c.is_spam])
        legitimate_count = len([c for c in all_classifications if not c.is_spam])
        
        accuracy = 0
        if all_feedbacks:
            correct = len([f for f in all_feedbacks if f.is_correct])
            accuracy = (correct / len(all_feedbacks)) * 100
        
        return {
            'total_classified': total,
            'spam_count': spam_count,
            'legitimate_count': legitimate_count,
            'spam_percentage': round((spam_count / total * 100) if total > 0 else 0, 2),
            'total_feedbacks': len(all_feedbacks),
            'accuracy_from_feedback': round(accuracy, 2)
        }
    except Exception as e:
        print(f"Error retrieving all-time statistics: {e}")
        return None

def delete_old_classifications(days=30):
    """
    Delete classifications older than specified days (for database cleanup)
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = Classification.query.filter(
            Classification.created_at < cutoff_date
        ).delete()
        db.session.commit()
        return deleted_count
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting old classifications: {e}")
        return 0

def clear_all_data():
    """
    Clear all data from database (use with caution!)
    """
    try:
        db.drop_all()
        db.create_all()
        print("✓ Database cleared successfully")
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        return False
