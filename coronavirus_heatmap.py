#!/usr/bin/env python
# coding: utf-8

# Import modules
import pandas as pd
import plotly.express as px
import plotly
import requests

# Fetch case data from wikipedia
url = 'https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_the_United_States'

data = pd.read_html(requests.get(url).content)[1]
data.columns = ['Drop','State','Cases','Deaths','Recoveries','Remaining','Source']

# Fetch state abbreviations from wikipedia
url2 = 'https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations'
states = pd.read_html(requests.get(url2).content)[0]
states.columns = ['Region','Status','ISO','ANSI','ANSI2','USPS','USCG','GPO','AP','Other']
states = states.query('Status == "State"').reset_index(drop = True).filter(items = ['Region','USPS'])

# Filter and clean data
state_names = states['Region']

p_data = (data.query('State in @state_names')
            .reset_index(drop=True)
            .filter(items=['State','Cases','Deaths'])
            .merge(states, how = 'left', left_on = ['State'], right_on = ['Region'])
            .filter(items = ['USPS','Cases','Deaths']))

p_data['Cases'] = pd.to_numeric(p_data['Cases'])
p_data['Deaths'] = pd.to_numeric(p_data['Deaths'])

p_data = p_data.assign(Mortality_Rate = lambda x: x.Deaths/x.Cases*100)

p_data.columns = ['State','Cases','Deaths','Mortality Rate (%)']

# Plot and save cases map
df = p_data

fig = px.choropleth(df, locations= "State",
                    locationmode="USA-states",
                    color= "Cases",
                    scope="usa",
                    range_color=[p_data['Cases'].min(),p_data['Cases'].max()],
                    color_continuous_scale=px.colors.sequential.thermal)

fig.update_layout(title = 'Coronavirus Confirmed Cases in the US by State')

plotly.offline.plot(fig, filename = 'Coronavirus_Map.html', auto_open=False)

# Plot and save mortality rate map

fig = px.choropleth(df, locations= "State",
                    locationmode="USA-states",
                    color= "Mortality Rate (%)",
                    scope="usa",
                    range_color=[p_data['Mortality Rate (%)'].min(),p_data['Mortality Rate (%)'].max()],
                    color_continuous_scale=px.colors.sequential.thermal)

fig.update_layout(title = 'Coronavirus Mortality Rate (%) in the US by State')

plotly.offline.plot(fig, filename = 'Coronavirus_Mortality_Rate_Map.html', auto_open=False)