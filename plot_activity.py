import sys
import json
import fitbit
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

with open('tokens.json') as f:
    tokens = json.load(f)

def update_tokens(token):
    with open('tokens.json', 'r') as f:
        data = json.load(f)
    data['users'][token['user_id']] = token
    with open('tokens.json', 'w') as f:
        json.dump(data, f)

if len(sys.argv) > 3:
    date = sys.argv[1]
    resolution = sys.argv[2]
    activities = sys.argv[3:]
else:
    date = date.today().strftime("%Y-%m-%d")
    resolution = '1min'
    activities = ['heart']

for act in activities:
    plt.figure()
    for user in tokens['users'].values():
        client = fitbit.Fitbit(
            tokens['client_id'], tokens['client_secret'],
            access_token=user['access_token'],
            refresh_token=user['refresh_token'],
            expires_at=user['expires_at'],
            refresh_cb=update_tokens
        )
        ts = client.intraday_time_series(
            f'activities/{act}',
            base_date=date,
            detail_level=resolution,
        )[f'activities-{act}-intraday']['dataset']
        df = pd.DataFrame(ts)
        df.time = pd.to_datetime(date+' '+df.time)
        df = df.set_index('time')
        height = df.value.max()

        plt.plot(df.index.to_list(), df.value.to_list())
        plt.ylabel(act)

        log = client.activity_logs_list(after_date=date)
        df = pd.DataFrame(log['activities'])
        df.startTime = pd.to_datetime(df.startTime).dt.tz_localize(None)
        df.duration = pd.to_timedelta(df.duration, unit='ms')
        df['endTime'] = df.startTime + df.duration
        df = df.set_index('logId')
        for idx, row in df.iterrows():
            plt.annotate(row['activityName'],
                xy=(row['startTime'], height),
                xytext=(row['endTime'], height),
                arrowprops={'arrowstyle': '|-|'},
                verticalalignment='center')

plt.show()
