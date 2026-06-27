// ============================================
// DOM Elements
// ============================================

const messageInput = document.getElementById('messageInput');
const classifyBtn = document.getElementById('classifyBtn');
const charCount = document.getElementById('charCount');
const resultSection = document.getElementById('resultSection');
const resultCard = document.getElementById('resultCard');
const exampleBtns = document.querySelectorAll('.example-btn');
const loadHistoryBtn = document.getElementById('loadHistoryBtn');
const historyContainer = document.getElementById('historyContainer');
const feedbackBtns = document.querySelectorAll('.feedback-btn');
const feedbackComment = document.getElementById('feedbackComment');

// State
let currentClassificationId = null;

// ============================================
// Event Listeners
// ============================================

messageInput.addEventListener('input', updateCharCount);
classifyBtn.addEventListener('click', classifyMessage);
loadHistoryBtn.addEventListener('click', loadHistory);

exampleBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        messageInput.value = this.getAttribute('data-text');
        updateCharCount();
        messageInput.focus();
        messageInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
});

feedbackBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const isCorrect = this.getAttribute('data-feedback') === 'true';
        submitFeedback(isCorrect);
    });
});

messageInput.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        classifyMessage();
    }
});

// ============================================
// Functions
// ============================================

function updateCharCount() {
    const count = messageInput.value.length;
    charCount.textContent = count;
    
    if (count >= 10) {
        classifyBtn.disabled = false;
    } else {
        classifyBtn.disabled = true;
    }
}

