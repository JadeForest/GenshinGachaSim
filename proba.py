import numpy as np
import random


def get(prob: float) -> bool:
    assert 0 <= prob <= 1, "Invalid probability."
    rand = random.random()
    return True if rand <= 1 * prob else False


if __name__ == "__main__":
    lt = []
    for i in range(10000):
        if get(1 / 2):
            lt.append(1)
        else:
            lt.append(0)

    arr = np.array(lt)

    print((arr.sum() / arr.shape[0]).round(2))
