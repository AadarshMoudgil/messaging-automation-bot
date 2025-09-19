# bot.py
"""Messaging Automation Bot demo (console only).

Features:
- Daily digest scheduled at 8:00 AM Pacific (APScheduler).
- Simulated real-time alerts for new/updated events.
- Console commands: today, week, kpi, help, exit
- Mocked Google Calendar data (no real API calls).

Run:
    python bot.py            # runs in interactive mode
    python bot.py --demo     # runs a short demo (shows scheduled job and alerts)
"""
import argparse
import json
import os
import random
import threading
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

PACIFIC = pytz.timezone('US/Pacific')

# --- Mock Calendar Store -------------------------------------------------
class MockCalendar:
    def __init__(self):
        self.events = []
        self._seed_events()

    def _seed_events(self):
        now = datetime.now(PACIFIC).replace(tzinfo=PACIFIC)
        # create events across today and next 10 days
        for i in range(1, 11):
            start = (now + timedelta(days=i-1)).replace(hour=9, minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1)
            self.events.append({
                "id": f"evt-{i}",
                "summary": f"Mock Event {i}",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "updated": (start - timedelta(hours=1)).isoformat(),
                "kpi_estimate": random.randint(10, 200)
            })

    def list_events(self, start_date, end_date):
        out = []
        for e in self.events:
            s = datetime.fromisoformat(e["start"])
            if start_date <= s <= end_date:
                out.append(e)
        return out

    def simulate_new_event(self):
        now = datetime.now(PACIFIC).replace(tzinfo=PACIFIC)
        i = len(self.events) + 1
        start = (now + timedelta(days=random.randint(0, 5))).replace(hour=10, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        evt = {
            "id": f"evt-{i}",
            "summary": f"Simulated Event {i}",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "updated": now.isoformat(),
            "kpi_estimate": random.randint(5, 300)
        }
        self.events.append(evt)
        return evt

    def simulate_update_event(self):
        if not self.events:
            return None
        e = random.choice(self.events)
        now = datetime.now(PACIFIC).replace(tzinfo=PACIFIC)
        e["updated"] = now.isoformat()
        # slightly bump KPI
        e["kpi_estimate"] = e.get("kpi_estimate", 10) + random.randint(1, 50)
        return e

# --- Bot Logic -----------------------------------------------------------
cal = MockCalendar()

def format_event(e):
    s = datetime.fromisoformat(e["start"]).astimezone(PACIFIC)
    return f"- {e['summary']} ({s.strftime('%Y-%m-%d %H:%M')}) — KPI est: {e.get('kpi_estimate', 'N/A')}"

def daily_digest():
    now = datetime.now(PACIFIC).replace(tzinfo=PACIFIC)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1, seconds=-1)
    events = cal.list_events(start, end)
    print('\n' + '='*40)
    print(f"DAILY DIGEST — {now.strftime('%Y-%m-%d (%Z) %H:%M')}")
    if events:
        for e in events:
            print(format_event(e))
    else:
        print("No events scheduled for today.")
    print('='*40 + '\n')

def realtime_alert(evt, action='created'):
    now = datetime.now(PACIFIC).replace(tzinfo=PACIFIC)
    print('\n' + '!'*10)
    print(f"REAL-TIME ALERT — event {action} at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(format_event(evt))
    print('!'*10 + '\n')

def run_demo(duration=30):
    """Run a short demo: trigger a digest immediately and produce a few alerts."""
    print("Starting demo run (will run for approx {} seconds)...".format(duration))
    # immediate digest
    daily_digest()
    start = time.time()
    while time.time() - start < duration:
        time.sleep(random.uniform(2, 6))
        if random.random() < 0.6:
            evt = cal.simulate_new_event()
            realtime_alert(evt, 'created')
        else:
            evt = cal.simulate_update_event()
            if evt:
                realtime_alert(evt, 'updated')
    print("Demo finished. Exiting.")

def interactive_console():
    print(CONFIG.get('pinned_header', 'Messaging Automation Bot'))
    print('Type "help" for commands.')
    while True:
        try:
            cmd = input('> ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting.')
            break
        if not cmd:
            continue
        if cmd in ('exit','quit'):
            print('Goodbye.')
            break
        if cmd == 'help':
            print('Commands: today, week, kpi, help, exit')
            continue
        if cmd == 'today':
            now = datetime.now(PACIFIC).replace(tzinfo=PACIFIC)
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1, seconds=-1)
            events = cal.list_events(start, end)
            print(f"Events for today ({start.date()}):")
            for e in events:
                print(format_event(e))
            continue
        if cmd == 'week':
            now = datetime.now(PACIFIC).replace(tzinfo=PACIFIC)
            start = now
            end = now + timedelta(days=7)
            events = cal.list_events(start, end)
            print(f"Events for next 7 days ({start.date()} — {end.date()}):")
            for e in events:
                print(format_event(e))
            continue
        if cmd == 'kpi':
            # KPI summary over next 7 days
            now = datetime.now(PACIFIC).replace(tzinfo=PACIFIC)
            end = now + timedelta(days=7)
            events = cal.list_events(now, end)
            total_kpi = sum(e.get('kpi_estimate', 0) for e in events)
            avg_kpi = total_kpi / len(events) if events else 0
            print('KPI Summary (next 7 days):')
            print(f'  Events: {len(events)}')
            print(f'  Total KPI est: {total_kpi}')
            print(f'  Average KPI est: {avg_kpi:.1f}')
            continue
        print('Unknown command. Type "help".')

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=PACIFIC)
    # Schedule daily_digest at 8:00 AM Pacific
    trigger = CronTrigger(hour=8, minute=0)
    scheduler.add_job(daily_digest, trigger=trigger, id='daily_digest')
    scheduler.start()
    return scheduler

def start_alert_simulator(stop_event):
    """Background thread that simulates real-time alerts intermittently."""
    def worker():
        while not stop_event.is_set():
            time.sleep(random.uniform(10, 20))
            if random.random() < 0.7:
                evt = cal.simulate_new_event()
                realtime_alert(evt, 'created')
            else:
                evt = cal.simulate_update_event()
                if evt:
                    realtime_alert(evt, 'updated')
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='Run a short demo and exit.')
    args = parser.parse_args()

    if args.demo:
        run_demo(duration=30)
    else:
        stop_event = threading.Event()
        scheduler = start_scheduler()
        alert_thread = start_alert_simulator(stop_event)
        try:
            interactive_console()
        finally:
            stop_event.set()
            scheduler.shutdown(wait=False)
