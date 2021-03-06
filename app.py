import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
import folium 
import flask
from getIndiaData import getIndiaData,getCountryWiseData
from streamlit import getMergeData
from apscheduler.scheduler import Scheduler
import time,json
import datetime as dt 
from datetime import timedelta

global dateTime
global recent_updated
global df_total

sched = Scheduler() # Scheduler object
sched.start()

server = flask.Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,server=server)


baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"




tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}

def loadData(fileName, columnName): 
    # data = pd.read_csv(baseURL + fileName) \
    #         .drop(['Lat', 'Long'], axis=1) \
    #         .melt(id_vars=['Province/State', 'Country/Region'], var_name='date', value_name=columnName) \
    #         .fillna('<all>')

    data = pd.read_csv(baseURL + fileName)
    
    yesterday_1 = dt.datetime.strftime(dt.datetime.now() - timedelta(1), "%-m/%-d/%y")
    yesterday_2 = dt.datetime.strftime(dt.datetime.now() - timedelta(2), "%-m/%-d/%y")
    # print(yesterday_1,"-->>",yesterday_2)
    # print(data.head())
    if 'CumRecovered' == columnName:
        data[yesterday_1] = data[yesterday_2]
    # print(data.head())
    data = data.drop(['Lat', 'Long'], axis=1) \
            .melt(id_vars=['Province/State', 'Country/Region'], var_name='date', value_name=columnName) \
            .fillna('<all>')


    data['date'] = pd.to_datetime(data['date'])
    # print("11111111111111111111",data.tail())
    # data['date'] = data['date'].astype('datetime64[ns]')
    # print(data['date'][1])pan
    # data['date'] = data['date'].tz_localize(tz = 'Asia/Kolkata')
    return data


allData = loadData("time_series_covid19_confirmed_global.csv", "CumConfirmed") \
    .merge(loadData("time_series_covid19_deaths_global.csv", "CumDeaths")) \
    .merge(loadData("time_series_covid19_recovered_global.csv", "CumRecovered"))

countries = allData['Country/Region'].unique()
countries.sort()




map_india = folium.Map(location=[20, 80], zoom_start=4.5,tiles='Stamen Toner')


def getIndiaStats(map_india):

    df_full = getMergeData()
    # df_full_org.dropna(how='all', axis=1,inplace=True)
    # df_total = (df_full_org.tail(1).apply(lambda x: x.to_json(), axis=1))['Total']
    

    # df_total = json.loads(df_total)
    # print(df_total)
    # print('0000---->>>',df_total['Active Cases'])
    # df_full = df_full_org.drop(df_full_org.tail(1).index,inplace=False)

    for lat, lon, confirm, name, deltaConfirm in zip(df_full['lat'], df_full['lon'], df_full['confirmed'], df_full['city_name'],df_full['delta.confirmed']):
        folium.CircleMarker([lat, lon],
                            radius=confirm*0.0001,
                            tooltip = ('<strong>State</strong>: ' + str(name).capitalize() + '<br>'
                                    '<strong>Active Cases</strong>: ' + str(confirm) + '<br>'
                                    '<strong>Delta Cases</strong>: ' + str(deltaConfirm) + '<br>'),
                            color='red',
                            
                            fill_color='red',
                            fill_opacity=0.3 ).add_to(map_india)
    return map_india


map_india = getIndiaStats(map_india)    
map_india.save('india_data.html')



map_world = folium.Map(location=[20, 30], zoom_start=2.0,tiles='Stamen Toner')

def getCountryWiseDataStats(map_world):

    df_full,recent_updated = getCountryWiseData()

    for lat, lon, value, active_cases,name, last_updated,confirmed,deaths,recovered in zip(df_full['Latitude'], df_full['Longitude'], df_full['mean_active'],df_full['Active Cases'], df_full['Country_Region'],df_full['Last_Update'],df_full['Confirmed'],df_full['Deaths'],df_full['Recovered']):
        folium.CircleMarker([lat, lon],
                            radius=value*0.0001,
                            tooltip = ('<strong>State</strong>: ' + str(name).capitalize() + '<br>'
                                    '<strong>Active Cases</strong>: ' + str(active_cases) + '<br>'
                                    '<strong>Last_updated</strong>: ' + str(last_updated) + '<br>'
                                    '<strong>Confirmeds</strong>: ' + str(confirmed) + '<br>'
                                    '<strong>Deaths </strong>: ' + str(deaths) + '<br>'
                                    '<strong>Recovered </strong>: ' + str(recovered) + '<br>'),
                            color='red',
                            
                            fill_color='red',
                            fill_opacity=0.3 ).add_to(map_world)
    return map_world,recent_updated

map_world,recent_updated = getCountryWiseDataStats(map_world)    
map_world.save('world_data.html')




