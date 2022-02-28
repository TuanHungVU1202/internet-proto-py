import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_json('delay_112_1_1.json')


sub_10 = pd.read_json('delay_112_112_1.json' , orient='index')
sub_10 = sub_10.transpose()

sub_100 = pd.read_json('delay_112_336_1.json' , orient='index')
sub_100 = sub_100.transpose()

sub_500 = pd.read_json('delay_112_560_1.json' , orient='index')
sub_500 = sub_500.transpose()

sub_784 = pd.read_json('delay_112_784_1.json' , orient='index')
sub_784 = sub_784.transpose()

sub_1680 = pd.read_json('delay_112_1680_1.json' , orient='index')
sub_1680 = sub_1680.transpose()

sub_2240 = pd.read_json('delay_112_2240_1.json' , orient='index')
sub_2240 = sub_2240.transpose()

data = data['0x7fd6080bb790'].to_numpy()
# # sub_10 = sub_10.to_numpy()
print(sub_10.mean(axis=0))
print(np.mean(data))
sub_10 = sub_10.mean(axis=0).to_numpy()
sub_100 = sub_100.mean(axis=0).to_numpy()
sub_500 = sub_500.mean(axis=0).to_numpy()
sub_784 = sub_784.mean(axis=0).to_numpy()
sub_1680 = sub_1680.mean(axis=0).to_numpy()
sub_2240 = sub_2240.mean(axis=0).to_numpy()

print(sub_10)
x = range(len(sub_10))
x2 = range(len(sub_100))
x3 = range(len(sub_500))
x4 = range(len(sub_500))
x5 = range(len(sub_500))
x6 = range(len(sub_500))

print("array  of mean",np.average(sub_10))
y_mean = [np.mean(sub_10)]*len(x)
y_mean100 = [np.mean(sub_100)]*len(x2)
y_mean500 = [np.mean(sub_500)]*len(x3)
y_mean784 = [np.mean(sub_784)]*len(x3)
y_mean1680 = [np.mean(sub_1680)]*len(x3)
y_mean2240 = [np.mean(sub_2240)]*len(x3)

fig, ax = plt.subplots(figsize=(10, 7))

# Creating plot
ax.set(title='Delay vs increasing subscribers')
ax.set_xlabel('Subscribers')
ax.set_ylabel('Delay(ms)')
ax.scatter(x, sub_10, label="112 Subscribers")
ax.plot(x,y_mean, label='Mean 112 subs', linestyle='-.')
ax.scatter(x2,sub_100, label='336 Subscribers')
ax.plot(x2,y_mean100, label='Mean of 336 subs', linestyle='--')
ax.scatter(x3,sub_500, label='560 Subscribers')
ax.plot(x3,y_mean500, label='Mean of 560 subs', linestyle='-')

ax.scatter(x4,sub_784, label='784 Subscribers')
ax.plot(x4,y_mean784, label='Mean of 784 subs', linestyle='-')
ax.scatter(x5,sub_1680, label='1680 Subscribers')
ax.plot(x5,y_mean1680, label='Mean of 1680 subs', linestyle='-.')
ax.scatter(x6,sub_2240, label='2240 Subscribers')
ax.plot(x6,y_mean2240, label='Mean of 2240 subs', linestyle=':')

ax.legend()

# show plot
plt.show()


