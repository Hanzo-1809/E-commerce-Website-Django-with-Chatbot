from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse 
import json
from django.db import models

from app.models import *
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

# Create your views here.
   
def detail(request):
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

    id = request.GET.get('id', '')
    products = Product.objects.filter(id=id)
    categories = Category.objects.filter(is_sub=False)
    context ={'products':products,'categories': categories ,'id':id ,'order': order, 'items': items, 'cartItems': cartItems, 'user_login': user_login, 'user_not_login': user_not_login}
    return render(request, 'app/detail.html', context)
def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    if active_category:
        products = Product.objects.filter(category__slug=active_category)

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
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
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
        carrtItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
        products = Product.objects.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        carrtItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    products = Product.objects.all()
    context ={'products': products, 'carrtItems': carrtItems, 'user_not_login': user_not_login, 'user_login': user_login, 'categories': categories, 'active_category': active_category}
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
    context ={'order': order, 'items': items}
    return render(request, 'app/cart.html', context)
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
    context ={'order': order, 'items': items}
    return render(request, 'app/checkout.html', context)
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

