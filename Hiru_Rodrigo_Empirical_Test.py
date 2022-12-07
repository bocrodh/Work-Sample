# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""
Date: December 8, 2022                  " 
Author: Hiru Rodrigo                    " 
Subject: Empirical Test                 "
"""""""""""""""""""""""""""""""""""""""""
#################################################################### Code outline #########################################################################
"Section 1: Library imports 
"Section 2: Data cleaning and verifications
"Section 3: Data manipulation 
"Section 4: Dashboard 

###################################################################### Library imports ####################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

############################################################# Data cleaning and verifications ##############################################################

#Read in data
df = pd.read_csv("", header=0)

#Sort data
df.sort_values("date", inplace=True)

#Delete duplicate rows and only keep first instance
df = df.drop_duplicates(keep='first')

#Subset relevant fields for analysis"
df = df["AAA","BBB"]

#Format date object 
df['date'] = pd.to_datetime(df["date"].dt.strftime('%Y-%m'))

###################################################################### Data manipulation ##################################################################



###################################################################### Dashboard ############################################################################
