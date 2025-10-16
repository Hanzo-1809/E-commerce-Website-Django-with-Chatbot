"""
openai_api.py - Tích hợp OpenAI API (ChatGPT) cho chatbot thông minh

Module này sử dụng OpenAI API để tạo phản hồi thông minh cho chatbot.
Bạn cần đăng ký tài khoản OpenAI và lấy API key tại: https://platform.openai.com/
"""

import os
import json
import requests
import time
from django.conf import settings
from app.chatbot_data import WEB_FEATURES, FAQS, STORE_INFO
from app.simple_chatbot import get_simple_response

import logging
logger = logging.getLogger(__name__)

# Cấu hình OpenAI API
# Lấy API key từ settings.py hoặc biến môi trường
# Bạn cần thêm OPENAI_API_KEY vào file settings.py: OPENAI_API_KEY = "your-api-key"
def get_api_key():
    """Lấy API key từ settings hoặc biến môi trường"""
    try:
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            api_key = os.environ.get('OPENAI_API_KEY')
        return api_key
    except Exception as e:
        logger.error(f"Không thể lấy API key: {str(e)}")
        return None

def get_openai_response(prompt, product_info=None, conversation_history=None):
    """
    Sử dụng OpenAI API để tạo phản hồi thông minh
    
    Args:
        prompt (str): Câu hỏi của người dùng
        product_info (list, optional): Thông tin sản phẩm từ database
        conversation_history (str, optional): Lịch sử cuộc trò chuyện
        
    Returns:
        str: Phản hồi từ API hoặc fallback
    """
    api_key = get_api_key()
    
    if not api_key:
        logger.error("Không tìm thấy OpenAI API key")
        return get_simple_response(prompt)
        
    # API endpoint
    api_url = "https://api.openai.com/v1/chat/completions"
    
    # Chuẩn bị thông tin cửa hàng và sản phẩm cho prompt
    store_info_text = f"""
    Thông tin cửa hàng:
    - Tên: {STORE_INFO['tên']}
    - Địa chỉ: {STORE_INFO['địa chỉ']}
    - Giờ làm việc: {STORE_INFO['giờ làm việc']}
    - Email: {STORE_INFO['email']}
    - Điện thoại: {STORE_INFO['điện thoại']}
    """
    
    product_info_text = ""
    if product_info and len(product_info) > 0:
        product_info_text = "Thông tin sản phẩm có liên quan:\n"
        for i, product in enumerate(product_info[:5], 1):  # Giới hạn 5 sản phẩm
            product_info_text += f"{i}. {product.get('name', 'Không có tên')}"
            
            if 'author' in product and product['author']:
                product_info_text += f" - Tác giả: {product['author']}"
                
            if 'price' in product:
                product_info_text += f" - Giá: {product['price']}đ"
                
            if 'categories' in product:
                product_info_text += f" - Thể loại: {product['categories']}"
                
            product_info_text += "\n"
    
    # Tạo system message
    system_message = f"""Bạn là trợ lý ảo của cửa hàng sách JBook.com. 
    Hãy trả lời ngắn gọn, thân thiện và hữu ích bằng tiếng Việt.
    {store_info_text}
    {product_info_text}
    
    Lưu ý: 
    - Trả lời ngắn gọn, thân thiện 
    - Chỉ trả lời bằng tiếng Việt
    - Nếu không biết câu trả lời, hãy nói bạn không biết và đề xuất liên hệ với cửa hàng
    - Không được tạo ra thông tin không có trong dữ liệu
    """
    
    # Chuẩn bị messages cho API
    messages = [
        {"role": "system", "content": system_message}
    ]
    
    # Thêm lịch sử cuộc trò chuyện nếu có
    if conversation_history:
        messages.append({"role": "system", "content": f"Lịch sử trò chuyện gần đây:\n{conversation_history}"})
    
    # Thêm câu hỏi của người dùng
    messages.append({"role": "user", "content": prompt})
    
    # Cấu hình request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",  # Hoặc "gpt-4" nếu bạn có quyền truy cập
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 200,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    
    try:
        # Gọi API
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content'].strip()
                return answer
        
        # Nếu API trả về lỗi
        logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
        return get_simple_response(prompt)
        
    except Exception as e:
        logger.error(f"Lỗi khi gọi OpenAI API: {str(e)}")
        return get_simple_response(prompt)
