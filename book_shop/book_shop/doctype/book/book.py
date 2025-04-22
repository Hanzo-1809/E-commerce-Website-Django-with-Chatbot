import frappe
from frappe.model.document import Document
from frappe.utils import now
import json

class Book(Document):
    def validate(self):
        # Validate price is positive
        if self.price and self.price <= 0:
            frappe.throw('Price must be greater than 0')
        
        # Cập nhật thời gian
        if self.is_new():
            self.created_at = frappe.utils.now_datetime()
        self.updated_at = frappe.utils.now_datetime()
        
        if not self.quantity:
            self.quantity = 0
        
        if self.quantity < 0:
            frappe.throw("Quantity cannot be negative")
        
    def before_save(self):
        # Set created_at on first save
        if not self.created_at:
            self.created_at = now()
        
        # Update updated_at on every save
        self.updated_at = now()
        
    def after_insert(self):
        # Thực hiện các hành động sau khi tạo mới
        self.handle_thumbnail()
        
    def on_update(self):
        # Xử lý các thay đổi khi cập nhật
        self.handle_thumbnail()
    
    def handle_thumbnail(self):
        # Xử lý ảnh thumbnail nếu có sự thay đổi
        if self.has_value_changed("thumbnail") and self.thumbnail:
            # Log thông tin về việc cập nhật hình ảnh
            frappe.logger().info(f"Book {self.name}: Thumbnail updated to {self.thumbnail}")
            
            # Đảm bảo thumbnail đã được lưu trữ trong hệ thống file
            # Frappe đã tự động xử lý việc lưu trữ file, không cần thêm xử lý đặc biệt
            
            # Cập nhật URL của thumbnail nếu cần
            if not self.thumbnail.startswith(('http://', 'https://', '/')):
                # Đảm bảo đường dẫn đầy đủ cho thumbnail
                self.db_set('thumbnail', f"/{self.thumbnail}", update_modified=False)
                
            # Tối ưu hóa ảnh nếu cần
            self.optimize_thumbnail()
    
    def optimize_thumbnail(self):
        """Tối ưu hóa ảnh thumbnail nếu kích thước quá lớn"""
        try:
            # Chỉ xử lý với các file ảnh
            if not self.thumbnail or not self.thumbnail.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return
                
            # Có thể thêm logic tối ưu hóa ảnh ở đây nếu cần
            frappe.logger().info(f"Book {self.name}: Thumbnail optimization completed")
        except Exception as e:
            frappe.logger().error(f"Error optimizing thumbnail for book {self.name}: {str(e)}")
    
    def check_stock(self, required_qty):
        """Check if there is enough stock for the required quantity"""
        if self.quantity < required_qty:
            return False, self.quantity
        return True, self.quantity
        
    def update_stock(self, quantity_change, reference_type=None, reference_name=None):
        """Update book stock with change tracking"""
        if not isinstance(quantity_change, (int, float)):
            frappe.throw("Quantity change must be a number")
            
        new_quantity = self.quantity + quantity_change
        if new_quantity < 0:
            frappe.throw(f"Cannot reduce stock below 0. Current stock: {self.quantity}")
            
        old_quantity = self.quantity
        self.quantity = new_quantity
        
        # Add a comment to track the stock change
        self.add_comment('Info', 
            f'Stock changed from {old_quantity} to {new_quantity} ({quantity_change:+d} units). ' +
            (f'Reference: {reference_type} {reference_name}' if reference_type else 'Manual adjustment')
        )
        
        self.save()

@frappe.whitelist()
def get_books(filters=None):
    """Get list of books based on filters"""
    books = frappe.get_all('Book',
        filters=filters,
        fields=['name', 'id', 'book_name', 'category_id', 'price', 'status','quantity', 'thumbnail', 'created_at', 'updated_at'],
        order_by='modified desc'
    )
    
    # Xử lý thumbnail URL cho mỗi sách
    for book in books:
        if book.get('thumbnail'):
            # Đảm bảo đường dẫn đầy đủ cho thumbnail
            if not book['thumbnail'].startswith(('http://', 'https://', '/')):
                book['thumbnail'] = '/' + book['thumbnail']
        else:
            # Sử dụng ảnh mặc định nếu không có thumbnail
            book['thumbnail'] = '/assets/book_shop/images/default-book.svg'
    
    return books

