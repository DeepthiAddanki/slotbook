from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal, engine
from models import Slot, Base

Base.metadata.create_all(bind=engine)


templates = Jinja2Templates(directory="templates")

def get_all_slots():
    slots = []
    for hour in range(9,17):
        slots.append(f"{hour:02d}:00 - {hour+1:02d}:00")
    return slots

@app.get("/", response_class=HTMLResponse)
def show_slots(request: Request, date: str = None):

    db = SessionLocal()

    if date:
        selected_date = datetime.strptime(date,"%Y-%m-%d").date()
    else:
        selected_date = datetime.today().date()

    all_slots = get_all_slots()

    booked = db.query(Slot).filter(Slot.slot_date == selected_date).all()

    slots = []

    current_hour = datetime.now().hour
    today = datetime.today().date()

    for time in all_slots:

        slot_hour = int(time.split(":")[0])

        if selected_date == today and slot_hour <= current_hour:
            continue

        booking = next((b for b in booked if b.slot_time == time), None)

        if booking:
            slots.append({
                "slot_time": time,
                "status": "booked",
                "booked_by": booking.booked_by,
                "phone": booking.phone,
                "id": booking.id
            })
        else:
            slots.append({
                "slot_time": time,
                "status": "available"
            })

    available_slots = len([s for s in slots if s["status"] == "available"])

    return templates.TemplateResponse(
        "slots.html",
        {
            "request": request,
            "slots": slots,
            "selected_date": selected_date,
            "today": today,
            "available_slots": available_slots
        }
    )
@app.post("/book")
def book_slot(
    slot_time: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    date: str = Form(...)
):

    db = SessionLocal()

    selected_date = datetime.strptime(date,"%Y-%m-%d").date()

    existing = db.query(Slot).filter(
        Slot.slot_date == selected_date,
        Slot.slot_time == slot_time
    ).first()

    if existing:
        return RedirectResponse("/",status_code=303)

    booking = Slot(
        slot_date=selected_date,
        slot_time=slot_time,
        booked_by=name,
        phone=phone
    )

    db.add(booking)
    db.commit()

    return RedirectResponse("/",status_code=303)

@app.get("/booked", response_class=HTMLResponse)
def booked_slots(request: Request):

    db = SessionLocal()

    slots = db.query(Slot).all()

    return templates.TemplateResponse(
        "booked.html",
        {
            "request": request,
            "slots": slots
        }
    )

@app.get("/delete/{slot_id}")
def delete_booking(slot_id: int):

    db = SessionLocal()

    db.query(Slot).filter(Slot.id == slot_id).delete()

    db.commit()

    return RedirectResponse("/booked",status_code=303)

@app.get("/edit/{slot_id}", response_class=HTMLResponse)
def edit_booking(request: Request, slot_id: int):

    db = SessionLocal()

    slot = db.query(Slot).filter(Slot.id == slot_id).first()

    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "slot": slot
        }
    )

@app.post("/edit/{slot_id}")
def update_booking(
    slot_id:int,
    name:str=Form(...),
    phone:str=Form(...)
):

    db = SessionLocal()

    slot = db.query(Slot).filter(Slot.id==slot_id).first()

    slot.booked_by = name
    slot.phone = phone

    db.commit()

    return RedirectResponse("/booked",status_code=303)