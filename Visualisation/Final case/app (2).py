import pandas as pd
from dash import Dash, Input, Output, callback, State, dash_table, html
from dash import dcc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_mantine_components as dmc
from datetime import datetime as dt


def load_data():
    data_calendar = pd.read_csv("AirBnB Amsterdam Data\public.calendar_amsterdam_airbnb.csv")
    data_listing = pd.read_csv("AirBnB Amsterdam Data\public.listings_amsterdam_airbnb.csv")
    data_listing_return = data_listing

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

    list_features = ['id', 'name', 'neighbourhood_cleansed', 'description', 'latitude', 'longitude', 'property_type',
                     'accommodates', 'price', 'number_of_reviews', 'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness',
                     'review_scores_checkin', 'review_scores_communication', 'review_scores_location',
                     'review_scores_value', 'reviews_per_month']
    data_listing = data_listing[list_features]

    df = data_calendar.merge(data_listing, left_on='listing_id', right_on='id')
    return df, data_listing_return


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
    list_review_id = ['id', 'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness',
                      'review_scores_checkin', 'review_scores_communication', 'review_scores_location',
                      'review_scores_value']
    data_call[list_review_id] = data_call[list_review_id].fillna(0)
    data_rating_sorted = data_call[list_review_id].sort_values(by='review_scores_rating', ascending=False).iloc[:15]
    data_rating_sorted['id'] = data_rating_sorted['id'].apply(str)
    return data_rating_sorted


def get_data_for_reviews(data_call):
    data_call['reviews_per_month'] = data_call['reviews_per_month'].fillna(0)
    data_views = data_call[['id', 'reviews_per_month']]
    data_views = data_views.sort_values(by='reviews_per_month', ascending=False).iloc[:15]
    data_views['id'] = data_views['id'].apply(str)
    return data_views


def get_data_for_price(data_call):
    data_call_price = data_call[data_call.price_x > 0].pivot_table(
        values=['price_x', 'rating'],
        index='listing_id',
        aggfunc={'price_x': 'sum', 'rating': 'mean'}
    ).reset_index().sort_values(by=['price_x', 'rating'], ascending=[True, False])
    data_call_price['listing_id'] = list(map(str, data_call_price.listing_id))
    return data_call_price


def get_data_for_table(data_call):
    data_views_id = get_data_for_reviews(data_call)['id'].apply(int)
    data_rating_id = get_data_for_rating(data_call)['id'].apply(int)
    data_for_table = df_listing[(df_listing.id.isin(data_views_id)) | (df_listing.id.isin(data_rating_id))]
    data_for_table = data_for_table[['id', 'name', 'description', 'neighborhood_overview']]
    return data_for_table


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


def get_fig_3(data_call):
    data_rating_sorted = get_data_for_rating(data_call)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data_rating_sorted['id'],
        y=data_rating_sorted['review_scores_cleanliness'],
        name='Cleanliness',
        marker_color='cornflowerblue'
    ))
    fig.add_trace(go.Bar(
        x=data_rating_sorted['id'],
        y=data_rating_sorted['review_scores_location'],
        name='Location',
        marker_color='violet'
    ))
    fig.add_trace(go.Bar(
        x=data_rating_sorted['id'],
        y=data_rating_sorted['review_scores_accuracy'],
        name='Accuracy',
        marker_color='mediumseagreen'
    ))
    fig.add_trace(go.Bar(
        x=data_rating_sorted['id'],
        y=data_rating_sorted['review_scores_value'],
        name='Value',
        marker_color='sandybrown'
    ))

    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(title='Top-15 based on overall rating with detailed rating by different parameters')
    return fig


def get_fig_4(data_call):
    data_views = get_data_for_reviews(data_call)
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=data_views['id'],
        y=data_views['reviews_per_month'],
        name='Reviews per month',
        marker_color='cornflowerblue'
    ))
    fig1.update_layout(title='Top-15 based on the number of reviews per month')
    return fig1


def get_fig_map(data_call):
    px.set_mapbox_access_token('pk.eyJ1IjoibWFjbGVvZG11cyIsImEiOiJjbGk0ZDZ5azgwNzU3M2RrYjlveHQ1b3J2In0.G4ojaQdXmXzu4f1JehGdUw')
    fig = px.scatter_mapbox(data_call, lat="latitude", lon="longitude", color="price_y", size="number_of_reviews",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
    return fig


def get_fig_table(data_call):
    fig = dash_table.DataTable(
        id='datatable_id',
        data=data_call.to_dict('records'),
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": False} for i in data_call.iloc[:15].columns
        ],
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        row_deletable=False,
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=len(data_call.id),
        style_cell_conditional=[
            {'if': {'column_id': 'price_y'},
             'width': '40%', 'textAlign': 'left'},
            {'if': {'column_id': 'price_x'},
             'width': '30%', 'textAlign': 'left'},
            {'if': {'column_id': 'cases'},
             'width': '30%', 'textAlign': 'left'},
        ],
        style_data={'whiteSpace': 'normal',
                    'height': 'auto'}
    )
    return fig


