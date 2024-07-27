# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', 
                                                options=[
                                                    {'label':'All Site','value':'ALL'},
                                                    {'label':'CCAFS LC-40','value':'CCAFS LC-40'},
                                                    {'label':'CCAFS SLC-40','value':'CCAFS SLC-40'},
                                                    {'label':'KSC LC-39A','value':'KSC LC-39A'},
                                                    {'label':'VAFB SLC-4E','value':'VAFB SLC-4E'}
                                                    ],
                                            value='ALL',
                                            placeholder="Select a Lauch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                            min=0, max=10000, step=1000,
                                                #marks={0:'0 Kg',1000:'1000 Kg', 2000:'2000 Kg', 3000:'3000 Kg', 4000:'4000 Kg', 5000:'5000 Kg', 6000: '6000 Kg', 7000: '7000 Kg', 8000: '8000 Kg', 9000: '9000 Kg', 10000: '10000 Kg'},
                                            value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='<b>Successful Launches Count by Site (%)</b>')
        return fig
    else:
        filtered_df=spacex_df[spacex_df['Launch Site']== entered_site]
        filtered_df=filtered_df.groupby(['Launch Site','class']).size().reset_index(name='class count')
        
        failure_count= filtered_df['class count'][0]
        success_count= filtered_df['class count'][1]
        total_number_launch=filtered_df['class count'].sum()
        
        fig=px.pie( filtered_df,values=[failure_count, success_count],
                   names=['<b>Failure</b>', '<b>Success</b>'], color=['Failure', 'Success'], 
                   color_discrete_map={'Failure':px.colors.qualitative.G10[1], 'Success':px.colors.qualitative.G10[5]}, 
               title=f"<b>Launch attempts outcome (%) for site {entered_site}</b><br>Total number of attempts= {total_number_launch}<br>Number of success= {success_count}<br>Number of failures= {failure_count}"  )
        return fig    
        # return the outcomes piechart for a selected site

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'))

def get_scatter_chart(entered_site, payload):
    #filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between('payload[0]','payload[1]')]
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload[0],payload[1])]

    if entered_site == 'ALL':
        low, high = payload
        #filtered_df = spacex_df
        #fig = go.Figure(Filtered_df=go.Scatter(x=line_data['Payload Mass (kg)'],y=line_data['class'],color="Booster Version Category",title='<b>Launch outcome vs. Payload mass for all sites</b>')) 
        mask = (filtered_df['Payload Mass (kg)'] > low) & (filtered_df['Payload Mass (kg)'] < high)
        fig = px.scatter(
            filtered_df[mask], x="Payload Mass (kg)", y="class",
            color="Booster Version",
            size='Payload Mass (kg)',
            hover_data=['Payload Mass (kg)']) 
        return fig
    else:
        low, high = payload
        filtered_df=spacex_df.loc[spacex_df['Launch Site']== entered_site]
        #filtered_df=filtered_df.groupby(['Launch Site','class']).reset_index()
        mask = (filtered_df['Payload Mass (kg)'] > low) & (filtered_df['Payload Mass (kg)'] < high)
        fig = px.scatter(
            filtered_df[mask], x="Payload Mass (kg)", y="class",
            color="Booster Version",
            size='Payload Mass (kg)',
            hover_data=['Payload Mass (kg)'])
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
