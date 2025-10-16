"""
deepseek_api.py - Tích hợp DeepSeek API (qua OpenRouter) cho chatbot thông minh

Module này sử dụng OpenRouter API để tạo phản hồi thông minh từ DeepSeek cho chatbot.
Bạn cần đăng ký tài khoản OpenRouter và lấy API key tại: https://openrouter.ai/
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

# Cấu hình DeepSeek API qua OpenRouter
# Lấy API key từ settings.py hoặc biến môi trường
def get_api_key():
    """Lấy API key từ settings hoặc biến môi trường"""
    try:
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not api_key:
            api_key = os.environ.get('DEEPSEEK_API_KEY')
        return api_key
    except Exception as e:
        logger.error(f"Không thể lấy DeepSeek API key: {str(e)}")
        return None

def get_deepseek_response(prompt, product_info=None, conversation_history=None):
    """
    Sử dụng DeepSeek API (qua OpenRouter) để tạo phản hồi thông minh
    
    Args:
        prompt (str): Câu hỏi của người dùng
        product_info (list, optional): Thông tin sản phẩm từ database
        conversation_history (str, optional): Lịch sử cuộc trò chuyện 
    Returns:
        str: Phản hồi từ API hoặc fallback
    """
    api_key = get_api_key()
    
    if not api_key:
        logger.error("Không tìm thấy DeepSeek API key")
        return get_simple_response(prompt)
        
    # OpenRouter API endpoint
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    
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
    
    # # Chuẩn bị system message và messages cho API
    # system_message = f"""Bạn là trợ lý ảo của cửa hàng sách JBook.com. 
    # Hãy trả lời ngắn gọn, thân thiện và hữu ích bằng tiếng Việt.
    # {store_info_text}
    # {product_info_text}
    
    # Lưu ý: 
    # - Trả lời ngắn gọn, thân thiện 
    # - Chỉ trả lời bằng tiếng Việt
    # - Nếu không biết câu trả lời, hãy nói bạn không biết và đề xuất liên hệ với cửa hàng
    # - Không được tạo ra thông tin không có trong dữ liệu
    # """
    
    # # Chuẩn bị messages cho API
    # messages = [
    #     {"role": "user", "content": system_message}
    # ]
    
    # # Thêm lịch sử cuộc trò chuyện nếu có
    # if conversation_history:
    #     messages.append({"role": "user", "content": f"Lịch sử trò chuyện gần đây:\n{conversation_history}"})
    
    # # Thêm câu hỏi của người dùng
    # messages.append({"role": "user", "content": prompt})
    # Chuẩn bị system message không chứa thông tin sản phẩm cụ thể
    system_message = f"""Bạn là trợ lý ảo của cửa hàng sách JBook.com. 
    Hãy trả lời ngắn gọn, thân thiện và hữu ích bằng tiếng Việt nếu không có thông tin bạn có thể tìm kiếm online và trả về kết quả.
    {store_info_text}
    Lưu ý: 
    - Nếu vẫn không rõ, hãy nói bạn không chắc và đề xuất khách liên hệ với nhân viên cửa hàng.
    - Jbook có đặt hàng trực tuyến.
    - Nếu tìm sách thì nói cho khách hàng tìm kiếm theo tên sách, tác giả hoặc thể loại một số sách bán chạy Jbook: 
        The Lord of the Rings($8.00),The Name of the Wind($13.00),Effective Python($15.00),Guide to Competitive Programming (Second Edition)($11.00),Clean Code: A Handbook of Agile Software Craftsmanship ($18.00)
    - Hướng dẫn khách hàng đặt hàng, tìm kiếm nếu được đề cập.
    """
    
    # Chuẩn bị messages cho API
    messages = [
        {"role": "system", "content": system_message}
    ]
    
    # Thêm thông tin sản phẩm vào message riêng biệt
    if product_info and len(product_info) > 0:
        # Kiểm tra câu hỏi để xử lý thông tin sản phẩm phù hợp
        relevant_fields = ["name", "author", "price"]
        
        # Thêm trường mô tả nếu câu hỏi hỏi về thông tin chi tiết
        if any(keyword in prompt.lower() for keyword in ["chi tiết", "mô tả", "nội dung", "tóm tắt"]):
            relevant_fields.append("description")
        
        # Thêm trường đánh giá nếu câu hỏi liên quan
        if any(keyword in prompt.lower() for keyword in ["đánh giá", "review", "feedback", "rating"]):
            relevant_fields.extend(["rating", "reviews"])
        
        # Định dạng thông tin sản phẩm
        product_info_text = "Thông tin sản phẩm có liên quan:\n"
        for i, product in enumerate(product_info[:5], 1):
            # Tên sản phẩm (luôn hiển thị)
            product_name = product.get('name', 'Không có tên')
            product_info_text += f"{i}. {product_name}"
            
            # Thêm các trường thông tin khác nếu có
            for field in relevant_fields:
                if field != "name" and field in product and product[field]:
                    if field == "price":
                        product_info_text += f" - Giá: {product[field]}đ"
                    elif field == "author":
                        product_info_text += f" - Tác giả: {product[field]}"
                    elif field == "description":
                        # Rút gọn mô tả nếu quá dài
                        desc = product[field]
                        if len(desc) > 100:
                            desc = desc[:97] + "..."
                        product_info_text += f"\n   Mô tả: {desc}"
                    else:
                        product_info_text += f" - {field.capitalize()}: {product[field]}"
            
            product_info_text += "\n"
        
        # Thêm vào messages dưới dạng message riêng
        messages.append({"role": "user", "content": product_info_text})
    
    # Thêm lịch sử cuộc trò chuyện nếu có
    if conversation_history:
        messages.append({"role": "user", "content": f"Lịch sử trò chuyện gần đây:\n{conversation_history}"})
    
    # Thêm câu hỏi của người dùng
    messages.append({"role": "user", "content": prompt})
      # Cấu hình request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jbook.com",  # Thay bằng trang web thực của bạn nếu có
        "X-Title": "JBook Chatbot",
    }
    
    payload = {
        "model": "deepseek/deepseek-r1:free",  # Sử dụng phiên bản miễn phí của DeepSeek
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800,
    }

    try:
        # Gọi API
        logger.info(f"Gọi OpenRouter API với prompt: {prompt[:50]}...")
        logger.info(f"API URL: {api_url}")
        logger.info(f"API Key: {api_key[:5]}...{api_key[-4:] if len(api_key) > 9 else ''}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)[:200]}...")
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)  # Tăng timeout
        
        logger.info(f"API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"API response JSON: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
            
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content'].strip()
                logger.info(f"Nhận được phản hồi từ API: {answer[:100]}...")
                return answer
            else:
                logger.error(f"Không tìm thấy 'choices' trong kết quả API: {json.dumps(result, indent=2, ensure_ascii=False)}")
                logger.error(f"Kết quả API đầy đủ: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Nếu API trả về lỗi
        logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
        
        # Thêm thông tin chi tiết về lỗi
        error_detail = ""
        try:
            error_json = response.json()
            if 'error' in error_json:
                error_detail = f"Error type: {error_json.get('error', {}).get('type', 'unknown')}, message: {error_json.get('error', {}).get('message', 'unknown')}"
                logger.error(f"API error details: {error_detail}")
        except:
            pass
            
        return get_simple_response(prompt)
    except Exception as e:
        logger.error(f"Lỗi khi gọi DeepSeek API: {str(e)}")
        
        # Thêm thông tin chi tiết hơn về lỗi
        import traceback
        logger.error(f"Chi tiết lỗi: {traceback.format_exc()}")
        
        # Thử xác định loại lỗi cụ thể
        if isinstance(e, requests.exceptions.Timeout):
            logger.error("Lỗi timeout khi kết nối tới API")
        elif isinstance(e, requests.exceptions.ConnectionError):
            logger.error("Lỗi kết nối tới API - kiểm tra kết nối internet")
        elif isinstance(e, requests.exceptions.RequestException):
            logger.error("Lỗi request tới API")
        
        return get_simple_response(prompt)