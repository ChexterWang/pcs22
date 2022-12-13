# plot fig2
from pandas import DataFrame
from plotly.graph_objects import Figure, Scatter
from run import single_run as sr
from numpy import average

# collect data
df = DataFrame(data = dict(
    edge = [[] for i in range(7)],
    local = [[] for i in range(7)],
    partial = [[] for i in range(7)],
), 
    index=[10, 15, 20, 25, 30, 35, 40],
)
for a in range(10):
    print(f'{a}')
    for i in df.index:
        print(f'  {i}')
        cal = sr(i)
        for j in df.columns:
            df.loc[i, j] = df.loc[i, j] + [cal[j]]
for i in df.index:
    for j in df.columns:
        df.loc[i, j] = average(df.loc[i, j])

# plot fig 2
## config for traces
config = DataFrame(dict(
    name = [
        'Partial Offloading',
        'Local Processing',
        'Edge Processing',
    ],
    line = [
        dict(color='#FF6600'),
        dict(color='#757563'),
        dict(color='#4785C4'),
    ],
), index = ['partial','local','edge',])

## init figure
fig = Figure()

## add trace
for i in config.index:
    fig.add_trace(Scatter(x=df.index, y=df[i], name=config.loc[i,'name'], line=config.loc[i,'line']))

## config for figure
fig.update_layout(dict(
    title=dict(
        text='Fig.2. Maximum delay against the number of devices in three schemes.',
        font=dict(size=16),
    ),
    xaxis=dict(
        title=dict(
            text='Number of devices',
            font=dict(size=12),
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Max delay of all devices in system(s)',
            font=dict(size=12),
        ),
    ),
    legend=dict(
        yanchor='top',
        y=0.99,
        xanchor='left',
        x=0.01,
        font=dict(size=11)
    ),
    width=720,
    height=480
))

## show and wirte figure
fig.show()
fig.write_image(file='fig2.jpg')