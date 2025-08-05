# Construction Materials POS System

A complete offline Point of Sale system designed specifically for construction material shops (quincailleries). Built with Python and Tkinter for reliability and ease of use.

## Features

### 🛒 Point of Sale
- Fast product search and barcode scanning
- Shopping cart with quantity management
- Multiple payment methods (cash, card, credit)
- Receipt generation (PDF and text formats)
- Customer selection and management
- Real-time tax calculation

### 📦 Inventory Management
- Product catalog with categories
- Stock level tracking with alerts
- Stock movements history
- Low stock notifications
- Bulk stock adjustments
- Product activation/deactivation

### 📊 Reports & Analytics
- Daily sales reports
- Inventory reports
- Low stock alerts
- Sales history by customer
- Product performance analysis

### 🔧 Additional Features
- Offline operation (no internet required)
- Automatic database backups
- Multi-unit support (pieces, bags, meters, kg, etc.)
- Customizable receipt templates
- User-friendly interface in French/English

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Step 1: Download and Setup

1. **Create project directory:**
```bash
mkdir construction_pos
cd construction_pos
```

2. **Create the directory structure:**
```
construction_pos/
├── main.py
├── database/
│   ├── __init__.py
│   ├── models.py
│   ├── database.py
│   └── seed_data.py
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── pos_window.py
│   ├── inventory_window.py
│   └── reports_window.py
├── utils/
│   ├── __init__.py
│   ├── receipt_printer.py
│   └── backup.py
├── receipts/          # Created automatically
├── reports/           # Created automatically
├── backups/           # Created automatically
└── requirements.txt
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database

Run the application for the first time to create the database:
```bash
python main.py
```

The system will automatically:
- Create the SQLite database
- Create all necessary tables
- Add sample categories and products
- Set up default settings

### Step 3: Customize Settings

After first run, you can customize:
- Shop name and address
- Tax rates
- Currency
- Receipt templates
- Default categories and products

## Usage Guide

### Starting the Application
```bash
python main.py
```

### Main Interface Navigation

**Dashboard Sections:**
- **Point of Sale**: Process customer transactions
- **Inventory**: Manage products and stock
- **Reports**: View sales and inventory reports
- **Customers**: Manage customer database
- **Settings**: Configure system preferences

### Processing Sales

1. **Select Products:**
   - Search by name or scan barcode
   - Double-click to add to cart
   - Adjust quantities as needed

2. **Choose Customer:**
   - Select from existing customers
   - Use "Walk-in Customer" for cash sales

3. **Complete Transaction:**
   - Choose payment method
   - Enter amount paid (for cash)
   - Process sale and print receipt

### Managing Inventory

1. **Add Products:**
   - Click "Add Product" in Inventory tab
   - Fill in product details
   - Set pricing and stock levels

2. **Adjust Stock:**
   - Select product and click "Adjust Stock"
   - Enter new quantity and reason
   - System tracks all movements

3. **Monitor Alerts:**
   - Check "Low Stock Alerts" tab
   - Review products below minimum levels
   - Plan restocking accordingly

### Generating Reports

1. **Daily Sales:**
   - View today's sales summary
   - Export to PDF for records

2. **Inventory Reports:**
   - Current stock levels
   - Product valuations
   - Movement history

## Configuration

### Database Settings
The system uses SQLite for local storage. Database file: `construction_pos.db`

### Backup Strategy
- Automatic daily backups
- Manual backup via File → Backup Database
- Store backups on external drive for safety

### Receipt Customization
Edit receipt templates in `utils/receipt_printer.py`:
- Shop information
- Logo placement
- Footer text
- Format layout

### Adding Categories
Default categories include:
- Cement & Concrete
- Steel & Iron
- Bricks & Blocks
- Roofing Materials
- Plumbing
- Electrical
- Tools & Hardware
- Paint & Finishes

Add more via Inventory → Categories tab.

## Sample Products

The system comes with sample products:
- Portland Cement 50kg
- Steel Rebar 12mm
- Red Building Brick
- Aluminum Roofing Sheet
- PVC Pipe 4inch
- Hammer 500g
- And more...

## Troubleshooting

### Common Issues

**Database Error on Startup:**
- Check file permissions in installation directory
- Ensure Python has write access
- Try running as administrator (Windows)

**Receipt Generation Failed:**
- Install ReportLab: `pip install reportlab`
- Check receipts directory permissions
- Verify disk space availability

**Products Not Loading:**
- Check database connection
- Refresh product list
- Restart application

### Getting Help

1. **Check Error Messages**: Most errors include helpful information
2. **Restart Application**: Solves many temporary issues
3. **Check Log Files**: Look in application directory for error logs
4. **Database Backup**: Always keep recent backups

## Advanced Features

### Barcode Integration
- Connect USB/Serial barcode scanner
- Configure as keyboard input device
- Test with sample products

### Thermal Printer Setup
- Use simple text receipts for thermal printers
- Configure printer in system settings
- Test print functionality

### Multi-Location Support
- Each location needs separate installation
- Use data export/import for product sync
- Centralize reporting if needed

## Data Management

### Export Data
```python
# Example: Export products to CSV
import csv
from database.database import db_manager
from database.models import Product

session = db_manager.get_session()
products = session.query(Product).all()

with open('products_export.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['ID', 'Name', 'Price', 'Stock'])
    for product in products:
        writer.writerow([product.id, product.name, 
                        product.selling_price, product.stock_quantity])
```

### Import Data
- Use the product dialog for manual entry
- Create bulk import scripts for large datasets
- Maintain data consistency

## Security Considerations

- **Local Database**: No network security concerns
- **Physical Access**: Secure the computer running POS
- **Backup Security**: Encrypt backup files if needed
- **User Access**: Add login system if multiple users

## Performance Tips

- **Regular Cleanup**: Archive old sales data periodically
- **Database Maintenance**: Run integrity checks monthly
- **Disk Space**: Monitor available space for receipts/reports
- **System Updates**: Keep Python and dependencies updated

## Future Enhancements

Potential additions:
- Multi-user support with login system
- Cloud synchronization for backups
- Mobile app for inventory checking
- Advanced reporting with charts
- Integration with accounting software
- Multi-language support
- Supplier management
- Purchase order system

## Support

For technical support or feature requests:
1. Check this documentation first
2. Review error messages and logs
3. Test with sample data
4. Contact system administrator

## License

This POS system is designed for construction material shops. Customize and extend as needed for your specific business requirements.

---

**Version 1.0** - Built with Python, SQLAlchemy, Tkinter, and ReportLab
