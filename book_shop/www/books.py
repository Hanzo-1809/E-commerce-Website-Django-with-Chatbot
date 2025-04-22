import frappe
from book_shop.book_shop.doctype.book.book import get_books as get_books_from_doctype

def get_context(context):
    """
    This function prepares the context for the books.html template
    """
    context.title = "Book Management"
    
    # Get initial data for the page
    # This data can be used for server-side rendering or initial loading
    context.books = get_books()
    context.categories = get_categories()
    
    return context

def get_books():
    """
    Get a list of books for initial page load
    """
    try:
        # Sử dụng import trực tiếp thay vì frappe.call
        books = get_books_from_doctype()
        return books or []
    except Exception as e:
        frappe.log_error(f"Error fetching books: {str(e)}")
        return []

def get_categories():
    """
    Get a list of book categories
    """
    try:
        categories = frappe.get_all('Category', 
            fields=['name', 'category_name'],
            order_by='category_name asc'
        )
        return categories or []
    except Exception as e:
        frappe.log_error(f"Error fetching categories: {str(e)}")
        return []

@frappe.whitelist()
def search_books(query=None, category=None, status=None, date_filter=None):
    """
    Search books with various filters
    """
    filters = {}
    
    if query:
        filters['book_name'] = ['like', f'%{query}%']
    
    if category:
        filters['category_id'] = category
    
    if status and status != 'all':
        filters['status'] = status
    
    if date_filter:
        filters['created_at'] = ['>=', date_filter]
    
    # Sử dụng hàm đã import thay vì frappe.call
    return get_books_from_doctype(filters=filters)