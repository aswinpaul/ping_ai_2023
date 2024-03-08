#!/usr/bin/env python
# coding: utf-8

#%% Import all modules. Set path for importing DishBrain original data

import sys
import numpy as np
import pandas as pd
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
        # .get(x, 0) returns a default of 0 so you don't have to do
        # if x in counts
        counts[x] = counts.get(x, 0) + 1
    return [key for key, value in counts.items() if value == 1]

df99 = pd.read_csv('in_vitro_cells_sentience.csv')
df99 = df99[df99['chip_id']!= 7282]
df99 = df99[(df99['group'] == 0) | (df99['group'] == 3) | (df99['group'] == 2)]

df99['group_name'] = 99
df99['group_name'] = np.where((df99['group']== 0), "MCC", df99['group_name'])
df99['group_name'] = np.where((df99['group']== 1), "CTL", df99['group_name'])
df99['group_name'] = np.where((df99['group']== 2), "HCC", df99['group_name'])
df99['group_name'] = np.where((df99['group']== 3), "RST", df99['group_name'])
df99['group_name'] = np.where((df99['group']== 4), "IS", df99['group_name'])

#%% Importing all New active-inference agent performance data

new_data = pd.read_csv('p_data.csv')
new_data['group'] = 7
new_data['tag'] = 'aif-agent'
new_data['date'] = '28.02.2024'
new_data['chip_id'] = 10
new_data['group_name'] = "AIF-1"

df99 = pd.concat([df99, new_data])

#%% Data cleanup

# Neccesary columns for all data
df99['long_rally'] = np.where((df99['hit_count'] >= 3), 1, 0)
df99['ace'] = np.where((df99['hit_count'] == 0), 1, 0)
df99["number"] = df99.index

# Group into minutes and take the mean.
# Filter out data where errors in collection or cell activity have been noted.
# Typically this is when testing was done on chips that never displayed
# suitable activity but we wanted to investigate for a different reason or when
# a chip was faulty. Note that here most filtered (both rest and active sessions)
# are from a single tag where cells never displayed any robust activity.
# in-silico sessions removed are 1) due to faulty record and
# due to the wrong tag being put in on one nuc so it was testing something else.

df2 = df99.groupby(['group', 'tag', 'chip_id', 'date', 'session_num',
                    'half', 'elapse_minute_rounded', 'group_name']).mean(numeric_only = True)

# to analyse by timepoint we then reset the index and
# group it by the half we defined earlier.

df4 = df2.reset_index()
df5 = df4.groupby(['group', 'tag', 'chip_id', 'date',
                   'session_num', 'half', 'group_name']).mean(numeric_only = True)

# We then reset the index again to get a single index dataframe and
# assign a unique id to each chip

df4 = df5.reset_index()
df4["id"] = ((df4['chip_id']).astype(str)) + (
    (df4['date']).astype(str)) +((df4['session_num']).astype(str))

#%% Long Rallies box plot

#box plot for long rallies
df4['%long_rally'] = df4['long_rally']*100
df4['%ace'] = df4['ace']*100

df_test2 = df4

labels = df_test2.group_name.unique()
x_pos = np.arange(len(labels))

x = df_test2['group_name']
y = df_test2['%long_rally']

hue = df_test2['half']

sns.set(style="darkgrid")
sns.set(font_scale=1.4)

ax = sns.boxplot(data=df99, x=x, y=y, hue=hue, palette="Set2", 
                 showfliers=False,
                 showmeans = True,
                 meanprops={"markerfacecolor":"black",
                       "markeredgecolor":"black",
                      "markersize":"5"})

ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=16)

ax.set_ylabel('% Long-Rallies',fontsize = 18)
ax.set_xlabel('Group',fontsize = 18)
ax.grid(False)
ax.legend([0, 1], ["0-5", "6-20"], fontsize = 14)

L = plt.legend(loc='upper right', bbox_to_anchor=(1.29, 1.1),
               title = "Minutes", borderaxespad=0.1, frameon=False)

L.get_texts()[0].set_text('0-5')
L.get_texts()[1].set_text('6-20')

plt.savefig('long-rallies_AIF_vs_SBI.png', bbox_inches='tight')
plt.show()

#%% Aces boxplot
plt.clf()

#box plot for aces

df_test2 = df4

