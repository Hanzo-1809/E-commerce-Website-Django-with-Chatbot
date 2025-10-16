from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse 
import json
from django.db import models
from django.contrib import messages
from app.models import *
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth import authenticate, login, logout
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Sum, F, Q

# views.py
from django.shortcuts import render
from django.http import JsonResponse
import json
import os
from django.conf import settings
from app.chatbot_data import WEB_FEATURES, FAQS, STORE_INFO

# Sử dụng chatbot thông minh
from .smart_chatbot_deepseek import get_smart_response
from .simple_chatbot import get_simple_response

import logging
logger = logging.getLogger(__name__)

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        try:
            # Log chi tiết request
            logger.info(f"Nhận được POST request đến chatbot endpoint")
            logger.info(f"Headers: {request.headers}")
            
            # Parse JSON request body
            data = json.loads(request.body)
            user_input = data.get('message', '')
            
            # Log raw input
            logger.info(f"Chatbot received raw input: '{user_input}'")
            
            if not user_input or len(user_input.strip()) == 0:
                return JsonResponse({'reply': 'Xin lỗi, tôi không nhận được câu hỏi của bạn.'})
            
            # Get or create a session ID for conversation memory
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
                logger.info(f"Tạo session mới, ID: {session_id}")
            else:
                logger.info(f"Sử dụng session hiện có, ID: {session_id}")
                
            try:
                # Lấy thông tin sản phẩm từ database
                products_info = []
                # Get more products for better search capabilities
                products = Product.objects.filter(status=True).order_by('-id')[:15]  # Top 15 active products
                
                for product in products:
                    product_info = {
                        'id': product.id,
                        'name': product.name,
                        'price': str(product.price),
                        'quantity': product.quantity,
                        'status': product.status
                    }
                    
                    # Thêm thông tin tác giả và mô tả nếu có
                    if hasattr(product, 'author') and product.author:
                        product_info['author'] = product.author
                    
                    if hasattr(product, 'description') and product.description:
                        # Keep full description for better search results
                        product_info['description'] = product.description
                    
                    # Thêm danh mục sản phẩm
                    categories = [cat.name for cat in product.category.all()]
                    if categories:
                        product_info['categories'] = ', '.join(categories)
                    
                    products_info.append(product_info)
                
                # Log the interaction (for debugging)
                logger.info(f"Chatbot session {session_id} received: {user_input}")
                
                # Use the enhanced smart chatbot with product info and conversation memory
                logger.info("Gọi hàm get_smart_response để lấy câu trả lời từ DeepSeek API")
                response = get_smart_response(
                    user_input=user_input, 
                    products=products_info, 
                    session_id=session_id
                )
                
                # Log the final response
                logger.info(f"Chatbot response: {response[:100]}...")
                
                # Trả về response cho client
                logger.info("Gửi phản hồi JSON về client")
                return JsonResponse({'reply': response})
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error in chatbot: {error_msg}")
                logger.exception("Detailed exception:")
                
                # If any error occurs, use the simplest fallback
                simple_response = get_simple_response(user_input)
                return JsonResponse({
                    'reply': f"Xin lỗi, có lỗi xảy ra. {simple_response}"
                })
                
        except json.JSONDecodeError as je:
            logger.error(f"Invalid JSON in request body: {je}")
            logger.error(f"Raw request body: {request.body}")
            return JsonResponse({'reply': 'Lỗi định dạng dữ liệu JSON.'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.exception("Detailed exception:")
            return JsonResponse({'reply': 'Xin lỗi, có lỗi xảy ra.'}, status=500)

    return JsonResponse({'reply': 'Chỉ hỗ trợ phương thức POST'}, status=405)



def profile(request):
    if request.user.is_authenticated:
        customer = request.user
        orders = Order.objects.filter(customer=customer,complete=True).order_by('-date_ordered')
        # Get shipping info for each order
        orders_with_shipping = []
        for order in orders:
            try:
                shipping = order.shippingaddress  # Using OneToOneField relationship
            except ShippingAddress.DoesNotExist:
                shipping = None
            order_items = order.orderitem_set.all()
            orders_with_shipping.append({
                'order': order,
                'shipping': shipping,
                'items': order_items,
                'total_items': order.get_cart_items,
                'date': order.date_ordered,
                'status': order.status
            })
        user_login = "show"
        user_not_login = "hidden"
    else:
        user_login = "hidden"
        user_not_login = "show"
        orders_with_shipping = []
        
    context = {
        'orders': orders_with_shipping, 
        'user_login': user_login, 
        'user_not_login': user_not_login
    }
    return render(request, 'app/profile.html', context)
def detail(request, product_id=None):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_login = "show"
        user_not_login = "hidden"
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']
        user_login = "hidden"
        user_not_login = "show"

    # Get product ID from either URL parameter or query parameter
    if product_id is None:
        product_id = request.GET.get('id', '')
    
    product = Product.objects.get(id=product_id)
    categories = Category.objects.filter(is_sub=False)
    related_books = Product.objects.filter(
        category__in=product.category.all()
    ).exclude(
        id=product_id
    ).distinct()[:4] 
     # Hoặc tìm theo tác giả
    if not related_books and product.author:
        related_books = Product.objects.filter(
            author=product.author
        ).exclude(id=product_id)[:4]
    
    # Nếu vẫn không có sách liên quan, lấy một số sách mới nhất
    if not related_books:
        related_books = Product.objects.exclude(id=product_id).order_by('-id')[:4]
    

    # Check if user can review (has purchased and hasn't reviewed)
    can_review = False
    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(
            customer=request.user,
            complete=True,
            orderitem__product=product
        ).exists()
        has_reviewed = Review.objects.filter(
            user=request.user,
            product=product
        ).exists()
        can_review = has_purchased and not has_reviewed

    context = {
        'product': product,
        'categories': categories,
        'order': order, 
        'items': items, 
        'cartItems': cartItems,
        'user_login': user_login,
        'user_not_login': user_not_login,
        'can_review': can_review,
        'related_books': related_books
    }
    return render(request, 'app/detail.html', context)
def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    
    # Khởi tạo products với tất cả sản phẩm nếu không có category được chọn
    if active_category:
        products = Product.objects.filter(category__slug=active_category)
    else:
        # Hiển thị tất cả sản phẩm nếu không có category nào được chọn
        products = Product.objects.all()

    context = {'categories': categories, 'active_category': active_category, 'products': products}
    return render(request, 'app/category.html', context) 
def search(request):
    if request.method == 'POST':
        search = request.POST['query']
        products = Product.objects.filter(name__contains=search)
        return render(request, 'app/search.html', {'query':search, 'keys':products})
    else:
        
        return render(request, 'app/search.html', {})

def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')
    context = {}

    return render(request, 'app/login.html', context)
def logoutPage(request):
    logout(request)
    return redirect('login')
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context = {'form': form}
    return render(request, 'app/register.html', context)
def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
        products = Product.objects.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    products = Product.objects.all()
    top_selling_products = OrderItem.objects.filter(
        order__complete=True
    ).values('product__id').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    # Lấy chi tiết sản phẩm
    top_products = []
    for item in top_selling_products:
        try:
            product = Product.objects.get(id=item['product__id'])
            # Thêm thông tin số lượng đã bán
            product.sold = item['total_quantity']
            top_products.append(product)
        except Product.DoesNotExist:
            pass
            
    context ={ 'products': products,'top_products': top_products, 'cartItems': cartItems, 'user_not_login': user_not_login, 'user_login': user_login, 'categories': categories, 'active_category': active_category}
    return render(request, 'app/home.html', context)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_login = "show"
        user_not_login = "hidden"
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']
        user_login = "hidden"
        user_not_login = "show"
    context ={'order': order, 'items': items, 'cartItems': cartItems, 'user_login': user_login, 'user_not_login': user_not_login}
    return render(request, 'app/cart.html', context)
from django.shortcuts import render, redirect
from .models import Order, OrderItem, ShippingAddress

def checkout(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Please login first!"})
        
    customer = request.user
    
    if request.method == "POST":
        try:
            # Lấy đơn hàng hiện tại chưa hoàn thành
            order = Order.objects.filter(customer=customer, complete=False).first()
            
            # Kiểm tra xem đơn hàng có tồn tại và có sản phẩm không
            if not order or order.get_cart_items == 0:
                return JsonResponse({"status": "error", "message": "Your cart is empty!"})

            # Kiểm tra thông tin bắt buộc
            receiver_name = request.POST.get("name")
            phone = request.POST.get("mobile")
            address = request.POST.get("address")
            city = request.POST.get("city", "")
            pincode = request.POST.get("pincode", "")
            payment = request.POST.get("payment")

            if not all([receiver_name, phone, address]):
                return JsonResponse({"status": "error", "message": "Please fill all required fields!"})

            # Lưu thông tin shipping
            shipping = ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=address,
                city=city,
                mobile=phone,
                state=pincode
            )

            # Đánh dấu đơn hàng đã hoàn tất
            order.complete = True
            order.save()

            return JsonResponse({"status": "success"})
            
        except Exception as e:
            print("Checkout error:", str(e))
            return JsonResponse({"status": "error", "message": "An error occurred during checkout!"})
            
    return JsonResponse({"status": "error", "message": "Invalid request method!"})


def order_success(request):
    customer = request.user
    order = Order.objects.filter(customer=customer, complete=True).last()
    if not order:
        return redirect("home")
    context = {"order": order}
    return render(request, "app/cart.html", context)
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)
    customer = request.user 
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity +=1
    elif action == 'remove':
        orderItem.quantity -=1
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')
        
    # Lấy thống kê cơ bản
    abandoned_cart = Order.objects.filter(complete=False).count()
    total_customers = User.objects.filter(is_superuser=False).count()
    active_customers = Order.objects.filter(complete=True).values('customer').distinct().count()
    all_orders = Order.objects.filter(complete=True)
    
    # Thống kê đơn hàng theo trạng thái
    pending_orders = Order.objects.filter(complete=True, status='pending').count()
    confirmed_orders = Order.objects.filter(complete=True, status='confirmed').count()
    shipping_orders = Order.objects.filter(complete=True, status='shipping').count()
    completed_orders = Order.objects.filter(complete=True, status='completed').count()
    cancelled_orders = Order.objects.filter(complete=True, status='cancelled').count()
    
    # Lấy đơn hàng gần đây
    recent_orders = Order.objects.filter(complete=True).order_by('-date_ordered')[:10]
    
    # Tính toán thống kê doanh thu
    # Tổng doanh thu
    total_revenue = sum(order.get_cart_total for order in all_orders)
    
    # Lấy ngày đầu tiên và cuối cùng của tháng hiện tại
    today = timezone.now()
    first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Lấy ngày đầu tiên của tháng trước
    last_month = (first_day_current_month - timedelta(days=1)).replace(day=1)
    
    # Tháng này và tháng trước
    orders_this_month = all_orders.filter(date_ordered__gte=first_day_current_month)
    orders_last_month = all_orders.filter(date_ordered__gte=last_month, date_ordered__lt=first_day_current_month)
    
    # Doanh thu tháng này và tháng trước
    this_month_revenue = sum(order.get_cart_total for order in orders_this_month)
    last_month_revenue = sum(order.get_cart_total for order in orders_last_month)
    
    # Tính tỷ lệ tăng trưởng
    if last_month_revenue > 0:
        revenue_growth = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
    else:
        revenue_growth = 100 if this_month_revenue > 0 else 0
    
    # Tính trung bình giá trị đơn hàng
    average_order = total_revenue / all_orders.count() if all_orders.count() > 0 else 0
    
    # Thống kê doanh thu theo tháng trong năm hiện tại
    current_year = timezone.now().year
    monthly_revenue = [0] * 12  # Khởi tạo danh sách 12 tháng với giá trị 0
    
    # Lấy tất cả đơn hàng hoàn thành trong năm hiện tại
    year_orders = all_orders.filter(date_ordered__year=current_year)
    
    # Tính tổng doanh thu cho mỗi tháng
    for order in year_orders:
        month_index = order.date_ordered.month - 1  # Index từ 0-11
        monthly_revenue[month_index] += order.get_cart_total
    
    # Lấy top sản phẩm bán chạy
    top_products = OrderItem.objects.filter(
        order__complete=True
    ).values('product__id', 'product__name', 'product__price').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
    ).order_by('-total_quantity')[:5]
    
    # Lấy thông tin chi tiết của từng sản phẩm
    top_products_list = []
    for item in top_products:
        try:
            product = Product.objects.get(id=item['product__id'])
            top_products_list.append({
                'product': product,
                'total_quantity': item['total_quantity'],
                'total_revenue': item['total_revenue']
            })
        except Product.DoesNotExist:
            # Bỏ qua sản phẩm không tồn tại
            pass

    context = {
        'abandoned_cart': abandoned_cart,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'all_orders': all_orders.count(),
        'pending_orders': pending_orders,
        'shipping_orders': shipping_orders,
        'completed_orders': completed_orders,
        'confirmed_orders': confirmed_orders,
        'cancelled_orders': cancelled_orders,
        'recent_orders': recent_orders,
        
        # Thông tin doanh thu
        'total_revenue': total_revenue,
        'this_month_revenue': this_month_revenue,
        'last_month_revenue': last_month_revenue,
        'revenue_growth': revenue_growth,
        'average_order': average_order,
        'monthly_revenue': monthly_revenue,
        'top_products': top_products_list,
    }
    
    return render(request, 'app/admin/dashboard.html', context)

