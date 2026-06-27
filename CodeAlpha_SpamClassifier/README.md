# 📧 CodeAlpha Spam Email Classifier

An AI-powered email classification system built with Flask and Machine Learning that detects spam emails with high accuracy.

## 🎯 Features

- ✅ **Real-time Classification**: Instantly classify emails as spam or legitimate
- 🤖 **Machine Learning Model**: Trained Naive Bayes classifier with TF-IDF vectorization
- 📊 **Confidence Scores**: Get probability percentages for each classification
- 🎨 **Modern UI**: Beautiful, responsive, and animated interface
- ⚡ **Fast Processing**: Optimized text preprocessing and classification pipeline
- 📱 **Mobile Friendly**: Works perfectly on desktop, tablet, and mobile devices
- 🔍 **Text Analysis**: Shows original vs processed message length metrics
- 💾 **Database Integration**: SQLite database to store all classifications and feedback
- 📈 **Statistics & Analytics**: Track spam vs legitimate emails, accuracy from user feedback
- ⭐ **User Feedback System**: Rate classifications as correct/incorrect to improve model
- 📜 **Classification History**: View recent classifications with timestamps and scores

## 🏗️ Project Structure

```
CodeAlpha_SpamClassifier/
├── app.py                    # Flask backend application with database endpoints
├── train_model.py           # Model training script
├── models.py                # Database models (Classification, Feedback, Statistics)
├── database.py              # Database functions and utilities
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
├── dataset/
│   └── spam_emails.csv      # Sample training data
├── model/
│   ├── spam_model.pkl       # Trained Naive Bayes model
│   └── vectorizer.pkl       # TF-IDF vectorizer
├── templates/
│   └── index.html           # Main HTML interface with stats & history
├── static/
│   ├── style.css            # Styling (CSS) with new sections
│   └── script.js            # Frontend logic (JavaScript) with DB operations
└── spam_classifier.db       # SQLite database (auto-created on first run)
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python) |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **ML Model** | Scikit-learn (Naive Bayes) |
| **NLP** | NLTK, Pandas, NumPy |
| **Vectorization** | TF-IDF |
| **Model Serialization** | Joblib |

## 📋 Requirements

- Python 3.7+
- pip (Python package manager)

## 🚀 Quick Start

### 1. Navigate to Project Directory
```bash
cd CodeAlpha_SpamClassifier
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the Model
```bash
python train_model.py
```

This will:
- Create sample dataset (spam_emails.csv)
- Preprocess the text data
- Train Naive Bayes model
- Save model and vectorizer to the `model/` directory
- Display performance metrics

### 5. Start Flask Server
```bash
python app.py
```

The server will start on **http://localhost:5000**

### 6. Open in Browser
Open your web browser and navigate to:
```
http://localhost:5000
```

## 📖 How to Use

1. **Enter Message**: Paste your email or message in the text area
2. **Click Classify**: Press the "Classify Message" button or press Ctrl+Enter
3. **View Results**: Get instant classification with:
   - Spam/Not Spam verdict
   - Confidence percentage for each class
   - Message statistics

### Keyboard Shortcuts
- **Alt + C**: Focus on text input area
- **Ctrl + Enter**: Classify message
- **Alt + Shift + C**: Classify message

### Feedback System
1. **Rate Classifications**: After classification, use feedback buttons to indicate if the result was correct
2. **Add Comments**: Optionally add comments about why a classification is incorrect
3. **Improve Model**: Your feedback helps track model accuracy and can be used for retraining

### View Analytics
- **Statistics Panel**: See total classifications, spam/legitimate counts, and accuracy metrics
- **History Panel**: Load recent classifications with details and timestamps

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/classify` | Classify an email message |
| GET | `/history` | Get classification history (default: 50 latest) |
| GET | `/statistics` | Get today's and all-time statistics |
| POST | `/feedback` | Submit user feedback for a classification |
| GET | `/classification/<id>` | Get detailed info about a specific classification |
| GET | `/health` | Health check endpoint |

### Example API Usage

**Classify a message:**
```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"message": "Click here to claim your prize!"}'
```

**Submit feedback:**
```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "classification_id": 1,
    "is_correct": true,
    "user_comment": "Correct classification!"
  }'
