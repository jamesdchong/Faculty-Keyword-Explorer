import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table, State
import dash_bootstrap_components as dbc

from mysql_utils import sql_insert, sql_delete, sql_select, getFacultyTable, updateFacultyTable
from mongodb_utils import get_faculty_info, get_universities, get_faculty, get_faculty_all, getFacultyPublications
from neo4j_utils import get_scores, getFacultyCount

external_stylesheets = ['styles.css']

# Figure 1
#--------------------------------
input1 = dcc.Input(id='input1', placeholder="Add a keyword")
submit1 = html.Button('add', id="submit1", n_clicks=0,)
input2 = dcc.Input(id='input2', placeholder="Delete a keyword")
delete1 = html.Button('delete', id='delete1', n_clicks=0)

table1 = dash_table.DataTable(
    columns=[{"name": "keyword", "id": "keyword"}],
    id="keyword_table",
    style_table={'overflowX': 'auto'}
)

table2 = dash_table.DataTable(
    columns=[{"name": "faculty_name", "id": "faculty_name"}, 
             {"name": "num_matches", "id": "num_matches"}, 
             {"name": "total_score", "id": "total_score"}],
    id="rec_prof_table",
    style_table={'overflowX': 'auto'}
)

table3 = dash_table.DataTable(
    columns=[{"name": "title", "id": "title"}, 
             {"name": "num_matches", "id": "num_matches"}, 
             {"name": "total_score", "id": "total_score"}],
    id="rec_pub_table",
    style_table={'overflowX': 'auto'}
)

@callback(
    Output("keyword_table", "data", allow_duplicate=True),
    Output("rec_prof_table", "data", allow_duplicate=True),
    Output("rec_pub_table", "data", allow_duplicate=True),
    State("input1", "value"),
    Input("submit1", "n_clicks"),
    prevent_initial_call=True
)
def add_keyword(input_value, n_clicks):
    if not input_value:
        return dash.no_update
    sql_insert(input_value)
    result1, result2, result3 = sql_select()
    return result1, result2, result3

@callback(
    Output("keyword_table", "data"),
    Output("rec_prof_table", "data"),
    Output("rec_pub_table", "data"),
    State("input2", "value"),
    Input("delete1", "n_clicks"),
)
def delete_keyword(input_value, n_clicks):
    if not input_value:
        return dash.no_update
    sql_delete(input_value)
    result1, result2, result3 = sql_select()
    return result1, result2, result3

# Figure 2
#--------------------------------
dropdown1 = dcc.Dropdown(get_universities(), placeholder="Select a University", id="dropdown1")
dropdown2 = dcc.Dropdown([], placeholder="Select a Faculty Member", id="dropdown2")

image1 = html.Img(id="prof_img", src="assets/No_Image_Available.jpg", alt="No Image Available")

row1 = html.Tr([html.Td("Name:"), html.Td(id="row1")])
row2 = html.Tr([html.Td("Position:"), html.Td(id="row2")])
row3 = html.Tr([html.Td("Email:"), html.Td(id="row3")])
row4 = html.Tr([html.Td("Phone:"), html.Td(id="row4")])
row5 = html.Tr([html.Td("Research:"), html.Td(id="row5")])
row6 = html.Tr([html.Td("Publications:"), html.Td(id="row6")])
row7 = html.Tr([html.Td("University:"), html.Td(id="row7")])
table_body1 = [html.Tbody([row1, row2, row3, row4, row5, row6, row7])]
table4 = dbc.Table(table_body1)

@callback(
    Output("dropdown2", "options"),
    Input("dropdown1", "value")
)
def get_faculty_members(input_value):
    if not input_value:
        return dash.no_update
    return get_faculty(input_value)

@callback(
    Output("row1", "children"),
    Output("row2", "children"),
    Output("row3", "children"),
    Output("row4", "children"),
    Output("row5", "children"),
    Output("row6", "children"),
    Output("row7", "children"),
    Output("prof_img", "src"),
    Input("dropdown2", "value")
)
def get_info(input_value):
    if not input_value:
        return dash.no_update
    result = get_faculty_info(input_value)
    return result["name"], result["position"], result["email"], result["phone"], result["researchInterest"], result["publications"], result["affiliation"]["name"], result["photoUrl"]

# Figure 3
#--------------------------------
input3 = dcc.Input( id='input3', placeholder="Add a keyword")
submit2 = html.Button('submit', id="submit2", n_clicks=0)
graph1_layout = {
    'xaxis': {'title': 'University'},
    'yaxis': {'title': 'Keyword Score'},
}
graph1 = dcc.Graph(
    id="graph1",
    figure={
        'data': [],
        'layout': graph1_layout
    }
)

@callback(
    Output("graph1", "figure"),
    State("input3", "value"),
    Input("submit2", "n_clicks"),
)
def add_keyword_neo(input_value, n_clicks):
    if not input_value:
        return dash.no_update
    result = get_scores(input_value)
    x = list(result.keys())
    y = list(result.values())
    return {
        'data': [{'x': x, 'y': y, 'type': 'bar'}],
        'layout': graph1_layout
    }

