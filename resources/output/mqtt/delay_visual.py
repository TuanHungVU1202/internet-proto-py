import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_json('delay_112_1_1.json')


sub_10 = pd.read_json('delay_112_10_1.json' , orient='index')
sub_10 = sub_10.transpose()

sub_100 = pd.read_json('delay_112_100_1.json' , orient='index')
sub_100 = sub_100.transpose()

sub_500 = pd.read_json('delay_112_500_1.json' , orient='index')
sub_500 = sub_500.transpose()

data = data['0x7fd6080bb790'].to_numpy()
# # sub_10 = sub_10.to_numpy()
print(sub_10.mean(axis=0))
print(np.mean(data))
sub_10 = sub_10.mean(axis=0).to_numpy()
sub_100 = sub_100.mean(axis=0).to_numpy()
sub_500 = sub_500.mean(axis=0).to_numpy()

print(sub_10)
x = range(len(sub_10))
x2 = range(len(sub_100))
x3 = range(len(sub_500))

print("array  of mean",np.average(sub_10))
y_mean = [np.mean(sub_10)]*len(x)
y_mean100 = [np.mean(sub_100)]*len(x2)
y_mean500 = [np.mean(sub_500)]*len(x3)

fig, ax = plt.subplots(figsize=(10, 7))

# Creating plot
ax.set(title='Delay vs increasing subscribers')
ax.set_xlabel('Subscribers')
ax.set_ylabel('Delay(ms)')
ax.scatter(x, sub_10, label="10 Subscribers")
ax.plot(x,y_mean, label='Mean 10 subs', linestyle='--')
ax.scatter(x2,sub_100, label='100 Subscribers')
ax.plot(x2,y_mean100, label='Mean of 100 subs', linestyle='-.')
ax.scatter(x3,sub_500, label='500 Subscribers')
ax.plot(x3,y_mean500, label='Mean of 500 subs', linestyle='-')

ax.legend()

# show plot
plt.show()


