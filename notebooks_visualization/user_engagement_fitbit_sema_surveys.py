# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# Round 1: 
# Start: 24/05/2021
# End: 26/07/2021
#
# Round 2:
# Start: 15/11/2021
# End: 17/01/2022

# %% [markdown]
# # User Engagement

# %%
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import json
from bson import ObjectId
from pprint import pprint
import streamlit as st
import seaborn as sns
import pickle
import ast

# %%
#sns.set_context("paper", rc={"font.size":20,"axes.titlesize":20,"axes.labelsize":20})  
#sns.set(font_scale=1.3)
#plt.rcParams['xtick.major.size'] = 4
#plt.rcParams['xtick.major.width'] = 4
#plt.rcParams['xtick.bottom'] = True
#plt.rcParams['ytick.left'] = True
#sns.set_style('ticks')
sns.set_palette(palette='Dark2')

# %%
with open('../credentials.json') as f:
    data = json.load(f)
    username = data['username']
    password = data['password']

# %%
client = MongoClient('mongodb://%s:%s@127.0.0.1' % (username, password))
db = client.raisv2

# %% [markdown]
# # SEMA
#
# # 1) Context and Mood Survey

# %%
collection = db.sema
df = pd.DataFrame(list(collection.find()))

# %%
# Deleting the no-responses and nones
df=pd.DataFrame(list(collection.find( { '$and': [ {"data.MOOD": { "$ne": "<no-response>" }},{"data.MOOD": { "$ne": None }}, {"data.PLACE": { "$ne": "<no-response>" }},{"data.PLACE": { "$ne": None }} ] } )))

# %%
df=df[['user_id']].join(pd.DataFrame(df['data'].tolist(), index=df.index).add_prefix('data.'))

# %%
df['Dates'] = pd.to_datetime(df['data.CREATED_TS']).dt.date
df['Time'] = pd.to_datetime(df['data.CREATED_TS']).dt.time
users=df['user_id']
days=df['Dates']
place=df['data.PLACE']
mood=df['data.MOOD']
df = pd.concat([users, days, place, mood],axis=1)
df = df.sort_values(by='Dates', ascending=True)
df['Dates'] = pd.to_datetime(df['Dates'].astype("str"), format='%Y-%m-%d')

# %%
df2 = df.groupby('Dates')['user_id'].nunique()
df2 =pd.DataFrame(df2)
df2 = df2.rename(columns={'user_id': 'Number of participants'})

# %%
df2.reset_index(inplace=True)
# Separating the two rounds
df2['Dates'] = pd.to_datetime(df2['Dates']) 
round1 = (df2['Dates'] >= "2021-05-24") & (df2['Dates'] <= "2021-07-26")
round1=df2.loc[round1]

df2['Dates'] = pd.to_datetime(df2['Dates']) 
round2 = (df2['Dates'] >= "2021-11-15") & (df2['Dates'] <= "2022-01-17")
round2=df2.loc[round2]

# %% [markdown]
# # SEMA
#
# # 2) Step Goals Survey

# %%
collection = db.sema
step_goal = pd.DataFrame(list(collection.find()))

# %%
# Deleting the no-responses and nones
step_goal=pd.DataFrame(list(collection.find( { '$and': [{"data.STEPS": { "$ne": "<no-response>" }},{"data.STEPS": { "$ne": None }} ] } )))

# %%
step_goal=step_goal[['user_id']].join(pd.DataFrame(step_goal['data'].tolist(), index=step_goal.index).add_prefix('data.'))

# %%
step_goal['Dates'] = pd.to_datetime(step_goal['data.CREATED_TS']).dt.date
step_goal['Time'] = pd.to_datetime(step_goal['data.CREATED_TS']).dt.time
users=step_goal['user_id']
days=step_goal['Dates']
steps=step_goal['data.STEPS']
step_goal = pd.concat([users, days, steps],axis=1)
step_goal = step_goal.sort_values(by='Dates', ascending=True)
step_goal['Dates'] = pd.to_datetime(step_goal['Dates'].astype("str"), format='%Y-%m-%d')
step_goal.head()

