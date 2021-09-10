import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import sys

app = dash.Dash()

df = pd.read_csv("us_disaster_declarations.csv")


ans = df[['fy_declared','incident_type']].value_counts().sort_index(level=0)
ans = ans.reset_index().set_index(['incident_type'])
vals = df['incident_type'].unique()
years = df['fy_declared'].unique()
val = df['state'].value_counts()
print(val.values)

bars = []
for i in vals:
    arr = ans.loc[i].values
    dc = dict()
    try:
        arr.shape[1]
    except IndexError:
        dc[arr[0]] = arr[1]
        arr = []

    for k in arr:
        dc[k[0]] = k[1]

    for j in years:
        if j not in dc.keys():
            dc[j] = 0
    bars.append(go.Bar(
        y = list(dc.values()),
        x = list(dc.keys()),
        name=str(i)
    ))

app.layout = html.Div(
    [
        html.Div([
            dcc.Graph(
                id='plot-bars',
                figure=go.Figure(data=bars,
                                 layout=go.Layout(barmode='stack'))
            ),
            dcc.Graph(
                id='plot-pie',
                figure=go.Figure(data=[go.Pie(labels=val.index.values[:20],values=val.values[:20])])
            )
        ])
        # html.Div([
        #     id='plot-something',
        #     figure=go.Scatter()
        # ])
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
