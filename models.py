from sqlalchemy import Column, Integer, String, Date
from database import Base

class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    slot_date = Column(Date)
    slot_time = Column(String(50))
    booked_by = Column(String(100))
    phone = Column(String(20))