# %%
step_goal = step_goal.groupby('Dates')['user_id'].nunique()
step_goal =pd.DataFrame(step_goal)
step_goal = step_goal.rename(columns={'user_id': 'Number of participants'})
step_goal.head()

# %%
step_goal.reset_index(inplace=True)
step_goal['Dates'] = pd.to_datetime(step_goal['Dates']) 
step_goal_round1 = (step_goal['Dates'] >= "2021-05-24") & (step_goal['Dates'] <= "2021-07-26")
step_goal_round1=step_goal.loc[step_goal_round1]


step_goal['Dates'] = pd.to_datetime(step_goal['Dates']) 
step_goal_round2 = (step_goal['Dates'] >= "2021-11-15") & (step_goal['Dates'] <= "2022-01-17")
step_goal_round2=step_goal.loc[step_goal_round2]

# %% [markdown]
# # Fitbit synced data (wear-days)

# %%
# Loading the data of daily user steps

infile = open('../data/users_steps_daily','rb')
steps_daily = pickle.load(infile)
infile.close()

steps_daily.head() 

# %%
# deleting the <500 values of steps
steps_daily = steps_daily[steps_daily.steps >= 500] # actual wear-days

# %%
steps_daily = steps_daily.sort_values(by='date', ascending=True)
steps_daily.head()

# %%
dict = {'date': 'Dates','id':'user_id'}
 
steps_daily.rename(columns=dict,inplace=True)
steps_daily

# %%
steps_daily.reset_index(inplace=True)
steps_daily= steps_daily.groupby('Dates')['user_id'].nunique()
steps_daily =pd.DataFrame(steps_daily)
steps_daily = steps_daily.rename(columns={'user_id': 'Number of participants'})
steps_daily

# %%
#Separating the two Rounds
steps_daily.reset_index(inplace=True)
steps_daily['Dates'] = pd.to_datetime(steps_daily['Dates']) 
steps_daily_round1 = (steps_daily['Dates'] >= "2021-05-24") & (steps_daily['Dates'] <= "2021-07-26")
steps_daily_round1=steps_daily.loc[steps_daily_round1]


steps_daily['Dates'] = pd.to_datetime(steps_daily['Dates']) 
steps_daily_round2 = (steps_daily['Dates'] >= "2021-11-24") & (steps_daily['Dates'] <= "2022-01-17")
steps_daily_round2=steps_daily.loc[steps_daily_round2]

# %% [markdown]
# # Surveys completed over time

# %%
collection = db.surveys
surveys = pd.DataFrame(list(collection.find()))
surveys.head()

# %%
surveys=surveys[['user_id']].join(pd.DataFrame(surveys['data'].tolist(), index=surveys.index).add_prefix('data.'))

# %%
surveys['Dates'] = pd.to_datetime(surveys['data.datestamp']).dt.date
surveys['Time'] = pd.to_datetime(surveys['data.datestamp']).dt.time
users=surveys['user_id']
days=surveys['Dates']
surveys = pd.concat([users, days],axis=1)
surveys = surveys.sort_values(by='Dates', ascending=True)
surveys['Dates'] = pd.to_datetime(surveys['Dates'].astype("str"), format='%Y-%m-%d')
surveys

# %%
surveys= surveys.groupby('Dates')['user_id'].nunique()
surveys =pd.DataFrame(surveys)
surveys = surveys.rename(columns={'user_id': 'Number of participants'})
surveys

# %%
#Separating the two rounds
surveys.reset_index(inplace=True)
surveys['Dates'] = pd.to_datetime(surveys['Dates']) 
surveys_round1 = (surveys['Dates'] >= "2021-05-24") & (surveys['Dates'] <= "2021-07-26")
surveys_round1=surveys.loc[surveys_round1]


surveys['Dates'] = pd.to_datetime(surveys['Dates']) 
surveys_round2 = (surveys['Dates'] >= "2021-11-15") & (surveys['Dates'] <= "2022-01-17")
surveys_round2=surveys.loc[surveys_round2]

# %%
file = open(r'../data\round1_fitbit','rb')
df1 = pickle.load(file)
file.close()
df1

