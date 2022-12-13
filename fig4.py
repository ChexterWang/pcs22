# output fig4 data
from run import single_run as sr
from numpy import array, average
from pandas import DataFrame
from plotly.graph_objects import Figure, Scatter

# collect data
df = DataFrame(dict(
    ul0 = [[] for i in range(7)],
    dl0 = [[] for i in range(7)],
    ul1 = [[] for i in range(7)],
    dl1 = [[] for i in range(7)],
    ul2 = [[] for i in range(7)],
    dl2 = [[] for i in range(7)],
), index=[i/2 for i in range(2, 9)])
for a in range(2, 9):
    print(a)
    d = a/2
    for b in range(10):
        cal = sr(size=3, add_param=dict(
            omega=array([6e4 for i in range(3)]),
            f_l=array([d*1e9, 2e9, 3e9])
        ))
        print(f'  {b}')
        for c in range(3):
            df.loc[d, f'ul{c}'] = df.loc[d, f'ul{c}'] + [cal['ul'][c]]
            df.loc[d, f'dl{c}'] = df.loc[d, f'dl{c}'] + [cal['dl'][c]]
for i in df.index:
    for j in df.columns:
        df.loc[i, j] = average(df.loc[i, j])

# plot fig4
fig = Figure()

## config for traces
config = DataFrame(dict(
    name = [
        'Device 1 upload',
        'Device 2 upload',
        'Device 3 upload',
        'Device 1 download',
        'Device 2 download',
        'Device 3 download',
    ],
    line = [
        dict(color='#FF8330'),
        dict(color='#412A14'),
        dict(color='#0F60B2'),
        dict(color='#FFD74F', dash='3px'),
        dict(color='#9A9A8D', dash='3px'),
        dict(color='#79CAE5', dash='3px'),
    ],
), index = ['ul0','ul1','ul2','dl0','dl1','dl2',])

## add traces to figure
for i in config.index:
    fig.add_trace(Scatter(x=df.index, y=df[i], name=config.loc[i,'name'], line=config.loc[i,'line']))

## config for figure
fig.update_layout(dict(
    title=dict(
        text='Fig.4. Optimal time-slot allocation under different<br>computation capacities of device 1.',
        font=dict(size=16),
    ),
    xaxis=dict(
        title=dict(
            text='Device 1 computation capacity(x 1e9 CPU cycle/s)',
            font=dict(size=12),
        ),
    ),
    yaxis=dict(
        title=dict(
            text='UL/DL time slot allocation of device 1, 2 and 3',
            font=dict(size=12),
        ),
    ),
    legend=dict(
        yanchor='top',
        y=0.99,
        xanchor='right',
        x=0.99,
        font=dict(size=11)
    ),
    width=720,
    height=480
))

## show and write figure
fig.show()
fig.write_image(file='fig4.jpg')