def admin_orders(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            try:
                order = Order.objects.get(id=order_id)
                success = order.update_status(new_status)
                if success:
                    messages.success(request, f'Đơn hàng #{order_id} đã được cập nhật thành {order.get_status_display_name}')
                else:
                    messages.error(request, f'Không thể cập nhật trạng thái đơn hàng. Trạng thái "{new_status}" không hợp lệ.')
            except Order.DoesNotExist:
                messages.error(request, 'Không tìm thấy đơn hàng')
            except Exception as e:
                messages.error(request, f'Lỗi khi cập nhật trạng thái: {str(e)}')
            
        elif action == 'delete':
            order_id = request.POST.get('order_id')
            try:
                Order.objects.get(id=order_id, complete=True).delete()
                messages.success(request, 'Đơn hàng đã xóa thành công')
            except Order.DoesNotExist:
                messages.error(request, 'Không tìm thấy đơn hàng')
    
    # Chỉ hiển thị đơn hàng thật (complete=True), không hiển thị giỏ hàng
    orders = Order.objects.filter(complete=True).order_by('-date_ordered')
    
    # Lọc theo status nếu có
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Lọc theo ID đơn hàng nếu có
    order_id = request.GET.get('order_id', '')
    if order_id:
        orders = orders.filter(id=order_id)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'order_id': order_id,
        'status_choices': Order.STATUS_CHOICES
    }
    return render(request, 'app/admin/orders.html', context)

