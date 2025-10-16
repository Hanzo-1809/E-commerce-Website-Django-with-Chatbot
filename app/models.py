from django.db import models
from django.contrib.auth.models import User # type: ignore
from django.contrib.auth.forms import UserCreationForm  


# Create your models here.
# Change forms register django

 

class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True)
    def __str__(self):
        return self.name

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email','first_name', 'last_name', 'password1', 'password2']
 
class Product(models.Model):
    category = models.ManyToManyField(Category,related_name='product')
    name = models.CharField(max_length=200,null=True)
    author = models.CharField(max_length=200, null=True, blank=True)  # Thêm trường author
    description = models.TextField(null=True, blank=True)  # Thêm trường description
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('in_stock', 'Còn hàng'),
        ('out_stock', 'Hết hàng'),
        ('coming_soon', 'Sắp có'),
    ], default='in_stock')

    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def total_reviews(self):
        return self.reviews.count()

    @property 
    def star_ratings(self):
        ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in self.reviews.all():
            ratings[review.rating] += 1
        return ratings

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chưa xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao hàng'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy')
    )
    
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        null=True,
        blank=True
    )

    def __str__(self):
        return str(self.id)    
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
        
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
        
    @property
    def get_status_display_name(self):
        """Trả về tên hiển thị của trạng thái"""
        return dict(self.STATUS_CHOICES).get(self.status, 'Không xác định')
        
    def update_status(self, new_status):
        """Cập nhật trạng thái đơn hàng"""
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            if new_status == 'completed':
                self.complete = True
            self.save()
            return True
        return False

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,blank= True ,null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL,blank= True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True) # Changed from ForeignKey to OneToOneField
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    mobile = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'order')  # Ensures one shipping address per order

    def __str__(self):
        return self.address

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 sao'),
        (2, '2 sao'), 
        (3, '3 sao'),
        (4, '4 sao'),
        (5, '5 sao'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Đảm bảo mỗi user chỉ đánh giá 1 lần cho mỗi sản phẩm trong 1 đơn hàng
        unique_together = ['product', 'user', 'order']
        ordering = ['-created_at']

    def __str__(self):
        return f'Đánh giá của {self.user.username} cho {self.product.name}'

