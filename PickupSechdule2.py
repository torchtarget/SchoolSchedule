#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prettytable import PrettyTable
from datetime import datetime, timedelta
import sys
from typing import List, Dict, Any, Tuple

# --- Configuration ---

# Schedule timing
START_DATE: datetime = datetime(2025, 5, 12)
DAYS: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
NUM_DAYS: int = len(DAYS)

# Schedule status codes (using constants for clarity)
TICK: int = 1
CROSS: int = 0
COMPLICATED: int = 2
TRAVEL: int = 3
OFFICE: int = 4
HOLIDAY: int = 5
UNKNOWN: int = 6 # New status code for Question Mark

# Status definitions: code -> {description, text symbol, html representation}
# Centralized mapping makes updates easier
STATUS_DEFINITIONS: Dict[int, Dict[str, str]] = {
    TICK: {
        "desc": "Available",
        "text": "\u2713", # Check mark
        "html": "<span class='status-tick' title='Available'>&#10003;</span>"
    },
    CROSS: {
        "desc": "Unavailable",
        "text": "\u2717", # Cross mark
        "html": "<span class='status-cross' title='Unavailable'>&#10007;</span>"
    },
    COMPLICATED: {
        "desc": "Complicated Drop-off",
        "text": "\u26A0", # Warning sign
        "html": "<span class='status-complicated' title='Complicated Drop-off'>&#9888;</span>"
    },
    TRAVEL: {
        "desc": "Travel",
        "text": "\u2708", # Airplane
        "html": "<span class='status-travel' title='Travel'>&#9992;</span>"
    },
    OFFICE: {
        "desc": "Office",
        "text": "\U0001F4BC", # Briefcase
        "html": "<span class='status-office' title='Office'>&#128188;</span>"
    },
    HOLIDAY: {
        "desc": "Holiday/No School",
        "text": "\u2600", # Sun
        "html": "<span class='status-holiday' title='Holiday/No School'>&#9728;</span>"
    },
    UNKNOWN: { # Added Question Mark status
        "desc": "Unknown / TBD",
        "text": "?", # Simple question mark for text
        "html": "<span class='status-unknown' title='Unknown / TBD'>?</span>" # Simple question mark for HTML
    }
}
DEFAULT_STATUS_CODE: int = HOLIDAY # Use Holiday as the default if code is unknown/invalid

# Data for multiple weeks (using constants improves readability)
# Ensure inner lists have NUM_DAYS elements
SCHEDULE_DATA: List[Dict[str, Any]] = [
    {
        "week_start": START_DATE + timedelta(weeks=0),
        "pick_up_1": [TICK, TICK, TICK, TICK, OFFICE],
        "pick_up_2": [TICK, TICK, OFFICE, UNKNOWN, TICK],
    },
    {
        "week_start": START_DATE + timedelta(weeks=1),
        "pick_up_1": [TICK, TRAVEL, OFFICE, TICK, OFFICE], # Example usage of UNKNOWN
        "pick_up_2": [TRAVEL, TRAVEL, OFFICE, TICK, TICK],
    },
    {
        "week_start": START_DATE + timedelta(weeks=2), # Added another week for demo
        "pick_up_1": [TICK, TICK, TICK, HOLIDAY, HOLIDAY], # Example usage of UNKNOWN
        "pick_up_2": [TICK, TRAVEL, OFFICE, HOLIDAY, HOLIDAY], # Example usage of UNKNOWN
    },
    {
        "week_start": START_DATE + timedelta(weeks=3), # Added another week for demo
        "pick_up_1": [OFFICE, TICK, TICK, TICK, TICK], # Example usage of UNKNOWN
        "pick_up_2": [TICK, OFFICE, TICK, TICK, UNKNOWN], # Example usage of UNKNOWN
    },

    {
        "week_start": START_DATE + timedelta(weeks=4), # Added another week for demo
        "pick_up_1": [HOLIDAY, TICK, TICK, HOLIDAY, HOLIDAY], # Example usage of UNKNOWN
        "pick_up_2": [HOLIDAY, COMPLICATED, HOLIDAY,OFFICE,TICK], # Example usage of UNKNOWN
    },
    {
        "week_start": START_DATE + timedelta(weeks=5), # Added another week for demo
        "pick_up_1": [TICK, TICK, TICK,TICK, HOLIDAY], # Example usage of UNKNOWN
        "pick_up_2": [TICK, TICK, OFFICE,TICK,HOLIDAY], # Example usage of UNKNOWN
    },


    # Add more weeks as needed
]

# --- Helper Functions ---

def get_week_dates(start_date: datetime) -> List[str]:
    """Generates formatted date strings for the week."""
    return [
        (start_date + timedelta(days=i)).strftime("%d %b")
        for i in range(NUM_DAYS)
    ]

def convert_codes_to_symbols(codes: List[int], format_type: str = 'text') -> List[str]:
    """Converts a list of status codes to symbols based on format_type ('text' or 'html')."""
    if format_type not in ['text', 'html']:
        raise ValueError("format_type must be 'text' or 'html'")

    # Use the defined default status if a code isn't found in the map
    default_definition = STATUS_DEFINITIONS.get(DEFAULT_STATUS_CODE, {"text": "?", "html": "?"})
    default_symbol = default_definition.get(format_type, "?")

    symbols = []
    for code in codes:
        definition = STATUS_DEFINITIONS.get(code)
        if definition:
            symbols.append(definition.get(format_type, default_symbol))
        else:
            # Handle codes truly not in the map (shouldn't happen with UNKNOWN defined)
            symbols.append(default_symbol)
            print(f"Warning: Unknown status code {code} encountered.", file=sys.stderr)

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