def admin_customers(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete':
            customer_id = request.POST.get('customer_id')
            user = User.objects.get(id=customer_id)
            if not user.is_superuser:
                user.delete()
                messages.success(request, 'Customer deleted successfully')
    
    customers = User.objects.all()
    for customer in customers:
        # Đếm đơn hàng đã hoàn thành
        customer.completed_orders = customer.order_set.filter(status='completed').count()
        
        # Tính tổng chi tiêu (cho các đơn hàng đã hoàn thành)
        total_spent = 0
        completed_orders = customer.order_set.filter(status='completed')
        for order in completed_orders:
            total_spent += order.get_cart_total
        customer.total_spent = total_spent
    context = {'customers': customers}
    return render(request, 'app/admin/customers.html', context)

def admin_products(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_category':
            name = request.POST.get('category_name')
            slug = request.POST.get('category_slug')
            parent_id = request.POST.get('parent_category')
            
            category = Category.objects.create(
                name=name,
                slug=slug,
                is_sub=bool(parent_id)
            )
            if parent_id:
                category.sub_category_id = parent_id
                category.save()
                
        elif action == 'edit_category':
            category_id = request.POST.get('category_id')
            category = Category.objects.get(id=category_id)
            category.name = request.POST.get('category_name')
            category.slug = request.POST.get('category_slug')
            parent_id = request.POST.get('parent_category')
            
            category.is_sub = bool(parent_id)
            category.sub_category_id = parent_id if parent_id else None
            category.save()
            
        elif action == 'delete_category':
            category_id = request.POST.get('category_id')
            Category.objects.get(id=category_id).delete()
            
        # Existing product actions...
        elif action == 'edit':
            product_id = request.POST.get('product_id')
            product = Product.objects.get(id=product_id)
            
            product.name = request.POST.get('name')
            product.price = request.POST.get('price')
            product.quantity = request.POST.get('quantity')
            product.status = request.POST.get('status')
            
            if 'image' in request.FILES:
                product.image = request.FILES['image']
                
            product.category.set(request.POST.getlist('category'))
            product.save()
            messages.success(request, 'Product updated successfully')
            
        elif action == 'delete':
            product_id = request.POST.get('product_id')
            Product.objects.get(id=product_id).delete()
            messages.success(request, 'Product deleted successfully')
        else:
            name = request.POST.get('name')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            categories = request.POST.getlist('category')
            
            product = Product.objects.create(
                name=name,
                price=price,
                quantity=quantity,
                status=status,
                image=image
            )
            product.category.set(categories)
            messages.success(request, 'Product added successfully')
            
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'app/admin/products.html', context)

def add_review(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để đánh giá sản phẩm')
        return redirect('login')
        
    product = Product.objects.get(id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Kiểm tra xem người dùng đã mua sản phẩm chưa
        order = Order.objects.filter(
            customer=request.user,
            complete=True,
            orderitem__product=product
        ).first()
        
        if not order:
            messages.error(request, 'Bạn cần mua sản phẩm trước khi đánh giá')
            return redirect('detail', product_id=product_id)
            
        # Kiểm tra xem đã đánh giá chưa
        if Review.objects.filter(user=request.user, product=product, order=order).exists():
            messages.error(request, 'Bạn đã đánh giá sản phẩm này cho đơn hàng này rồi')
            return redirect('detail', product_id=product_id)
            
        if not rating or not comment:
            messages.error(request, 'Vui lòng chọn số sao và nhập nội dung đánh giá')
            return redirect('detail', product_id=product_id)
            
        Review.objects.create(
            product=product,
            user=request.user,
            order=order,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
        return redirect('detail', product_id=product_id)
        
    return redirect('detail', product_id=product_id)
def admin_reviews(request):
    if not request.user.is_superuser:
        return redirect('login')
        
    # Lấy tất cả đánh giá và sản phẩm
    reviews = Review.objects.all().order_by('-created_at')
    products = Product.objects.all()
    
    # Filter theo sản phẩm
    current_product = request.GET.get('product', '')
    if current_product:
        reviews = reviews.filter(product_id=current_product)
    
    # Filter theo rating
    current_rating = request.GET.get('rating', '')
    if current_rating:
        reviews = reviews.filter(rating=current_rating)
    
    # Filter theo ngày
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if date_from:
        reviews = reviews.filter(created_at__gte=date_from)
    
    if date_to:
        reviews = reviews.filter(created_at__lte=date_to)
    
    context = {
        'reviews': reviews,
        'products': products,
        'current_product': current_product,
        'current_rating': current_rating,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'app/admin/reviews.html', context)

@csrf_exempt  # Thêm bảo mật CSRF sau khi hoạt động
def delete_review(request, review_id):
    if not request.user.is_superuser:
        # Nếu là AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Authentication required'})
        return redirect('login')
        
    try:
        review = Review.objects.get(id=review_id)
        review.delete()
        messages.success(request, 'Đánh giá đã được xóa thành công!')
        
        # Kiểm tra nếu là AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
            
        return redirect('admin_reviews')
    except Review.DoesNotExist:
        messages.error(request, 'Không tìm thấy đánh giá này!')
        
        # Kiểm tra nếu là AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Review not found'})
            
        return redirect('admin_reviews')

