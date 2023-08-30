from core import get

import numpy as np

lt = []
for i in range(10000):
    if get(1/2):
        lt.append(1)
    else:
        lt.append(0)

arr = np.array(lt)

print((arr.sum()/arr.shape[0]).round(2))