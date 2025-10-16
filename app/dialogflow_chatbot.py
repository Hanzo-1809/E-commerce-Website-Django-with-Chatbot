import os
from google.cloud import dialogflow_v2
from google.api_core.exceptions import InvalidArgument
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, Category, Order
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class DialogflowChatbot:
    def __init__(self):
        self.project_id = settings.DIALOGFLOW_PROJECT_ID
        self.language_code = 'vi'
        try:
            self.session_client = dialogflow_v2.SessionsClient()
            logger.info("Dialogflow client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Dialogflow client: {str(e)}")
            raise

    def detect_intent(self, session_id, text):
        try:
            session = self.session_client.session_path(self.project_id, session_id)
            text_input = dialogflow_v2.TextInput(text=text, language_code=self.language_code)
            query_input = dialogflow_v2.QueryInput(text=text_input)

            logger.info(f"Sending request to Dialogflow - Session: {session_id}, Text: {text}")
            
            response = self.session_client.detect_intent(
                request={"session": session, "query_input": query_input}
            )
            
            intent_name = response.query_result.intent.display_name
            logger.info(f"Received response from Dialogflow - Intent: {intent_name}")
            
            # Handle different intents
            intent_handlers = {
                "Book_Search": self._handle_book_search,
                "Book_Price": self._handle_book_price,
                "Order_Status": self._handle_order_status,
                "Payment_Methods": self._handle_payment_methods,
                "Store_Hours": self._handle_store_hours,
                "Book_Recommendation": self._handle_book_recommendation,
                "Customer_Support": self._handle_customer_support
            }
            
            if intent_name in intent_handlers:
                return intent_handlers[intent_name](response)
            
            return {
                'fulfillment_text': response.query_result.fulfillment_text,
                'intent': intent_name,
                'confidence': response.query_result.intent_detection_confidence
            }
            
        except InvalidArgument as e:
            logger.error(f"Invalid argument error: {str(e)}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in detect_intent: {str(e)}")
            return {'error': 'Internal server error'}

    def _handle_book_search(self, response):
        try:
            parameters = response.query_result.parameters
            category = parameters.get('book_category')
            author = parameters.get('author')
            price_range = parameters.get('price_range')

            query = Product.objects.filter(status=True)

            if category:
                query = query.filter(category__name__icontains=category)
            if author:
                query = query.filter(author__icontains=author)
            if price_range:
                min_price = price_range.get('min', 0)
                max_price = price_range.get('max', float('inf'))
                query = query.filter(price__gte=min_price, price__lte=max_price)

            books = query[:5]
            
            if not books:
                return {
                    'fulfillment_text': "Xin lỗi, tôi không tìm thấy sách phù hợp với yêu cầu của bạn.",
                    'intent': response.query_result.intent.display_name,
                    'confidence': response.query_result.intent_detection_confidence
                }

            book_list = "\n".join([
                f"- {book.name} của {book.author}: {book.price:,}đ" 
                for book in books
            ])
            
            return {
                'fulfillment_text': f"Đây là một số sách phù hợp:\n{book_list}",
                'intent': response.query_result.intent.display_name,
                'confidence': response.query_result.intent_detection_confidence,
                'suggestions': ['Xem chi tiết sách', 'Thêm vào giỏ hàng', 'Tìm sách khác']
            }

        except Exception as e:
            logger.error(f"Error in _handle_book_search: {str(e)}")
            return {'error': 'Error processing book search'}

    def _handle_book_price(self, response):
        try:
            book_name = response.query_result.parameters.get('book_name')
            if book_name:
                try:
                    book = Product.objects.get(name__icontains=book_name)
                    return {
                        'fulfillment_text': f"Sách '{book.name}' có giá {book.price:,}đ",
                        'intent': response.query_result.intent.display_name,
                        'confidence': response.query_result.intent_detection_confidence,
                        'suggestions': ['Mua ngay', 'Xem chi tiết', 'Tìm sách khác']
                    }
                except Product.DoesNotExist:
                    return {
                        'fulfillment_text': f"Xin lỗi, tôi không tìm thấy sách có tên '{book_name}'",
                        'intent': response.query_result.intent.display_name,
                        'confidence': response.query_result.intent_detection_confidence,
                        'suggestions': ['Tìm sách khác', 'Xem sách mới', 'Liên hệ hỗ trợ']
                    }
        except Exception as e:
            logger.error(f"Error in _handle_book_price: {str(e)}")
            return {'error': 'Error processing book price query'}

    def _handle_order_status(self, response):
        try:
            order_id = response.query_result.parameters.get('order_id')
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    status_map = {
                        'pending': 'đang chờ xử lý',
                        'processing': 'đang xử lý',
                        'shipped': 'đã gửi hàng',
                        'delivered': 'đã giao hàng',
                        'cancelled': 'đã hủy'
                    }
                    status = status_map.get(order.status, order.status)
                    return {
                        'fulfillment_text': f"Đơn hàng #{order_id} của bạn hiện {status}",
                        'intent': response.query_result.intent.display_name,
                        'confidence': response.query_result.intent_detection_confidence
                    }
                except Order.DoesNotExist:
                    return {
                        'fulfillment_text': f"Không tìm thấy đơn hàng #{order_id}",
                        'suggestions': ['Kiểm tra lại mã đơn hàng', 'Liên hệ hỗ trợ']
                    }
        except Exception as e:
            logger.error(f"Error in _handle_order_status: {str(e)}")
            return {'error': 'Error checking order status'}

    def _handle_payment_methods(self, response):
        payment_info = """Chúng tôi hỗ trợ các phương thức thanh toán sau:
1. Thanh toán khi nhận hàng (COD)
2. Chuyển khoản ngân hàng
3. Ví điện tử (Momo, ZaloPay)
4. Thẻ tín dụng/ghi nợ

Bạn muốn tìm hiểu chi tiết về phương thức nào?"""
        return {
            'fulfillment_text': payment_info,
            'intent': response.query_result.intent.display_name,
            'confidence': response.query_result.intent_detection_confidence,
            'suggestions': ['COD', 'Chuyển khoản', 'Ví điện tử', 'Thẻ tín dụng']
        }

    def _handle_store_hours(self, response):
        store_hours = """Giờ làm việc của cửa hàng:
- Thứ 2 - Thứ 6: 8:00 - 21:00
- Thứ 7 - Chủ nhật: 9:00 - 22:00
- Ngày lễ: 9:00 - 20:00"""
        return {
            'fulfillment_text': store_hours,
            'intent': response.query_result.intent.display_name,
            'confidence': response.query_result.intent_detection_confidence
        }

    def _handle_book_recommendation(self, response):
        try:
            parameters = response.query_result.parameters
            category = parameters.get('book_category')
            price_range = parameters.get('price_range', {'min': 0, 'max': 1000000})

            # Get top rated books in category
            books = Product.objects.filter(
                status=True,
                price__gte=price_range['min'],
                price__lte=price_range['max']
            ).order_by('-rating')[:3]

            if category:
                books = books.filter(category__name__icontains=category)

            if not books:
                return {
                    'fulfillment_text': "Xin lỗi, hiện tại chúng tôi không có sách phù hợp với yêu cầu của bạn.",
                    'suggestions': ['Xem sách mới', 'Tìm theo thể loại khác']
                }

            recommendations = "\n".join([
                f"- {book.name} của {book.author} - Đánh giá: {book.rating}/5 - Giá: {book.price:,}đ"
                for book in books
            ])

            return {
                'fulfillment_text': f"Đây là một số sách được đề xuất cho bạn:\n{recommendations}",
                'intent': response.query_result.intent.display_name,
                'confidence': response.query_result.intent_detection_confidence,
                'suggestions': ['Xem chi tiết', 'Đặt mua ngay', 'Đề xuất khác']
            }

        except Exception as e:
            logger.error(f"Error in _handle_book_recommendation: {str(e)}")
            return {'error': 'Error generating recommendations'}

    def _handle_customer_support(self, response):
        support_info = """Bạn có thể liên hệ với chúng tôi qua:
1. Hotline: 1900-xxxx (8:00 - 22:00)
2. Email: support@jbook.com
3. Facebook Messenger: fb.com/jbook
4. Zalo: zalo.me/jbook"""
        return {
            'fulfillment_text': support_info,
            'intent': response.query_result.intent.display_name,
            'confidence': response.query_result.intent_detection_confidence,
            'suggestions': ['Gọi điện', 'Gửi email', 'Chat Facebook', 'Chat Zalo']
        }

@csrf_exempt
def dialogflow_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            message = data.get('message')

            if not session_id or not message:
                return JsonResponse({'error': 'Missing session_id or message'}, status=400)

            chatbot = DialogflowChatbot()
            response = chatbot.detect_intent(session_id, message)
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error in dialogflow_webhook: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405) 