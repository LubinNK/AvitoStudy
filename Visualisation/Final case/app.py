from dash import Dash, Input, Output, callback, State, dash_table
import dash_mantine_components as dmc
from dash import dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy
from datetime import datetime as dt


def load_data():
    data_calendar = pd.read_csv("AirBnB Amsterdam Data\public.calendar_amsterdam_airbnb.csv")
    data_listing = pd.read_csv("AirBnB Amsterdam Data\public.listings_amsterdam_airbnb.csv")

    def mod_price(x):
        if x == 'an':
            return None
        else:
            x = str(x).replace(',', '')
            return float(x)

    data_calendar['date'] = pd.to_datetime(data_calendar['date'])
    data_calendar['price'] = data_calendar.price.apply(mod_price)
    data_calendar = data_calendar.dropna(subset=['price', 'minimum_nights', 'maximum_nights'])

    list_review = ['review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness',
                   'review_scores_checkin', 'review_scores_communication', 'review_scores_location',
                   'review_scores_value']
    data_listing[list_review] = data_listing[list_review].fillna(0)
    data_listing['price'] = data_listing['price'].apply(mod_price)
    data_listing['review_scores_extra'] = data_listing[list_review[1:]].mean(axis=1)
    data_listing['rating'] = data_listing[['review_scores_rating', 'review_scores_extra']].mean(axis=1)

    list_features = ['id', 'name', 'neighbourhood_cleansed', 'description', 'latitude', 'longitude', 'property_type',
                     'accommodates', 'price', 'number_of_reviews', 'rating']
    data_listing = data_listing[list_features]

    df = data_calendar.merge(data_listing, left_on='listing_id', right_on='id')
    return df


plot_default_params = dict(
    showlegend=True,
    height=325,
    plot_bgcolor="#ffffff",
    margin_b=5,
    margin_l=5,
    margin_r=5,
    margin_t=50,
)


def get_data_for_rating(data_call):
    data_call_rating = data_call[['rating', 'listing_id', 'price_y']].drop_duplicates().sort_values(by=['rating',
                                                                                                        'price_y'],
                                                                                                    ascending=[False,
                                                                                                               True])
    data_call_rating['listing_id'] = list(map(str, data_call_rating.listing_id))
    return data_call_rating


def get_data_for_price(data_call):
    data_call_price = data_call[data_call.price_x > 0].pivot_table(
        values=['price_x', 'rating'],
        index='listing_id',
        aggfunc={'price_x': 'sum', 'rating': 'mean'}
    ).reset_index().sort_values(by=['price_x', 'rating'], ascending=[True, False])
    data_call_price['listing_id'] = list(map(str, data_call_price.listing_id))
    return data_call_price

def get_data_for_info(data_id):
    data_listing = pd.read_csv("AirBnB Amsterdam Data\public.listings_amsterdam_airbnb.csv")


def get_fig_1(data_cell):
    fig = px.bar(
        data_frame=data_cell.iloc[:15],
        x='listing_id',
        y='rating'
    )
    fig.update_layout(title='Rating')
    return fig


def get_fig_2(data_cell):
    fig = px.bar(
        data_frame=data_cell.iloc[:15],
        x='listing_id',
        y='price_x'
    )
    fig.update_layout(title='Price')
    return fig


def get_fig_map(data_call):
    px.set_mapbox_access_token('pk.eyJ1IjoibWFjbGVvZG11cyIsImEiOiJjbGk0ZDZ5azgwNzU3M2RrYjlveHQ1b3J2In0.G4ojaQdXmXzu4f1JehGdUw')
    fig = px.scatter_mapbox(data_call, lat="latitude", lon="longitude", color="price_y", size="number_of_reviews",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
    return fig


df = load_data()

# Определим селекторы
district_selector = dmc.MultiSelect(
    id='district_selector',
    label='District selector',
    data=df['neighbourhood_cleansed'].sort_values().unique()
)
property_type_selector = dmc.MultiSelect(
    id='property_type_selector',
    label='Property Type',
    data=df['property_type'].unique()
)

app = Dash()

app.layout = dmc.Container(
        children=(
            dmc.Title('Choose your best place!'),
            dmc.Grid(children=(
                dmc.Col(district_selector, span=2),
                dmc.Col(property_type_selector, span=2),
                dmc.Col(dcc.DatePickerRange(
                    id='dt_pick_range',
                    start_date=dt(2023, 4, 1),
                    end_date=dt(2023, 4, 2),
                    persistence=True,
                    persistence_type='session',
                    persisted_props=['start_date', 'end_date'],
                    minimum_nights=1
                )),
                dmc.Button(id='button1', n_clicks=0, children="Show places")
            )),
            dmc.Grid(
                children=(
                    dmc.Col(dcc.Loading(dcc.Graph(id='rating_chart')), span=4),
                    dmc.Col(dcc.Loading(dcc.Graph(id='price_chart')), span=4),
                    dmc.Col(dcc.Loading(dcc.Graph(id='map')), span=8)
                ),
                justify="center",
                align="center",
                gutter="xl"
            ),
            dmc.Title('C!'),
            dash_table.DataTable(
                        id='datatable_id',
                        data=df.iloc[:15].to_dict('records'),
                        columns=[
                            {"name": i, "id": i, "deletable": False, "selectable": False} for i in df.iloc[:15].columns
                        ],
                        editable=False,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        row_selectable="multi",
                        row_deletable=False,
                        selected_rows=[],
                        page_action="native",
                        page_current= 0,
                        page_size= 6,
                        # page_action='none',
                        # style_cell={
                        # 'whiteSpace': 'normal'
                        # },
                        # fixed_rows={ 'headers': True, 'data': 0 },
                        # virtualization=False,
                        style_cell_conditional=[
                            {'if': {'column_id': 'price_y'},
                             'width': '40%', 'textAlign': 'left'},
                            {'if': {'column_id': 'price_x'},
                             'width': '30%', 'textAlign': 'left'},
                            {'if': {'column_id': 'cases'},
                             'width': '30%', 'textAlign': 'left'},
                        ],
                        style_data={'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'maxWidth': 0}
                    )
        ),
        fluid=True
)


@callback(
    Output(component_id='rating_chart', component_property='figure'),
    Output(component_id='price_chart', component_property='figure'),
    Output(component_id='map', component_property='figure'),
    State(component_id='district_selector', component_property='value'),
    State(component_id='property_type_selector', component_property='value'),
    [State(component_id='dt_pick_range', component_property='start_date'),
     State(component_id='dt_pick_range', component_property='end_date')],
    Input(component_id='button1', component_property='n_clicks')
)
def update_plots(district, property_type, start_date, end_date, n):
    data_call = df
    if district:
        data_call = data_call[data_call['neighbourhood_cleansed'].isin(district)]
    if property_type:
        data_call = data_call[data_call['property_type'].isin(property_type)]
    if start_date and end_date:
        data_call = data_call[(data_call['date'] >= start_date) & (data_call['date'] < end_date)]

    fig1 = get_fig_1(get_data_for_rating(data_call))
    fig2 = get_fig_2(get_data_for_price(data_call))
    fig_map = get_fig_map(data_call[['name', 'latitude', 'longitude', 'price_y', 'number_of_reviews', 'rating']])

    fig1.update_layout(plot_default_params)
    fig2.update_layout(plot_default_params)
    fig_map.update_layout(plot_default_params)

    return fig1, fig2, fig_map


if __name__ == '__main__':
    app.run_server(debug=True)