# Figure 4
#--------------------------------
facultyDropdown2 = dcc.Dropdown(get_faculty_all(), placeholder="Select a Faculty Member", id="facultyDropdown2")
submitFaculty = html.Button('Submit', id='submitFaculty', n_clicks=0)
facultyLine = dash_table.DataTable(
    columns=[{"name": "Name", "id": "name"}, 
             {"name": "Position", "id": "position"}, 
             {"name": "Research Interest", "id": "research_interest"},
             {"name": "Email", "id": "email"},
             {"name": "Phone", "id": "phone"},
             {"name": "Photo URL", "id": "photo_url"}],
    id="facultyLine",
    style_table={'overflowX': 'auto'},
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto'
    }
)

@callback(
    Output("facultyLine", "data", allow_duplicate=True),
    Input("facultyDropdown2", "value"),
    prevent_initial_call=True
)

def displayFacultyLine(facultyDropdown2):
    if not facultyDropdown2:
        return dash.no_update
    facultyData = getFacultyTable(facultyDropdown2)
    return facultyData

facultyColumns = dcc.Dropdown(["position", "research_interest", "email", "phone", "photo_url"], placeholder="Select Attribute", id="facultyColumns")
changeInput = dcc.Input(id='changeInput', placeholder="Enter Edit")

@callback(
    Output("facultyLine", "data", allow_duplicate=True),
    State("facultyDropdown2", "value"),
    State("facultyColumns", "value"),
    State("changeInput", "value"),
    Input("submitFaculty" ,"n_clicks"),
    prevent_initial_call=True
)

def updateFaculty(facultyDropdown2, facultyColumns, changeInput, n_clicks):
    if not facultyColumns or not changeInput or not facultyDropdown2:
        return dash.no_update
    updateFacultyTable(facultyDropdown2, facultyColumns, changeInput)
    facultyData = getFacultyTable(facultyDropdown2)
    return facultyData



# Figure 5
#--------------------------------
facultyDropdown = dcc.Dropdown(get_faculty_all(), placeholder="Select a Faculty Member", id="facultyDropdown")
pubTable = dash_table.DataTable(
    columns=[{"name": "Title", "id": "title"}, 
             {"name": "Venue", "id": "venue"}, 
             {"name": "Year", "id": "year"},
             {"name": "number of Citations", "id": "numCitations"}],
    id="pubTable",
    style_table={'overflowX': 'auto', 'overflowY': 'scroll', 'height': '500px'},
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto'
    }
)

@callback(
    Output("pubTable", "data", allow_duplicate=True),
    Input("facultyDropdown", "value"),
    prevent_initial_call=True
)

def addPubData(input_value):
    if not input_value:
        return dash.no_update
    pubData = getFacultyPublications(input_value)
    return pubData


# Figure 6
#--------------------------------
universityDropdown = dcc.Dropdown(get_universities(), placeholder="Select a University", id="universityDropdown")
graph6_layout = {
    'xaxis': {'title': 'Keyword'},
    'yaxis': {'title': 'Faculty Count'},
}
graph6 = dcc.Graph(
    id="graph6",
    figure={
        'data': [],
        'layout': graph6_layout
    }
)
@callback(
    Output("graph6", "figure"),
    Input("universityDropdown", "value"),
)
def addUniversity(input_value):
    if not input_value:
        return dash.no_update
    result = getFacultyCount(input_value)
    x = list(result.keys())
    y = list(result.values())
    return {
        'data': [{'x': x, 'y': y, 'type': 'bar', 'marker': {'color': 'red'}}],
        'layout': graph6_layout,
    }

# Define the layout
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.H1("Faculty and Keyword Explorer", style={"text-align":"center"}),
    html.Div([
        html.Div([
            html.Div([
                input1, submit1, input2, delete1
            ], className="figurecomponents"),
            html.H2("Favorite Keywords", style={"text-align":"center"}),
            html.Div([
                table1
            ], className="figurecomponents"),
            html.H2("Recommended Professors", style={"text-align":"center"}),
            html.Div([
                table2
            ], className="figurecomponents"),
            html.H2("Recommended Publications", style={"text-align":"center"}),
            html.Div([
                table3
            ], className="figurecomponents"),
        ], className="figure"),
        html.Div([
            html.H1("Faculty Directory", style={"text-align":"center"}),
            html.Div([
                dropdown1, dropdown2
            ], className="figurecomponents"),
            html.Div([
                image1, table4,
            ], className="figurecomponents")
        ], className="figure"),
        html.Div([
            html.H1("Top Universities by Keyword", style={"text-align":"center"}),
            html.Div([
                input3, submit2
            ], className="figurecomponents"),
            html.Div([
                graph1
            ], className="figurecomponents")
        ], className="figure")
    ], className="row"),
    html.Div([
        html.Div([
            html.H1("Edit Faculty Information", style={"text-align":"center"}),
            html.Div([
                facultyDropdown2
            ], className="figurecomponents"),
            html.Div([
                facultyLine
            ], className="figurecomponents"),
            html.Div([
                facultyColumns
            ], className="figurecomponents"),
            html.Div([
                changeInput, submitFaculty
            ], className="figurecomponents"),
        ], className="figure"),
        html.Div([
            html.H1("Search Publications by Faculty", style={"text-align":"center"}),
            html.Div([
                facultyDropdown
            ], className="figurecomponents"),
            html.Div([
                pubTable
            ], className="figurecomponents")
        ], className="figure"),
        html.Div([
            html.H1("Top Keywords by University", style={"text-align":"center"}),
            html.Div([
                universityDropdown
            ], className="figurecomponents"),
            html.Div([
                graph6
            ], className="figurecomponents")
        ], className="figure")
    ], className="row")
])

if __name__ == '__main__':
    app.run_server(debug=True)
