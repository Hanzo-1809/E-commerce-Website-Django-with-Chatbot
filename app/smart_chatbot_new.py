"""
smart_chatbot_new.py - Enhanced chatbot system combining multiple techniques

This module provides an advanced chatbot implementation that:
1. Uses k                try:
                    # Get response from DeepSeek with product info
                    api_response = get_deepseek_response(enhanced_prompt, relevant_products, conversation_history if has_context else None)
                    
                    # If we got a meaningful response, store and return it
                    if api_response and len(api_response) > 15:  # Minimum length check
                        chatbot_memory.add_message(session_id, 'bot', api_response)
                        return api_response
                except Exception as e:or quick, reliable responses to common questions
2. Uses the DeepSeek API (via OpenRouter) for more complex questions
3. Incorporates product information from the database with search and recommendations
4. Has proper fallbacks when APIs fail
5. Tracks conversation memory for context-aware responses
6. Uses sentiment analysis to better respond to user emotions
"""

import re
import random
import logging
from app.chatbot_data import WEB_FEATURES, FAQS, STORE_INFO
from app.simple_chatbot import get_simple_response, FALLBACK_RESPONSES
from app.deepseek_api import get_deepseek_response

# Import our new modules
from app.chatbot_memory import memory as chatbot_memory
from app.product_search import search_products, recommend_similar_products
from app.sentiment_analysis import analyze_sentiment, get_sentiment_response

# Configure logging
logger = logging.getLogger(__name__)

# Product-related patterns for detection
PRODUCT_PATTERNS = {
    "sách|book|sản phẩm|tác phẩm|tác giả|truyện|tiểu thuyết|tác phẩm": True,
    "giá|price|cost|bao nhiêu tiền|đắt|rẻ|giá bao nhiêu|giá cả": True,
    "mới|new|bán chạy|best seller|nổi tiếng|phổ biến|popular|hot|xu hướng": True,
    "khuyến mãi|giảm giá|sale|discount|ưu đãi|khuyến mãi|giảm": True,
    "thể loại|category|danh mục|loại sách|genre|chủ đề": True,
    "tìm|find|search|kiếm|gợi ý|recommend|đề xuất": True
}

def is_product_query(user_input):
    """Check if the query is about products"""
    user_input = user_input.lower()
    for pattern in PRODUCT_PATTERNS:
        if re.search(pattern, user_input):
            return True
    return False

def format_product_info(products, max_display=3, query=None):
    """
    Format product information in a readable way
    
    Args:
        products (list): List of product dictionaries
        max_display (int): Maximum number of products to display
        query (str, optional): User's query for context
        
    Returns:
        str: Formatted product information string
    """
    if not products or len(products) == 0:
        return "Hiện tại không có thông tin sản phẩm phù hợp với yêu cầu của bạn."
    
    # Customize heading based on query context
    if query and "giá" in query.lower():
        result = "Thông tin giá sách bạn quan tâm:\n"
    elif query and ("tác giả" in query.lower() or "author" in query.lower()):
        result = "Thông tin sách theo tác giả bạn yêu cầu:\n"
    elif query and ("mới" in query.lower() or "new" in query.lower()):
        result = "Các sách mới của chúng tôi:\n"
    else:
        result = "Một số sách phù hợp với yêu cầu của bạn:\n"
    
    for i, product in enumerate(products[:max_display], 1):
        result += f"{i}. {product['name']}"
        
        if 'author' in product and product['author']:
            result += f" - Tác giả: {product['author']}"
            
        if 'price' in product:
            result += f" - Giá: {product['price']}đ"
            
        if 'categories' in product:
            result += f" - Thể loại: {product['categories']}"
            
        result += "\n"
    
    if len(products) > max_display:
        result += f"...và {len(products) - max_display} sách khác"
        
    result += "\nBạn có thể hỏi thêm về bất kỳ cuốn sách nào bạn quan tâm."
    
    return result

