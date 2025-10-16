# Thêm vào đầu file (sau các import hiện có)
from django.db.models import Sum, F
from app.models import OrderItem, Product

# Định nghĩa các câu trả lời mặc định khi không hiểu câu hỏi của người dùng
FALLBACK_RESPONSES = [
    "Tôi là một chatbot đơn giản. Đối với các câu hỏi phức tạp hơn, hãy sử dụng chatbot thông minh của chúng tôi!",
    "Tôi không hiểu ý bạn. Bạn có thể diễn đạt lại không?",
    "Tôi không chắc là tôi hiểu. Tôi có thể giúp bạn điều gì khác không?",
    "Điều này nằm ngoài khả năng của tôi. Hãy để tôi chuyển sang chatbot thông minh hơn."
]

def get_simple_response(user_message):
    """
    Một hàm đơn giản để trả về câu trả lời cơ bản dựa trên đầu vào của người dùng
    Args:
        user_message (str): Tin nhắn từ người dùng
    Returns:
        str: Một câu trả lời đơn giản
    """
    # Chuyển tin nhắn thành chữ thường để dễ dàng so khớp
    message = user_message.lower()
        # Kiểm tra câu hỏi về sách bán chạy
    if ('top' in message or 'bán chạy' in message or 'phổ biến' in message) and ('sách' in message):
        try:
            # Lấy top 5 sách bán chạy nhất
            top_products = OrderItem.objects.filter(
                order__complete=True
            ).values('product__name').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5]
            
            if top_products:
                response = "Top sách bán chạy nhất tại cửa hàng chúng tôi:\n"
                for i, product in enumerate(top_products, 1):
                    response += f"{i}. {product['product__name']} - Đã bán: {product['total_quantity']} cuốn\n"
                response += "\nBạn có thể tìm hiểu thêm về bất kỳ cuốn sách nào trong danh sách này."
                return response
            
        except Exception as e:
            pass  # Nếu có lỗi, sử dụng câu trả lời mặc định bên dưới
    
    # Các câu trả lời cơ bản
    if 'hello' in message or 'hi' in message or 'chào' in message:
        return "Xin chào! Tôi có thể giúp gì cho bạn hôm nay?"
    elif 'help' in message or 'giúp' in message:
        return "Tôi ở đây để giúp bạn! Bạn muốn biết gì về sản phẩm của chúng tôi?"
    elif 'bye' in message or 'tạm biệt' in message:
        return "Tạm biệt! Chúc bạn một ngày tốt lành!"
    elif 'book' in message or 'sách' in message:  # Loại bỏ 'ice and fire' từ điều kiện này
        return "Chúng tôi có nhiều loại sách trong cửa hàng. Bạn có thể duyệt theo danh mục trên trang web của chúng tôi hoặc hỏi về một tựa sách cụ thể."
    # Thay đổi 2: Thêm mẫu câu hỏi về tựa sách cụ thể
    elif any(book_title in message for book_title in ['song of ice', 'game of thrones', 'harry potter', 'lord of the rings']):
        return "Để biết thông tin chi tiết về sách này, vui lòng cung cấp tên đầy đủ. Chúng tôi có nhiều đầu sách nổi tiếng với giá cạnh tranh."

    # Thay đổi 3: Cải thiện phát hiện câu hỏi về giá
    elif 'price' in message or 'cost' in message or 'giá' in message or 'bao nhiêu' in message:
        if any(book_title in message for book_title in ['song of ice', 'game of thrones', 'harry potter', 'lord of the rings']):
            return "Để biết giá chính xác của sách này, vui lòng kiểm tra trang sản phẩm hoặc liên hệ với nhân viên cửa hàng."
        else:
            return "Giá của chúng tôi thay đổi theo từng sản phẩm. Bạn có thể kiểm tra giá cụ thể trên trang sản phẩm."
    # Phản hồi mặc định
    else:
        return FALLBACK_RESPONSES[0]
