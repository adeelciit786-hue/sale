# Sale Management System

A simple and efficient command-line application for managing products and sales transactions.

## Features

- **Product Management**: Add, update, delete, and list products
- **Sales Transactions**: Create and track sales with automatic inventory updates
- **Revenue Tracking**: Calculate total revenue from all sales
- **Data Persistence**: All data is saved to JSON format for easy storage
- **Comprehensive Testing**: Full unit test coverage

## Installation

No external dependencies required! This application uses only Python standard library.

Requirements:
- Python 3.6 or higher

## Usage

### Running the Demo

To see the system in action with sample data:

```bash
python3 sale.py
```

This will create sample products and sales, demonstrating all core functionality.

### Interactive CLI

For interactive use:

```bash
python3 cli.py
```

The CLI provides a menu-driven interface with the following options:
1. Add Product - Create new products in inventory
2. Update Product - Modify existing product details
3. Delete Product - Remove products from inventory
4. List Products - View all products
5. Create Sale - Process a sale transaction
6. List Sales - View all sales history
7. View Total Revenue - See cumulative revenue
8. Exit - Close the application

### Programmatic Usage

You can also use the SaleManager class in your own Python code:

```python
from sale import SaleManager

# Initialize the manager
manager = SaleManager()

# Add products
manager.add_product("P001", "Laptop", 999.99, 10)
manager.add_product("P002", "Mouse", 29.99, 50)

# Create sales
manager.create_sale("S001", "P001", 2)  # Sell 2 laptops

# View products and sales
products = manager.list_products()
sales = manager.list_sales()

# Calculate revenue
revenue = manager.get_total_revenue()
print(f"Total Revenue: ${revenue:.2f}")
```

## Running Tests

To run the unit tests:

```bash
python3 test_sale.py
```

Or with verbose output:

```bash
python3 test_sale.py -v
```

## Data Storage

All data is stored in `sales_data.json` by default. The file is automatically created and updated as you manage products and sales.

## Architecture

The application consists of three main components:

1. **Product Class**: Represents individual products with ID, name, price, and stock
2. **Sale Class**: Represents sales transactions with automatic timestamp
3. **SaleManager Class**: Manages all operations with data persistence

## Example

```bash
$ python3 sale.py

=== Sale Management System ===

Adding sample products...
Product P001 added successfully!
Product P002 added successfully!
Product P003 added successfully!

=== Product List ===
Product(P001): Laptop - $999.99 (Stock: 10)
Product(P002): Mouse - $29.99 (Stock: 50)
Product(P003): Keyboard - $79.99 (Stock: 30)

=== Creating Sales ===
Sale S001 created successfully! Total: $1999.98
Sale S002 created successfully! Total: $149.95
Sale S003 created successfully! Total: $239.97

=== Sales List ===
Sale(S001): Product P001 x 2 = $1999.98 at 2026-01-19T12:00:00
Sale(S002): Product P002 x 5 = $149.95 at 2026-01-19T12:00:05
Sale(S003): Product P003 x 3 = $239.97 at 2026-01-19T12:00:10

=== Total Revenue ===
Total Revenue: $2389.90

=== Updated Product List (after sales) ===
Product(P001): Laptop - $999.99 (Stock: 8)
Product(P002): Mouse - $29.99 (Stock: 45)
Product(P003): Keyboard - $79.99 (Stock: 27)
```

## License

This project is open source and available for educational purposes.