@frappe.whitelist()
def update_book_status(name, status):
    """Update book status"""
    if status not in ['Draft', 'Published', 'Archived']:
        frappe.throw('Invalid status value')
        
    book = frappe.get_doc('Book', name)
    book.status = status
    book.save()
    return book

@frappe.whitelist()
def get_books_by_category(category_id):
    """Get books filtered by category"""
    books = frappe.get_all('Book',
        filters={'category_id': category_id},
        fields=['name', 'id', 'book_name', 'price', 'status','quantity', 'thumbnail', 'created_at', 'updated_at'],
        order_by='book_name asc'
    )
    
    # Xử lý thumbnail URL cho mỗi sách
    for book in books:
        if book.get('thumbnail'):
            # Đảm bảo đường dẫn đầy đủ cho thumbnail
            if not book['thumbnail'].startswith(('http://', 'https://', '/')):
                book['thumbnail'] = '/' + book['thumbnail']
        else:
            # Sử dụng ảnh mặc định nếu không có thumbnail
            book['thumbnail'] = '/assets/book_shop/images/default-book.svg'
    
    return books

@frappe.whitelist()
def save_book():
    """Save book data with thumbnail support"""
    try:
        # Get book data from request
        book_data = frappe.local.form_dict.get('book_data')
        frappe.logger().info(f"Received book_data: {book_data}")
        
        # Parse JSON if it's a string
        if isinstance(book_data, str):
            book_data = json.loads(book_data)
        
        book_id = book_data.get('name')
        frappe.logger().info(f"Processing book with ID: {book_id}")
        
        has_thumbnail = 'thumbnail' in book_data and book_data.get('thumbnail')
        thumbnail_is_base64 = has_thumbnail and book_data.get('thumbnail').startswith('data:image')
        
        # Lưu dữ liệu thumbnail nếu có
        temp_thumbnail_data = None
        if thumbnail_is_base64:
            temp_thumbnail_data = book_data.pop('thumbnail')
        
        # Nếu là sách mới thì tạo document mới
        if not book_id:
            book = frappe.new_doc('Book')
        else:
            # Nếu cập nhật sách hiện có
            book = frappe.get_doc('Book', book_id)
        
        # Cập nhật các trường thông tin
        for field in ['id', 'book_name', 'category_id', 'quantity', 'price', 'status', 'description']:
            if field in book_data:
                book.set(field, book_data.get(field))
        
        # Lưu book trước để có name
        book.save()
        frappe.db.commit()
        
        # Bây giờ xử lý thumbnail sau khi đã có book.name
        if has_thumbnail:
            if not thumbnail_is_base64:
                # Trường hợp là URL, không phải base64
                thumbnail_data = book_data.get('thumbnail')
                book.thumbnail = thumbnail_data
                frappe.logger().info(f"Setting thumbnail URL: {thumbnail_data}")
            elif temp_thumbnail_data:
                # Trường hợp là dữ liệu base64 mới
                import base64
                from frappe.utils.file_manager import save_file
                
                # Xác định định dạng file từ header
                content_type = temp_thumbnail_data.split(';')[0].split(':')[1]
                file_ext = content_type.split('/')[1]
                if file_ext == 'jpeg':
                    file_ext = 'jpg'
                
                # Lấy dữ liệu base64
                base64_data = temp_thumbnail_data.split(',')[1]
                decoded_data = base64.b64decode(base64_data)
                
                # Tạo tên file
                filename = f"book_thumb_{book.name}.{file_ext}"
                
                # Lưu file vào hệ thống - bây giờ chúng ta đã có book.name
                fileobj = save_file(
                    filename,
                    decoded_data,
                    'Book',
                    book.name,
                    folder='Home/Attachments',
                    is_private=0
                )
                
                # Cập nhật trường thumbnail
                book.thumbnail = fileobj.file_url
                frappe.logger().info(f"Saved new image file: {fileobj.file_url}")
                
                # Lưu lại book sau khi đã cập nhật thumbnail
                book.save()
                frappe.db.commit()
        
        return {
            "success": True,
            "message": "Book saved successfully",
            "book": book.as_dict()
        }
    except Exception as e:
        frappe.logger().error(f"Error saving book: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Book Save Error")
        return {
            "success": False,
            "message": str(e)
        }