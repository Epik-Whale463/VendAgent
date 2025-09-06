from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

DATABASE_URL = "sqlite:///./vending_machine.db"

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
# CRUD operations

def get_session():
    return SessionLocal()

def add_item(db_session, name: str, price: float, quantity: int):
    item  = ItemDB(name=name, price=price, quantity=quantity)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item

def get_item(db_session, name: str):
    return db_session.query(ItemDB).filter(ItemDB.name == name).first()
