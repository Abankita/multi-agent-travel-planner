import os
from datetime import date
import airportsdata
import requests
from dotenv import load_dotenv

load_dotenv()
AIRPORTS = airportsdata.load("IATA")


def airport_code(value: str) -> str | None:
    cleaned = value.strip().upper()
    if cleaned in AIRPORTS:
        return cleaned
    lowered = value.strip().lower()
    matches = [code for code, airport in AIRPORTS.items() if lowered in airport.get("city", "").lower() or lowered in airport.get("name", "").lower()]
    return matches[0] if matches else None


def lookup_flights(origin: str, destination: str, departure_date: date) -> dict:
    origin_code, destination_code = airport_code(origin), airport_code(destination)
    result = {"origin_code": origin_code, "destination_code": destination_code, "flights": [], "notice": None}
    if not origin_code or not destination_code:
        result["notice"] = "I could not match one of those locations to an airport. Try an IATA code such as DEL or LHR."
        return result
    api_key = os.getenv("AVIATIONSTACK_API_KEY")
    if not api_key:
        result["notice"] = "Flight lookup is not configured. Add AVIATIONSTACK_API_KEY to .env."
        return result
    if departure_date != date.today():
        result["notice"] = (
            "Showing currently tracked flights on this route; confirm your trip-date schedule with an airline or upgrade for Future Flight access."
        )
    try:
        response = requests.get(
            "https://api.aviationstack.com/v1/flights",
            params={"access_key": api_key, "dep_iata": origin_code, "arr_iata": destination_code, "limit": 8},
            timeout=15,
        )
        payload = response.json()
        if response.status_code != 200 or payload.get("error"):
            result["notice"] = payload.get("error", {}).get("message", "The flight provider could not return results for this route.")
            return result
        for item in payload.get("data", []):
            flight, airline = item.get("flight", {}), item.get("airline", {})
            departure, arrival = item.get("departure", {}), item.get("arrival", {})
            result["flights"].append({"airline": airline.get("name", "Unknown airline"), "number": flight.get("iata", ""), "departure": departure.get("scheduled") or departure.get("estimated") or "Not provided", "arrival": arrival.get("scheduled") or arrival.get("estimated") or "Not provided", "status": item.get("flight_status", "scheduled")})
        if not result["flights"] and not result["notice"]:
            result["notice"] = "No flight data was returned. Availability and fares should be confirmed with an airline or booking site."
    except (requests.RequestException, ValueError):
        result["notice"] = "Flight lookup is temporarily unavailable. Please try again shortly."
    return result
