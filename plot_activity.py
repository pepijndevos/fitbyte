import sys
import json
import fitbit
import pandas as pd
import matplotlib.pyplot as plt
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

if len(sys.argv) == 2:
    date = sys.argv[1]
    activities = ['heart']
elif len(sys.argv) > 2:
    date = sys.argv[1]
    activities = sys.argv[2:]
else:
    date = 'today'
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
            detail_level='15min',
        )[f'activities-{act}-intraday']['dataset']
        df = pd.DataFrame(ts)
        df.time = pd.to_datetime(df.time).dt.time
        df = df.set_index('time')
        plt.plot(df.index.to_list(), df.value.to_list())
        plt.ylabel(act)

plt.show()
