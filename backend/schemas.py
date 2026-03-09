from pydantic import BaseModel
from datetime import date, time
from typing import List

class BookingCreate(BaseModel):
    bus_id: int
    seat_number: int
    passenger_name: str
    passenger_phone: str

class RouteResponse(BaseModel):
    id: int
    origin: str
    destination: str

    class Config:
        from_attributes = True

class BusResponse(BaseModel):
    id: int
    route_id: int
    travel_date: date
    departure_time: time
    total_seats: int

    class Config:
        from_attributes = True

class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    bus_id: int
    seat_number: int
    passenger_name: str
    passenger_phone: str
    status: str

    class Config:
        from_attributes = True