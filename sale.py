#!/usr/bin/env python3
"""
Sale Management System
A simple command-line application for managing sales and products.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Product:
    """Represents a product in the inventory."""
    
    def __init__(self, product_id: str, name: str, price: float, stock: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
    
    def to_dict(self) -> Dict:
        """Convert product to dictionary."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Product':
        """Create product from dictionary."""
        return Product(
            data['product_id'],
            data['name'],
            data['price'],
            data['stock']
        )
    
    def __str__(self) -> str:
        return f"Product({self.product_id}): {self.name} - ${self.price:.2f} (Stock: {self.stock})"


class Sale:
    """Represents a sales transaction."""
    
    def __init__(self, sale_id: str, product_id: str, quantity: int, 
                 total_price: float, timestamp: Optional[str] = None):
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert sale to dictionary."""
        return {
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'timestamp': self.timestamp
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Sale':
        """Create sale from dictionary."""
        return Sale(
            data['sale_id'],
            data['product_id'],
            data['quantity'],
            data['total_price'],
            data['timestamp']
        )
    
    def __str__(self) -> str:
        return f"Sale({self.sale_id}): Product {self.product_id} x {self.quantity} = ${self.total_price:.2f} at {self.timestamp}"


class SaleManager:
    """Manages products and sales transactions."""
    
    def __init__(self, data_file: str = 'sales_data.json'):
        self.data_file = data_file
        self.products: Dict[str, Product] = {}
        self.sales: Dict[str, Sale] = {}
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.products = {
                        pid: Product.from_dict(p) 
                        for pid, p in data.get('products', {}).items()
                    }
                    self.sales = {
                        sid: Sale.from_dict(s) 
                        for sid, s in data.get('sales', {}).items()
                    }
            except Exception as e:
                print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save data to JSON file."""
        try:
            data = {
                'products': {pid: p.to_dict() for pid, p in self.products.items()},
                'sales': {sid: s.to_dict() for sid, s in self.sales.items()}
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_product(self, product_id: str, name: str, price: float, stock: int) -> bool:
        """Add a new product to inventory."""
        if product_id in self.products:
            print(f"Product {product_id} already exists!")
            return False
        
        self.products[product_id] = Product(product_id, name, price, stock)
        self.save_data()
        print(f"Product {product_id} added successfully!")
        return True
    
    def update_product(self, product_id: str, name: Optional[str] = None, 
                      price: Optional[float] = None, stock: Optional[int] = None) -> bool:
        """Update an existing product."""
        if product_id not in self.products:
            print(f"Product {product_id} not found!")
            return False
        
        product = self.products[product_id]
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        
        self.save_data()
        print(f"Product {product_id} updated successfully!")
        return True
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product from inventory."""
        if product_id not in self.products:
            print(f"Product {product_id} not found!")
            return False
        
        del self.products[product_id]
        self.save_data()
        print(f"Product {product_id} deleted successfully!")
        return True
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by ID."""
        return self.products.get(product_id)
    
    def list_products(self) -> List[Product]:
        """List all products."""
        return list(self.products.values())
    
    def create_sale(self, sale_id: str, product_id: str, quantity: int) -> bool:
        """Create a new sale transaction."""
        if product_id not in self.products:
            print(f"Product {product_id} not found!")
            return False
        
        product = self.products[product_id]
        
        if product.stock < quantity:
            print(f"Insufficient stock! Available: {product.stock}, Requested: {quantity}")
            return False
        
        if sale_id in self.sales:
            print(f"Sale {sale_id} already exists!")
            return False
        
        total_price = product.price * quantity
        sale = Sale(sale_id, product_id, quantity, total_price)
        
        # Update stock
        product.stock -= quantity
        
        self.sales[sale_id] = sale
        self.save_data()
        print(f"Sale {sale_id} created successfully! Total: ${total_price:.2f}")
        return True
    
    def get_sale(self, sale_id: str) -> Optional[Sale]:
        """Get a sale by ID."""
        return self.sales.get(sale_id)
    
    def list_sales(self) -> List[Sale]:
        """List all sales."""
        return list(self.sales.values())
    
    def get_total_revenue(self) -> float:
        """Calculate total revenue from all sales."""
        return sum(sale.total_price for sale in self.sales.values())


def main():
    """Main function to demonstrate the sale system."""
    manager = SaleManager()
    
    print("=== Sale Management System ===\n")
    
    # Add some sample products
    print("Adding sample products...")
    manager.add_product("P001", "Laptop", 999.99, 10)
    manager.add_product("P002", "Mouse", 29.99, 50)
    manager.add_product("P003", "Keyboard", 79.99, 30)
    
    print("\n=== Product List ===")
    for product in manager.list_products():
        print(product)
    
    # Create some sales
    print("\n=== Creating Sales ===")
    manager.create_sale("S001", "P001", 2)
    manager.create_sale("S002", "P002", 5)
    manager.create_sale("S003", "P003", 3)
    
    print("\n=== Sales List ===")
    for sale in manager.list_sales():
        print(sale)
    
    print(f"\n=== Total Revenue ===")
    print(f"Total Revenue: ${manager.get_total_revenue():.2f}")
    
    print("\n=== Updated Product List (after sales) ===")
    for product in manager.list_products():
        print(product)


if __name__ == "__main__":
    main()
