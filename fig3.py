# output fig3 data(run for 95-120 min)
from run import multiple_run as mr
from pandas import DataFrame
from plotly.graph_objects import Figure, Scatter

# collect data
df = DataFrame(data = dict(
    n10 = [0 for i in range(10, 90, 10)],
    n20 = [0 for i in range(10, 90, 10)],
    n30 = [0 for i in range(10, 90, 10)],
    n40 = [0 for i in range(10, 90, 10)],
), index = [i for i in range(10, 90, 10)])
for i in range(10, 50, 10):
    print(f'{i}')
    for j in df.index:
        print(f'  {j}')
        col = 'n'+str(i)
        cal = mr(run=10, size=i, f_e=j*1e9)['partial']
        df.loc[j, col] = cal

# plot fig3
## config for traces
config = DataFrame(dict(
    name = [
        'N=10',
        'N=20',
        'N=30',
        'N=40',
    ],
    line = [
        dict(color='#FF6600'),
        dict(color='#0099CC'),
        dict(color='#FFCA18'),
        dict(color='#246EB9'),
    ],
), index = ['n10','n20','n30','n40',])

fig = Figure()

## add traces to figure
for i in config.index:
    fig.add_trace(Scatter(x=df.index, y=df[i], name=config.loc[i,'name'], line=config.loc[i,'line']))

## config for figure
fig.update_layout(dict(
    title=dict(
        text='Fig.3. Maximum delay against the edge computation<br>capacity with different numbers of users.',
        font=dict(size=16,),
    ),
    xaxis=dict(
        title=dict(
            text='Edge computation capacity(x 1e9 CPU cycle/s)',
            font=dict(size=12),
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Max delay of all devices in system(s)',
            font=dict(size=12),
        ),
    ),
    width=720,
    height=480
))

## show and write figure
fig.show()
fig.write_image(file='fig3.jpg')