labels = df_test2.group_name.unique()
x_pos = np.arange(len(labels))
x = df_test2['group_name']
y = df_test2['%ace']
hue = df_test2['half']
sns.set(style="darkgrid")
sns.set(font_scale=1.4)
ax = sns.boxplot(data=df_test2, x=x, y=y, hue=hue, palette="Set2", 
                 showfliers=False, showmeans = True,
                 meanprops={"markerfacecolor":"black",
                       "markeredgecolor":"black",
                      "markersize":"5"})
ax.set_xticks(x_pos)
ax.set_xticklabels(labels,fontsize = 16)
ax.set_ylabel('% Aces',fontsize = 18)
ax.set_xlabel('Group',fontsize = 18)
ax.grid(False)
ax.legend([0, 1], ["0-5", "6-20"],fontsize = 14)
L = plt.legend(loc='lower left', bbox_to_anchor=(1, 0.85), 
               title = "Minutes", borderaxespad=0.1, frameon=False)
L.get_texts()[0].set_text('0-5')
L.get_texts()[1].set_text('6-20')

sns.set(rc={'figure.figsize':(6,6)})
plt.savefig('aces_AIF_vs_SBI.png', bbox_inches='tight')
plt.show()

#%% Average Rally Length box plot
plt.clf()

df2 = df99.groupby(['group', 
                    'group_name',
                    'session_num',
                    'date',
                    'tag', 'chip_id',
                    'elapse_minute_rounded']).mean(numeric_only = True)

cleanDF = df2

lines = cleanDF.reset_index()

lines['Zhit_count'] = (lines.hit_count - 
                         lines.hit_count.mean())/lines.hit_count.std(ddof=0)
lines['Zhit_count'] = lines['Zhit_count'].abs()
lines = lines[lines.Zhit_count <= 2]

df_test = lines

labels = df_test.group_name.unique()

x_pos = np.arange(len(labels))
x = df_test['group']
y = df_test['hit_count']
hue = df_test['half'].astype(int)
sns.set(style="darkgrid")
sns.set(font_scale=1.4)
ax = sns.boxplot(data=df_test, x=x, y=y, hue=hue, palette="Set2", 
                 showfliers=False, showmeans = True,
                 meanprops={"markerfacecolor":"black",
                       "markeredgecolor":"black",
                      "markersize":"5"})
ax.set_xticks(x_pos)
ax.set_xticklabels(labels,fontsize = 16)
ax.set_ylabel('Average Rally Length',fontsize = 18)
ax.set_xlabel('Group',fontsize = 18)
ax.grid(False)
ax.legend([0, 1], ["0-5", "6-20"],fontsize = 14)
L = plt.legend(loc='lower left', bbox_to_anchor=(1, 0.85), title = "Minutes", 
               borderaxespad=0.1, frameon=False)
L.get_texts()[0].set_text('0-5')
L.get_texts()[1].set_text('6-20')

sns.set(rc={'figure.figsize':(6,6)})

plt.savefig('Avg_Rally_length_AIF_vs_SBI.png', bbox_inches='tight')
plt.show()

#%% RI Catplot

plt.clf()

#df4['pltgroup'] = df4['group']
#df4 = df4.sort_values(by=['pltgroup'])

#normalises only by group
filtdf = df4.groupby(['group_name', "group", 'tag', 'chip_id', 'date', 
                      'session_num', 'half']).mean(numeric_only = True)

data = filtdf[['hit_count']].copy()
data = data.unstack(level=6)

data = data.sort_values(by=["group_name"])

data = data[data[("hit_count", 0)] != 0]
data["normhc"] = ((data[('hit_count', 1)] - data[('hit_count', 0)]) / 
                  data[('hit_count', 0)] ) *100

data = data.reset_index()

#bar graphs for hit count
data2 = data

x = 'group_name'
y = 'normhc'

sns.set(style="darkgrid")
sns.set(rc={'figure.figsize':(8,8)})
sns.set(font_scale=1.4)
ax = sns.catplot(data=data2, kind="bar", x=x, y=y, ci=95, palette="Set2", 
                 alpha=.6, height=6)

ax.set_axis_labels("Group", "Relative Improvement (%) Over Time",fontsize = 18)
ax.set(ylim=(0, 180))
plt.savefig('Rel_Improvement_AIF_vs_SBI.png', bbox_inches='tight')
plt.show()

