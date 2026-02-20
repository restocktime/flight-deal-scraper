# Flight Deal Scraper

Free, open-source flight deal scraper powered by the [Kiwi Tequila API](https://tequila.kiwi.com/) (free tier). Scans multiple routes, finds the cheapest round-trip deals, and outputs clean results with direct booking links.

## Features

- Scans multiple routes in a single run
- Finds cheapest round-trip flights sorted by price
- Outputs direct booking links (Kiwi.com)
- Configurable date ranges, max price, trip duration
- Saves top 20 deals to JSON file
- Supports max 1 stopover filter
- Free API — no credit card required

## Quick Start

### 1. Get a Free API Key

1. Go to [tequila.kiwi.com/portal/login](https://tequila.kiwi.com/portal/login)
2. Sign up (takes 30 seconds)
3. Create a "Solution" and copy your API key

### 2. Install & Run

```bash
git clone https://github.com/restocktime/flight-deal-scraper.git
cd flight-deal-scraper
pip install -r requirements.txt

# Option 1: Environment variable
KIWI_API_KEY=your_key_here python3 flight_scraper.py

# Option 2: Pass as argument
python3 flight_scraper.py your_key_here

# Option 3: Paste key directly in flight_scraper.py line 16
```

### 3. Set a Max Price Filter

```bash
# Only show flights under $500
KIWI_API_KEY=your_key python3 flight_scraper.py 500
```

## Customize Routes

Edit the `EXAMPLE_ROUTES` list in `flight_scraper.py`:

```python
EXAMPLE_ROUTES = [
    ("MIA", "TLV", "Miami -> Tel Aviv"),
    ("MIA", "BCN", "Miami -> Barcelona"),
    ("JFK", "NRT", "New York -> Tokyo"),
    # Add your own routes here
]
```

Use any valid [IATA airport code](https://www.iata.org/en/publications/directories/code-search/).

## Sample Output

```
  FLIGHT DEAL SCANNER
  Scanning 10 routes | Dates: next 60 days

============================================================
  Miami -> Cancun — 10 deals
============================================================

  #1  $89
  OUT: 2026-03-15T06:30  (direct)
  RET: 2026-03-22T14:20  (direct)
  Airlines: NK
  Book: https://www.kiwi.com/deep?...
```

## How It Works

1. The script calls the Kiwi Tequila `/v2/search` API endpoint
2. For each route, it searches round-trip flights within the next 60 days (default)
3. Results are sorted by price, formatted, and displayed
4. Top deals across all routes are ranked and saved to JSON

## API Details

- **Provider:** [Kiwi.com Tequila API](https://tequila.kiwi.com/)
- **Tier:** Free (rate-limited)
- **Data:** Real-time flight prices from 750+ airlines
- **Booking:** Deep links go directly to Kiwi.com checkout

## License

MIT — do whatever you want with it.

## Contributing

PRs welcome. Ideas for improvements:
- Add email/SMS alerts for price drops
- Add one-way flight support
- Add multi-city trip support
- Web dashboard for results
- Scheduled cron job scanning
