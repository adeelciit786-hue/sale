#!/usr/bin/env python3
"""
Command-line interface for the Sale Management System
"""

import sys
from sale import SaleManager


def print_menu():
    """Print the main menu."""
    print("\n=== Sale Management System ===")
    print("1. Add Product")
    print("2. Update Product")
    print("3. Delete Product")
    print("4. List Products")
    print("5. Create Sale")
    print("6. List Sales")
    print("7. View Total Revenue")
    print("8. Exit")
    print("=" * 30)


def add_product_cli(manager):
    """Add a product through CLI."""
    print("\n--- Add Product ---")
    product_id = input("Enter Product ID: ").strip()
    name = input("Enter Product Name: ").strip()
    try:
        price = float(input("Enter Price: ").strip())
        stock = int(input("Enter Stock Quantity: ").strip())
    except ValueError:
        print("Invalid input! Price must be a number and stock must be an integer.")
        return
    
    manager.add_product(product_id, name, price, stock)


def update_product_cli(manager):
    """Update a product through CLI."""
    print("\n--- Update Product ---")
    product_id = input("Enter Product ID to update: ").strip()
    
    product = manager.get_product(product_id)
    if not product:
        print(f"Product {product_id} not found!")
        return
    
    print(f"Current: {product}")
    print("Leave blank to keep current value")
    
    name = input(f"Enter new name [{product.name}]: ").strip()
    price_str = input(f"Enter new price [{product.price}]: ").strip()
    stock_str = input(f"Enter new stock [{product.stock}]: ").strip()
    
    name = name if name else None
    price = float(price_str) if price_str else None
    stock = int(stock_str) if stock_str else None
    
    manager.update_product(product_id, name, price, stock)


def delete_product_cli(manager):
    """Delete a product through CLI."""
    print("\n--- Delete Product ---")
    product_id = input("Enter Product ID to delete: ").strip()
    confirm = input(f"Are you sure you want to delete {product_id}? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        manager.delete_product(product_id)
    else:
        print("Deletion cancelled.")


def list_products_cli(manager):
    """List all products through CLI."""
    print("\n--- Product List ---")
    products = manager.list_products()
    if not products:
        print("No products found.")
    else:
        for product in products:
            print(product)


def create_sale_cli(manager):
    """Create a sale through CLI."""
    print("\n--- Create Sale ---")
    sale_id = input("Enter Sale ID: ").strip()
    product_id = input("Enter Product ID: ").strip()
    
    try:
        quantity = int(input("Enter Quantity: ").strip())
    except ValueError:
        print("Invalid input! Quantity must be an integer.")
        return
    
    manager.create_sale(sale_id, product_id, quantity)


def list_sales_cli(manager):
    """List all sales through CLI."""
    print("\n--- Sales List ---")
    sales = manager.list_sales()
    if not sales:
        print("No sales found.")
    else:
        for sale in sales:
            print(sale)


def view_revenue_cli(manager):
    """View total revenue through CLI."""
    print("\n--- Total Revenue ---")
    revenue = manager.get_total_revenue()
    print(f"Total Revenue: ${revenue:.2f}")


def main():
    """Main CLI loop."""
    manager = SaleManager()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            add_product_cli(manager)
        elif choice == '2':
            update_product_cli(manager)
        elif choice == '3':
            delete_product_cli(manager)
        elif choice == '4':
            list_products_cli(manager)
        elif choice == '5':
            create_sale_cli(manager)
        elif choice == '6':
            list_sales_cli(manager)
        elif choice == '7':
            view_revenue_cli(manager)
        elif choice == '8':
            print("\nThank you for using Sale Management System!")
            sys.exit(0)
        else:
            print("Invalid choice! Please enter a number between 1 and 8.")


if __name__ == "__main__":
    main()
