import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import sys

app = dash.Dash()

df = pd.read_csv("Datasets/us_disaster_declarations.csv")
df2 = pd.read_csv('Datasets/Final_dataset.csv')


ans = df[['fy_declared','incident_type']].value_counts().sort_index(level=0)
ans = ans.reset_index().set_index(['incident_type'])
vals = df['incident_type'].unique()
years = df['fy_declared'].unique()
val = df['state'].value_counts()


imp = df['incident_type'].value_counts()
frequent = list(imp[imp/df.shape[0] > (4/68)].index)
occasional = list(imp[(imp/df.shape[0] <= (4/68)) & (imp/df.shape[0] > (1/68))].index)
rare = list(imp[imp/df.shape[0] <= (1/68)].index)

efd = {j:(i + 1) for i,j in enumerate(df2['damageCategory'].unique())}

df['Rating'] = 0
df.loc[df['incident_type'].isin(frequent),'Rating'] = 3
df.loc[df['incident_type'].isin(occasional),'Rating'] = 2
df.loc[df['incident_type'].isin(rare),'Rating'] = 1

df['Economic_impact'] = np.nan
df['Population_impact'] = np.nan
df2['Property_impact'] = 0
df['Property_impact'] = np.nan

ifs = df2['propertyAction'].value_counts()
high_imp = ifs[ifs/df2.shape[0] > (30/21 - 1)].index
med_imp = ifs[(ifs/df2.shape[0] <= (30/21 - 1)) & (ifs/df2.shape[0] > ((30/21 - 1)/50))].index
low_imp = ifs[(ifs/df2.shape[0] <= ((30/21 - 1)/50))].index

df2.loc[df2['propertyAction'].isin(high_imp),'Property_impact'] = 3
df2.loc[df2['propertyAction'].isin(med_imp),'Property_impact'] = 2
df2.loc[df2['propertyAction'].isin(low_imp),'Property_impact'] = 1



j = 0
su = 0
su2 = 0
for i in df.loc[(df['fy_declared'] >= 1997) & (df['fy_declared'] <= 2018)].index:
    if j == df2.shape[0]:
        break
    df.loc[i,'Economic_impact'] = df2.loc[j,'actualAmountPaid']
    df.loc[i, 'Population_impact'] = efd[df2.loc[j, 'damageCategory']]
    df.loc[i, 'Property_impact'] = df2.loc[j,'Property_impact']
    su+=efd[df2.loc[j, 'damageCategory']]
    su2+=df2.loc[j, 'Property_impact']
    j+=1


df['Economic_impact'] = df['Economic_impact'].fillna(df2['actualAmountPaid'].mean())
df['Population_impact'] = df['Population_impact'].fillna(su/df2.shape[0])
df['Property_impact'] = df['Property_impact'].fillna(su2/df2.shape[0])

std = df['Economic_impact'].std(ddof=0)
mn = df['Economic_impact'].mean()
high_imp = df[df['Economic_impact'] >= (std + mn)].index
mid_imp = df[(df['Economic_impact'] < (std + mn)) & (df['Economic_impact'] >= mn)].index
low_imp = df[df['Economic_impact'] < mn].index


df['Economic_impact_modified'] = 0
df.loc[df['Economic_impact'].isin(high_imp),'Economic_impact_modified'] = 3
df.loc[df['Economic_impact'].isin(mid_imp),'Economic_impact_modified'] = 2
df.loc[df['Economic_impact'].isin(low_imp),'Economic_impact_modified'] = 1
df['Economic_impact'] = df['Economic_impact_modified']
del df['Economic_impact_modified']


df['Impact_factor'] = df['Economic_impact']*1 + df['Property_impact']*2 + df['Population_impact']*3
df['Hazard_ranking'] = round(df['Impact_factor']*df['Rating'])


finals = df.groupby(['incident_type','fy_declared']).size().reset_index(name='Counts').sort_values(by=['Counts','incident_type'],ascending=False)
fed = df['Rating'].value_counts()

dfed = df.groupby(['incident_type','Hazard_ranking']).size().reset_index(name="Counts").sort_values(by=['Counts','Hazard_ranking'],ascending=False)
print(df['Hazard_ranking'].mean())

freq = df.groupby(['incident_type','Rating']).size().reset_index(name="Counts").sort_values(by=["Counts"],ascending=False)

fig = px.scatter( y = df['Impact_factor'].values, x = df['incident_type'].values)
fig2 = px.bar(dfed, x = 'incident_type', y = 'Counts',color = 'Hazard_ranking', title='Stacked')
fig3 = px.bar(finals, x = 'fy_declared', y = 'Counts', color ='incident_type')
fig4 = px.bar(freq, x ='incident_type', y='Counts', color ='Rating', title="Some good one")
df.to_csv('Hazard_Ranked.csv',index='fema_declaration_string')
app.layout = html.Div(
    [
        html.Div([
            dcc.Graph(
                id='plot-bars',
                figure=fig3
            ),
            dcc.Graph(
                id='plot-pie',
                figure=go.Figure(data=[go.Pie(labels=val.index.values[:20],values=val.values[:20])])
            ),
            dcc.Graph(
                id='plot-bar2',
                figure=fig2
            ),
        ]),
        html.Div([
            dcc.Graph(
                id = "Scatter",
                figure= fig
            ),
            dcc.Graph(
                id='baring',
                figure=fig4
            ),
            dcc.Graph(
                id='plot-bar',
                figure=go.Figure(data=[go.Bar(y = fed.values, x = ["Frequent",'Occasional','Rare'],name='Rating')])
            )
        ])
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)