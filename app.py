from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, model_validator
from backend import plan_trip

load_dotenv()
app = FastAPI(title="Waypoint AI")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class TripRequest(BaseModel):
    origin: str = Field(min_length=2, max_length=80)
    destination: str = Field(min_length=2, max_length=80)
    start_date: date
    end_date: date
    travellers: int = Field(default=1, ge=1, le=12)
    budget: str = Field(default="moderate", max_length=30)
    interests: str = Field(default="", max_length=300)
    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date: raise ValueError("End date must be on or after the start date.")
        if (self.end_date - self.start_date).days > 21: raise ValueError("Please plan trips of 21 days or fewer.")
        return self


@app.get("/", response_class=HTMLResponse)
def home(request: Request): return templates.TemplateResponse(request, "index.html")


@app.post("/api/plan")
def create_plan(trip: TripRequest):
    try: return plan_trip(trip.model_dump())
    except Exception as exc: raise HTTPException(status_code=500, detail="We could not create the travel plan. Please try again.") from exc
