"""
sentiment_analysis.py - Basic sentiment analysis for chatbot responses

This module provides simple sentiment analysis to detect user frustration
and adjust chatbot responses accordingly.
"""

import re

# Positive sentiment indicators in Vietnamese
POSITIVE_PATTERNS = [
    r'cảm ơn|thank|thanks|tuyệt|tốt|hay|thích|mừng|vui|hài lòng|tuyệt vời|tuyệt quá',
    r'giúp|hữu ích|có ích|tốt|đúng|chính xác'
]

# Negative sentiment indicators in Vietnamese
NEGATIVE_PATTERNS = [
    r'không hiểu|sai|lỗi|kém|tệ|tồi|chẳng|không đúng|không chính xác',
    r'thất vọng|buồn|bực|khó chịu|không vui|không hài lòng',
    r'không thể|không được|không biết|không hiểu',
    r'gì vậy|đâu có|chẳng đúng|ngu|kém'
]

# Urgency indicators in Vietnamese
URGENCY_PATTERNS = [
    r'ngay|lập tức|nhanh|gấp|khẩn|cần|phải',
    r'giúp tôi|giúp với|help|cứu|cứu giúp'
]

# Frustration indicators in Vietnamese
FRUSTRATION_PATTERNS = [
    r'\?{2,}|\!{2,}',  # Multiple question marks or exclamation points
    r'không hiểu gì cả|chẳng hiểu|cái gì vậy',
    r'mãi|nhiều lần|lặp lại',
    r'thôi|quên đi|nevermind|thôi vậy'
]

def analyze_sentiment(text):
    """
    Analyzes sentiment and emotion in user text
    
    Args:
        text (str): User message text
        
    Returns:
        dict: Sentiment analysis results
    """
    text = text.lower()
    
    # Initialize sentiment scores
    sentiment = {
        'positive': 0,
        'negative': 0,
        'urgency': 0,
        'frustration': 0
    }
    
    # Check each pattern category
    for pattern in POSITIVE_PATTERNS:
        matches = re.findall(pattern, text)
        sentiment['positive'] += len(matches)
        
    for pattern in NEGATIVE_PATTERNS:
        matches = re.findall(pattern, text)
        sentiment['negative'] += len(matches)
        
    for pattern in URGENCY_PATTERNS:
        matches = re.findall(pattern, text)
        sentiment['urgency'] += len(matches)
        
    for pattern in FRUSTRATION_PATTERNS:
        matches = re.findall(pattern, text)
        sentiment['frustration'] += len(matches)
    
    # Calculate the overall sentiment
    sentiment['overall'] = sentiment['positive'] - sentiment['negative']
    
    # Determine if user seems frustrated
    is_frustrated = (sentiment['frustration'] > 0) or (sentiment['negative'] > 1 and sentiment['urgency'] > 0)
    sentiment['is_frustrated'] = is_frustrated
    
    return sentiment

def get_sentiment_response(sentiment):
    """
    Get an appropriate response based on detected sentiment
    
    Args:
        sentiment (dict): Sentiment analysis results
        
    Returns:
        str or None: Sentiment-specific response, or None if no special response needed
    """
    if sentiment['is_frustrated']:
        responses = [
            "Tôi rất tiếc vì không thể giúp bạn một cách hiệu quả. Hãy cho tôi biết cụ thể hơn về điều bạn cần.",
            "Tôi hiểu bạn đang cảm thấy thất vọng. Hãy thử diễn đạt yêu cầu của bạn theo cách khác để tôi có thể giúp tốt hơn.",
            "Tôi xin lỗi vì sự bất tiện này. Bạn có thể liên hệ với đội hỗ trợ khách hàng của chúng tôi qua số điện thoại 1900-1234 để được giúp đỡ ngay lập tức."
        ]
        return responses[sentiment['frustration'] % len(responses)]
        
    elif sentiment['positive'] > 1:
        return "Rất vui khi có thể giúp đỡ bạn! Bạn còn cần hỗ trợ gì nữa không?"
        
    return None
