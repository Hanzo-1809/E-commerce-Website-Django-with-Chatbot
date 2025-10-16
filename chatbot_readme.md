# Enhanced Chatbot for JBook.com

## Overview
This is an enhanced chatbot implementation for a Django-based online bookstore. The chatbot uses a hybrid approach combining keyword detection, DeepSeek API integration via OpenRouter, and product information integration to provide a robust customer support experience.

## Features
- **Multi-method response generation**: Uses keyword matching for common questions and API-based responses for complex queries
- **Product search and recommendations**: Integrates with the product database to provide relevant information
- **Conversation memory**: Remembers previous interactions during a session
- **Sentiment analysis**: Detects user frustration and responds appropriately
- **Graceful fallbacks**: Multiple fallback mechanisms ensure users always get a response
- **Modern UI**: Loading animations, suggestion buttons, and a responsive interface

## Installation and Setup
1. The chatbot is already integrated into the Django project
2. Add your DeepSeek API key to the `.env` file in the project root:
```
DEEPSEEK_API_KEY=your-actual-api-key-here
```
3. If you don't have a DeepSeek API key:
   - Sign up at [openrouter.ai](https://openrouter.ai/)
   - Create an API key in your account dashboard
   - You can start with the free tier without adding credit

## Usage
1. Run the Django server:
```bash
python manage.py runserver
```

2. Navigate to the home page where the chatbot is available
3. Click on the "Chat với tôi" button in the bottom-right corner
4. Start asking questions about books, store information, or services

## Testing
Try these queries to test different capabilities:
- "Xin chào" - Basic greeting
- "Có sách nào mới không?" - Product search
- "Làm thế nào để đặt hàng?" - Store process information
- "Giờ làm việc của cửa hàng?" - Store information
- "Phương thức thanh toán?" - Payment information
- "Bạn có sách về lập trình không?" - Specific category search
- "Gợi ý một số sách nổi tiếng" - Get recommendations
- "Tôi muốn tìm sách của tác giả Nguyễn Nhật Ánh" - Author search

## Technical Components
- `smart_chatbot_deepseek.py`: Main chatbot logic combining different response methods
- `deepseek_api.py`: Integration with DeepSeek API via OpenRouter for intelligent responses
- `simple_chatbot.py`: Basic keyword-based responses for common questions
- `chatbot_memory.py`: Session-based conversation memory
- `product_search.py`: Product search and recommendation functions
- `sentiment_analysis.py`: Basic sentiment analysis for detecting user emotions
- `views.py`: Django view handling chatbot requests

## Future Improvements
- Add user authentication integration to personalize responses
- Implement more advanced recommendation algorithms
- Support for image attachments and rich media responses
- Fine-tune the OpenAI model for e-commerce specific interactions
- Add voice recognition for audio-based interactions

## Troubleshooting
### API Key Issues
If the chatbot is returning simple responses and not using DeepSeek AI:
1. Check that your API key is correctly configured in the `.env` file
2. Run the debug script to test direct API access: `test_deepseek_direct.bat`
3. Check the Django console for API-related error messages
4. Verify that you've entered the correct OpenRouter API key for accessing DeepSeek

### DeepSeek API via OpenRouter Issues
If you encounter rate limit or connection errors:
1. Consider upgrading your OpenRouter plan if you need higher usage limits
2. Implement caching for common responses to reduce API calls
3. Use the chatbot's fallback mechanisms which will still provide basic responses
4. Check if your OpenRouter account has credits and is properly configured for DeepSeek access

### Server Connection Issues
If the chatbot fails to connect:
1. Make sure your Internet connection is active
2. Check if OpenRouter or DeepSeek API services are experiencing downtime
3. Check your Django server logs for connection-related errors
4. Try the dedicated testing page: http://127.0.0.1:8000/test-deepseek/

### Widget Connection Issues
If the chatbot widget is not getting responses from DeepSeek:
1. Check that the widget is sending requests to `/chat/` endpoint, not `/api/dialogflow/webhook/`
2. Inspect browser network requests to verify the correct API endpoint is being used
3. Try using the test page to isolate front-end vs back-end issues
- Analytics dashboard to track common questions and issues
- Add more language support beyond Vietnamese

## Notes
- The chatbot falls back to keyword-based responses when API calls fail
- The conversation memory is session-based and preserved between page loads
- Product recommendations are based on category and author matching