```

**Get statistics:**
```bash
curl http://localhost:5000/statistics
```

## 🛢️ Database Schema

### Classifications Table
Stores all email classifications made by the system:
- `id` - Primary key
- `message` - Original email text
- `is_spam` - Boolean prediction
- `spam_confidence` - Spam probability (0-100)
- `not_spam_confidence` - Legitimate probability (0-100)
- `message_length` - Original message character count
- `processed_length` - Processed message word count
- `ip_address` - IP address of requester
- `created_at` - Timestamp of classification

### Feedbacks Table
Stores user feedback on classifications:
- `id` - Primary key
- `classification_id` - Foreign key to Classifications
- `is_correct` - Whether model predicted correctly
- `user_comment` - Optional comment from user
- `created_at` - Timestamp of feedback

### Statistics Table
Stores daily aggregated statistics:
- `id` - Primary key
- `total_classified` - Total classifications on that day
- `spam_count` - Number of spam classifications
- `legitimate_count` - Number of legitimate classifications
- `accuracy_from_feedback` - Model accuracy based on user feedback
- `date` - Date of statistics
- `last_updated` - Last update timestamp

### Text Preprocessing
1. Convert text to lowercase
2. Remove special characters and numbers
3. Remove stopwords (common words like "the", "and", etc.)
4. Keep only meaningful words (length > 2)

### Feature Extraction
- Uses **TF-IDF Vectorizer** to convert text to numerical features
- Captures word importance and frequency

### Classification
- **Naive Bayes Classifier** makes predictions
- Calculates confidence scores for each class
- Returns probability percentages

## 📊 Model Performance

Typical metrics from the trained model:
- **Accuracy**: ~95% (varies with dataset)
- **Precision**: Minimizes false positives
- **Recall**: Catches most spam emails
- **F1-Score**: Balanced performance metric

## 🎓 Sample Spam Indicators

The model learns to identify:
- ⚠️ Urgent or time-sensitive language
- 💰 Money-related promises
- 🎁 Suspicious offers and deals
- ✋ Suspicious links and URLs
- 🆘 Requests for personal information
- 🔔 Excessive capitalization and exclamation marks

## 🔧 Configuration

### Modify Model Parameters
Edit `train_model.py`:
```python
# Change test split ratio
test_size=0.2  # Adjust to 0.3 for more testing data

# Adjust TF-IDF parameters
TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
```

### Customize Dataset
Replace `dataset/spam_emails.csv` with your own data:
```csv
message,label
"Your message here",0
"SPAM MESSAGE HERE",1
```

## 📝 Dataset Format

CSV file with two columns:
- **message**: The email or message text
- **label**: 0 for legitimate, 1 for spam

## 🐛 Troubleshooting

### Model files not found
```bash
# Retrain the model
python train_model.py
```

### NLTK data missing
```bash
# Download NLTK data manually
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Port 5000 already in use
```bash
# Use a different port
python -c "from app import app; app.run(port=5001)"
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🔐 Security Considerations

- Input text is limited to reasonable length
- No sensitive data is logged
- Model processes text locally
- No data is stored or transmitted externally

## 📈 Improving Model Performance

1. **Expand Dataset**: Add more examples of spam and legitimate emails
2. **Fine-tune Parameters**: Adjust TF-IDF and model hyperparameters
3. **Add Features**: Incorporate sender information, email headers, etc.
4. **Use Better Models**: Experiment with SVM, Random Forest, or Neural Networks

## 🚀 Future Enhancements

- [ ] Deep Learning models (LSTM, BERT)
- [ ] Multi-language support
- [ ] Email header analysis
- [ ] Attachment scanning
- [ ] Integration with email clients
- [ ] User feedback loop for model improvement
- [ ] API for external integrations
- [ ] Advanced analytics dashboard

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💼 Author

**CodeAlpha** - AI & Machine Learning Solutions

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Add new features
- Improve documentation

## 📞 Support

For issues or questions, please check the troubleshooting section or review the code comments.

---

**Made with ❤️ using Flask, Scikit-learn, and Machine Learning**
