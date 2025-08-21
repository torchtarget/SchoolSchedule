from flask import Flask, render_template, request
from datetime import timedelta

from PickupSechdule2 import (
    STATUS_DEFINITIONS,
    SCHEDULE_DATA,
    get_week_dates,
    DAYS,
    save_schedule,
    DEFAULT_STATUS_CODE,
    START_DATE,
)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the schedule table and handle updates from the form."""
    if request.method == 'POST':
        for w, week in enumerate(SCHEDULE_DATA):
            for key in ['pick_up_1', 'pick_up_2']:
                for d in range(len(DAYS)):
                    for role, idx in [('m', 0), ('f', 1)]:
                        field = f'w{w}_{key}_{role}{d}'
                        value = request.form.get(field)
                        if value is not None:
                            try:
                                week[key][d][idx] = int(value)
                            except (ValueError, IndexError):
                                pass
        save_schedule(SCHEDULE_DATA)
        return ('', 204)

    return render_template(
        'index.html',
        schedule=SCHEDULE_DATA,
        status_defs=STATUS_DEFINITIONS,
        days=DAYS,
        get_week_dates=get_week_dates,
    )


@app.post('/add_week')
def add_week():
    last_start = SCHEDULE_DATA[-1]['week_start'] if SCHEDULE_DATA else START_DATE
    new_week = {
        'week_start': last_start + timedelta(days=7),
        'pick_up_1': [[DEFAULT_STATUS_CODE, DEFAULT_STATUS_CODE] for _ in range(len(DAYS))],
        'pick_up_2': [[DEFAULT_STATUS_CODE, DEFAULT_STATUS_CODE] for _ in range(len(DAYS))],
    }
    SCHEDULE_DATA.append(new_week)
    save_schedule(SCHEDULE_DATA)
    return ('', 204)


@app.post('/remove_week/<int:index>')
def remove_week(index: int):
    if 0 <= index < len(SCHEDULE_DATA):
        SCHEDULE_DATA.pop(index)
        save_schedule(SCHEDULE_DATA)
    return ('', 204)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
