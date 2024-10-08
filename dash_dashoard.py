import dash  
import dash_bootstrap_components as dbc  
import dash_core_components as dcc  
import dash_html_components as html  
import dash_table  
import pandas as pd  
import plotly.express as px  
from dash.dependencies import Input, Output  
import dash_daq as daq  

# Load your dataset  
data = pd.read_csv('cleaned_data.csv')  

# Create a Dash app  
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  

# Layout Configuration  
app.layout = dbc.Container([  
    dbc.Row(html.H1("App Analytics Dashboard"), className='mb-4'),  

    dbc.Row([  
        dbc.Col(dcc.Dropdown(  
            id='category-dropdown',  
            options=[{'label': category, 'value': category} for category in data['Category'].unique()],  
            multi=True,  
            placeholder='Select categories'  
        ), width=6),  

        dbc.Col(dcc.Dropdown(  
            id='type-dropdown',  
            options=[{'label': 'Free', 'value': 'Free'},  
                     {'label': 'Paid', 'value': 'Paid'}],  
            multi=True,  
            placeholder='Select type'  
        ), width=6),  
    ], className='mb-4'),  

    dbc.Row([  
        dbc.Col(dcc.RangeSlider(  
            id='rating-slider',  
            min=0,  
            max=5,  
            step=0.1,  
            marks={i: str(i) for i in range(6)},  
            value=[0, 5],  
            tooltip={"placement": "bottom", "always_visible": True},  
        ), width=12),  
    ], className='mb-4'),  

    # Additional User Interface Components  
    dbc.Row([  
        dbc.Col(dbc.Button("Download Data", id="download-button", color="primary"), width=2),  
        dbc.Col(dbc.Input(id="search-input", placeholder="Search for an app...", type="text"), width=6),  
    ], className='mb-4'),  

    dbc.Row([  
        dbc.Col(dcc.Graph(id='rating-histogram')),  
        dbc.Col(dcc.Graph(id='installs-vs-rating')),  
    ]),  

    dbc.Row([  
        dbc.Col(dcc.Graph(id='price-vs-rating')),  
        dbc.Col(dcc.Graph(id='installs-bar-chart')),  
    ]),  

    dbc.Row([  
        dbc.Col(dcc.Graph(id='box-plot'), width=12),  
    ]),  

    dbc.Row([  
        dbc.Col(html.Div(id='summary-stats'), width=12),  
    ]),  

    # Pivot Table Section  
    dbc.Row([  
        dbc.Col(dash_table.DataTable(  
            id='pivot-table',  
            columns=[{'name': 'Category', 'id': 'Category'},  
                     {'name': 'Type', 'id': 'Type'},  
                     {'name': 'Average Rating', 'id': 'Average Rating'},  
                     {'name': 'Total Installs', 'id': 'Total Installs'}],  
            style_table={'overflowX': 'auto'},  
            style_cell={'textAlign': 'left'},  
            page_size=10,  
            filter_action='native',  
            sort_action='native',  
            row_selectable='single',  
            selected_rows=[],  
        ), width=12),  
    ]),  
    
], fluid=True)  

# Callback to update graphs and pivot table based on selected category and rating  
@app.callback(  
    Output('rating-histogram', 'figure'),  
    Output('installs-vs-rating', 'figure'),  
    Output('price-vs-rating', 'figure'),  
    Output('installs-bar-chart', 'figure'),  
    Output('box-plot', 'figure'),  
    Output('summary-stats', 'children'),  
    Output('pivot-table', 'data'),  
    Input('category-dropdown', 'value'),  
    Input('type-dropdown', 'value'),  
    Input('rating-slider', 'value'),  
    Input('search-input', 'value')  
)  
def update_graphs(selected_categories, selected_types, rating_range, search_value):  
    # Filter data based on user selections  
    filtered_data = data[  
        (data['Category'].isin(selected_categories) if selected_categories else True) &  
        (data['Type'].isin(selected_types) if selected_types else True) &  
        (data['Rating'] >= rating_range[0]) &   
        (data['Rating'] <= rating_range[1]) &  
        (data['App'].str.contains(search_value, case=False) if search_value else True)  
    ]  

    # Rating histogram  
    rating_hist = px.histogram(filtered_data, x='Rating', nbins=10,  
                               title="Distribution of Ratings",  
                               labels={'Rating': 'Rating'})  

    # Installs vs Rating scatter plot  
    installs_rating_fig = px.scatter(filtered_data, x='Installs', y='Rating',  
                                      title='Installs vs Rating',  
                                      labels={'Installs': 'Number of Installs', 'Rating': 'Rating'})  

    # Price vs Rating scatter plot  
    price_rating_fig = px.scatter(filtered_data, x='Price', y='Rating',  
                                   title='Price vs Rating',  
                                   labels={'Price': 'Price (USD)', 'Rating': 'Rating'})  

    # Bar chart of average installations by category  
    installs_bar_fig = px.bar(  
        filtered_data,  
        x='Category',  
        y='Installs',  
        title='Total Number of Installs by Category',  
        labels={'Category': 'Category', 'Installs': 'Total Installs'},  
        text='Installs'  
    )  

    # Box plot of rating by Type  
    box_fig = px.box(filtered_data, x='Type', y='Rating', title='Box Plot of Ratings by Type')  

    # Summary statistics  
    avg_rating = filtered_data['Rating'].mean() if not filtered_data.empty else 0  
    total_apps = filtered_data.shape[0]  

    summary = f"Total Apps: {total_apps}, Average Rating: {avg_rating:.2f}"  

    # Create pivot table  
    pivot_table = filtered_data.groupby(['Category', 'Type']).agg({  
        'Rating': 'mean',  
        'Installs': 'sum'  
    }).reset_index().rename(columns={'Rating': 'Average Rating', 'Installs': 'Total Installs'})  

    pivot_table_data = pivot_table.to_dict('records')  

    return (rating_hist, installs_rating_fig, price_rating_fig,   
            installs_bar_fig, box_fig, summary, pivot_table_data)  

# Callback for download button (for demonstration, you won't be downloading files here)  
@app.callback(  
    Output("download-button", "children"),  
    Input("download-button", "n_clicks")  
)  
def download_data(n_clicks):  
    if n_clicks:  
        return "Data Downloaded!"  
    return "Download Data"  

# Run the app  
if __name__ == '__main__':  
    app.run_server(debug=True)