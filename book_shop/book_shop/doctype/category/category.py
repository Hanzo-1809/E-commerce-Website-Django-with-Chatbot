import frappe
from frappe.model.document import Document

class Category(Document):
    def validate(self):
        # Prevent circular parent references
        if self.parent_category == self.name:
            frappe.throw("A category cannot be its own parent")
            
        # Check for deeper circular references
        self.check_for_circular_parent_reference()
    
    def check_for_circular_parent_reference(self):
        """Check if there's a circular reference in the parent category chain"""
        if not self.parent_category:
            return
            
        parent_chain = [self.name]
        current_parent = self.parent_category
        
        while current_parent:
            if current_parent in parent_chain:
                frappe.throw("Circular reference detected in parent categories")
                
            parent_chain.append(current_parent)
            
            # Get the parent of this parent
            parent_doc = frappe.get_value("Category", current_parent, "parent_category")
            current_parent = parent_doc

@frappe.whitelist()
def get_all_categories(include_inactive=False):
    """Get all categories with optional filtering for active status"""
    filters = {}
    
    if not include_inactive:
        filters["is_active"] = 1
        
    return frappe.get_all('Category', 
        filters=filters,
        fields=['name', 'category_name', 'parent_category', 'is_active'],
        order_by='category_name asc'
    )

@frappe.whitelist()
def get_category_tree():
    """Get categories in a hierarchical tree structure"""
    categories = get_all_categories()
    
    # Organize into a tree
    category_map = {}
    root_categories = []
    
    # First pass: create map of all categories
    for category in categories:
        category['children'] = []
        category_map[category['name']] = category
    
    # Second pass: build the tree structure
    for category in categories:
        if category['parent_category']:
            if category['parent_category'] in category_map:
                category_map[category['parent_category']]['children'].append(category)
        else:
            root_categories.append(category)
    
    return root_categories