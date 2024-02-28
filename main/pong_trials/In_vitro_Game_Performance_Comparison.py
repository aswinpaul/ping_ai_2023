#!/usr/bin/env python
# coding: utf-8

#%% Import all modules. Set path for importing dishpill_models

import sys
import numpy as np
import pandas as pd
import scipy.stats as sp
import matplotlib.pyplot as plt
import seaborn as sns

pd.options.display.max_columns = 150

sns.set()
pd.set_option('display.max_rows', 250)
sns.set_style("whitegrid")

import warnings
warnings.filterwarnings('ignore')
path = "../models"
if not path in sys.path:
    sys.path.append(path)

# use this to find unique ids generated by error as part of 
# a false start.  

def find_unique_ids(ids):
    counts = {}
    for x in ids:
        # .get(x, 0) returns a default of 0 so you don't have to do if x in counts
        counts[x] = counts.get(x, 0) + 1
    return [key for key, value in counts.items() if value == 1]

df = pd.read_csv('in_vitro_cells_sentience.csv')

df99 = pd.concat([df])

# df99 = pd.concat([dqn, a2c, ppo])

df99['long_rally'] = np.where((df99['hit_count'] >= 3), 1, 0)
df99['ace'] = np.where((df99['hit_count'] == 0), 1, 0)
df99["number"] = df99.index



#%% Average number of episodes

#df99_count = df99[df99['group'] == 0|2]

#df99_count = df99_count[df99_count['chip_id']!= 7282]

#df_count = df99_count.groupby(['chip_id', 'date','session_num','tag','group']).size().sort_values(ascending=False).reset_index(name='count')


# Group into minutes and take the mean. 
# Filter out data where errors in collection or cell activity have been noted. 
# Typically this is when testing was done on chips that never displayed 
# suitable activity but we wanted to investigate for a different reason or when 
# a chip was faulty. Note that here most filtered (both rest and active sessions) 
# are from a single tag where cells never displayed any robust activity. 
# in-silico sessions removed are 1) due to faulty record and 
# due to the wrong tag being put in on one nuc so it was testing something else. 

df2 = df99.groupby(['group', 'tag', 'chip_id', 'date', 'session_num', 'half', 'elapse_minute_rounded']).mean(numeric_only = True)


#to analyse by timepoint we then reset the index and group it by the half we defined earlier. 

df4 = df2.reset_index()
df5 = df4.groupby(['group', 'tag', 'chip_id', 'date', 'session_num', 'half']).mean()

# We then reset the index again to get a single index dataframe and assign a unique id to each chip
df4 = df5.reset_index()
df4["id"] = ((df4['chip_id']).astype(str)) + ((df4['date']).astype(str)) +((df4['session_num']).astype(str))

#Create a string name for each group for easier access

df4['group_name'] = 99
df4['group_name'] = np.where((df4['group']== 0), "MCC", df4['group_name'])
df4['group_name'] = np.where((df4['group']== 1), "CTL", df4['group_name'])
df4['group_name'] = np.where((df4['group']== 2), "HCC", df4['group_name'])
df4['group_name'] = np.where((df4['group']== 3), "RST", df4['group_name'])
df4['group_name'] = np.where((df4['group']== 4), "IS", df4['group_name'])

check = df4.groupby(['group', 'half']).mean(numeric_only = True)
#check


#check for false starts that have no input in second half. 
#false_starts = find_unique_ids(df4['id'])
#for x in false_starts:
    #df4 = df4[df4.id != x]


#%% Long Rallies

#sort by group to make plotting easier

df4['pltgroup'] = 99
df4['pltgroup'] = np.where((df4['group']== 0), "3", df4['pltgroup'])
df4['pltgroup'] = np.where((df4['group']== 1), "0", df4['pltgroup'])
df4['pltgroup'] = np.where((df4['group']== 2), "4", df4['pltgroup'])
df4['pltgroup'] = np.where((df4['group']== 3), "2", df4['pltgroup'])
df4['pltgroup'] = np.where((df4['group']== 4), "1", df4['pltgroup'])
df4 = df4.sort_values(by=['pltgroup'])

#box plot for long rallies
df4['%long_rally'] = df4['long_rally']*100
df4['%ace'] = df4['ace']*100

df_test2 = df4[(df4['group'] == 0) | (df4['group'] == 2)]


labels = df_test2.group_name.unique()
x_pos = np.arange(len(labels))

x = df_test2['group_name']
y = df_test2['%long_rally']

hue = df_test2['half']
sns.set(style="darkgrid")
sns.set(font_scale=1.4)

ax = sns.boxplot(data=df, x=x, y=y, hue=hue, palette="Set2", showfliers=False, 
                 showmeans = True, 
                 meanprops={"markerfacecolor":"black", 
                       "markeredgecolor":"black",
                      "markersize":"5"})

