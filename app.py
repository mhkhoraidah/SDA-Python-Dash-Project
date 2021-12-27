import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash

#import dash_core_components as dcc
from dash import dcc

#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output

import dash
import dash_bootstrap_components as dbc
#from dash.dependencies import Input, Output
from dash import Input, Output, dcc, html


df = pd.read_csv('Data_Professional_Salary_Survey_Responses.csv')
df.rename(columns={' SalaryUSD ': 'SalaryUSD'}, inplace=True)


missing_val = ['Not Asked']
df.replace(missing_val, np.nan, inplace=True)


df = df.drop(['PostalCode', 'HowManyCompanies', 'CompanyEmployeesOverall', 'Education', 'EducationIsComputerRelated',
              'Certifications', 'HoursWorkedPerWeek', 'TelecommuteDaysPerWeek', 'NewestVersionInProduction', 'OldestVersionInProduction',
             'PopulationOfLargestCityWithin20Miles', 'OtherJobDuties', 'KindsOfTasksPerformed', 'LookingForAnotherJob'], axis=1)


df['OtherDatabases'] = df['OtherDatabases'].fillna(
    df['OtherDatabases'].mode()[0])
df['DatabaseServers'] = df['DatabaseServers'].fillna(
    df['DatabaseServers'].mode()[0])
df['CareerPlansThisYear'] = df['CareerPlansThisYear'].fillna(
    df['CareerPlansThisYear'].mode()[0])
# We can't fill the Gender by mode. We assume that it is Unknown
df['Gender'] = df['Gender'].fillna('Unknown')
df['Gender'] = df['Gender'].replace(['None'], 'Unknown')


#print(df['YearsWithThisTypeOfJob'].unique())
df.loc[df['YearsWithThisTypeOfJob'] > 45] = np.nan


m = df['YearsWithThisTypeOfJob'].mean(skipna=True)
df['YearsWithThisTypeOfJob'] = df['YearsWithThisTypeOfJob'].fillna(round(m))


df['SalaryUSD'] = df["SalaryUSD"].str.replace(",", "").astype(float)
df['SalaryUSD'] = pd.to_numeric(df["SalaryUSD"])


countries = df[['Country']].groupby(['Country']).count()
# Load country list as option for multi select dropdown select
optionsCountry = [{'label': "Select All", 'value': -1}]
for i in range(len(countries.index)):
    optionsCountry.append(
        {'label': countries.index[i], 'value': countries.index[i]})

countries


years = df[['Survey Year']].groupby(['Survey Year']).count()
years.index = years.index.astype(int)  # Convert type to int
# Load country list as option for multi select dropdown select
optionsYears = [{'label': "Select All", 'value': -1}]
for i in range(len(years.index)):
    optionsYears.append({'label': years.index[i], 'value': years.index[i]})

years


gender = df[['Gender']].groupby(['Gender']).count()
# Load gender list as option for dropdown select
optionsGender = [{'label': "Unknown", 'value': "Unknown"}]
for i in range(len(gender.index)-1):
    optionsGender.append({'label': gender.index[i], 'value': gender.index[i]})

optionsGender


def generate_selectionList(filteredDF):
    jobTitle = filteredDF[['JobTitle']].groupby(['JobTitle']).count()

    # Load gender list as option for dropdown select
    optionsJobs = []
    for i in range(1, len(jobTitle)):
        optionsJobs.append(
            {'label': jobTitle.index[i], 'value': jobTitle.index[i]})

    return optionsJobs
    

def generate_countriesList(filteredDF):
    countries = filteredDF[['Country']].groupby(['Country']).count()

    # Load country list as option for multi select dropdown select
    optionsCountry = []
    for i in range(len(countries.index)):
        optionsCountry.append(
            {'label': countries.index[i], 'value': countries.index[i]})

    return optionsCountry


yearsData = df[['Survey Year']].groupby(['Survey Year']).count()
yearsData.index = yearsData.index.astype(int)  # Convert type to int

# Load country list as option for multi select dropdown select
optionsYears = []
for i in range(len(yearsData.index)):
    optionsYears.append({'label': yearsData.index[i], 'value': yearsData.index[i]})




app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Salary Survey"
server = app.server

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Salary", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("Job Experience",
                    href="/page-1", active="exact")),
        dbc.NavItem(dbc.NavLink("Primary Database",
                    href="/page-2", active="exact")),
        dbc.NavItem(dbc.NavLink("Career Plans",
                    href="/page-3", active="exact")),
    ],
    brand="Data Professional Salary Survey Responses",
    brand_href="#",
    color="#000000",
    dark=True,
)
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


