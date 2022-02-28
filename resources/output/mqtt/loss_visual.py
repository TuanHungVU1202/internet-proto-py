import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


sent = 2352

sub_1 = pd.read_json('message_received_112_1_1.json' , orient='index')
sub_10 = pd.read_json('message_received_112_10_1.json' , orient='index')
sub_100 = pd.read_json('message_received_112_100_1.json' , orient='index')
sub_500 = pd.read_json('message_received_112_500_1.json' , orient='index')

print(sub_1)
sub_1 = sub_1.to_numpy()
sub_10 = sub_10.to_numpy()

sub_1 = ((sent - sub_1)/sent)*100
sub_10 = ((sent - sub_10)/sent)*100
# print(sub_10)
sub_100 = sub_100.to_numpy()
sub_100 = ((sent - sub_100)/sent)*100

sub_500 = sub_500.to_numpy()
sub_500 = ((sent - sub_500)/sent)*100

print(sub_10)

data = [sub_1, sub_10, sub_100, sub_500]

x = range(len(sub_10))
# x = range(len(sub_10))
x2 = range(len(sub_100))
x3 = range(len(sub_500))

y_mean = [np.mean(sub_10)]*len(x)
y_mean100 = [np.mean(sub_100)]*len(x2)
y_mean500 = [np.mean(sub_500)]*len(x3)

labels = ['Sub_1', 'Sub_10', 'Sub_100', 'Sub_500']


fig, ax = plt.subplots(figsize=(7.5, 5))
fig1, axes = plt.subplots(figsize=(7.5, 5))
# Creating plot
ax.set(title='Percentage Loss vs Subscribers')
ax.set_xlabel('Subscribers')
ax.set_ylabel('Losses (%)')
ax.scatter(x, sub_10, label="10 Subscribers")
ax.plot(x,y_mean, label='Mean 10 subs', linestyle='--')
ax.scatter(x2,sub_100, label='100 Subscribers')
ax.plot(x2,y_mean100, label='Mean of 100 subs', linestyle='-.')
ax.scatter(x3,sub_500, label='500 Subscribers')
ax.plot(x3,y_mean500, label='Mean of 500 subs', linestyle='-')
ax.xaxis.set_ticklabels([])
axes.boxplot(data,widths = 0.6, patch_artist = True, labels=labels)
axes.set(title='Percentage Loss vs Subscribers')
axes.set_ylabel('Losses (%)')
ax.legend()

# show plot
plt.show()