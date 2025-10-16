from django.urls import path
from . import views
from . import dialogflow_chatbot

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.register, name='register'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('search/', views.search, name='search'),
    path('detail/', views.detail, name='detail'),
    path('detail/<int:product_id>/', views.detail, name='detail'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('category/', views.category, name='category'),
    path('profile/', views.profile, name='profile'),
    path('chat/', views.chatbot_response, name='chat'),
    path('order_success/', views.order_success, name='order_success'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('admin-customers/', views.admin_customers, name='admin_customers'),
    path('admin-products/', views.admin_products, name='admin_products'),
    path('admin-reviews/', views.admin_reviews, name='admin_reviews'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    # path('chatbot/', views.chatbot_page, name='chatbot_page'),
    path('api/dialogflow/webhook/', dialogflow_chatbot.dialogflow_webhook, name='dialogflow_webhook'),
]