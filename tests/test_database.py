import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Customer, Order
import datetime

class TestDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()

    def test_create_customer_and_order_relationship(self):
        # Arrange
        new_customer = Customer(
            name="Jean Dupont",
            email="jean@example.com",
            city="Paris",
            created_at=datetime.date.today()
        )
        self.db.add(new_customer)
        self.db.commit()
        self.db.refresh(new_customer)

        new_order = Order(
            customer_id=new_customer.id,
            product_id=1,
            quantity=2,
            order_date=datetime.date.today(),
            total_amount=100.0
        )
        self.db.add(new_order)
        self.db.commit()

        # Act
        customer_from_db = self.db.query(Customer).filter_by(name="Jean Dupont").first()

        # Assert
        self.assertIsNotNone(customer_from_db)
        self.assertEqual(len(customer_from_db.orders), 1)
        self.assertEqual(customer_from_db.orders[0].total_amount, 100.0)

if __name__ == "__main__":
    unittest.main()
