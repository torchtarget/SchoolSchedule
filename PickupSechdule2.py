#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prettytable import PrettyTable
from datetime import datetime, timedelta
import sys
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path

# --- Configuration ---

# Schedule timing
START_DATE: datetime = datetime(2025, 8, 25)
DAYS: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
NUM_DAYS: int = len(DAYS)

# Schedule status codes (using constants for clarity)
CROSS: int = 0
TICK: int = 1
TRAVEL: int = 2
OFFICE: int = 3
UNKNOWN: int = 4  # Question mark / not sure

# Status definitions: code -> {description, text symbol, html representation}
# Centralized mapping makes updates easier

STATUS_DEFINITIONS: Dict[int, Dict[str, str]] = {
    TICK: {
        "desc": "Available",
        "text": "✓",  # Check mark
        "html": "<span class='status-tick' title='Available'>&#10003;</span>"
    },
    CROSS: {
        "desc": "Unavailable",
        "text": "✗",  # Cross mark
        "html": "<span class='status-cross' title='Unavailable'>&#10007;</span>"
    },
    TRAVEL: {
        "desc": "Travel",
        "text": "✈",  # Airplane
        "html": "<span class='status-travel' title='Travel'>&#9992;</span>"
    },
    OFFICE: {
        "desc": "Office",
        "text": "💼",  # Briefcase
        "html": "<span class='status-office' title='Office'>&#128188;</span>"
    },
    UNKNOWN: {
        "desc": "Unknown / TBD",
        "text": "?",
        "html": "<span class='status-unknown' title='Unknown / TBD'>?</span>"
    }
}
DEFAULT_STATUS_CODE: int = UNKNOWN

# Path to schedule data file
DATA_FILE: Path = Path(__file__).resolve().parent / "data" / "schedule.json"

def load_schedule(file_path: Path = DATA_FILE) -> List[Dict[str, Any]]:
    """Load schedule data from a JSON file."""
    if not file_path.exists():
        return []
    with file_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    schedule = []
    for item in raw:
        week_start = datetime.fromisoformat(item["week_start"])
        schedule.append({
            "week_start": week_start,
            "pick_up_1": item.get("pick_up_1", []),
            "pick_up_2": item.get("pick_up_2", []),
        })
    return schedule

def save_schedule(schedule: List[Dict[str, Any]], file_path: Path = DATA_FILE) -> None:
    """Persist schedule data to a JSON file."""
    serializable = []
    for item in schedule:
        serializable.append({
            "week_start": item["week_start"].strftime("%Y-%m-%d"),
            "pick_up_1": item["pick_up_1"],
            "pick_up_2": item["pick_up_2"],
        })
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)

# Load schedule data from JSON file
SCHEDULE_DATA: List[Dict[str, Any]] = load_schedule()

# --- Helper Functions ---

def get_week_dates(start_date: datetime) -> List[str]:
    """Generates formatted date strings for the week."""
    return [
        (start_date + timedelta(days=i)).strftime("%d %b")
        for i in range(NUM_DAYS)
    ]

def convert_codes_to_symbols(pairs: List[List[int]], format_type: str = 'text') -> List[str]:
    """Converts a list of [mother, father] codes to symbols."""
    if format_type not in ['text', 'html']:
        raise ValueError("format_type must be 'text' or 'html'")

    default_def = STATUS_DEFINITIONS.get(DEFAULT_STATUS_CODE, {"text": "?", "html": "?"})
    symbols: List[str] = []
    for pair in pairs:
        m_code, f_code = pair
        m_def = STATUS_DEFINITIONS.get(m_code, default_def)
        f_def = STATUS_DEFINITIONS.get(f_code, default_def)
        if format_type == 'text':
            symbols.append(f"M:{m_def['text']} F:{f_def['text']}")
        else:
            symbols.append(
                f"<div class='pair'><span class='status-icon'>{m_def['html']}</span>"
                f"<span class='status-icon'>{f_def['html']}</span></div>"
            )
    return symbols


# --- Table Generation Functions ---

