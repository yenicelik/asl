import numpy as np

def rel_err(y_hat, y):
    return (y_hat - y) / y

np.set_printoptions(suppress=True)

# MM1 predicted
MM1_hat = np.asarray([
    [50.38, 6.32536, 6.20456],
    [6.31, 0.78007, 0.68475],
    [1796.46, 152.72627, 152.64135],
    [13.63, 1.19927, 1.12226]
])

# MM1 observed
MM1 = np.asarray([
    [33.66, 9.737, 1.72],
    [2.40, 3.95, 2.90],
    [48.51, 13.61, 4.97],
    [13.64, 11.19, 8.76]
])

# MMm predicted
MMm_hat = np.asarray(
    [
        [211.4, 28.00, 26.04],
        [7.98, 4.100, 0.866],
        [1787, 157, 151],
        [5.14, 10.28, 0.42]
    ])

# MMm observed
MMm = np.asarray([
    [33.66, 9.737, 1.72],
    [2.40, 3.95, 2.90],
    [48.51, 13.61, 4.97],
    [13.64, 11.19, 8.76]
])

print("MM1")
print(rel_err(MM1_hat, MM1))

print("MMm")
print(rel_err(MMm_hat, MMm))
