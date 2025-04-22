import frappe
from frappe.model.document import Document

class OrderItem(Document):
    def validate(self):
        if not self.price or self.price <= 0:
            frappe.throw("Price must be greater than 0")
        
        if not self.num or self.num <= 0:
            frappe.throw("Quantity must be greater than 0")
            
        # Get book details to validate stock
        book = frappe.get_doc("Book", self.product_id)
        if not book:
            frappe.throw(f"Book {self.product_id} not found")
            
        if book.quantity < self.num:
            frappe.throw(f"Not enough stock for book {book.book_name}. Available: {book.quantity}")
            
        # Set price from book if not manually changed
        if not self.price:
            self.price = book.price