def get_smart_response(user_input, products=None, session_id=None):
    """
    Generate a smart response using multiple methods
    
    Args:
        user_input (str): User question or comment
        products (list): List of product dictionaries from database
        session_id (str): Session identifier for conversation memory
        
    Returns:
        str: Response to the user
    """
    if not session_id:
        session_id = "default_session"
    
    user_input = user_input.strip()
    user_input_lower = user_input.lower()
    
    # Store user message in memory
    chatbot_memory.add_message(session_id, 'user', user_input)
    
    # Analyze user sentiment
    sentiment = analyze_sentiment(user_input)
    logger.info(f"Sentiment analysis: {sentiment}")
    
    # If user seems frustrated, try to address that first
    if sentiment['is_frustrated']:
        sentiment_response = get_sentiment_response(sentiment)
        if sentiment_response:
            chatbot_memory.add_message(session_id, 'bot', sentiment_response)
            return sentiment_response
    
    # Check for conversation context
    conversation_history = chatbot_memory.get_formatted_history(session_id, limit=3)
    has_context = bool(conversation_history)
    
    # Check for simple greeting patterns first for speed
    greeting_patterns = ["xin chào", "chào", "hello", "hi", "hey"]
    if any(pattern in user_input_lower for pattern in greeting_patterns):
        greeting = "Xin chào! Tôi là trợ lý ảo của JBook.com. Tôi có thể giúp gì cho bạn về sách và các dịch vụ của chúng tôi?"
        chatbot_memory.add_message(session_id, 'bot', greeting)
        return greeting
    
    # Check for goodbye patterns
    goodbye_patterns = ["tạm biệt", "bye", "goodbye", "gặp lại sau", "hẹn gặp lại"]
    if any(pattern in user_input_lower for pattern in goodbye_patterns):
        goodbye = "Cảm ơn bạn đã trò chuyện! Hẹn gặp lại bạn sớm. Nếu bạn có thêm câu hỏi, đừng ngần ngại quay lại nhé!"
        chatbot_memory.add_message(session_id, 'bot', goodbye)
        return goodbye
    
    # Check if query is about products and we have product data
    if is_product_query(user_input_lower) and products and len(products) > 0:
        try:
            # Search for relevant products based on user query
            relevant_products = search_products(user_input, products)
            
            if relevant_products:
                # Format the product information with the user query for context
                product_info = format_product_info(relevant_products, query=user_input)
                
                # First try to get a specific answer from OpenAI with product context
                enhanced_prompt = f"""Thông tin sách: {product_info}
                {conversation_history if has_context else ''}
                Câu hỏi khách hàng: {user_input}
                
                Hãy trả lời ngắn gọn, đầy đủ và hữu ích bằng tiếng Việt."""
                try:
                    # Get response from DeepSeek with product info
                    api_response = get_deepseek_response(enhanced_prompt, relevant_products, conversation_history if has_context else None)
                    
                    # If we got a meaningful response, store and return it
                    if api_response and len(api_response) > 15:  # Minimum length check
                        chatbot_memory.add_message(session_id, 'bot', api_response)
                        return api_response
                except Exception as e:
                    logger.error(f"Error in product API response: {str(e)}")
                
                # If API fails, default to showing product information directly
                response = f"{product_info}\nBạn có cần thêm thông tin gì về các sản phẩm này không?"
                chatbot_memory.add_message(session_id, 'bot', response)
                return response
        except Exception as e:
            logger.error(f"Error in product search: {str(e)}")
    
    # Try keyword matching for common queries (fast and reliable)
    keyword_response = get_simple_response(user_input)
    
    # If keyword matching found something specific (not a fallback), return it
    if keyword_response not in FALLBACK_RESPONSES:
        chatbot_memory.add_message(session_id, 'bot', keyword_response)
        return keyword_response
    
    # For more complex queries, try the OpenAI API with conversation history
    try:
        enhanced_prompt = f"""{conversation_history if has_context else ''}
        Câu hỏi: {user_input}
        
        Trả lời câu hỏi một cách ngắn gọn, đầy đủ và hữu ích bằng tiếng Việt."""
        
        api_response = get_openai_response(enhanced_prompt, None, conversation_history if has_context else None)
        chatbot_memory.add_message(session_id, 'bot', api_response)
        return api_response
    except Exception as e:
        logger.error(f"API error in smart chatbot: {str(e)}")
        # If all else fails, return the simple response
        chatbot_memory.add_message(session_id, 'bot', keyword_response)
        return keyword_response
