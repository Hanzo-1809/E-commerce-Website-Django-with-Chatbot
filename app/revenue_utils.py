from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F
from .models import Order, OrderItem, Product

def get_monthly_revenue():
    """Lấy doanh thu theo tháng trong năm hiện tại"""
    current_year = timezone.now().year
    monthly_revenue = [0] * 12  # Khởi tạo danh sách 12 tháng với giá trị 0
    
    # Lấy tất cả đơn hàng hoàn thành trong năm hiện tại
    orders = Order.objects.filter(
        complete=True,
        date_ordered__year=current_year
    )
    
    # Tính tổng doanh thu cho mỗi tháng
    for order in orders:
        month_index = order.date_ordered.month - 1  # Index từ 0-11
        monthly_revenue[month_index] += order.get_cart_total
    
    return monthly_revenue

def get_top_products(limit=5):
    """Lấy top sản phẩm bán chạy nhất"""
    # Lấy danh sách sản phẩm và tổng số lượng bán của mỗi sản phẩm
    top_products = OrderItem.objects.filter(
        order__complete=True
    ).values('product__id', 'product__name', 'product__price').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
    ).order_by('-total_quantity')[:limit]
    
    # Lấy thông tin chi tiết của từng sản phẩm
    result = []
    for item in top_products:
        try:
            product = Product.objects.get(id=item['product__id'])
            result.append({
                'product': product,
                'total_quantity': item['total_quantity'],
                'total_revenue': item['total_revenue']
            })
        except Product.DoesNotExist:
            # Bỏ qua sản phẩm không tồn tại
            pass
    
    return result
