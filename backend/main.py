from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, SessionLocal
import uuid
from fastapi.middleware.cors import CORSMiddleware

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bus Seat Booking API")

# --- NEW CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any frontend to connect (good for local development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------------

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Bus Booking API is running!"}

# Endpoint to get all available routes
@app.get("/routes", response_model=list[schemas.RouteResponse])
def get_routes(db: Session = Depends(get_db)):
    return db.query(models.BusRoute).all()

# Endpoint to get buses for a specific route
@app.get("/routes/{route_id}/buses", response_model=list[schemas.BusResponse])
def get_buses_for_route(route_id: int, db: Session = Depends(get_db)):
    buses = db.query(models.Bus).filter(models.Bus.route_id == route_id).all()
    if not buses:
        raise HTTPException(status_code=404, detail="No buses found for this route")
    return buses

# --- ENDPOINT TO GET BOOKED SEATS ---
@app.get("/buses/{bus_id}/seats")
def get_booked_seats(bus_id: int, db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).filter(
        models.Booking.bus_id == bus_id,
        models.Booking.status == "Confirmed"
    ).all()
    # Returns a list of numbers, e.g., [3, 14, 22]
    return {"booked_seats": [b.seat_number for b in bookings]}
# ----------------------------------------

# Endpoint to book a seat
@app.post("/bookings")
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    # 1. Check if the bus exists
    bus = db.query(models.Bus).filter(models.Bus.id == booking.bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
        
    # 2. Check if the seat is valid
    if booking.seat_number < 1 or booking.seat_number > bus.total_seats:
        raise HTTPException(status_code=400, detail="Invalid seat number")

    # 3. Check if the seat is already booked
    existing_booking = db.query(models.Booking).filter(
        models.Booking.bus_id == booking.bus_id,
        models.Booking.seat_number == booking.seat_number,
        models.Booking.status == "Confirmed"
    ).first()
    
    if existing_booking:
        raise HTTPException(status_code=400, detail="Seat is already taken")

    # 4. Create the booking
    new_booking = models.Booking(
        booking_reference=str(uuid.uuid4())[:8].upper(), # Generate a short unique ID
        bus_id=booking.bus_id,
        seat_number=booking.seat_number,
        passenger_name=booking.passenger_name,
        passenger_phone=booking.passenger_phone
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return {"message": "Booking successful", "booking_reference": new_booking.booking_reference}

# --- ADMIN FEATURES ---

# Endpoint for admin to view all bookings
@app.get("/admin/bookings", response_model=list[schemas.BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(models.Booking).all()

# Endpoint for admin to cancel or reserve a seat
@app.put("/admin/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, status: str, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Valid statuses can be "Confirmed", "Cancelled", or "Reserved"
    booking.status = status
    db.commit()
    return {"message": f"Booking {booking.booking_reference} marked as {status}"}