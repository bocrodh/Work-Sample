# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Title: Sample Script for Pre-Doc Applications                   " 
Author: Hiru Rodrigo                                            "  
Disclaimer: The script only uses publicaly available information" 
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" 
################################################################ Import relevant libraries #################################################3 
import pandas as pd
import requests 
from bs4 import BeautifulSoup 
import math as mt
import numpy as np 
import os as o

############################################################## Webscraping ##################################################################
"The webscraping section of my script goes to the Canada's central counterparty for exchange traded derivatives and webscrapes margin files for the year 2019. 

#Connect to the website and locate the margin files  
page = requests.get("https://www.cdcc.ca/miFiles_en") 
bSoup = BeautifulSoup(page.content, 'html.parser') 
link_list = bSoup.find_all('a') 

#Collect all margin files and store them in an object called mi_files
mi_files = []
for link in link_list: 
    if 'href' in link.attrs: 
         mi_files.append((str(link.attrs['href']) + "\n")) 

#Subset through the list of files on the website and select only those that are from the year 2019 and .csv 
mi_2019 = [line for line in mi_files if 'MI_2019' in line]   
mi_2019_csv = [line for line in mi_2019 if '.csv' in line]   
mi_2019_csv = [x[:-1] for x in mi_2019_csv]
mi_2019_csv_full = ['https://www.cdcc.ca'+x for x in mi_2019_csv] #The list of files is stored in an object called mi_2019_csv_full

#Open each file contained in mi_2019_csv_full and select the date and margin interval for the SXF product
for file in mi_2019_csv_full:  #Change for particular file name 
     if file.endswith('.csv'):
         df = pd.read_csv(file, header=None)
         df.columns = ["Symbol"]
         df = df[df['Symbol'].str.contains("SXF;MarginInterval")]
         df.dropna(axis='columns')
         date = file[37:45]
         df['Date'] = date
         df.to_csv("Desktop\\MI_"+date+".csv", index=False) #Drop each file into a folder  
         
############################################################## HVAR ######################################################################
"The HVAR section of my script uses a file called raw (which contains the data and settlement price of SXF) to compute the initial margin model (Historical Value-at-Risk)
"model used by Canada's central counterparty for exchange traded derivatives  

#Concatenating datasets  
raw = pd.DataFrame(pd.read_excel(r"R:\\mfa\\PSD\\TMX\\Data\\CDCC\\Adhoc_Analysis\\Stress Testing\\artificial_prices.xlsx"), header=0)
raw = raw[['Date','Settlement Price']]

#Calculating daily returns and 260 day rolling average for SXF product   
raw['Return'] = raw['Settlement Price'].pct_change()
raw['Historical Average Return'] = raw['Return'].rolling(260).mean()   
raw = raw[pd.notnull(raw['Date'])] #Drop empty roes 

def sigma_simulation(y,prct,w,sr): #The inputs of the margin model are the file that contain daily margins, value for lambda, weight factor, and stressed risk  
    
    dv = pd.read_csv(r"R:\mfa\PSD\TMX\Data\CDCC\Adhoc_Analysis\2022 Margin Procyclicality\NonEstimate_Plots\raw datasets\lambda_decay_vector.csv", header=0)
    for i in range(260, len(y)):         
        y.loc[i, '1-lambda_99'] = 1-0.99 
        y.loc[i, '1-lambda260_99'] = 1-(0.99**260) 
    
    for i in range(261, len(y)):  
        y.loc[i,'decay*(Return - Hist Avg)**2'] = sum(((y['Return'][i-260:i].apply(lambda x: x-y.loc[i, 'Historical Average Return']))**2)*np.array(dv['decay_99'].tolist())) 
        y.loc[i, 'Sigma'] = mt.sqrt((y.loc[i, 'decay*(Return - Hist Avg)**2']*y.loc[i, '1-lambda_99'])/y.loc[i, '1-lambda260_99']) 

    for i in range(261, len(y)):  
        y.loc[i,'MI_Computation'] = y.loc[i,'Sigma']*3*mt.sqrt(2)
        y.loc[i,'MI_Computation_Weighted'] = (1-w)*y.loc[i,'MI_Computation'] + w*sr  
    
    y = y[pd.notnull(raw['Sigma'])]
    
    return pd.DataFrame(y)


mi_series = sigma_simulation(raw, 0.99, 0,0) #In this case, raw is the margin file, 0.99 is the value of lam  
 
############################################################## Graphs #########################################################################
"The Graph section of my script plots what the margin values from the margin model look like for different different values of lambda and 
"the weight = 0.15 and stress risk = 7.5. It assumes that a file called mi_15_7 has already been generated. 

