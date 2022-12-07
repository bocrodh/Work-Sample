# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""
Date: December 8, 2022                  " 
Author: Hiru Rodrigo                    " 
Subject: Empirical Test                 "
"""""""""""""""""""""""""""""""""""""""""
#################################################################### Code outline #########################################################################
#Section 1: Library imports 
#Section 2: Data cleaning and verifications
#Section 3: Data manipulation/Plots 
#Section 4: Dashboard 

###################################################################### Library imports ####################################################################
import pandas as pd 
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import plotly.express as px
import pickle
from pathlib import Path 
############################################################# Data cleaning and verifications ##############################################################
#Read in data
#url = (r'https://github.com/bocrodh/21eB6-WCN-Ao-v-JK-yRpRT0e-qp/blob/main/CB%20BB%20Dashboard%20for%20Canada%20(September%202022).csv?raw=true') 
#df = pd.read_csv(url, header=0)

#Sort data
#df.sort_values("date", inplace=True)

#Delete duplicate rows and only keep first instance
#df = df.drop_duplicates(keep='first')

#Subset relevant fields for analysis"
#df = df["AAA","BBB"]

#Format date object 
#df['date'] = pd.to_datetime(df["date"].dt.strftime('%Y-%m'))

xls = (r'https://github.com/bocrodh/21eB6-WCN-Ao-v-JK-yRpRT0e-qp/blob/main/wb_remittance_data.xlsx?raw=true')

cost = pd.read_excel(xls, 'Cost of sending $200', header=0)
times = pd.read_excel(xls, '<1 Hour Options', header=0)
provider = pd.read_excel(xls, 'Proportion of MT', header=0)
banked = pd.read_excel(xls, 'Banked', header=0)


###################################################################### Data manipulation/Plots ###############################################################

#Question 1 Plot: 
fig = px.line(cost, x="Year", y='%', color="Country", title="Remittance Fee as % of $200")
fig.update_traces(mode="lines")
fig.update_layout(hovermode="x unified") 
fig.update_xaxes(tickangle= -90, nticks=4)
fig.update_traces(patch={"line": {"color": "purple", "width": 6}}, selector={"legendgroup": "Canada"})
fig.update_traces(patch={"line": {"color": "MidnightBlue", "width": 6, "dash": 'dot'}}, selector={"legendgroup": "G8"}) 
fig.show() 

#Question 2 Plot:  
fig2 = px.line(times, x="Year", y='Number of Service Providers', color="Country", title="Access to <1 Hour Remittance Services (by corridor)")
fig2.update_traces(mode="lines")
fig2.update_layout(hovermode="x unified") 
fig2.update_xaxes(tickangle= -90, nticks=4)
fig2.show() 

#Question 3 Plot:  
fig3 = px.line(banked, x='Year', y='% Banked', color="Country", title="% of Banked Population")
fig3.update_traces(mode="lines")
fig3.update_layout(hovermode="x unified") 
fig3.update_xaxes(tickangle= -90)
fig3.update_traces(patch={"line": {"color": "purple", "width": 6}}, selector={"legendgroup": "Canada"})
fig3.update_traces(patch={"line": {"color": "MidnightBlue", "width": 6, "dash": 'dot'}}, selector={"legendgroup": "G8"}) 
fig3.show() 

#Question 4 Plot:  
fig4 = px.line(provider, x='Year', y='%', color="Country", title="% of Remittances Completed Money Transfer Services (by corridor)")
fig4.update_traces(mode="lines")
fig4.update_layout(hovermode="x unified") 
fig4.update_xaxes(tickangle= -90, nticks=4)
fig4.show()  

###################################################################### Dashboard ############################################################################
def main(): 
      
    #Create blank webpage 
    st.set_page_config(page_icon=":money_with_wings:", layout="wide",) 

    #Customizing sidebar filters 
    st.sidebar.header("Filter Criteria:") 
    #bb_number = st.sidebar.multiselect("BB Number:", options=df["BB Number"].unique(), default=df['BB Number'].unique(),)  
    #df_selection = df.query("`BB Number` ==@bb_number") 
    
    #Displaying Dataframe 
    #st.header('Table 1')
    #filtered = st.multiselect("Filter fields", options=df_selection.columns, default=['BB Number'])
 
    #Editing DataFrame Appearance  
    #fig = go.Figure(data=[go.Table(
    #header=dict(values=list(filtered),
    #  fill_color='#575a5e',
    #  align='center', 
    #  font=dict(color='white', size=15)),
    #cells=dict(values=[df_selection[col] for col in filtered],
    # fill_color='#ffffff',
    # align='center', 
    # font=dict(color='black', size=13)))])
    #fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=450)
    #st.plotly_chart(fig, use_container_width=True)

    st.markdown(
    """
    <style>
    span[data-baseweb="tag"] {background-color: #7E7F7A !important;}  
    span[data-baseweb="tag"]>span{font-size: 13px}  
    </style>
    """,
    unsafe_allow_html=True,) 

    #Displaying Plots      
    st.header('Plots')
    
    plot1, plot2 = st.columns(2,gap='small')
    plot1.plotly_chart(fig, use_container_width=True)    
    plot2.plotly_chart(fig2, use_container_width=True)    
    
    plot3, plot4 = st.columns(2,gap='small')
    plot3.plotly_chart(fig3, use_container_width=True)    
    plot4.plotly_chart(fig4, use_container_width=True)
    
    main() 
    
#END 
