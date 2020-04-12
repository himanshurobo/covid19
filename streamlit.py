import streamlit as st
import pandas as pd
from pandas.io.json import json_normalize
import requests


import plotly_express as px 
import folium 
from folium.plugins import HeatMap
import seaborn as sns

# Get the data from url and request it as json file
# @st.cache(persist=True, suppress_st_warning=True)
def getDistrictData(URL='https://api.covid19india.org/v2/state_district_wise.json'):
    response = requests.get(URL)

    if response.content : 
        print ('ok info Historical Stock')

    data = response.json()                

    return json_normalize(data,'districtData',['state'])



# @st.cache(persist=True, suppress_st_warning=True)
def display_map(df):
    st.subheader(" Displaying Point based map")
    px.set_mapbox_access_token(
        "pk.eyJ1Ijoic2hha2Fzb20iLCJhIjoiY2plMWg1NGFpMXZ5NjJxbjhlM2ttN3AwbiJ9.RtGYHmreKiyBfHuElgYq_w")
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", color="district",size="confirmed",
    color_continuous_scale=px.colors.cyclical.IceFire, zoom=3,width=900,height=900)
    return fig


def heat_map(df):
    locs = zip(df.lon, df.lat)
    m = folium.Map([22.3511148, 78.6677428], tiles='stamentoner', zoom_start=5)
    HeatMap(locs).add_to(m)
    return st.markdown(m._repr_html_(), unsafe_allow_html=True)


def getReverseGeo(cityName, stateName):
    try:
        URL = 'https://nominatim.openstreetmap.org/search?q='+cityName+'&format=json&accept-language=en'
        response = requests.get(URL)
        # if response.content : 
        #     print ('ok info Historical Stock')

        data = response.json()
        print(cityName,stateName)
        # d = [ x for x in data if x['type'] == 'city'][0]
        d = data[0]

        return {'district' : cityName, 'state' : stateName,'lat' : d['lat'],'lon' : d['lon'],'city_name' : d['display_name']}
    except Exception as e:
        return {'district' : cityName,'state' : stateName,'lat' : '6.402589949999999','lon' : '43.398382018489485','city_name' : 'Unknown'}




def getDistrictDataFinal(df):
    
    # print(df.head())
    # df_loc = json_normalize(df['district'].apply(lambda x: getReverseGeo(x)))

    df_loc = json_normalize(df.apply(lambda x: getReverseGeo(stateName = x['state'], cityName = x['district']), axis=1))

    # j = json_normalize(getReverseGeo('Thrissur'))
    # print(getReverseGeo('Thrissur'))
    # print(df_loc.head())
    df_loc.to_csv('./latlong_new.csv',index=False)

    # df_load_loc = pd.read_csv('./latlong_new.csv')
    print(df_load_loc.head())
    # st.map(df_load_loc.head())

# @st.cache(persist=True, suppress_st_warning=True)
def getMergeData():
    df_district_data = getDistrictData()
    df_load_loc = pd.read_csv('./latlong_new.csv')
    df_final = pd.merge(df_district_data, df_load_loc, on=['district','state'])

    return df_final

def main():

    df_final = getMergeData()
    st.header("COVID19 in INDIA")
    st.subheader("City Wise Analysis..!!!")


    if st.checkbox("show first rows of the data & shape of the data"):
        st.write(df_final.head())
        st.write(df_final.shape)
    # print(df_final.head())

    st.plotly_chart(display_map(df_final))

    # dataviz_choice = st.sidebar.selectbox("Choose Data Visualization",
    #                                       ["None", "Heatmap", "Countplot"])
    # if dataviz_choice == "Countplot":
    #     st.subheader("Countplot")
    #     sns.countplot("state", data=df_final)
    #     st.pyplot()

    # elif dataviz_choice == "Heatmap":
    #     st.subheader("Heat Map")
    #     heat_map(df_final)



if __name__ == "__main__":
    main()
    pass











