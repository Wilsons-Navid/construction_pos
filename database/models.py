# database/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    barcode = Column(String(50), unique=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    unit = Column(String(20), default="piece")  # piece, bag, meter, kg, ton
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    category = relationship("Category", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    credit_limit = Column(Float, default=0.0)
    current_credit = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    sales = relationship("Sale", back_populates="customer")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="cashier")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    sales = relationship("Sale", back_populates="user")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    sale_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(20), default="cash")  # cash, card, credit
    payment_status = Column(String(20), default="paid")  # paid, pending, partial
    amount_paid = Column(Float, default=0.0)
    change_amount = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    sale_items = relationship("SaleItem", back_populates="sale")
    user = relationship("User", back_populates="sales")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)

    # Relationships
    sale = relationship("Sale", back_populates="sale_items")
    product = relationship("Product", back_populates="sale_items")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    movement_type = Column(String(20), nullable=False)  # in, out, adjustment
    quantity = Column(Float, nullable=False)
    reference_type = Column(String(20))  # sale, purchase, adjustment
    reference_id = Column(Integer)  # ID of related record
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(100))

    # Relationships
    product = relationship("Product", back_populates="stock_movements")


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

