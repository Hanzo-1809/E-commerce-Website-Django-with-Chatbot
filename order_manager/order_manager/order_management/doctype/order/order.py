import frappe
from frappe.model.document import Document

class Order(Document):
    def validate(self):
        self.validate_items()
        self.calculate_total()
        
    def validate_items(self):
        if not self.order_items:
            frappe.throw("Order must have at least one item")
            
        # Ensure each item has sufficient stock
        for item in self.order_items:
            book = frappe.get_doc("Book", item.product_id)
            has_stock, available = book.check_stock(item.num)
            if not has_stock:
                frappe.throw(f"Not enough stock for book {book.book_name}. Available: {available}")
                
    def calculate_total(self):
        """Calculate total amount from order items"""
        self.total_money = sum((item.price * item.num) for item in self.order_items)
        
    def on_submit(self):
        """Handle order submission"""
        # Add a comment about order submission
        self.add_comment('Info', f'Order submitted - Total amount: {self.total_money}')
        self.update_book_stock()
        
    def update_book_stock(self):
        """Update book stock quantities"""
        for item in self.order_items:
            book = frappe.get_doc("Book", item.product_id)
            # Update book stock and let it handle the tracking
            book.update_stock(
                quantity_change=-item.num,
                reference_type="Order",
                reference_name=self.name
            )
            
    def on_cancel(self):
        """Handle order cancellation"""
        if self.status == "Đã giao hàng":
            frappe.throw("Cannot cancel a delivered order")
            
        self.status = "Đã hủy"
        self.add_comment('Info', 'Order cancelled')
        self.revert_book_stock()
        
    def revert_book_stock(self):
        """Revert book stock quantities on cancellation"""
        for item in self.order_items:
            book = frappe.get_doc("Book", item.product_id)
            # Revert book stock and let it handle the tracking
            book.update_stock(
                quantity_change=item.num,
                reference_type="Order Cancelled",
                reference_name=self.name
            )