df, df_listing = load_data()


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
price_slider = dmc.RangeSlider(
                    id='p_slider',
                    min=0,
                    max=7900,
                    value=[100, 1000],
                    marks=[
                        {"value": 1000, "label": "1000"},
                        {"value": 2000, "label": "2000"},
                        {"value": 3000, "label": "3000"},
                        {"value": 4000, "label": "4000"},
                        {"value": 5000, "label": "5000"},
                        {"value": 6000, "label": "6000"},
                        {"value": 7000, "label": "7000"},
                    ],
                    mb=35)

app = Dash()

app.layout = dmc.Container(
        children=(
            dmc.Title('Choose your best place!'),
            dmc.Grid(children=(
                dmc.Col(district_selector, span=2),
                dmc.Col(property_type_selector, span=2),
                dmc.Col(dcc.DatePickerRange(
                    id='dt_pick_range',
                    start_date=dt(2023, 4, 1).date(),
                    end_date=dt(2023, 4, 2).date(),
                    persistence=True,
                    persistence_type='session',
                    persisted_props=['start_date', 'end_date'],
                    minimum_nights=1
                )),
                dmc.Title('Choose price range', order=2),
                dmc.Col(price_slider, span=4),
                dmc.Button(id='button1', n_clicks=0, children="Show AVAILABLE places")
            )),
            dmc.Grid(
                children=(
                    dmc.Col(dcc.Loading(dcc.Graph(id='ratings_chart')), span=8),
                    dmc.Col(dcc.Loading(dcc.Graph(id='views_chart')), span=4),
                    dmc.Col(dcc.Loading(dcc.Graph(id='map')), span=8)
                ),
                justify="center",
                align="center",
                gutter="xl"
            ),
            dmc.Text('Check some description!'),
            get_fig_table(df_listing[['id', 'name', 'description', 'neighborhood_overview']].iloc[:15])
        ),
        fluid=True
)


def days_between(d1, d2):
    d1 = dt.strptime(d1, "%Y-%m-%d")
    d2 = dt.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


@callback(
    Output(component_id='ratings_chart', component_property='figure'),
    Output(component_id='views_chart', component_property='figure'),
    Output(component_id='map', component_property='figure'),
    Output(component_id='datatable_id', component_property='data'),
    State(component_id='district_selector', component_property='value'),
    State(component_id='property_type_selector', component_property='value'),
    [State(component_id='dt_pick_range', component_property='start_date'),
     State(component_id='dt_pick_range', component_property='end_date')],
    State(component_id='p_slider', component_property='value'),
    Input(component_id='button1', component_property='n_clicks')
)
def update_plots(district, property_type, start_date, end_date, p_slider,  n):
    data_call = df
    data_call_listing = df_listing

    if district:
        data_call = data_call[data_call['neighbourhood_cleansed'].isin(district)]
    if property_type:
        data_call = data_call[data_call['property_type'].isin(property_type)]
    if start_date and end_date:
        print(start_date, type(start_date))
        data_call = data_call[(data_call['date'] >= start_date) & (data_call['date'] < end_date)]
        data_call['available'] = data_call['available'].apply(int)
        good_id = data_call[['listing_id', 'available']].groupby('listing_id')['available'].sum().reset_index()
        good_id = good_id[good_id.available == days_between(start_date, end_date)]['listing_id']
        data_call = data_call[data_call['listing_id'].isin(good_id)]
    data_call = data_call[(data_call['price_y'] >= p_slider[0]) & (data_call['price_y'] <= p_slider[1])]
    data_call_listing = data_call_listing[data_call_listing['id'].isin(data_call['listing_id'])]

    fig3 = get_fig_3(data_call_listing)
    fig4 = get_fig_4(data_call_listing)
    fig_map = get_fig_map(data_call[['name', 'latitude', 'longitude', 'price_y', 'number_of_reviews',
                                     'review_scores_rating']])
    updated_data = get_data_for_table(data_call_listing)

    fig3.update_layout(plot_default_params)
    fig4.update_layout(plot_default_params)
    fig_map.update_layout(plot_default_params)

    return fig3, fig4, fig_map, updated_data.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)