# ax.set_ylim([0, 2.5])
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=16)

# ax.set_yticklabels([0,0,5,10,15,20,25,30], fontsize=16)
# ax.set_title('Pong Performance over Time With All Features')

ax.set_ylabel('% Long-Rallies',fontsize = 18)
ax.set_xlabel('Group',fontsize = 18)
ax.grid(False)
ax.legend([0, 1], ["0-5", "6-20"], fontsize = 14)

L = plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1), 
               title = "Minutes", borderaxespad=0.1, frameon=False)

L.get_texts()[0].set_text('0-5')
L.get_texts()[1].set_text('6-20')

# y, h, col = 30, 0.5, 'k'
# x00, x01 = -.2, .2
# x10, x11 = .8, 1.2
# x20, x21 = 1.8, 2.2
# x30, x31 = 2.8, 3.2
# x40, x41 = 3.8, 4.2

# #Plot t-test between groups

# ax.set_ylim([-2, 40])
# sns.set(rc={'figure.figsize':(6,6)})

# #= HCC
# % = MCC
# ^ = CTL
# @ = Rest
# plt.savefig('long-rallies_RL_vs_SBI.pdf', bbox_inches='tight')

#%% Reg plot long rally

df2 = df99.groupby(['group', 'tag', 'chip_id', 'date', 'session_num', 'elapse_minute_rounded']).mean(numeric_only = True)

cleanDF = df2

lines = cleanDF.reset_index()
control = lines[(lines.group == 0)]
control['Zhit_count'] = (control.hit_count - control.hit_count.mean())/control.hit_count.std(ddof=0) 
control['Zhit_count'] = control['Zhit_count'].abs()
control = control[control.Zhit_count <= 2]


primary = lines[(lines.group == 1)]
primary['Zhit_count'] = (primary.hit_count - primary.hit_count.mean())/primary.hit_count.std(ddof=0) 
primary['Zhit_count'] = primary['Zhit_count'].abs()
primary = primary[primary.Zhit_count <= 2]

human = lines[(lines.group == 2)]
human['Zhit_count'] = (human.hit_count - human.hit_count.mean())/human.hit_count.std(ddof=0) 
human['Zhit_count'] = human['Zhit_count'].abs()
human = human[human.Zhit_count <= 2]

# rest = lines[(lines.group == 3)]
# insilico = lines[(lines.group == 4)]

dqn = lines[(lines.group == 5)]
dqn['Zhit_count'] = (dqn.hit_count - dqn.hit_count.mean())/dqn.hit_count.std(ddof=0) 
dqn['Zhit_count'] = dqn['Zhit_count'].abs()
# dqn['Zhit_count'] = (dqn.hit_count - dqn.hit_count.min())/(dqn.hit_count.max()-dqn.hit_count.min())
dqn = dqn[dqn.Zhit_count <= 2]


a2c = lines[(lines.group == 6)]
a2c['Zhit_count'] = (a2c.hit_count - a2c.hit_count.mean())/a2c.hit_count.std(ddof=0) 
a2c['Zhit_count'] = a2c['Zhit_count'].abs()
a2c = a2c[a2c.Zhit_count <= 2]

ppo = lines[(lines.group == 7)]
ppo['Zhit_count'] = (ppo.hit_count - ppo.hit_count.mean())/ppo.hit_count.std(ddof=0) 
ppo['Zhit_count'] = ppo['Zhit_count'].abs()
ppo = ppo[ppo.Zhit_count <= 2]

control['%long_rally'] = control['long_rally']*100
control['%ace'] = control['ace']*100

human['%long_rally'] = human['long_rally']*100
human['%ace'] = human['ace']*100


px = control[control['elapse_minute_rounded']<20]['elapse_minute_rounded']
py = control[control['elapse_minute_rounded']<20]['%long_rally']
hx = human[human['elapse_minute_rounded']<20]['elapse_minute_rounded']
hy = human[human['elapse_minute_rounded']<20]['%long_rally']

sns.set(font_scale=1.4)
f, ax = plt.subplots(figsize=(7,7))
sns.regplot(x=ax.xaxis.convert_units(px), y=py, x_estimator=np.mean, ci=95, scatter = False, order = 1, label = "MCC",color='b')
sns.regplot(x=ax.xaxis.convert_units(hx), y=hy, x_estimator=np.mean, ci=95, scatter = False, order = 1, label = "HCC",color = "#FF7D40")


sns.set(style="darkgrid")

ax.set_ylabel('% Long Rallies',fontsize =20)
ax.set_xlabel('Elapsed Minute',fontsize =20)
plt.xlim([-0.5, 19.5])
plt.legend(loc='upper left',fontsize =14)
ax.grid(False)

