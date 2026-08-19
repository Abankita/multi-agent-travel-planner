
import concurrent.futures
import os
from datetime import date
from typing import Any
from langchain_groq import ChatGroq
from tools.flight_tool import lookup_flights
from tools.tavily_tool import search_travel


def _weather_agent(destination: str, start_date: date) -> dict[str, Any]:
    sources = search_travel(f"{destination} weather forecast {start_date.isoformat()} travel packing advice", 3)
    return {"summary": sources[0]["content"] if sources else "Live weather research was unavailable. Check a local forecast before departure.", "sources": sources[1:]}


def _research_agent(destination: str, interests: str, budget: str) -> dict[str, Any]:
    return {"sources": search_travel(f"best things to do in {destination} for {interests} travellers {budget} budget", 4)}


def _itinerary_agent(request: dict[str, Any], weather: dict, research: dict, flights: dict) -> str:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return "Itinerary generation is not configured. Add GROQ_API_KEY to .env and try again."
    research_text = "\n".join(f"- {item['title']}: {item['content']}" for item in research["sources"][:4])
    prompt = f"""You are the itinerary specialist in a multi-agent travel planner. Create a practical, concise day-by-day travel itinerary in Markdown.
Trip: from {request['origin']} to {request['destination']}; {request['start_date']} to {request['end_date']}; travellers: {request['travellers']}; budget: {request['budget']}; interests: {request['interests'] or 'general sightseeing'}.
Weather-agent briefing: {weather['summary']}
Destination-research briefing: {research_text or 'No web research available.'}
Flight-data agent briefing: route {flights.get('origin_code')} to {flights.get('destination_code')}; {len(flights.get('flights', []))} flight records found. AviationStack may provide real-time status for flights in progress; future-trip records are schedules and must be confirmed before booking.
Use each calendar day exactly once. Give morning, afternoon, evening and a practical food/transport tip per day. Respect realistic travel time and the stated budget. Include a short 'Before you book' checklist. Do not invent exact prices, ticket availability, weather facts, opening hours, or flight details. Mention when something needs confirmation."""
    try:
        return ChatGroq(model="openai/gpt-oss-120b", temperature=0.35, api_key=key).invoke(prompt).content
    except Exception:
        return "The itinerary agent could not reach the language model. Your flight, weather, and research results are still shown below."


def plan_trip(request: dict[str, Any]) -> dict[str, Any]:
    """Run specialist agents concurrently, then give their findings to the planner."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        flight = executor.submit(lookup_flights, request["origin"], request["destination"], request["start_date"])
        weather = executor.submit(_weather_agent, request["destination"], request["start_date"])
        research = executor.submit(_research_agent, request["destination"], request["interests"], request["budget"])
        flights, weather_data, research_data = flight.result(), weather.result(), research.result()
    return {"itinerary": _itinerary_agent(request, weather_data, research_data, flights), "flights": flights, "weather": weather_data, "research": research_data}