def create_schedule_table_text() -> PrettyTable:
    """Creates a PrettyTable object for console output."""
    table = PrettyTable()
    table.field_names = ["Week / Pick Up"] + DAYS
    table.align = "c" # Center align columns

    for week_data in SCHEDULE_DATA:
        week_start_date = week_data["week_start"]
        actual_dates = get_week_dates(week_start_date)
        pick_up_1_symbols = convert_codes_to_symbols(week_data["pick_up_1"], 'text')
        pick_up_2_symbols = convert_codes_to_symbols(week_data["pick_up_2"], 'text')

        # Add a separator row for visual clarity (optional)
        if table.rowcount > 0:
             table.add_row(["-" * 14] + ["-" * (len(d) + 2) for d in DAYS], divider=True)

        table.add_row([f"Week {week_start_date.strftime('%W')}"] + actual_dates) # Use week number
        table.add_row(["Pick AM"] + pick_up_1_symbols)
        table.add_row(["Pick PM"] + pick_up_2_symbols)

    return table

def generate_schedule_table_html() -> str:
    """Generates an HTML table string."""
    # Define CSS styles separately for better maintainability
    html_style = """
<style>
    body { font-family: Arial, sans-serif; }
    table { border-collapse: collapse; width: 100%; text-align: center; border: 1px solid #ccc; margin-bottom: 20px; }
    th { background-color: #d9ead3; padding: 10px; border: 1px solid #ccc; }
    td { padding: 8px; border: 1px solid #ccc; }
    tr.date-row { background-color: #cfe2f3; font-weight: bold; }
    tr.pickup-row-am { background-color: #f7f7f7; } /* Light alternating bg */
    tr.pickup-row-pm { background-color: #ffffff; }
    td.label-cell { font-weight: bold; text-align: left; padding-left: 15px;}
    .status-tick { color: green; font-weight: bold; }
    .status-cross { color: red; font-weight: bold; }
    .status-complicated { color: orange; font-weight: bold; }
    .status-travel { color: blue; font-style: italic; }
    .status-office { color: gray; }
    .status-holiday { color: #DAA520; } /* gold */
    .status-unknown { color: purple; font-weight: bold; } /* Style for Question Mark */
    ul.legend { list-style: none; padding: 0; }
    ul.legend li { margin-bottom: 5px; }
    ul.legend span { display: inline-block; min-width: 20px; text-align: center; margin-right: 10px;}
</style>
"""

    html_body = "<table border='1'>"
    # Table Header
    html_body += "<thead><tr><th>Week / Pick Up</th>"
    for day in DAYS:
        html_body += f"<th>{day}</th>"
    html_body += "</tr></thead><tbody>"

    # Table Body
    for i, week_data in enumerate(SCHEDULE_DATA):
        week_start_date = week_data["week_start"]
        actual_dates = get_week_dates(week_start_date)
        pick_up_1_symbols = convert_codes_to_symbols(week_data["pick_up_1"], 'html')
        pick_up_2_symbols = convert_codes_to_symbols(week_data["pick_up_2"], 'html')

        # Week/Dates row
        html_body += f"<tr class='date-row'><td class='label-cell'>Week {week_start_date.strftime('%W')}</td>" # Use week number
        html_body += "".join(f"<td>{date}</td>" for date in actual_dates)
        html_body += "</tr>"

        # Pick Up AM row
        html_body += f"<tr class='pickup-row-am'><td class='label-cell'>Pick AM</td>"
        html_body += "".join(f"<td>{symbol}</td>" for symbol in pick_up_1_symbols)
        html_body += "</tr>"

        # Pick Up PM row
        html_body += f"<tr class='pickup-row-pm'><td class='label-cell'>Pick PM</td>"
        html_body += "".join(f"<td>{symbol}</td>" for symbol in pick_up_2_symbols)
        html_body += "</tr>"

    html_body += "</tbody></table>"

    # Add legend - automatically includes the new status
    html_body += "<h2>Legend</h2><ul class='legend'>"
    # Sort items by code for consistent legend order (optional)
    sorted_status_items = sorted(STATUS_DEFINITIONS.items())
    for code, details in sorted_status_items:
         html_body += f"<li>{details['html']} : {details['desc']}</li>"
    html_body += "</ul>"


    # Combine header, style, and body
    html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pickup Schedule</title>
    {html_style}
</head>
<body>
    <h1>Pickup Schedule</h1>
    {html_body}
</body>
</html>"""
    return html_output

# --- Main Execution ---

def main():
    """Main function to generate schedule output."""
    output_format = 'text' # Default format
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["-h", "--html"]:
        output_format = 'html'

    if output_format == 'html':
        html_output = generate_schedule_table_html()
        filename = "pickup_schedule.html"
        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(html_output)
            print(f"HTML table has been written to {filename}")
        except IOError as e:
            print(f"Error writing file {filename}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        schedule_table = create_schedule_table_text()
        print(schedule_table)

if __name__ == "__main__":
    main()
