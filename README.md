# Messaging Automation Bot — Demo

A small Python demo project that simulates a messaging automation bot with Google Calendar integration (mocked data).

## Features
- Daily digest scheduled at 8:00 AM Pacific (using APScheduler).
- Simulated real-time alerts for new or updated events.
- Console-only commands: `today`, `week`, `kpi`.
- No external APIs called — calendar data is mocked for demo purposes.

## Files
- `bot.py` — main script (interactive + demo mode).
- `config.json` — pinned messages and settings.
- `.env.example` — example environment variables.
- `requirements.txt` — Python dependencies.

## Setup
1. Install Python 3.9+.
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate    # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
- Run interactive mode:
  ```bash
  python bot.py
  ```
  Type `help` to see available commands (`today`, `week`, `kpi`, `help`, `exit`).

- Run a short demo (recommended when first trying):
  ```bash
  python bot.py --demo
  ```
  The demo runs for ~30 seconds, prints an immediate daily digest and several simulated real-time alerts, then exits.

## How it works (high level)
- `MockCalendar` generates a set of fake events spanning today and the next 10 days.
- APScheduler schedules `daily_digest()` to run at 8:00 AM Pacific using a cron trigger.
- A background thread simulates new or updated events and prints alerts to the console.
- Commands query the mock store and print results to the console (no external calls).

## Future improvements (suggestions)
- Replace `MockCalendar` with real Google Calendar API integration.
- Add pluggable output adapters (Slack, Discord, Email).
- Make `kpi` calculation configurable with weights and more metrics.
- Persist events to a lightweight DB (SQLite) and add unit tests.

## License
MIT