#%% RI box plot
plt.clf()
data2 = data

x = 'group_name'
y = 'normhc'
# hue = df_test2['half']
sns.set(style="darkgrid")
sns.set(font_scale=1.4)

ax = sns.boxplot(data=data2, x=x, y=y, palette="Set2", showfliers=False, 
                 showmeans = True,
                 meanprops={"markerfacecolor":"black",
                       "markeredgecolor":"black",
                      "markersize":"5"})

ax.set_ylabel('Relative Improvement (%) Over Time',fontsize = 18)
ax.set_xlabel('Group',fontsize = 18)
ax.grid(False)
sns.set(rc={'figure.figsize':(6,6)})

plt.savefig('Rel_Improvement_AIF_vs_SBI_box.png', bbox_inches='tight')
plt.show()

#%% Long rally Reg plot

plt.clf()

df2 = df99.groupby(['group', 'tag', 'chip_id', 'date',
                    'session_num', 
                    'elapse_minute_rounded', 
                    'group_name']).mean(numeric_only = True)

cleanDF = df2

lines = cleanDF.reset_index()

lines['Zhit_count'] = (lines.hit_count - 
                         lines.hit_count.mean())/lines.hit_count.std(ddof=0)
lines['Zhit_count'] = lines['Zhit_count'].abs()
lines = lines[lines.Zhit_count <= 2]

lines['%long_rally'] = lines['long_rally']*100
lines['%ace'] = lines['ace']*100

sns.set(font_scale=1.4)
f, ax = plt.subplots(figsize=(7,7))

for i in lines.group.unique():
    control = lines[lines['group'] == i]
    label = control.group_name.unique()[0]
    
    px = control[control['elapse_minute_rounded']<20]['elapse_minute_rounded']
    py = control[control['elapse_minute_rounded']<20]['%long_rally']
    sns.regplot(x=ax.xaxis.convert_units(px), y=py, x_estimator=np.mean, ci=95, 
            scatter = False, order = 1, label = label)

sns.set(style="darkgrid")

ax.set_ylabel('% Long Rallies',fontsize =20)
ax.set_xlabel('Elapsed Minute',fontsize =20)
#plt.xlim([0.0, 19.2])
plt.legend(loc='upper left',fontsize =14)
ax.grid(False)

plt.savefig('regression_lines_LongRallies_AIF_v_SBI.png', bbox_inches='tight')
plt.show()

#%% Aces Reg plot
plt.clf()

sns.set(font_scale=1.4)
f, ax = plt.subplots(figsize=(7,7))

for i in lines.group.unique():
    control = lines[lines['group'] == i]
    label = control.group_name.unique()[0]
    
    px = control[control['elapse_minute_rounded']<20]['elapse_minute_rounded']
    py = control[control['elapse_minute_rounded']<20]['%ace']
    
    sns.regplot(x=ax.xaxis.convert_units(px), y=py, x_estimator=np.mean, ci=95, 
            scatter = False, order = 1, label = label)
    
sns.set(style="darkgrid")
ax.set_ylabel('% Aces',fontsize =20)
ax.set_xlabel('Elapsed Minute',fontsize =20)
plt.xlim([-0.5, 19.5])
plt.legend(loc='upper left',fontsize =14)
ax.grid(False)

plt.savefig('regression_lines_Aces_AIF_v_SBI.png', bbox_inches='tight')
plt.show()

#%% Regression Plot (Avg. hits per rally)

sns.set(font_scale=1.4)
f, ax = plt.subplots(figsize=(7,7))

for i in lines.group.unique():
    control = lines[lines['group'] == i]
    label = control.group_name.unique()[0]
    
    px = control[control['elapse_minute_rounded']<20]['elapse_minute_rounded']
    py = control[control['elapse_minute_rounded']<20]['hit_count']
    
    sns.regplot(x=ax.xaxis.convert_units(px), y=py, x_estimator=np.mean, ci=95, 
            scatter = False, order = 1, label = label)
    
sns.set(style="darkgrid")

ax.set_ylabel('Average Hits Per Rally',fontsize =20)
ax.set_xlabel('Elapsed Minute',fontsize =20)
plt.xlim([-0.5, 19.5])
plt.legend(loc='upper left',fontsize =14)
ax.grid(False)

plt.savefig('regression_lines_AIF_v_SBI.png', bbox_inches='tight')
plt.show()
