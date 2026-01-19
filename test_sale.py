#!/usr/bin/env python3
"""
Unit tests for the Sale Management System
"""

import unittest
import os
import json
from sale import Product, Sale, SaleManager


class TestProduct(unittest.TestCase):
    """Test cases for Product class."""
    
    def test_product_creation(self):
        """Test product creation."""
        product = Product("P001", "Laptop", 999.99, 10)
        self.assertEqual(product.product_id, "P001")
        self.assertEqual(product.name, "Laptop")
        self.assertEqual(product.price, 999.99)
        self.assertEqual(product.stock, 10)
    
    def test_product_to_dict(self):
        """Test product to dictionary conversion."""
        product = Product("P001", "Laptop", 999.99, 10)
        product_dict = product.to_dict()
        self.assertEqual(product_dict['product_id'], "P001")
        self.assertEqual(product_dict['name'], "Laptop")
        self.assertEqual(product_dict['price'], 999.99)
        self.assertEqual(product_dict['stock'], 10)
    
    def test_product_from_dict(self):
        """Test product creation from dictionary."""
        data = {
            'product_id': 'P001',
            'name': 'Laptop',
            'price': 999.99,
            'stock': 10
        }
        product = Product.from_dict(data)
        self.assertEqual(product.product_id, "P001")
        self.assertEqual(product.name, "Laptop")
        self.assertEqual(product.price, 999.99)
        self.assertEqual(product.stock, 10)


class TestSale(unittest.TestCase):
    """Test cases for Sale class."""
    
    def test_sale_creation(self):
        """Test sale creation."""
        sale = Sale("S001", "P001", 2, 1999.98, "2026-01-19T12:00:00")
        self.assertEqual(sale.sale_id, "S001")
        self.assertEqual(sale.product_id, "P001")
        self.assertEqual(sale.quantity, 2)
        self.assertEqual(sale.total_price, 1999.98)
        self.assertEqual(sale.timestamp, "2026-01-19T12:00:00")
    
    def test_sale_to_dict(self):
        """Test sale to dictionary conversion."""
        sale = Sale("S001", "P001", 2, 1999.98, "2026-01-19T12:00:00")
        sale_dict = sale.to_dict()
        self.assertEqual(sale_dict['sale_id'], "S001")
        self.assertEqual(sale_dict['product_id'], "P001")
        self.assertEqual(sale_dict['quantity'], 2)
        self.assertEqual(sale_dict['total_price'], 1999.98)
    
    def test_sale_from_dict(self):
        """Test sale creation from dictionary."""
        data = {
            'sale_id': 'S001',
            'product_id': 'P001',
            'quantity': 2,
            'total_price': 1999.98,
            'timestamp': '2026-01-19T12:00:00'
        }
        sale = Sale.from_dict(data)
        self.assertEqual(sale.sale_id, "S001")
        self.assertEqual(sale.product_id, "P001")
        self.assertEqual(sale.quantity, 2)
        self.assertEqual(sale.total_price, 1999.98)


class TestSaleManager(unittest.TestCase):
    """Test cases for SaleManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_file = 'test_sales_data.json'
        self.manager = SaleManager(self.test_data_file)
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
    
    def test_add_product(self):
        """Test adding a product."""
        result = self.manager.add_product("P001", "Laptop", 999.99, 10)
        self.assertTrue(result)
        self.assertIn("P001", self.manager.products)
        product = self.manager.get_product("P001")
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Laptop")
    
    def test_add_duplicate_product(self):
        """Test adding a duplicate product."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        result = self.manager.add_product("P001", "Mouse", 29.99, 50)
        self.assertFalse(result)
    
    def test_update_product(self):
        """Test updating a product."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        result = self.manager.update_product("P001", name="Gaming Laptop", price=1299.99)
        self.assertTrue(result)
        product = self.manager.get_product("P001")
        self.assertEqual(product.name, "Gaming Laptop")
        self.assertEqual(product.price, 1299.99)
    
    def test_update_nonexistent_product(self):
        """Test updating a non-existent product."""
        result = self.manager.update_product("P999", name="Test")
        self.assertFalse(result)
    
    def test_delete_product(self):
        """Test deleting a product."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        result = self.manager.delete_product("P001")
        self.assertTrue(result)
        self.assertNotIn("P001", self.manager.products)
    
    def test_delete_nonexistent_product(self):
        """Test deleting a non-existent product."""
        result = self.manager.delete_product("P999")
        self.assertFalse(result)
    
    def test_list_products(self):
        """Test listing products."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        self.manager.add_product("P002", "Mouse", 29.99, 50)
        products = self.manager.list_products()
        self.assertEqual(len(products), 2)
    
    def test_create_sale(self):
        """Test creating a sale."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        result = self.manager.create_sale("S001", "P001", 2)
        self.assertTrue(result)
        self.assertIn("S001", self.manager.sales)
        sale = self.manager.get_sale("S001")
        self.assertEqual(sale.quantity, 2)
        self.assertEqual(sale.total_price, 1999.98)
        # Check stock was updated
        product = self.manager.get_product("P001")
        self.assertEqual(product.stock, 8)
    
    def test_create_sale_insufficient_stock(self):
        """Test creating a sale with insufficient stock."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        result = self.manager.create_sale("S001", "P001", 20)
        self.assertFalse(result)
    
    def test_create_sale_nonexistent_product(self):
        """Test creating a sale for non-existent product."""
        result = self.manager.create_sale("S001", "P999", 2)
        self.assertFalse(result)
    
    def test_create_duplicate_sale(self):
        """Test creating a duplicate sale."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        self.manager.create_sale("S001", "P001", 2)
        result = self.manager.create_sale("S001", "P001", 1)
        self.assertFalse(result)
    
    def test_list_sales(self):
        """Test listing sales."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        self.manager.add_product("P002", "Mouse", 29.99, 50)
        self.manager.create_sale("S001", "P001", 2)
        self.manager.create_sale("S002", "P002", 5)
        sales = self.manager.list_sales()
        self.assertEqual(len(sales), 2)
    
    def test_get_total_revenue(self):
        """Test calculating total revenue."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        self.manager.add_product("P002", "Mouse", 29.99, 50)
        self.manager.create_sale("S001", "P001", 2)  # 1999.98
        self.manager.create_sale("S002", "P002", 5)  # 149.95
        total_revenue = self.manager.get_total_revenue()
        self.assertAlmostEqual(total_revenue, 2149.93, places=2)
    
    def test_data_persistence(self):
        """Test data persistence through save and load."""
        self.manager.add_product("P001", "Laptop", 999.99, 10)
        self.manager.create_sale("S001", "P001", 2)
        
        # Create new manager instance with same data file
        new_manager = SaleManager(self.test_data_file)
        
        # Check data was loaded
        self.assertIn("P001", new_manager.products)
        self.assertIn("S001", new_manager.sales)
        product = new_manager.get_product("P001")
        self.assertEqual(product.stock, 8)  # After sale


if __name__ == '__main__':
    unittest.main()