# plt.savefig('regression_lines_LongRallies_RL_v_SBI.pdf', bbox_inches='tight') 

#%% Aces

#box plot for aces

df_test2 = df4[(df4['group']== 0)|(df4['group']== 2)]

labels = df_test2.group_name.unique()
x_pos = np.arange(len(labels))
x = df_test2['group_name']
y = df_test2['%ace']
hue = df_test2['half']
sns.set(style="darkgrid")
sns.set(font_scale=1.4)
ax = sns.boxplot(data=df_test2, x=x, y=y, hue=hue, palette="Set2", showfliers=False, showmeans = True, 
                 meanprops={"markerfacecolor":"black", 
                       "markeredgecolor":"black",
                      "markersize":"5"})
ax.set_xticks(x_pos)
ax.set_xticklabels(labels,fontsize = 16)
# ax.set_yticklabels([0,0,10,20,30,40,50,60,70,80],fontsize = 16)
#ax.set_title('Pong Performance over Time With All Features')
ax.set_ylabel('% Aces',fontsize = 18)
ax.set_xlabel('Group',fontsize = 18)
ax.grid(False)
ax.legend([0, 1], ["0-5", "6-20"],fontsize = 14)
L = plt.legend(loc='lower left', bbox_to_anchor=(1, 0.85), title = "Minutes", borderaxespad=0.1, frameon=False)
L.get_texts()[0].set_text('0-5')
L.get_texts()[1].set_text('6-20')
#ax.set_ylim([0, 2.5])
y, h, col = 20, -1.5, 'k'
x00, x01 = -.2, .2
x10, x11 = .8, 1.2
x20, x21 = 1.8, 2.2
x30, x31 = 2.8, 3.2
x40, x41 = 3.8, 4.2


ax.set_ylim([10, 95])
sns.set(rc={'figure.figsize':(6,6)})
# #= HCC
# % = MCC

#^ = CTL
# @ = IS
# plt.savefig('aces_RL_vs_SBI.pdf', bbox_inches='tight') 

#%% Reg plot aces

control['%long_rally'] = control['long_rally']*100
control['%ace'] = control['ace']*100

human['%long_rally'] = human['long_rally']*100
human['%ace'] = human['ace']*100



px = control[control['elapse_minute_rounded']<20]['elapse_minute_rounded']
py = control[control['elapse_minute_rounded']<20]['%ace']
hx = human[human['elapse_minute_rounded']<20]['elapse_minute_rounded']
hy = human[human['elapse_minute_rounded']<20]['%ace']

sns.set(font_scale=1.4)
f, ax = plt.subplots(figsize=(7,7))
sns.regplot(x=ax.xaxis.convert_units(px), y=py, x_estimator=np.mean, ci=95, scatter = False, order = 1, label = "MCC",color='b')
sns.regplot(x=ax.xaxis.convert_units(hx), y=hy, x_estimator=np.mean, ci=95, scatter = False, order = 1, label = "HCC",color = "#FF7D40")


sns.set(style="darkgrid")

ax.set_ylabel('% Aces',fontsize =20)
ax.set_xlabel('Elapsed Minute',fontsize =20)
plt.xlim([-0.5, 19.5])
plt.legend(loc='upper left',fontsize =14)
ax.grid(False)

# plt.savefig('regression_lines_Aces_RL_v_SBI.pdf', bbox_inches='tight') 

#%% Average Rally Length

df2 = df99.groupby(['group', 'tag', 'chip_id', 'date', 'session_num', 'elapse_minute_rounded']).mean(numeric_only = True)

cleanDF = df2

lines = cleanDF.reset_index()
control = lines[(lines.group == 0)]
control['Zhit_count'] = (control.hit_count - control.hit_count.mean())/control.hit_count.std(ddof=0) 
control['Zhit_count'] = control['Zhit_count'].abs()
control = control[control.Zhit_count <= 2]

primary = lines[(lines.group == 1)]
primary['Zhit_count'] = (primary.hit_count - primary.hit_count.mean())/primary.hit_count.std(ddof=0) 
primary['Zhit_count'] = primary['Zhit_count'].abs()
primary = primary[primary.Zhit_count <= 2]

human = lines[(lines.group == 2)]
human['Zhit_count'] = (human.hit_count - human.hit_count.mean())/human.hit_count.std(ddof=0) 
human['Zhit_count'] = human['Zhit_count'].abs()
human = human[human.Zhit_count <= 2]

# rest = lines[(lines.group == 3)]
# insilico = lines[(lines.group == 4)]


# x = 'group'
# y = 'hit_count'
# hue = 'half'
df_test = pd.concat([control,human])


