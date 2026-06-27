from flask import Flask, render_template, request, jsonify
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np
import os
from dotenv import load_dotenv
from models import db
from database import (
    init_db, save_classification, get_classification_history, 
    save_feedback, get_feedback_for_classification, get_statistics,
    get_all_time_statistics
)

# Load environment variables
load_dotenv()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'sqlite:///spam_classifier.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Load trained model and vectorizer
model_path = 'model/spam_model.pkl'
vectorizer_path = 'model/vectorizer.pkl'

if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
    print("ERROR: Model files not found!")
    print("Please run train_model.py first to train and save the model.")
    exit(1)

try:
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    print("✓ Model and vectorizer loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

def preprocess_text(text):
    """
    Preprocess text by:
    1. Converting to lowercase
    2. Removing special characters and numbers
    3. Tokenizing
    4. Removing stopwords
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters, numbers, and extra spaces
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    return ' '.join(tokens)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    """
    Classify email/message as spam or not spam
    """
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Please enter a message to classify'
            }), 400
        
        # Preprocess the message
        processed_message = preprocess_text(message)
        
        if not processed_message:
            return jsonify({
                'success': False,
                'error': 'Message is too short or contains no valid words'
            }), 400
        
        # Vectorize the message
        message_tfidf = vectorizer.transform([processed_message])
        
        # Predict
        prediction = model.predict(message_tfidf)[0]
        confidence = model.predict_proba(message_tfidf)[0]
        
        # Get confidence scores
        spam_probability = float(confidence[1]) * 100
        not_spam_probability = float(confidence[0]) * 100
        
        result = {
            'success': True,
            'is_spam': bool(prediction),
            'prediction': 'SPAM 🚨' if prediction == 1 else 'NOT SPAM ✅',
            'spam_confidence': round(spam_probability, 2),
            'not_spam_confidence': round(not_spam_probability, 2),
            'message_length': len(message),
            'processed_length': len(processed_message)
        }
        
        # Save to database
        classification_data = save_classification(
            message=message,
            is_spam=bool(prediction),
            spam_confidence=spam_probability,
            not_spam_confidence=not_spam_probability,
            message_length=len(message),
            processed_length=len(processed_message),
            ip_address=request.remote_addr
        )
        
        if classification_data:
            result['database_id'] = classification_data['id']
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error during classification: {str(e)}'
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get classification history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_classification_history(limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(history),
            'data': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/statistics', methods=['GET'])
def get_stats():
    """Get today's statistics"""
    try:
        stats = get_statistics()
        all_time = get_all_time_statistics()
        
        return jsonify({
            'success': True,
            'today': stats,
            'all_time': all_time
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for a classification"""
    try:
        data = request.get_json()
        classification_id = data.get('classification_id')
        is_correct = data.get('is_correct')
        user_comment = data.get('user_comment', '')
        
        if classification_id is None or is_correct is None:
            return jsonify({
                'success': False,
                'error': 'classification_id and is_correct are required'
            }), 400
        
        feedback_data = save_feedback(
            classification_id=classification_id,
            is_correct=is_correct,
            user_comment=user_comment
        )
        
        if feedback_data:
            return jsonify({
                'success': True,
                'message': 'Feedback saved successfully',
                'feedback': feedback_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Classification not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/classification/<int:classification_id>', methods=['GET'])
def get_classification_detail(classification_id):
    """Get detailed information about a specific classification"""
    try:
        from models import Classification
        
        classification = Classification.query.get(classification_id)
        if not classification:
            return jsonify({
                'success': False,
                'error': 'Classification not found'
            }), 404
        
        feedbacks = get_feedback_for_classification(classification_id)
        
        return jsonify({
            'success': True,
            'data': classification.to_dict(),
            'feedbacks': feedbacks
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': True,
        'vectorizer_loaded': True,
        'database_connected': True
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Spam Email Classifier - Flask Server")
    print("="*50)
    print("Starting server on http://localhost:5000")
    print("Press CTRL+C to stop the server")
    print("="*50 + "\n")
    app.run(debug=True, host='localhost', port=5000)
