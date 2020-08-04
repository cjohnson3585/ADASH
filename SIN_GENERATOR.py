import numpy as np
import matplotlib.pyplot as plt

rand = np.random.RandomState(42)
#t = range(0,100,0.1)# + rand.rand(100)
t = np.arange(0,10,0.1) + rand.rand(100)
dy = 0.01 * (1 + rand.rand(100))
#y = np.sin(t)# + dy * rand.randn(100)
y = np.sin((2*np.pi* t)/5.15) + dy * rand.randn(100)

t0=0;period=5.15

phase = ((t - t0)/period)%1
idx = np.argsort(phase)
phasex=[];phasey=[]
for f in range(len(idx)):
    phasex.append(phase[idx[f]])
    phasey.append(y[idx[f]])

print('TIME,MAG,MERR')
for r in range(len(t)):
    print(t[r],y[r],dy[r],sep=',')
    
#plt.plot(phasex,phasey,'k*')
#plt.show()


