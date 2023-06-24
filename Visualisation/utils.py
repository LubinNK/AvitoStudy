import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def load_data():
    data = pd.read_csv('hotel_bookings.csv', delimiter=';')

    data.dropna(inplace=True)

    def with_children(row):
        if row['children'] > 0 or row['babies'] > 0:
            return 'С детьми'
        else:
            return 'Без детей'

    def get_season(row):
        if row['arrival_date_month'] in {'Декабрь', 'Январь', "Февраль"}:
            return "Winter"
        elif row['arrival_date_month'] in {'Март', 'Апрель', "Май"}:
            return "Spring"
        elif row['arrival_date_month'] in {'Июнь', 'Июль', "Август"}:
            return "Summer"
        elif row['arrival_date_month'] in {'Сентябрь', 'Октябрь', "Ноябрь"}:
            return "Autumn"

    data['with_children'] = data[['children', 'babies']].apply(with_children, axis=1)
    data['sum_children'] = data['children'] + data['babies']
    data['sum_days'] = data['stays_in_weekend_nights'] + data['stays_in_week_nights']
    data['season'] = data[['arrival_date_month']].apply(get_season, axis=1)
    data['adr'] = data['adr'].str.replace(',', '.').astype(float)
    return data


plot_default_params = dict(
    showlegend=True,
    height=325,
    plot_bgcolor="#ffffff",
    margin_b=5,
    margin_l=5,
    margin_r=5,
    margin_t=50,
)


def get_data_hotel_children(data_call):
    data_hotel_children = data_call.pivot_table(
        values=("is_canceled", "sum_days", "lead_time"),
        index=['hotel', 'sum_children']
    ).reset_index()
    data_hotel_children = data_hotel_children[data_hotel_children.sum_children < 4]
    return data_hotel_children


def get_data_season(data_call):
    data_season = data_call[data_call["is_canceled"] == 0].pivot_table(
        values=("adr", "sum_days"),
        index=['hotel', 'arrival_date_month']
    ).reset_index()
    return data_season


def get_data_monthyear(data_call):
    def month(row):
        l = ['Январь', 'Февраль', 'Март', 'Апрель', "Май", 'Июнь', 'Июль', "Август", 'Сентябрь', 'Октябрь', "Ноябрь",
             'Декабрь']
        return l.index(row['arrival_date_month']) + 1

    def month_year(row):
        l = ['Январь', 'Февраль', 'Март', 'Апрель', "Май", 'Июнь', 'Июль', "Август", 'Сентябрь', 'Октябрь', "Ноябрь",
             'Декабрь']
        return f"{l[row['arrival_date_month'] - 1]}-{row['arrival_date_year']}"

    data_monthyear = data_call[data_call["is_canceled"] == 0].pivot_table(
        values=("adr"),
        index=['hotel', 'arrival_date_month', 'arrival_date_year']
    ).reset_index()
    data_monthyear['arrival_date_month'] = data_monthyear[['arrival_date_month']].apply(month, axis=1)
    data_monthyear = data_monthyear.sort_values(by=['arrival_date_year', 'arrival_date_month'])
    data_monthyear['month_year'] = data_monthyear[['arrival_date_month', 'arrival_date_year']].apply(month_year, axis=1)
    return data_monthyear


def get_data_deposit_distrchannel(data_call):
    data_deposit_distrchannel = data_call.pivot_table(
        values=('is_canceled'),
        index=['deposit_type', 'distribution_channel'],
        aggfunc=('mean', 'count')
    ).reset_index()
    data_deposit_distrchannel.columns = ['deposit_type', 'distribution_channel', 'count', 'canceled_ratio']
    return data_deposit_distrchannel


def get_fig_1(data_call):
    fig_1 = px.bar(
        data_frame=get_data_hotel_children(data_call),
        x='sum_children',
        y='is_canceled',
        color='hotel',
        barmode='group'
    )
    fig_1.layout.yaxis1.tickformat = '.1%'
    fig_1.update_layout(title='Percent of canceled by the amount of children')
    return fig_1


def get_fig_2(data_call):
    fig_2 = px.bar(
        data_frame=get_data_hotel_children(data_call),
        x='sum_children',
        y='sum_days',
        color='hotel',
        barmode='group'
    )
    fig_2.update_layout(title='Average days in hotel by the amount of children')

    return fig_2


def get_fig_3(data_call):
    fig_3 = px.bar(
        data_frame=get_data_hotel_children(data_call),
        x='sum_children',
        y='lead_time',
        color='hotel',
        barmode='group'
    )
    fig_3.update_layout(title='Average days from booking to coming into the hotel by the amount of children')
    return fig_3


def get_fig_4(data_call):
    fig = px.bar(
        data_frame=get_data_season(data_call),
        x='arrival_date_month',
        y='sum_days',
        color='hotel',
        barmode='group'
    )
    fig.update_layout(title='Average days in hotel by arrival month',
                      xaxis={'categoryorder': 'array',
                             'categoryarray': ['Январь', 'Февраль', 'Март', 'Апрель', "Май", 'Июнь', 'Июль', "Август",
                                               'Сентябрь', 'Октябрь', "Ноябрь", 'Декабрь']})
    return fig


def get_fig_5(data_call):
    fig = px.bar(
        data_frame=get_data_season(data_call),
        x='arrival_date_month',
        y='adr',
        color='hotel',
        barmode='group'
    )
    fig.update_layout(title='ADR of hotel by arrival month',
                      xaxis={'categoryorder': 'array',
                             'categoryarray': ['Январь', 'Февраль', 'Март', 'Апрель', "Май", 'Июнь', 'Июль', "Август",
                                               'Сентябрь', 'Октябрь', "Ноябрь", 'Декабрь']})
    return fig


def get_fig_6(data_call):
    fig = px.line(data_frame=get_data_monthyear(data_call),
                  x='month_year',
                  y='adr',
                  color='hotel',
                  markers=True)
    fig.update_layout(title='ADR of hotel by month and year', xaxis_tickangle=-45)
    return fig


def get_fig_7(data_call):
    fig_7 = px.treemap(
        data_frame=get_data_deposit_distrchannel(data_call),
        path=[px.Constant('Total count'), 'deposit_type', 'distribution_channel'],
        values='count',  # чтобы каждый квадратик занимал столько, сколько имеет долю в общей прибыли
        color='canceled_ratio',
        color_continuous_scale='RdYlGn'
    )
    fig_7.update_layout(title='Canceled by deposit type and distribution channel')
    return fig_7

