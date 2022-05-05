"""
Uber Data Analysis
Author: Angie Grabmeier
Date: 5/5/2022
Description: Final Project
Packages Not Used in Class:
plotly_express--> used to easily make visually appealing charts
geopy--> used to calculate the distance traveled in miles from the longitude and latitudes given
folium--> used to make the map and the markers

"""
import random
import folium
import numpy as np
import pandas as pd
import streamlit as st
import streamlit_folium
import plotly_express as px
from geopy import distance
from PIL import Image

st.set_page_config(layout= "centered")


def get_data(filename):
    global rides_data
    global colors_list

    colors_list = [
    'red',
    'blue',
    'gray',
    'darkred',
    'lightred',
    'orange',
    'beige',
    'green',
    'darkgreen',
    'lightgreen',
    'darkblue',
    'lightblue',
    'purple',
    'darkpurple',
    'pink',
    'cadetblue',
    'lightgray',
    'black'
]

    colors_list.pop(2)

    rides_data = pd.read_csv(filename)
    return rides_data

def main():
    global feed_data
    global colors_list
    feed_data = get_data("uber_8000_sample.csv")
    options = st.sidebar.selectbox("Select Page to Explore:", ["Home Page","Rides Map", "Charts", "Rides Sort"])
    if options == "Home Page":
        home_page()
    if options == "Rides Map":
        rides_map(feed_data,colors_list)
    if options == "Charts":
        charts(feed_data)
    if options == "Rides Sort":
        sort_chart(feed_data)

st.markdown("<h1 style = 'text-align; center; color; green;'><u>Uber Rides Analysis</u></h1>",unsafe_allow_html = True)

def home_page():
    st.subheader("Home Page")
    img = Image.open("UberPhoto.png")
    picture = st.image(img, width=300)
    st.write("Welcome! This page was created to give viewers a brief analysis of a dataset containing data concerning Uber rides in New York. You may use the drop down menu on the side bar to look at a map of various Uber rides, charts of the Uber data, as well as sorting the data whatever way you please. Enjoy!")

def rides_map(dataframe,color_choices):
    st.subheader("Rides Map")
    map = folium.Map(location=[40.779352, -73.968431], name = "Map of Rides", zoom_start= 12, attr= "New York Map")
    slider = st.slider("Select Amount of Rides to Display:",25,8000,step = 25)
    feed_data = dataframe.head(slider)

    for _, rd in feed_data.iterrows():
        color_choice = random.choice(color_choices)
        folium.Marker(location=[rd["pickup_latitude"], rd["pickup_longitude"]], popup = rd["fare_amount"],icon=folium.Icon(color=color_choice)).add_to(map)
        folium.Marker(location=[rd["dropoff_latitude"], rd["dropoff_longitude"]], popup = rd["fare_amount"],icon=folium.Icon(color=color_choice)).add_to(map)
    streamlit_folium.folium_static(map, width = 800, height = 400)

def charts(dataframe):
    df = pd.DataFrame(dataframe)
    df = df.loc[df["passenger_count" ]>0]
    fig = px.pie(df, values= 'passenger_count', names = 'passenger_count', color_discrete_sequence=px.colors.sequential.Greens, title = "Uber Ride Passenger Count")
    st.write(fig)

    lst_rideid = []
    lst_time = []

    lst_distance=[]
    lst_fare = []


    for _,rd in feed_data.iterrows():
        time = rd["pickup_datetime"]
        rideid = rd["Ride_ID"]
        ridefare= rd["fare_amount"]
        lst_fare.append(ridefare)
        trip_beg = tuple((rd["pickup_latitude"],rd["pickup_longitude"]))
        trip_end = tuple((rd["dropoff_latitude"],rd["dropoff_longitude"]))
        trip_distance = distance.distance(trip_beg,trip_end).miles
        lst_distance.append(trip_distance)


        strip_text = int(time[11:13])
        lst_time.append(strip_text)
        lst_rideid.append(rideid)

    dict = {
        "Ride_ID":lst_rideid,
        "Time": lst_time,
    }

    dict2 = {
        "Ride Fare":lst_fare,
        "Ride Distance":lst_distance,
    }
    df = pd.DataFrame(dict,index =np.array(np.arange(1, len(feed_data)+1)) )
    reg_df = pd.DataFrame(dict2)
    reg_df2 = reg_df.loc[reg_df["Ride Distance" ] > 0.5]
    reg_df2 = reg_df2.loc[reg_df2["Ride Fare" ]< 60]
    reg_df2 = reg_df2.loc[reg_df2["Ride Distance" ] < 20]

    scat_plot = px.scatter(x=reg_df2["Ride Distance"],y=reg_df2["Ride Fare"],color_discrete_sequence =['green']*len(df),title = "Fare vs Distance", trendline="ols",trendline_color_override="white",range_y=[0,100], labels={
        "x":"Ride Distance (Miles)","y":"Ride Fare ($)", })

    time_freq = df.value_counts(subset="Time")

    fig = px.bar(time_freq,color_discrete_sequence =['green']*len(df),title="Ride Frequency By Time of Day")
    st.write(fig)
    st.write(scat_plot)
    
    st.write("Regression Equation: y = 3.66x + 3.58")

def sort_chart(dataframe):
    st.subheader("Rides Sort")
    sort_choice = st.selectbox("Sort by Criteria:", ["fare_amount", "passenger_count", "key"])
    col_list = list(feed_data.columns)
    col_view = st.multiselect("Select Data Fields", col_list)
    asc_dsc = st.selectbox("Ascending or Descending Order",["Descending", "Ascending"])
    slider = st.slider("Select Amount of Rides to Display:", 5,500, value=10, step=5)
    if asc_dsc== "Ascending":
        asc_dsc = True
    else:
        asc_dsc = False
    print_sort = feed_data.sort_values(by=[sort_choice], axis=0, ascending= asc_dsc)
    print_sort.index = np.arange(1, len(feed_data)+1)
    st.write(print_sort[col_view].head(slider))



if __name__ == "__main__":
    main()