# %%
file = open(r'../data\round2_fitbit','rb')
df2 = pickle.load(file)
file.close()
df2

# %%
fig, ax = plt.subplots(figsize = (11, 7))
sns.set_palette(palette='Dark2')
ax = sns.lineplot(data=step_goal_round1, x="Dates", y="Number of participants", label='Step Goal Semas')
#ax = sns.scatterplot(data=step_goal_round1, x="Dates", y="Number of participants")
ax = sns.lineplot(data=round1, x="Dates", y="Number of participants", ax=ax, label='Context/Mood Semas')
#ax = sns.scatterplot(data=round1, x="Dates", y="Number of participants")
ax = sns.lineplot(data=df1, x="Dates", y="NumberOfDistictUsers", ax=ax, label='Synced fitbit data', ci=None)
#ax = sns.scatterplot(data=df1, x="Dates", y="NumberOfDistictUsers")
#ax = sns.lineplot(data=steps_daily_round1, x="Dates", y="Number of participants", ax=ax, label='Synced fitbit data')
#ax = sns.scatterplot(data=steps_daily_round1, x="Dates", y="Number of participants")
ax = sns.lineplot(data=surveys_round1, x="Dates", y="Number of participants", ax=ax, label='Surveys data')
#ax = sns.scatterplot(data=surveys_round1, x="Dates", y="Number of participants")
#ax = step_goal_round1.plot(x ='Dates', y='Number of participants', kind = 'line', color='red', style='-o', label='Step Goal Sema Surveys')
#ax = round1.plot(x ='Dates', y='Number of participants', kind = 'line', color='black', style='-o', ax=ax, label='Context and Mood Sema Surveys')
#ax = steps_daily_round1.plot(x ='Dates', y='Number of participants', kind = 'line', color='blue', style='-o', ax=ax, label='Synced fitbit data') 
#ax = surveys_round1.plot(x = 'Dates', y='Number of participants', kind='line',color='green',style='-o',ax=ax,label='Surveys data')
plt.xlabel('Date',fontsize=35)
plt.ylabel('Number of participants',fontsize=35)
plt.title('User engagement Round 1',fontsize=35)
#plt.legend(loc='lower left', bbox_to_anchor=(0.6, 0.68))
#plt.legend(fontsize=10)
plt.legend(ncol=2, loc="upper right",fontsize=20)
plt.xticks(rotation = 55)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.ylim(0, 45)
plt.show()

# %%
fig, ax = plt.subplots(figsize = (11, 7))
sns.set_palette(palette='Dark2')
ax = sns.lineplot(data=step_goal_round2, x="Dates", y="Number of participants", label='Step Goal Semas')
#ax = sns.scatterplot(data=step_goal_round2, x="Dates", y="Number of participants")
ax = sns.lineplot(data=round2, x="Dates", y="Number of participants", ax=ax, label='Context/Mood Semas')
#ax = sns.scatterplot(data=round2, x="Dates", y="Number of participants")
ax = sns.lineplot(data=df2, x="Dates", y="NumberOfDistictUsers", ax=ax, label='Synced fitbit data', ci=None)
#ax = sns.scatterplot(data=df2, x="Dates", y="NumberOfDistictUsers")
#ax = sns.lineplot(data=steps_daily_round2, x="Dates", y="Number of participants", ax=ax, label='Synced fitbit data')
#ax = sns.scatterplot(data=steps_daily_round2, x="Dates", y="Number of participants")
ax = sns.lineplot(data=surveys_round2, x="Dates", y="Number of participants", ax=ax, label='Surveys data')
#ax = sns.scatterplot(data=surveys_round2, x="Dates", y="Number of participants")
plt.xlabel('Date',fontsize=35)
plt.ylabel('Number of participants',fontsize=35)
plt.title('User engagement Round 2',fontsize=35)
plt.legend(ncol=2, loc="upper right",fontsize=20)
plt.xticks(rotation = 55,fontsize=20)
plt.yticks(fontsize=20)
plt.ylim(0, 30)
plt.show()
