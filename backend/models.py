from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class BusRoute(Base):
    __tablename__ = "bus_routes"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    
    buses = relationship("Bus", back_populates="route")

class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("bus_routes.id"))
    travel_date = Column(Date, nullable=False)
    departure_time = Column(Time, nullable=False)
    total_seats = Column(Integer, default=40) 
    
    route = relationship("BusRoute", back_populates="buses")
    bookings = relationship("Booking", back_populates="bus")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(20), unique=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"))
    seat_number = Column(Integer, nullable=False)
    
    passenger_name = Column(String(100), nullable=False)
    passenger_phone = Column(String(20), nullable=False)
    status = Column(String(20), default="Confirmed") 

    bus = relationship("Bus", back_populates="bookings")