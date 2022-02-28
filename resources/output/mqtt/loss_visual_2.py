import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


sent_112 = 2352
sent_per_112 = 21
sub_112 = pd.read_json('message_received_112_112_1.json' , orient='index')
sub_112 = sub_112

sent_per_336 = 21
sub_336 = pd.read_json('message_received_112_336_1.json' , orient='index')

sub_784 = pd.read_json('message_received_112_784_1.json' , orient='index')
sub_1680 = pd.read_json('message_received_112_1680_1.json' , orient='index')
sub_2240 = pd.read_json('message_received_112_2240_1.json' , orient='index')

# print(sub_336.describe())
# print(sent_per_336)
sub_112 = sub_112.to_numpy()
sub_336 = sub_336.to_numpy()
sub_784 = sub_784.to_numpy()
sub_1680 = sub_1680.to_numpy()
sub_2240 = sub_2240.to_numpy()

sub_112 = ((sent_per_112-sub_112)/sent_per_112)*100
sub_336 = ((sent_per_336-sub_336)/sent_per_336)*100
sub_784 = ((sent_per_336-sub_784)/sub_784)*100
sub_1680 = ((sent_per_336-sub_1680)/sent_per_336)*100
sub_2240 = ((sent_per_336-sub_2240)/sent_per_336)*100

# sub_112 = sub_112.sum()
# sub_336 = sub_336.sum()
# sub_784 = sub_784.sum()
# sub_1680 = sub_1680.sum()
# sub_2240 = sub_2240.sum()
print(sub_2240)


print(sub_2240)
x = range(len(sub_112))
x2 = range(len(sub_336))
x3 = range(len(sub_784))
x4 = range(len(sub_1680))
x5 = range(len(sub_2240))

print(sub_336)

data = [sub_112, sub_336, sub_784, sub_1680,sub_2240]
labels = ['Sub_112', 'Sub_336', 'Sub_784', 'Sub_1680', 'sub_2240']

fig, ax = plt.subplots(figsize=(7.5, 5))
fig1, axes = plt.subplots(figsize=(7.5, 5))

ax.set(title='Percentage Loss vs Subscribers')
ax.set_xlabel('Subscribers per topic')
ax.set_ylabel('Losses (%)')
ax.scatter(x, sub_112, label="112 Subscribers per topic sent")
ax.scatter(x2, sub_336, label="336 Subscribers per topic sent")
ax.scatter(x3, sub_784, label="784 Subscribers per topic sent")
ax.scatter(x4, sub_1680, label="1680 Subscribers per topic sent")
ax.scatter(x5, sub_2240, label="2240 Subscribers per topic sent")
ax.xaxis.set_ticklabels([])
ax.legend()

axes.boxplot(data,widths = 0.6, patch_artist = True, labels=labels)
axes.set(title='Percentage Loss vs Subscribers')
axes.set_ylabel('Losses (%)')

# show plot
plt.show()