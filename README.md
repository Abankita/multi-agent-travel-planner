# Multi-agent travel planner

This is a web-based, multi-agent travel planner. It accepts your trip details and delegates the work to specialist agents: one retrieves AviationStack flight data and real-time status, another researches weather and packing considerations, a local-research agent finds useful destination information, and an itinerary agent combines the findings into a practical day-by-day plan.

The project is designed as a planning assistant, not a booking engine. Flight results are schedules only; prices, availability, weather, opening times, and bookings should always be confirmed with the relevant provider.

## Features

- AviationStack flight data and real-time flight-status lookup
- Weather and travel research through Tavily
- Day-by-day itinerary creation through Groq's `openai/gpt-oss-120b` model
- Airport/city-to-IATA matching for flight searches
- A responsive FastAPI web interface
- Clear fallbacks when a provider is unavailable

## Prerequisites

- Python 3.11 or newer
- A Groq API key for itinerary generation
- A Tavily API key for weather and destination research
- An AviationStack API key with Full Aviation Data and Real-Time Flights access

## Setup

1. Open PowerShell in the project folder.

2. Create and activate a virtual environment:

   ```powershell
   py -3.11 -m venv env_name
   .\\travel\\Scripts\\Activate.ps1
   ```

3. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root. Add your API keys without quotes:

   ```env
   GROQ_API_KEY=your_groq_key
   TAVILY_API_KEY=your_tavily_key
   AVIATIONSTACK_API_KEY=your_aviationstack_key
   ```


5. Start the development server:

   ```powershell
   uvicorn app:app --reload
   ```

6. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## How to use it

1. Enter an origin and destination. You can use a city name or an IATA code, such as `DEL` or `LHR`.
2. Select your departure and return dates, traveller count, and budget.
3. Add optional interests such as food, museums, hiking, or local culture.
4. Select **Build my travel plan**.

The agents run their research in parallel, then the itinerary agent uses those briefings to create the final trip plan. If one provider is unavailable, the rest of the result will still be shown with an explanatory notice.