async function classifyMessage() {
    const message = messageInput.value.trim();
    
    if (!message) {
        showError('Please enter a message to classify');
        return;
    }
    
    if (message.length < 10) {
        showError('Message must be at least 10 characters long');
        return;
    }
    
    // Disable button and show loading state
    classifyBtn.disabled = true;
    const btnText = classifyBtn.querySelector('.btn-text');
    const btnSpinner = classifyBtn.querySelector('.btn-spinner');
    btnText.textContent = 'Classifying...';
    btnSpinner.style.display = 'inline-block';
    
    try {
        const response = await fetch('/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult(data);
        } else {
            showError(data.error || 'An error occurred during classification');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to the server. Please try again.');
    } finally {
        classifyBtn.disabled = false;
        btnText.textContent = 'Classify Message';
        btnSpinner.style.display = 'none';
    }
}

function displayResult(data) {
    resultSection.style.display = 'block';
    
    const isSpam = data.is_spam;
    const resultClass = isSpam ? 'spam' : 'not-spam';
    const icon = isSpam ? '🚨' : '✅';
    
    // Store classification ID for feedback
    currentClassificationId = data.database_id || null;
    
    let html = `
        <div class="result-header">
            <span class="result-icon">${icon}</span>
            <h2 class="result-title ${resultClass}">${data.prediction}</h2>
        </div>
        
        <div class="result-details">
            <div class="detail-item ${resultClass}">
                <div class="detail-label">Spam Probability</div>
                <div class="detail-value">${data.spam_confidence.toFixed(2)}%</div>
                <div class="confidence-bar">
                    <div class="confidence-fill spam" style="width: ${data.spam_confidence}%"></div>
                </div>
            </div>
            
            <div class="detail-item ${resultClass}">
                <div class="detail-label">Legitimate Probability</div>
                <div class="detail-value">${data.not_spam_confidence.toFixed(2)}%</div>
                <div class="confidence-bar">
                    <div class="confidence-fill not-spam" style="width: ${data.not_spam_confidence}%"></div>
                </div>
            </div>
            
            <div class="detail-item ${resultClass}">
                <div class="detail-label">Original Length</div>
                <div class="detail-value">${data.message_length}</div>
                <div class="detail-label" style="margin-top: 8px;">characters</div>
            </div>
            
            <div class="detail-item ${resultClass}">
                <div class="detail-label">Processed Length</div>
                <div class="detail-value">${data.processed_length}</div>
                <div class="detail-label" style="margin-top: 8px;">words</div>
            </div>
        </div>
        
        <div class="result-message">
            <strong>Classification Details:</strong><br>
            ${isSpam 
                ? '⚠️ This message has been classified as SPAM. Common spam indicators include urgent language, excessive capitalization, suspicious links, or requests for personal information.' 
                : '✓ This message appears to be legitimate. It shows characteristics of genuine communication without typical spam indicators.'}
        </div>
    `;
    
    resultCard.innerHTML = html;
    resultCard.className = `${resultClass}`;
    
    // Show feedback section
    const feedbackSection = resultSection.querySelector('.feedback-section');
    if (feedbackSection && currentClassificationId) {
        feedbackSection.style.display = 'block';
        // Reset feedback inputs
        feedbackComment.value = '';
    }
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Load statistics after classification
    setTimeout(loadStatistics, 500);
}

function showError(message) {
    resultSection.style.display = 'block';
    resultCard.innerHTML = `
        <div class="error-message">
            <strong>⚠️ Error:</strong> ${message}
        </div>
    `;
    resultCard.className = '';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ============================================
// Database Functions
// ============================================

async function submitFeedback(isCorrect) {
    if (!currentClassificationId) {
        showNotification('Classification ID not found', 'error');
        return;
    }
    
    const userComment = feedbackComment.value.trim();
    
    try {
        const response = await fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                classification_id: currentClassificationId,
                is_correct: isCorrect,
                user_comment: userComment
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`✓ Thank you for the feedback!`, 'success');
            const feedbackSection = resultSection.querySelector('.feedback-section');
            feedbackSection.style.display = 'none';
            feedbackComment.value = '';
            // Reload statistics
            setTimeout(loadStatistics, 500);
        } else {
            showNotification(data.error || 'Failed to save feedback', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to submit feedback', 'error');
    }
}

async function loadStatistics() {
    try {
        const response = await fetch('/statistics');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.all_time;
            
            document.getElementById('totalClassified').textContent = stats.total_classified;
            document.getElementById('spamCount').textContent = stats.spam_count;
            document.getElementById('legitimateCount').textContent = stats.legitimate_count;
            document.getElementById('accuracy').textContent = stats.accuracy_from_feedback.toFixed(1) + '%';
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

async function loadHistory() {
    try {
        loadHistoryBtn.disabled = true;
        loadHistoryBtn.textContent = 'Loading...';
        
        const response = await fetch('/history?limit=20');
        const data = await response.json();
        
        if (data.success) {
            displayHistory(data.data);
        } else {
            historyContainer.innerHTML = '<div class="history-empty">Failed to load history</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        historyContainer.innerHTML = '<div class="history-empty">Error loading history</div>';
    } finally {
        loadHistoryBtn.disabled = false;
        loadHistoryBtn.textContent = 'Load Recent Classifications';
    }
}

function displayHistory(classifications) {
    if (classifications.length === 0) {
        historyContainer.innerHTML = '<div class="history-empty">No classifications yet. Start classifying emails!</div>';
        return;
    }
    
    historyContainer.innerHTML = '';
    
    classifications.forEach(item => {
        const predictionClass = item.is_spam ? 'spam' : 'legitimate';
        const predictionText = item.is_spam ? '🚨 SPAM' : '✅ LEGITIMATE';
        const date = new Date(item.created_at);
        const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const dateStr = date.toLocaleDateString();
        
        const historyHTML = `
            <div class="history-item ${predictionClass}">
                <div class="history-prediction ${predictionClass}">${predictionText}</div>
                <div class="history-message">"${item.message.substring(0, 100)}${item.message.length > 100 ? '...' : ''}"</div>
                <div class="history-confidence">
                    Spam: ${item.spam_confidence.toFixed(1)}% | Legit: ${item.not_spam_confidence.toFixed(1)}%
                </div>
                <div class="history-time">${dateStr} at ${timeStr}</div>
            </div>
        `;
        
        historyContainer.innerHTML += historyHTML;
    });
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.textContent = message;
    
    const bgColor = type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#f59e0b';
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 9999;
        animation: slideDownIn 0.3s ease-out;
        font-weight: 600;
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    updateCharCount();
    loadStatistics();
    console.log('✓ Spam Email Classifier with Database initialized');
});

// ============================================
// Keyboard Shortcuts
// ============================================

document.addEventListener('keydown', function(event) {
    // Alt + C: Focus on text area
    if (event.altKey && event.key === 'c') {
        event.preventDefault();
        messageInput.focus();
    }
    
    // Alt + Shift + C: Classify
    if (event.altKey && event.shiftKey && event.key === 'C') {
        event.preventDefault();
        if (!classifyBtn.disabled) {
            classifyMessage();
        }
    }
});

// ============================================
// Additional Features
// ============================================

// Clear button functionality (optional enhancement)
function clearInput() {
    messageInput.value = '';
    resultSection.style.display = 'none';
    updateCharCount();
    messageInput.focus();
}

// Copy result to clipboard (optional enhancement)
function copyResultToClipboard() {
    const resultText = resultCard.innerText;
    navigator.clipboard.writeText(resultText).then(() => {
        showNotification('Result copied to clipboard!');
    });
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #22c55e;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 9999;
        animation: slideDownIn 0.3s ease-out;
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// ============================================
// Console Welcome Message
// ============================================

console.log('%c🚀 Spam Email Classifier', 'font-size: 24px; color: #6366f1; font-weight: bold;');
console.log('%cPowered by Machine Learning', 'font-size: 12px; color: #818cf8;');
console.log('%cPress Ctrl+Enter to classify or use Alt+C to focus input', 'font-size: 11px; color: #cbd5e1;');