def lamda_plot(x,w,sr):
    
    fig, ax1 = plt.subplots(figsize=(30,12))
    
    a = x['Date']
    
    #line plot creationi
    ax1.plot(a, x['MI_NEW_998'], linewidth=4, label="λ = 99.8%") 
    ax1.plot(a, x['MI_NEW_995'], linewidth=4, label="λ = 99.5%") 
    ax1.plot(a, x['MI_NEW_99'], linewidth=4, label="λ = 99%") 
    ax1.plot(a, x['MI_NEW_985'], linewidth=4, label="λ = 98.5%") 
    ax1.plot(a, x['MI_NEW_98'], linewidth=4, label="λ = 98%") 
    ax1.plot(a, x['MI_NEW_97'], linewidth=4, label="λ = 97%") 
    ax1.plot(a, x['MI_NEW_95'], linewidth=4, label="λ = 95%") 
    ax1.axhline(sr, linestyle='--',lw=2, label = 'Stress Risk', color='tab:gray')
    ax1.set_ylim([0, 25])
    
    ax1.set_title(f"Weight = " + str(w) + " & Stress Risk = " + str(sr) ,fontweight="bold",fontsize=20, color='darkred') 
    ax1.set_ylabel("Margin Interval",fontweight="bold",fontsize=16)
    plt.xticks(a[0::10])
    plt.xticks(rotation=90)
    
    fig.tight_layout()
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes, fontsize = 'xx-large')
    plt.grid(fig)
    fig.show() 
    fig.savefig("Desktop\\lambda_plot_"+str(w)+"_"+ str(sr)+".png",bbox_inches='tight') 
    plt.close(fig) 
    x = x[['Date','MI_NEW_998','MI_NEW_995','MI_NEW_99','MI_NEW_985', 'MI_NEW_98','MI_NEW_97','MI_NEW_95']]
    x.to_csv('Desktop\\lambda_file_'+str(w)+"_"+ str(sr)+'.csv', index=False) 

lamda_plot(mi_15_7, 0.15, 7.5) #By change the values of weight and stress risk, we can conduct a sensitivity analysis. 

############################################################## Dashboard #########################################################################
"This section of code is a dashboard I made using World Bank remittance data" 
#Import libraries 
import pandas as pd 
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import plotly.express as px
import streamlit_authenticator as stauth 
import pickle
from pathlib import Path 

def main(): 
      
    #Create blank webpage 
    st.set_page_config( 
            page_icon=":money_with_wings:", 
            layout="wide", 
    ) 

    #Plots
    #Reading Main CB Dashboard tab from workbook 
    xls = (r'https://github.com/bocrodh/21eB6-WCN-Ao-v-JK-yRpRT0e-qp/blob/main/wb_remittance_data.xlsx?raw=true')

    cost = pd.read_excel(xls, 'Cost of sending $200', header=0)
    times = pd.read_excel(xls, '<1 Hour Options', header=0)
    provider = pd.read_excel(xls, 'Proportion of MT', header=0)
    banked = pd.read_excel(xls, 'Banked', header=0)
      
    st.header('Trends in XB Payment')
    st.subheader('Remittances')

    
    fig = px.line(cost, x="Year", y='%', color="Country", title="Remittance Fee as % of $200 <br><sup>Source: https://remittanceprices.worldbank.org/</sup>")
    fig.update_traces(mode="lines")
    fig.update_layout(hovermode="x unified") 
    fig.update_xaxes(tickangle= -90, nticks=4)
    fig.update_traces(patch={"line": {"color": "purple", "width": 6}}, selector={"legendgroup": "Canada"})
    fig.update_traces(patch={"line": {"color": "MidnightBlue", "width": 6, "dash": 'dot'}}, selector={"legendgroup": "G8"}) 
    fig.show() 
    #st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(times, x="Year", y='Number of Service Providers', color="Country", title="Access to <1 Hour Remittance Services (by corridor)<br><sup>Source: https://remittanceprices.worldbank.org/</sup>")
    fig2.update_traces(mode="lines")
    fig2.update_layout(hovermode="x unified") 
    fig2.update_xaxes(tickangle= -90, nticks=4)
    fig2.show() 
    #st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(banked, x='Year', y='% Banked', color="Country", title="% of Banked Population <br><sup>Source: https://databank.worldbank.org/source/global-financial-inclusion/</sup>")
    fig3.update_traces(mode="lines")
    fig3.update_layout(hovermode="x unified") 
    fig3.update_xaxes(tickangle= -90)
    fig3.update_traces(patch={"line": {"color": "purple", "width": 6}}, selector={"legendgroup": "Canada"})
    fig3.update_traces(patch={"line": {"color": "MidnightBlue", "width": 6, "dash": 'dot'}}, selector={"legendgroup": "G8"}) 
    fig3.show() 
    
    fig4 = px.line(provider, x='Year', y='%', color="Country", title="% of Remittances Completed Money Transfer Services (by corridor) <br><sup>Source: https://remittanceprices.worldbank.org/</sup>")
    fig4.update_traces(mode="lines")
    fig4.update_layout(hovermode="x unified") 
    fig4.update_xaxes(tickangle= -90, nticks=4)
    fig4.show() 
    
    plot1, plot2 = st.columns(2,gap='small')
    plot1.plotly_chart(fig, use_container_width=True)    
    plot2.plotly_chart(fig2, use_container_width=True)    
    
    plot3, plot4 = st.columns(2,gap='small')
    plot3.plotly_chart(fig3, use_container_width=True)    
    plot4.plotly_chart(fig4, use_container_width=True)
    
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    main()
  