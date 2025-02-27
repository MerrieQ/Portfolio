# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 11:30:25 2024

@author: merli
"""

#Per maand alle meldingen samen doen, minder te berekenen, als het goed is gaat het smoother dan.

import pandas as pd
from geopy.geocoders import Nominatim
import time
import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'

##Datasets
#Reading the datasets
Wolfwaarnemingen = "C:/Users/merli/Documents/Wolfwaarnemingen.csv"
df = pd.read_csv(Wolfwaarnemingen)

Wolvenschade = "C:/Users/merli/Documents/Wolfschade.csv"
df2 = pd.read_csv(Wolvenschade)

#Only instances where the wolf was seen, not just footprints or other marks
Wolf = df[df["Type waarneming"] == "Wolf gezien"]

#Noord, Midden and zuid veluwe, replaced with "veluwe" so the data can be read while geocoding
df["Leefgebied of gemeente"] = df["Leefgebied of gemeente"].replace({
    "Noord- en Midden-Veluwe": "Veluwe",
    "Zuid-Veluwe": "Veluwe",
    "Zuidwest-Veluwe": "Veluwe"
    })
Wolf["Leefgebied of gemeente"] = df["Leefgebied of gemeente"].replace({
    "Noord- en Midden-Veluwe": "Veluwe",
    "Zuid-Veluwe": "Veluwe",
    "Zuidwest-Veluwe": "Veluwe"
    })


##GEOCODING
#Initialise the geolocator
geolocator = Nominatim(user_agent="geoapiExcercises")

#make empty cache
cache = {}

#Function to get the coöridinates
def get_coordinates(place):
    if place in cache:
        return cache[place]
    try:
        location = geolocator.geocode(place)
        if location:
            cache[place] = (location.latitude, location.longitude)
            return cache[place]
        else:
            cache[place] = (None, None)
            return None, None
    except:
        return None, None
            
#Add new columns for lat en long 
df["latitude"], df["longitude"] = zip(*df["Leefgebied of gemeente"].apply(get_coordinates))

##WOLFAANVALLEN GEOCODING
#make empty cache
cache2 = {}

#Functie om cooridinaten te krijgen
def get_coordinates(place):
    if place in cache2:
        return cache2[place]
    try:
        location = geolocator.geocode(place)
        if location:
            cache2[place] = (location.latitude, location.longitude)
            return cache2[place]
        else:
            cache2[place] = (None, None)
            return None, None
    except:
        return None, None
            
#Voeg nieuwe klommen voor lat en long toe
df2["latitude"], df2["longitude"] = zip(*df2["Locatie aanval"].apply(get_coordinates))


#print(df.head())

#time
time.sleep(1)

  # Sla de geocoded DataFrame op in een nieuw CSV-bestand
df.to_csv("Wolfwaarnemingen_geocoded.csv", index=False)


# Veronderstel dat 'Datum melding' al in datetime-formaat is
# Zo niet, zorg dan dat je 'Datum melding' naar datetime omzet
df2['Datum melding'] = pd.to_datetime(df2['Datum melding'], format='%d-%m-%y')

# Maak een nieuwe kolom die de maand en jaar bevat
df2['year_month'] = df2['Datum melding'].dt.to_period('M')  # Formatteer de datum naar jaar-maand

# Groepeer de data per locatie en per maand, en tel het aantal slachtoffers op per maand
df2_grouped = df2.groupby(['year_month', 'latitude', 'longitude'], as_index=False).agg({
    'Totaal aantal dode slachtoffers': 'sum'
}).rename(columns={'Totaal aantal dode slachtoffers': 'slachtoffers_per_maand'})

# Bereken het cumulatieve aantal slachtoffers per locatie per maand
df2_grouped['cumulative_slachtoffers'] = df2_grouped.groupby(['latitude', 'longitude'])['slachtoffers_per_maand'].cumsum()

# Maak een jaar-maandkolom aan voor de animatie
df2_grouped['animation_month'] = df2_grouped['year_month'].astype(str)

# Vervang NaN waarden door 0, omdat er mogelijk locaties zijn met nog geen incidenten in het begin
df2['cumulative_slachtoffers'].fillna(0, inplace=True)

# Maak een nieuwe DataFrame waarin elk jaar alle voorgaande jaren bevat
cumulative_df = pd.DataFrame()
for year in df2['Datum melding'].unique():
    # Selecteer de data tot en met het huidige jaar
    cumulative_data = df2[df2['Datum melding'] <= year].copy()
    # Zet het jaar om naar het huidige jaar voor animatie
    cumulative_data['animation_year'] = year
    # Voeg toe aan de cumulatieve DataFrame
    cumulative_df = pd.concat([cumulative_df, cumulative_data])

# Controleer opnieuw op NaN waarden en vul ze indien nodig op
cumulative_df['cumulative_slachtoffers'].fillna(0, inplace=True)

# Bereken het maximum aantal cumulatieve slachtoffers in de gehele dataset
max_slachtoffers = cumulative_df['cumulative_slachtoffers'].max()

##Interactieve Map df

print("Getting Data")

fig = px.scatter_mapbox(df,
                        lon = df["longitude"],
                        lat = df["latitude"],
                        zoom = 3, 
                        width = 1200,
                        height = 900,
                        title = "De wolf in nederland"
                        )
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":50,"l":0,"b":10})
fig.show()
print("plot complete")

##Interactieve Map 2 Slachtoffers

print("Getting Data")

# Maak een nieuwe interactieve kaart met maandelijkse data
fig = px.scatter_mapbox(
    df2_grouped,
    lon='longitude',
    lat='latitude',
    zoom=7,  # Zoomniveau zodat Nederland goed in beeld is
    size='cumulative_slachtoffers',  # Gebruik de cumulatieve slachtoffers voor de grootte van de stippen
    color='cumulative_slachtoffers',  # Kleur op basis van het aantal slachtoffers
    width=1200,
    height=900,
    title="Vermoorde dieren per maand per stad",
    animation_frame='animation_month',  # Gebruik de maand voor animatie
    color_continuous_scale=px.colors.cyclical.IceFire,  # Optioneel: kleurenschema
    range_color=[0, df2_grouped['cumulative_slachtoffers'].max()]  # Zet het kleurenschema vast
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":50,"l":0,"b":10})

# Animatie-instellingen aanpassen
fig.update_layout(
    updatemenus=[{
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 200, "redraw": True},
                                "fromcurrent": True, "transition": {"duration": 500, "easing": "linear"}}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": False,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }]
)

# Zet de coloraxis vast om knipperen te voorkomen
fig.update_layout(
    coloraxis=dict(
        cmin=0,
        cmax=max_slachtoffers,
        colorbar=dict(title="Cumulatieve Slachtoffers"),
        
        )
    )

# Stel de mapbox layout vast om onverwachte zoom te voorkomen
fig.update_layout(mapbox=dict(
    style="open-street-map",
    zoom=7,  # Vastzetten van de zoom
    center=dict(lat=52.2, lon=5.3)  # Optioneel: centrale positie (Nederland)
))

# Update marges en layout om onnodige layoutverschuivingen te minimaliseren
fig.update_layout(margin={"r":0, "t":50, "l":0, "b":10})

fig.show()
print("plot complete")