# The controls of Salary page
controls_page0 = dbc.Card(
    [
        html.Label('Group By'),
        dcc.Dropdown(
            id="groupby",
            options=[{'label': 'Country', 'value': 'Country'},
                     {'label': 'Survey Year', 'value': 'Survey Year'},
                     {'label': 'Employment Sector', 'value': 'EmploymentSector'},
                     {'label': 'Employment Status', 'value': 'EmploymentStatus'},
                     {'label': 'Manage Staff', 'value': 'ManageStaff'},
                     {'label': 'Gender', 'value': 'Gender'},
                     {'label': 'Career Plans This Year', 'value': 'CareerPlansThisYear'}],
            value='Country',
        ),

        html.Br(),
        html.Label('Operation'),
        dcc.Dropdown(
            id="operation",
            options=[{'label': 'mean()', 'value': 'mean'},
                     {'label': 'sum()', 'value': 'sum'},
                     {'label': 'count()', 'value': 'count'}],
            value='mean',
        ),

        html.Br(),
        html.Label('Country'),
        dcc.Dropdown(
            id="country",
            options=optionsCountry,
            value=-1,
            multi=True
        ),

        html.Br(),
        html.Label('Plot Type'),
        dbc.Card([dbc.RadioItems(
            id='plot_radio_items',
            value="1",
            options=[{
                'label': 'Bar',
                'value': '1'
            },
                {
                    'label': 'Line',
                    'value': '2'
            },

            ],

        )]),
    ],
    body=True,
)

# The controls of Job Experience page
controls_page1 = dbc.Card(
    [

        html.Label('Gender'),
        dbc.Card([
            dcc.RadioItems(
                id="gender-slider",
                value='Female',
                options=optionsGender,
                labelStyle={'display': 'block'},

            )]),


        html.Br(),
        html.Label('Job Title'),
        dcc.Dropdown(id="slct_job",
                     multi=False,
                     optionHeight=60,
                     ),


    ],
    body=True,
)

# The controls of Primary Database page
controls_page2 = dbc.Card(
    [

        html.Label("Year"),
        dcc.Dropdown(
            id='yrs',
            value=2021,  # it is the default value
            options=optionsYears,
        ),
        html.Br(),
        html.Label("Country"),
        dcc.Dropdown(
            id='c',
            clearable=True,
        ),

    ],
    body=True,
)

# The controls of Career Plans page
controls_page3 = dbc.Card(
    [
        html.Label('Slider for the years'),
                       dcc.Slider(
                                id = "slide",
                                min=2017,
                                max=2021,
                                step=None,
                                marks={
                                     2017: '2017',
                                     2018: '2018',
                                     2019: '2019',
                                     2020: '2020',
                                     2021: '2021',
                                     },  
                                value= 2017,
                             ), 
                       html.Br([]),
    ],
    body=True,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), navbar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    ############# Salary ###############
    if pathname == "/":
        return [
            dbc.Row(
                [
                    dbc.Col(
                        width=4,
                        children=dbc.Card(
                            [dbc.CardHeader("Controls"),
                             dbc.CardBody(controls_page0), ]
                        ),
                    ),
                    dbc.Col(
                        width=8,
                        children=dbc.Card(
                            [
                                dbc.CardHeader("The Visualization"),
                                dbc.CardBody(dcc.Graph(id="graphCountry"), style={
                                    "height": "100%"}),
                            ],
                            style={"height": "80vh"},
                        ),
                    ),
                ],
            ),

        ]
        ############# End Salary ###############

        ############# Job Experience ###############
    elif pathname == "/page-1":
        return [
            dbc.Row(
                [
                    dbc.Col(
                        width=4,
                        children=dbc.Card(
                            [dbc.CardHeader("Controls"),
                             dbc.CardBody(controls_page1), ]
                        ),
                    ),
                    dbc.Col(
                        width=8,
                        children=dbc.Card(
                            [
                                dbc.CardHeader("The Visualization"),
                                dbc.CardBody(dcc.Graph(id="Experience"),
                                             style={"height": "100%"}),
                            ],
                            style={"height": "80vh"},
                        ),
                    ),
                ],
            ),

        ]
        ############ End Job Experience ##############

        ############# Primary Database ###############
    elif pathname == "/page-2":
        return [
            dbc.Row(
                [
                    dbc.Col(
                        width=4,
                        children=dbc.Card(
                            [dbc.CardHeader("Controls"),
                             dbc.CardBody(controls_page2), ]
                        ),
                    ),
                    dbc.Col(
                        width=8,
                        children=dbc.Card(
                            [
                                dbc.CardHeader("The Visualization"),
                                dbc.CardBody(dcc.Graph(id="graph2"),
                                             style={"height": "100%"}),
                            ],
                            style={"height": "80vh"},
                        ),
                    ),
                ],
            ),

        ]
        ############# End Primary Database ###############

        ############# Career Plans ###############
    elif pathname == "/page-3":
        return [
                dbc.Row(
                    [
                        dbc.Col(
                            width=4,
                            children=dbc.Card(
                                [dbc.CardHeader("Controls"),
                                 dbc.CardBody(controls_page3), ]
                            ),
                        ),
                        dbc.Col(
                            width=8,
                            children=dbc.Card(
                                [
                                    dbc.CardHeader("The Visualization"),
                                    dbc.CardBody(dcc.Graph(id="careerPlans"),
                                                 style={"height": "100%"}),
                                ],
                                style={"height": "80vh"},
                            ),
                        ),
                    ],
                ),

            ]
         ############# End Career Plans ###############

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

