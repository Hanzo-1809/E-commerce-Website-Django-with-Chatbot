"""
Test DeepSeek API Connection

This script tests the connection to OpenRouter's DeepSeek API.
It will help us understand if the API is accessible and responding correctly.
"""

import requests
import json
import os
import sys

# Lấy API key từ environment variable hoặc hardcoded để test
api_key = os.environ.get('DEEPSEEK_API_KEY', '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')

# API endpoint
api_url = "https://openrouter.ai/api/v1/chat/completions"

# Headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://jbook.com",
    "X-Title": "JBook Test",
}

# Test message - lấy từ command line nếu có, nếu không thì dùng mặc định
test_message = sys.argv[1] if len(sys.argv) > 1 else "Xin chào, bạn là ai?"

# Payload
payload = {
    "model": "deepseek/deepseek-r1:free",
    "messages": [
        {"role": "system", "content": "Bạn là trợ lý ảo của cửa hàng sách JBook.com. Hãy trả lời ngắn gọn bằng tiếng Việt."},
        {"role": "user", "content": test_message}
    ],
    "temperature": 0.7,
    "max_tokens": 800,
}

print(f"📝 Đang gửi tin nhắn: '{test_message}'")
print(f"🔑 Dùng API key: '{api_key[:5]}...{api_key[-4:]}'")
print("📡 Đang kết nối...")

try:
    # Gửi request đến API
    response = requests.post(api_url, headers=headers, json=payload, timeout=15)
    
    # In mã trạng thái
    print(f"📞 Mã trạng thái: {response.status_code}")
    
    # Xử lý kết quả
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            answer = result['choices'][0]['message']['content'].strip()
            print(f"\n✅ Phản hồi từ DeepSeek API: \n{'-'*50}\n{answer}\n{'-'*50}")
            
            # In thêm thông tin khác từ API
            if 'model' in result:
                print(f"🤖 Model: {result['model']}")
            if 'usage' in result:
                print(f"📊 Token usage: {result['usage']}")
        else:
            print(f"❌ Không tìm thấy phản hồi trong kết quả API.")
            print(f"📄 Nội dung trả về: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Lỗi từ API: {response.status_code}")
        try:
            error_data = response.json()
            print(f"📄 Chi tiết lỗi: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"📄 Nội dung phản hồi: {response.text}")
            
except Exception as e:
    print(f"❌ Lỗi kết nối: {str(e)}")
    
    # In thêm thông tin về lỗi
    import traceback
    print(f"📄 Chi tiết lỗi: {traceback.format_exc()}")
