from flask import Flask, render_template, request, redirect, url_for

from PickupSechdule2 import (
    STATUS_DEFINITIONS,
    SCHEDULE_DATA,
    get_week_dates,
    DAYS,
    save_schedule,
)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the schedule table and handle updates from the form."""
    if request.method == 'POST':
        # Values now come from hidden inputs populated by JS
        for w, week in enumerate(SCHEDULE_DATA):
            for key in ['pick_up_1', 'pick_up_2']:
                for d in range(len(DAYS)):
                    field = f'w{w}_{key}_{d}'
                    value = request.form.get(field)
                    if value is not None:
                        try:
                            week[key][d] = int(value)
                        except ValueError:
                            pass
        save_schedule(SCHEDULE_DATA)
        return redirect(url_for('index'))

    return render_template(
        'index.html',
        schedule=SCHEDULE_DATA,
        status_defs=STATUS_DEFINITIONS,
        days=DAYS,
        get_week_dates=get_week_dates,
    )


if __name__ == '__main__':
    app.run(debug=True)
