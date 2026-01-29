from faker import Faker
from sqlalchemy.orm import Session
from .models import Customer, Product, Order
import random
from datetime import datetime, timedelta

fake = Faker(['fr_FR'])

def seed_db(db: Session):
    if db.query(Customer).count() > 0:
        return

    # Generate Customers
    customers = []
    for _ in range(60):
        customer = Customer(
            name=fake.name(),
            email=fake.email(),
            city=fake.city(),
            created_at=fake.date_between(start_date='-3y', end_date='today')
        )
        db.add(customer)
        customers.append(customer)
    
    # Generate Products
    products = []
    categories = ['Électronique', 'Vêtements', 'Maison', 'Sport', 'Livres']
    for _ in range(30):
        product = Product(
            name=fake.word().capitalize(),
            category=random.choice(categories),
            price=round(random.uniform(10, 1000), 2)
        )
        db.add(product)
        products.append(product)
    
    db.commit()


    for _ in range(250):
        customer = random.choice(customers)
        product = random.choice(products)
        quantity = random.randint(1, 5)
        order_date = fake.date_between(start_date='-1y', end_date='today')
        total_amount = round(float(product.price) * quantity, 2)
        
        order = Order(
            customer_id=customer.id,
            product_id=product.id,
            quantity=quantity,
            order_date=order_date,
            total_amount=total_amount
        )
        db.add(order)
    
    db.commit()