labels =['MCC', 'HCC'] #df_test.group.unique()
x_pos = np.arange(len(labels))
x = df_test['group']
y = df_test['hit_count']
hue = df_test['half']
sns.set(style="darkgrid")
sns.set(font_scale=1.4)
ax = sns.boxplot(data=df_test, x=x, y=y, hue=hue, palette="Set2", showfliers=False, showmeans = True, 
                 meanprops={"markerfacecolor":"black", 
                       "markeredgecolor":"black",
                      "markersize":"5"})
ax.set_xticks(x_pos)
ax.set_xticklabels(labels,fontsize = 16)
ax.set_ylabel('Average Rally Length',fontsize = 18)
ax.set_xlabel('Group',fontsize = 18)
ax.grid(False)
ax.legend([0, 1], ["0-5", "6-20"],fontsize = 14)
L = plt.legend(loc='lower left', bbox_to_anchor=(1, 0.85), title = "Minutes", borderaxespad=0.1, frameon=False)
L.get_texts()[0].set_text('0-5')
L.get_texts()[1].set_text('6-20')

# ax.set_ylim([10, 95])
sns.set(rc={'figure.figsize':(6,6)})
 
# plt.savefig('BAR_Pong_Over_Time_0,1half_box.pdf', bbox_inches='tight') 

#%% Relative Imporvement plot

#normalises only by group
filtdf = df4.groupby(['group_name', "pltgroup", 'tag', 'chip_id', 'date', 'session_num', 'half']).mean(numeric_only = True)
data = filtdf[['hit_count']].copy()
data = data.unstack(level=6)
data=data.sort_values(by=["pltgroup"])
#data[('hit_count', 1)] = data[('hit_count', 1)].fillna(method='ffill', inplace=False)
#data = data.dropna()
data["normhc"] = ((data[('hit_count', 1)] - data[('hit_count', 0)]) / data[('hit_count', 0)] ) *100
data = data.reset_index()


#bar graphs for hit count
data2 = data[(data['group_name']== 'MCC')|(data['group_name']== 'HCC')]

x = 'group_name'
y = 'normhc'
sns.set(style="darkgrid")
sns.set(rc={'figure.figsize':(5,8)})
sns.set(font_scale=1.4)
ax = sns.catplot(data=data2, kind="bar",x=x, y=y, ci=95, palette="Set2", alpha=.6, height=6)

ax.set_axis_labels("Group", "Relative Improvement (%) Over Time",  fontsize = 20)
ax.set_xticklabels(["MCC", "HCC"],  fontsize = 18)

ax.set(ylim=(-5, 145))
# plt.savefig('Rel_Improvement_RL_vs_SBI.pdf', bbox_inches='tight')  


#%% Regression RI plot

data2 = data[(data['group_name']== 'MCC')|(data['group_name']== 'HCC')]


x = 'group_name'
y = 'normhc'
# hue = df_test2['half']
sns.set(style="darkgrid")
sns.set(font_scale=1.4)
ax = sns.boxplot(data=data2, x=x, y=y, palette="Set2", showfliers=False, showmeans = True, 
                 meanprops={"markerfacecolor":"black", 
                       "markeredgecolor":"black",
                      "markersize":"5"})
ax.set_ylabel('Relative Improvement (%) Over Time',fontsize = 18)
ax.set_xlabel('Group',fontsize = 18)
ax.grid(False)


# ax.set_ylim([10, 95])
sns.set(rc={'figure.figsize':(6,6)})

# plt.savefig('Rel_Improvement_RL_vs_SBI_box.pdf', bbox_inches='tight') 

#%% Regression Plots

px = control[control['elapse_minute_rounded']<20]['elapse_minute_rounded']
py = control[control['elapse_minute_rounded']<20]['hit_count']
hx = human[human['elapse_minute_rounded']<20]['elapse_minute_rounded']
hy = human[human['elapse_minute_rounded']<20]['hit_count']

sns.set(font_scale=1.4)
f, ax = plt.subplots(figsize=(7,7))
sns.regplot(x=ax.xaxis.convert_units(px), y=py, x_estimator=np.mean, ci=95, scatter = False, order = 1, label = "MCC",color='b')
sns.regplot(x=ax.xaxis.convert_units(hx), y=hy, x_estimator=np.mean, ci=95, scatter = False, order = 1, label = "HCC",color = "#FF7D40")


sns.set(style="darkgrid")

ax.set_ylabel('Average Hits Per Rally',fontsize =20)
ax.set_xlabel('Elapsed Minute',fontsize =20)
plt.xlim([-0.5, 19.5])
plt.legend(loc='upper left',fontsize =14)
ax.grid(False)

# plt.savefig('regression_lines_RL_v_SBI.pdf', bbox_inches='tight') 