# utils/receipt_printer.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from database.database import DatabaseUtils, get_app_dir

from utils.i18n import translate as _

from datetime import datetime
import os

class ReceiptPrinter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for receipt"""
        # Shop name style
        self.styles.add(ParagraphStyle(
            name='ShopName',
            parent=self.styles['Title'],
            fontSize=18,
            alignment=1,  # Center
            spaceAfter=6,
            textColor=colors.black
        ))
        
        # Shop info style
        self.styles.add(ParagraphStyle(
            name='ShopInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=1,  # Center
            spaceAfter=12
        ))
        
        # Receipt header style
        self.styles.add(ParagraphStyle(
            name='ReceiptHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=1,  # Center
            spaceAfter=12
        ))
        
        # Item style
        self.styles.add(ParagraphStyle(
            name='Item',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=2
        ))
        
        # Total style
        self.styles.add(ParagraphStyle(
            name='Total',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=2,  # Right
            fontName='Helvetica-Bold'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=1,  # Center
            spaceBefore=12
        ))
    
    def generate_receipt(self, sale):
        """Generate PDF receipt for a sale"""
        try:
            # Create receipts directory inside the application folder
            receipts_dir = os.path.join(get_app_dir(), "receipts")
            if not os.path.exists(receipts_dir):
                os.makedirs(receipts_dir, exist_ok=True)
            
            # Generate filename
            filename = f"receipt_{sale.sale_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(receipts_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Shop header
            shop_name = DatabaseUtils.get_setting_value('shop_name', 'Quincaillerie Fexson')
            shop_address = DatabaseUtils.get_setting_value('shop_address', '123 Main Street')
            shop_phone = DatabaseUtils.get_setting_value('shop_phone', '+1234567890')
            
            story.append(Paragraph(shop_name, self.styles['ShopName']))
            story.append(Paragraph(f"{shop_address}<br/>{shop_phone}", self.styles['ShopInfo']))
            
            # Receipt header
            story.append(Paragraph(_("sales_receipt"), self.styles['ReceiptHeader']))
            
            # Sale information
            sale_info = [
                [_('receipt_number'), sale.sale_number],
                [_('date'), sale.created_at.strftime('%Y-%m-%d %H:%M:%S')],
                [_('cashier'), sale.user.username if sale.user else 'System'],
                [_('customer_label') + ':', sale.customer.name if sale.customer else 'Walk-in Customer']
            ]
            
            sale_info_table = Table(sale_info, colWidths=[1.5*inch, 3*inch])
            sale_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(sale_info_table)
            story.append(Spacer(1, 12))
            
            # Items table
            items_data = [[_('items'), _('qty'), _('unit_price'), _('total')]]
            
            currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
            
            for item in sale.sale_items:
                items_data.append([
                    item.product.name[:30] + "..." if len(item.product.name) > 30 else item.product.name,
                    f"{item.quantity:,.1f}",
                    f"{item.unit_price:,.0f}",
                    f"{item.total_price:,.0f}"
                ])
            
            items_table = Table(items_data, colWidths=[2.8*inch, 0.8*inch, 1*inch, 1*inch])
            items_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Item names left aligned
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Alternate row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 12))
            
            # Totals section
            totals_data = [
                [_('subtotal_label'), f"{sale.subtotal:,.0f} {currency}"],
                [_('tax_label'), f"{sale.tax_amount:,.0f} {currency}"],
                [_('total_label'), f"{sale.total_amount:,.0f} {currency}"]
            ]
            
            if sale.discount_amount > 0:
                totals_data.insert(-1, ['Discount:', f"-{sale.discount_amount:,.0f} {currency}"])
            
            totals_data.extend([
                [_('payment_method_label'), sale.payment_method.title()],
                [_('amount_paid_label'), f"{sale.amount_paid:,.0f} {currency}"],
                [_('change_label'), f"{sale.change_amount:,.0f} {currency}"]
            ])
            
            totals_table = Table(totals_data, colWidths=[2*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),  # Bold for total, payment, change
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, -4), (-1, -4), 1, colors.black),  # Line above total
            ]))
            
            story.append(totals_table)
            story.append(Spacer(1, 20))
            
            # Footer
            footer_text = DatabaseUtils.get_setting_value('receipt_footer', 'Thank you for your business!')
            story.append(Paragraph(footer_text, self.styles['Footer']))
            story.append(Paragraph("All sales are final. Please keep this receipt for your records.", self.styles['Footer']))
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Failed to generate receipt: {e}")
    
    def generate_simple_receipt(self, sale):
        """Generate a simple text receipt for thermal printers"""
        try:
            # Create receipts directory inside the application folder
            receipts_dir = os.path.join(get_app_dir(), "receipts")
            if not os.path.exists(receipts_dir):
                os.makedirs(receipts_dir, exist_ok=True)
            
            # Generate filename
            filename = f"receipt_{sale.sale_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(receipts_dir, filename)
            
            # Get settings
            shop_name = DatabaseUtils.get_setting_value('shop_name', 'Quincaillerie Fexson')
            shop_address = DatabaseUtils.get_setting_value('shop_address', '123 Main Street')
            shop_phone = DatabaseUtils.get_setting_value('shop_phone', '+1234567890')
            currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
            footer_text = DatabaseUtils.get_setting_value('receipt_footer', 'Thank you for your business!')
            
            # Build receipt text
            receipt_lines = []
            
            # Header
            receipt_lines.append("=" * 40)
            receipt_lines.append(shop_name.center(40))
            receipt_lines.append(shop_address.center(40))
            receipt_lines.append(shop_phone.center(40))
            receipt_lines.append("=" * 40)
            receipt_lines.append("")
            
            # Receipt info
            receipt_lines.append("SALES RECEIPT".center(40))
            receipt_lines.append("")
            receipt_lines.append(f"Receipt #: {sale.sale_number}")
            receipt_lines.append(f"Date: {sale.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            receipt_lines.append(f"Cashier: {sale.user.username if sale.user else 'System'}")
            customer_name = sale.customer.name if sale.customer else 'Walk-in Customer'
            receipt_lines.append(f"Customer: {customer_name}")
            receipt_lines.append("-" * 40)
            
            # Items
            receipt_lines.append("Item                    Qty  Price   Total")
            receipt_lines.append("-" * 40)
            
            for item in sale.sale_items:
                name = item.product.name[:20] if len(item.product.name) > 20 else item.product.name
                line = f"{name:<20} {item.quantity:>3.1f} {item.unit_price:>6.0f} {item.total_price:>8.0f}"
                receipt_lines.append(line)
            
            receipt_lines.append("-" * 40)
            
            # Totals
            receipt_lines.append(f"Subtotal: {sale.subtotal:>28,.0f} {currency}")
            if sale.discount_amount > 0:
                receipt_lines.append(f"Discount: {-sale.discount_amount:>28,.0f} {currency}")
            receipt_lines.append(f"Tax: {sale.tax_amount:>32,.0f} {currency}")
            receipt_lines.append("=" * 40)
            receipt_lines.append(f"TOTAL: {sale.total_amount:>30,.0f} {currency}")
            receipt_lines.append("=" * 40)
            receipt_lines.append("")
            
            # Payment info
            receipt_lines.append(f"Payment Method: {sale.payment_method.title()}")
            receipt_lines.append(f"Amount Paid: {sale.amount_paid:>24,.0f} {currency}")
            receipt_lines.append(f"Change: {sale.change_amount:>29,.0f} {currency}")
            receipt_lines.append("")
            
            # Footer
            receipt_lines.append(footer_text.center(40))
            receipt_lines.append("All sales are final.".center(40))
            receipt_lines.append("Keep this receipt for your records.".center(40))
            receipt_lines.append("=" * 40)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(receipt_lines))
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Failed to generate simple receipt: {e}")
    
    def print_receipt_to_printer(self, receipt_path, printer_name=None):
        """Print receipt to specified printer (Windows only)"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                if printer_name:
                    # Print to specific printer
                    subprocess.run([
                        "python", "-c", 
                        f"import os; os.startfile('{receipt_path}', 'print')"
                    ], check=True)
                else:
                    # Print to default printer
                    os.startfile(receipt_path, "print")
            else:
                # For Linux/Mac, use lpr command
                subprocess.run(["lpr", receipt_path], check=True)
                
        except Exception as e:
            raise Exception(f"Failed to print receipt: {e}")
    
    def email_receipt(self, receipt_path, customer_email, sale_number):
        """Email receipt to customer (requires email configuration)"""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Email configuration (should be in settings)
            smtp_server = DatabaseUtils.get_setting_value('smtp_server', 'smtp.gmail.com')
            smtp_port = int(DatabaseUtils.get_setting_value('smtp_port', '587'))
            email_user = DatabaseUtils.get_setting_value('email_user', '')
            email_password = DatabaseUtils.get_setting_value('email_password', '')
            
            if not email_user or not email_password:
                raise Exception("Email configuration not set up")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = customer_email
            msg['Subject'] = f"Receipt #{sale_number} - {DatabaseUtils.get_setting_value('shop_name', 'Shop')}"
            
            # Email body
            body = f"""
            Dear Customer,
            
            Thank you for your purchase! Please find your receipt attached.
            
            Receipt Number: {sale_number}
            Date: {datetime.now().strftime('%Y-%m-%d')}
            
            Best regards,
            {DatabaseUtils.get_setting_value('shop_name', 'Quincaillerie Fexson')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach receipt
            with open(receipt_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= receipt_{sale_number}.pdf'
            )
            
            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, customer_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to email receipt: {e}")
    
    def generate_daily_sales_report(self, date):
        """Generate daily sales report"""
        try:
            from database.models import Sale
            from database.database import db_manager
            
            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Generate filename
            filename = f"daily_sales_report_{date.strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(reports_dir, filename)
            
            # Get sales data
            session = db_manager.get_session()
            try:
                sales = session.query(Sale).filter(
                    Sale.created_at >= date,
                    Sale.created_at < date.replace(hour=23, minute=59, second=59)
                ).order_by(Sale.created_at).all()
            finally:
                session.close()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            # Report header
            shop_name = DatabaseUtils.get_setting_value('shop_name', 'Quincaillerie Fexson')
            story.append(Paragraph(shop_name, self.styles['ShopName']))
            story.append(Paragraph(f"Daily Sales Report - {date.strftime('%Y-%m-%d')}", self.styles['ReceiptHeader']))
            story.append(Spacer(1, 12))
            
            if not sales:
                story.append(Paragraph("No sales recorded for this date.", self.styles['Normal']))
            else:
                # Sales summary
                total_sales = len(sales)
                total_amount = sum(sale.total_amount for sale in sales)
                total_items = sum(len(sale.sale_items) for sale in sales)
                
                currency = DatabaseUtils.get_setting_value('currency', 'FCFA')
                
                summary_data = [
                    ['Total Sales:', str(total_sales)],
                    ['Total Items Sold:', str(total_items)],
                    ['Total Amount:', f"{total_amount:,.0f} {currency}"]
                ]
                
                summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                story.append(summary_table)
                story.append(Spacer(1, 20))
                
                # Sales details
                story.append(Paragraph("Sales Details", self.styles['Heading2']))
                
                sales_data = [['Receipt #', 'Time', 'Customer', 'Items', 'Total']]
                
                for sale in sales:
                    customer_name = sale.customer.name if sale.customer else 'Walk-in'
                    if len(customer_name) > 15:
                        customer_name = customer_name[:12] + "..."
                    
                    sales_data.append([
                        sale.sale_number,
                        sale.created_at.strftime('%H:%M'),
                        customer_name,
                        str(len(sale.sale_items)),
                        f"{sale.total_amount:,.0f}"
                    ])
                
                sales_table = Table(sales_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 0.8*inch, 1.2*inch])
                sales_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Customer names left aligned
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                story.append(sales_table)
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Failed to generate daily sales report: {e}")
