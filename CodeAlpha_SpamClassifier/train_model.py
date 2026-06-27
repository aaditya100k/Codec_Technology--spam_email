import pandas as pd
import numpy as np
import nltk
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Create dataset directory if it doesn't exist
if not os.path.exists('dataset'):
    os.makedirs('dataset')

# Create sample dataset (you can replace this with your own CSV file)
sample_data = {
    'message': [
        'Click here to claim your FREE prize now!!!',
        'Hello, how are you doing today?',
        'Congratulations! You have won $1,000,000! Claim now!',
        'Let\'s catch up over coffee this weekend',
        'Urgent: Your account has been compromised. Click here to verify',
        'Meeting scheduled for tomorrow at 10 AM',
        'AMAZING OFFER! Get 90% discount on all products NOW',
        'Can you send me the project report?',
        'You are selected as a winner! Claim your prize immediately',
        'Thanks for your email, I\'ll reply soon',
        'LIMITED TIME OFFER! Buy now and save 50%',
        'Lunch at the new restaurant tomorrow?',
        'VERIFY YOUR ACCOUNT NOW OR IT WILL BE DELETED',
        'Just finished the presentation, sending you the slides',
        'Unlock premium membership for just $0.99 this month',
        'Coffee break in 10 minutes?',
        'Free iPhone available for you! Click here!',
        'Team meeting notes attached',
        'Act now! This offer expires in 24 hours!',
        'Looking forward to seeing you tomorrow',
        'CLICK NOW to see shocking photos!',
        'Can we reschedule our meeting?',
        'Inheritance from a distant relative! Claim your millions',
        'The report you requested is ready for review',
        'Special promotion just for you - 80% OFF!',
        'Hope you had a great weekend',
        'Nigerian Prince has money for you!',
        'Let me know if you need anything else',
        'EXCLUSIVE DEAL! Limited slots available!',
        'See you at the conference tomorrow'
    ],
    'label': [
        1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0
    ]
}

df = pd.DataFrame(sample_data)
df.to_csv('dataset/spam_emails.csv', index=False)
print("Sample dataset created: dataset/spam_emails.csv")

# Load dataset
df = pd.read_csv('dataset/spam_emails.csv')
print(f"Dataset loaded with {len(df)} samples")
print(f"Spam samples: {(df['label'] == 1).sum()}")
print(f"Not Spam samples: {(df['label'] == 0).sum()}")

# Text preprocessing function
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

print("\nPreprocessing text...")
df['processed_text'] = df['message'].apply(preprocess_text)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    df['processed_text'], 
    df['label'], 
    test_size=0.2, 
    random_state=42
)

print(f"Training set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

# TF-IDF Vectorization
print("\nVectorizing text...")
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"Vectorizer features: {len(vectorizer.get_feature_names_out())}")

# Train Naive Bayes model
print("\nTraining Naive Bayes model...")
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)

# Evaluate model
y_pred = model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n" + "="*50)
print("MODEL PERFORMANCE METRICS")
print("="*50)
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print("="*50)

# Create model directory if it doesn't exist
if not os.path.exists('model'):
    os.makedirs('model')

# Save model and vectorizer
joblib.dump(model, 'model/spam_model.pkl')
joblib.dump(vectorizer, 'model/vectorizer.pkl')
print("\nModel saved: model/spam_model.pkl")
print("Vectorizer saved: model/vectorizer.pkl")
