import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.utils import seed_db
from backend.models import Customer, Product, Order

class TestUtils(unittest.TestCase):
    def setUp(self):
        # Utilisation d'une base de données SQLite en mémoire pour les tests
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_seed_db_populates_tables(self):
        # Act
        seed_db(self.db)
        
        # Assert
        customer_count = self.db.query(Customer).count()
        product_count = self.db.query(Product).count()
        order_count = self.db.query(Order).count()
        
        self.assertEqual(customer_count, 60)
        self.assertEqual(product_count, 30)
        self.assertEqual(order_count, 250)

    def test_seed_db_does_not_duplicate_if_already_seeded(self):
        # Arrange
        seed_db(self.db)
        initial_count = self.db.query(Customer).count()
        
        # Act
        seed_db(self.db)
        
        # Assert
        self.assertEqual(self.db.query(Customer).count(), initial_count)

if __name__ == "__main__":
    unittest.main()