############# Salary ###############


@app.callback(Output('graphCountry', 'figure'), [Input("country", "value"), Input("groupby", "value"), Input("operation", "value"), Input("plot_radio_items", "value"), ])
def update_figure(val_country, val_groupby, val_operation, plot_radio_items):
    data = df

    if (val_country != -1):
        data = data[data["Country"].isin(val_country)]

    if (val_operation == 'mean'):
        data = data.groupby([val_groupby]).mean()
        ytitle= "Average Salary in USD"
        title= 'The Average Salary Based on '
    if (val_operation == 'sum'):
        data = data.groupby([val_groupby]).sum()
        ytitle= "SalaryUSD"
        title= 'The Amount of Salary Based on '
    if (val_operation == 'count'):
        data = data.groupby([val_groupby]).count()
        ytitle= "Number of people"
        title= 'Number of people Based on '

    data = data.reset_index()

    plot = 0
    if (plot_radio_items == '1'):
        plot = px.bar(
            data,
            x=val_groupby,
            y="SalaryUSD",
            labels={
                     "SalaryUSD": ytitle
                 },
             
        )
    elif (plot_radio_items == '2'):
        plot = px.line(data, x=val_groupby, y="SalaryUSD", markers=True, labels={
                     "SalaryUSD": ytitle
                 },)

    plot.update_layout(title={
        'text': title +val_groupby,
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return plot
############ End Salary ##############

############# Job Experince ###############
@app.callback(Output("slct_job", 'options'), [Input("gender-slider", 'value')])
def update_selections(value):
    dff = df[df['Gender'] == value]
    return generate_selectionList(dff)

# set the value to the first available selection
@app.callback(
    Output('slct_job', 'value'),
    Input('slct_job', 'options'))
def set_cities_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('Experience', 'figure'),

    [Input("gender-slider", "value"),
     Input("slct_job", "value"), ]
)
def update_Experince(slctdGender, slctdJob):
    data = df.copy()

    data = data[data["Gender"] == slctdGender]
    data = data[data["JobTitle"] == slctdJob]

    fig = px.box(data, y="YearsWithThisTypeOfJob", labels={
                 "YearsWithThisTypeOfJob": "Years", })

    fig.update_layout(title={
        'text': "Experience Years for a Specific Job Title",
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

    return fig
############ End Job Experince ##############

############# Primary Database ###############

@app.callback(Output("c", 'options'), [Input("yrs", 'value')])
def update_selections(value):
    dff = df[df['Survey Year'] == value]
    return generate_countriesList(dff)

# set the value to the first available selection
@app.callback(
    Output('c', 'value'),
    Input('c', 'options'))
def set_cities_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('graph2', 'figure'),
    [Input("yrs", "value"),
     Input("c", "value")]

)
def update_figure(val, c):

    test = df[(df['Survey Year'] == val) & (df['Country'] == c)]
    title= "The Most Used Databases in {}, in {}".format(c,val)
    # value counts for primary database
    value_counts = test['PrimaryDatabase'].value_counts()
    fig = px.bar(x=value_counts.index, y=value_counts, labels={
                 "x": " Primary Databases", "y": "No. of Used Database"}, 
                  )  # bar graph
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    return fig

############ End Primary Database ##############

############# Career Plans ###############

@app.callback(
    Output('careerPlans', 'figure'),

    [Input("slide", "value"),]
)

def update_figure(years):
    data = df.copy()

    data = data[data['Survey Year'] <= years]
   
    fig= px.bar(
        data,
         x= "CareerPlansThisYear",
         hover_data=['CareerPlansThisYear', 'Survey Year'],
         labels={"CareerPlansThisYear": "Career Plan", "count": "No. of Employees"},
         color='Survey Year',
    )
    fig.update_traces(
                  marker_line_width = 0)
    
    fig.update_layout(
        title={
            'text': "Career Plans Based on Years",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}) 


    return fig

############# End Career Plans ###############


if __name__ == "__main__":
    #app.run_server(port=8888)
    app.run_server(debug=True)
