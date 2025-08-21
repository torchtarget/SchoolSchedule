# SchoolSchedule

This project provides tools to view and modify school pick‑up schedules.

## Command line usage

Run the existing script to print a text table or generate static HTML:

```bash
python PickupSechdule2.py        # text table output
python PickupSechdule2.py --html # write pickup_schedule.html
```

## Web interface

A basic Flask app offers an interactive table for editing the schedule.

### Run the web app

```bash
pip install flask prettytable
python app.py
```

Open <http://127.0.0.1:5000> in a browser and use the drop‑down menus to set
status values for each day. Press **Save** to update the schedule in memory.