app.layout = html.Div(
    style={ 'font-family':"Courier New, monospace" },
    children=[
    html.H1('Case History of the Coronavirus (COVID-19)'),
    html.Div(className="row", children=[
        html.Div(className="four columns", children=[
            html.H5('Country'),
            dcc.Dropdown(
                id='country',
                options=[{'label':c, 'value':c} for c in countries],
                value='India'
            )
        ]),
        html.Div(className="four columns", children=[
            html.H5('State / Province'),
            dcc.Dropdown(
                id='state'
            )
        ]),
        html.Div(className="four columns", children=[
            html.H5('Selected Metrics'),
            dcc.Checklist(
                id='metrics',
                options=[{'label':m, 'value':m} for m in ['Confirmed', 'Deaths', 'Recovered']],
                value=['Confirmed', 'Deaths','Recovered']
            )
        ])
    ]),
    dcc.Graph(
        id="plot_new_metrics",
        config={ 'displayModeBar': False }
    ),
    dcc.Graph(
        id="plot_cum_metrics",
        config={ 'displayModeBar': False }
    ),

html.H5(id = 'india_text_update',title = 'India Map View' ),
html.Iframe(id = 'map_india',  srcDoc = open("india_data.html",'r').read(), width='100%',height='600',loading_state={'is_loading' : True}),
html.Button(id='map-submit-button', n_clicks=1, children='Submit'),
html.H5(id = 'world_text_update',title = 'World Map View '),
html.Iframe(id = 'map_world',  srcDoc = open("world_data.html",'r').read(), width='100%',height='600')


])

@app.callback(
    [Output('state', 'options'), Output('state', 'value')],
    [Input('country', 'value')]
)
def update_states(country):
    states = list(allData.loc[allData['Country/Region'] == country]['Province/State'].unique())
    states.insert(0, '<all>')
    states.sort()
    state_options = [{'label':s, 'value':s} for s in states]
    state_value = state_options[0]['value']
    return state_options, state_value

def nonreactive_data(country, state):
    data = allData.loc[allData['Country/Region'] == country]
    if state == '<all>':
        data = data.drop('Province/State', axis=1).groupby("date").sum().reset_index()
    else:
        data = data.loc[data['Province/State'] == state]
    newCases = data.select_dtypes(include='int64').diff().fillna(0)
    # print("nsofwefoiwehfewoih-->>",newCases.columns)
    newCases.columns = [column.replace('Cum', 'New') for column in newCases.columns]
    data = data.join(newCases)
    data['dateStr'] = data['date'].dt.strftime('%b %d, %Y')
    return data

def barchart(data, metrics, prefix="", yaxisTitle=""):
    figure = go.Figure(data=[
        go.Bar( 
            name=metric, x=data.date, y=data[prefix + metric],
            marker_line_color='rgb(0,0,0)', marker_line_width=1,
            marker_color={ 'Deaths':'rgb(200,30,30)', 'Recovered':'rgb(30,200,30)', 'Confirmed':'rgb(100,140,240)'}[metric]
        ) for metric in metrics
    ])
    figure.update_layout( 
            barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.5)'), 
            plot_bgcolor='#FFFFFF', font=tickFont) \
        .update_xaxes( 
            title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', 
            tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
        .update_yaxes(
            title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    return figure

@app.callback(
    Output('plot_new_metrics', 'figure'), 
    [Input('country', 'value'), Input('state', 'value'), Input('metrics', 'value')]
)
def update_plot_new_metrics(country, state, metrics):
    data = nonreactive_data(country, state)
    return barchart(data, metrics, prefix="New", yaxisTitle="New Cases per Day")

@app.callback(
    Output('plot_cum_metrics', 'figure'), 
    [Input('country', 'value'), Input('state', 'value'), Input('metrics', 'value')]
)
def update_plot_cum_metrics(country, state, metrics):
    data = nonreactive_data(country, state)
    # print('DATA -- >>> ',data.tail())
    return barchart(data, metrics, prefix="Cum", yaxisTitle="Cumulated Cases")


@app.callback(
    dash.dependencies.Output('map_india', 'srcDoc'),
    [dash.dependencies.Input('map-submit-button', 'n_clicks')])
def update_map(n_clicks):
    print("india Click")
    if n_clicks is None:
        return dash.no_update
    else:
        return open('india_data.html', 'r').read()


@app.callback(
    dash.dependencies.Output('map_world', 'srcDoc'),
    [dash.dependencies.Input('map-submit-button', 'n_clicks')])
def update_map(n_clicks):
    print("World click")
    if n_clicks is None:
        return dash.no_update
    else:
        return open('world_data.html', 'r').read()



@app.callback(
    Output('india_text_update', 'children'),
    [Input('map-submit-button', 'n_clicks')])
def update_statusBar_india(n_clicks):
    return 'India Map View'
  


@app.callback(Output("world_text_update", "children"),
              [Input("map-submit-button", "n_clicks")])
def update_statusBar_world(n_clicks):
    return 'World Map View '





def job():
    print("I'm working...")
    map_india1 = getIndiaStats(map_india)    
    map_india1.save('india_data.html')

    map_world1,recent_updated = getCountryWiseDataStats(map_world)    
    map_world1.save('world_data.html')

    allData = loadData("time_series_19-covid-Confirmed.csv", "CumConfirmed") \
    .merge(loadData("time_series_19-covid-Deaths.csv", "CumDeaths")) \
    .merge(loadData("time_series_19-covid-Recovered.csv", "CumRecovered"))

    countries = allData['Country/Region'].unique()
    countries.sort()

sched.add_interval_job(job,minutes=15)

if __name__ == '__main__':
    app.server.run(debug=True,threaded=True)
