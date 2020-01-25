import sys
import json
import fitbit
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

levelnr = {
    "deep": 0,
    "light": 1,
    "rem": 2,
    "wake": 3,
}

with open('tokens.json') as f:
    tokens = json.load(f)

def update_tokens(token):
    with open('tokens.json', 'r') as f:
        data = json.load(f)
    data['users'][token['user_id']] = token
    with open('tokens.json', 'w') as f:
        json.dump(data, f)

for user in tokens['users'].values():
    client = fitbit.Fitbit(
        tokens['client_id'], tokens['client_secret'],
        access_token=user['access_token'],
        refresh_token=user['refresh_token'],
        expires_at=user['expires_at'],
        refresh_cb=update_tokens
    )
    client.API_VERSION = 1.2
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = None
    sleep = client.sleep(date=date)
    df = pd.DataFrame(sleep['sleep'][0]['levels']['data'])
    df.dateTime = pd.to_datetime(df.dateTime)
    #df.seconds = pd.to_timedelta(df.seconds, unit='s')
    df['levelnr'] = df.level.map(levelnr)
    df = df.set_index('dateTime')
    #breakpoint()
    print(df)
    #df.level.plot()
    plt.step(df.index.to_list(), df.levelnr.to_list(), where='post')
    plt.yticks(list(levelnr.values()), list(levelnr.keys()))

plt.show()
