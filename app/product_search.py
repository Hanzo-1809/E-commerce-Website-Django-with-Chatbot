"""
product_search.py - Provides product search and recommendation functionality

This module helps the chatbot provide relevant product information and recommendations
based on user queries and preferences.
"""

import re
from collections import Counter
from difflib import SequenceMatcher

def similarity_score(a, b):
    """Calculate text similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_keywords(text):
    """
    Extract potential product search keywords from user query
    """
    # Lower case and split by common separators
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stopwords (Vietnamese and English)
    stopwords = {"và", "hoặc", "là", "của", "có", "được", "không", "những", "một", "các", 
                "the", "a", "an", "and", "or", "but", "for", "with", "in", "on", "at"}
    
    keywords = [word for word in words if word not in stopwords and len(word) > 1]
    return keywords

def search_products(query, products):
    """
    Search for products based on user query
    """
    query_lower = query.lower()
    
    if ('mới' in query_lower or 'new' in query_lower or 'mới nhất' in query_lower):
        # Sắp xếp sản phẩm theo ID giảm dần (giả sử ID lớn hơn = thêm sau = mới hơn)
        # Hoặc nếu có trường date_added, dùng nó để sắp xếp
        sorted_products = sorted(products, key=lambda p: p.get('id', 0), reverse=True)
        # Trả về 5 sách mới nhất
        return sorted_products[:5]
    
    # Kiểm tra nếu người dùng đang tìm top sách bán chạy
    if ('top' in query_lower or 'bán chạy' in query_lower or 'phổ biến' in query_lower) and ('sách' in query_lower):
        try:
            from django.db.models import Sum
            from app.models import OrderItem
            
            # Lấy danh sách id của sản phẩm bán chạy nhất
            top_product_ids = OrderItem.objects.filter(
                order__complete=True
            ).values('product__id').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5].values_list('product__id', flat=True)
            
            # Lọc danh sách sản phẩm theo top bán chạy
            top_products = [p for p in products if p['id'] in top_product_ids]
            
            # Nếu tìm thấy ít nhất 1 sản phẩm, trả về danh sách
            if top_products:
                return top_products
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error finding top products: {e}")
    
    
    # Tiếp tục với code tìm kiếm hiện tại...
    # (giữ nguyên code tìm kiếm thông thường hiện tại)
    result = []
    for product in products:
        # Logic tìm kiếm hiện tại
        product_name = product.get('name', '').lower()
        product_desc = product.get('description', '').lower()
        product_author = product.get('author', '').lower()
        product_categories = product.get('categories', '').lower()
        
        # Tìm kiếm trong tên, mô tả, tác giả, danh mục
        if (query_lower in product_name or 
            query_lower in product_desc or 
            query_lower in product_author or 
            query_lower in product_categories):
            result.append(product)
    
    return result

def recommend_similar_products(product_id, products, limit=2):
    """
    Recommend similar products to a given product ID
    
    Args:
        product_id (int): ID of the reference product
        products (list): List of all product dictionaries 
        limit (int): Maximum recommendations to return
    
    Returns:
        list: Similar product recommendations
    """
    if not products:
        return []
        
    # Find the reference product
    ref_product = None
    for product in products:
        if product.get('id') == product_id:
            ref_product = product
            break
    
    if not ref_product:
        return []
    
    # Get reference product attributes
    ref_categories = ref_product.get('categories', '').lower().split(', ')
    ref_author = ref_product.get('author', '').lower()
    
    # Calculate similarity scores for each product
    similar_products = []
    
    for product in products:
        # Skip the reference product itself
        if product.get('id') == product_id:
            continue
            
        score = 0
        
        # Compare categories
        product_categories = product.get('categories', '').lower().split(', ')
        common_categories = set(ref_categories) & set(product_categories)
        score += len(common_categories) * 3
        
        # Compare author (significant match)
        if ref_author and product.get('author') and ref_author == product.get('author').lower():
            score += 4
            
        # Only include products with some similarity
        if score > 0:
            similar_products.append((score, product))
    
    # Sort by score (descending) and limit results
    similar_products.sort(reverse=True, key=lambda x: x[0])
    return [product for _, product in similar_products[:limit]]
