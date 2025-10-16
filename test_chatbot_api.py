"""
Script kiểm tra kết nối DeepSeek API và hiển thị thông tin chi tiết lỗi
"""
import os
import json
import logging
import sys
from django.conf import settings

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Thiết lập Django để có thể truy cập settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webbanhang.settings')
import django
django.setup()

# Import các module cần thiết sau khi đã thiết lập Django
from app.deepseek_api import get_deepseek_response
from django.conf import settings

def check_api_key():
    """Kiểm tra API key có tồn tại không"""
    api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
    if not api_key:
        logger.error("❌ Không tìm thấy DEEPSEEK_API_KEY trong settings")
        return False
    
    if api_key.startswith('sk-or-'):
        logger.info(f"✅ Tìm thấy API key hợp lệ (Bắt đầu với: {api_key[:8]}...)")
        return True
    else:
        logger.error(f"❌ API key không đúng định dạng OpenRouter: {api_key[:8]}...")
        return False

def test_deepseek_response():
    """Kiểm tra phản hồi từ DeepSeek API"""
    test_message = "Xin chào, cho tôi biết về 3 cuốn sách bán chạy nhất"
    
    try:
        logger.info(f"🔄 Đang gửi tin nhắn test: '{test_message}'")
        response = get_deepseek_response(test_message)
        
        if response:
            logger.info(f"✅ Nhận được phản hồi từ DeepSeek API:")
            logger.info(f"---\n{response}\n---")
            return True
        else:
            logger.error("❌ Không nhận được phản hồi từ DeepSeek API")
            return False
    except Exception as e:
        logger.error(f"❌ Lỗi khi gọi DeepSeek API: {str(e)}")
        import traceback
        logger.error(f"Chi tiết lỗi: {traceback.format_exc()}")
        return False

def main():
    print("\n===== KIỂM TRA KẾT NỐI CHATBOT =====")
    print("\n1. Kiểm tra API Key")
    api_key_valid = check_api_key()
    
    print("\n2. Kiểm tra kết nối DeepSeek API")
    api_response_valid = test_deepseek_response()
    
    print("\n===== KẾT QUẢ =====")
    if api_key_valid:
        print("✅ API Key: HỢP LỆ")
    else:
        print("❌ API Key: KHÔNG HỢP LỆ")
        
    if api_response_valid:
        print("✅ Kết nối API: THÀNH CÔNG")
    else:
        print("❌ Kết nối API: THẤT BẠI")
        
    if api_key_valid and api_response_valid:
        print("\n🎉 Tất cả các kiểm tra đều thành công! DeepSeek API đang hoạt động bình thường.")
    else:
        print("\n⚠️ Có vấn đề với cấu hình hoặc kết nối DeepSeek API.")
        print("🔍 Hãy kiểm tra log để biết thêm chi tiết.")

if __name__ == "__main__":
    main()
