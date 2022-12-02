import numpy as np
from sklearn.utils import Bunch


def transform(X, y):
    X_transformed = X.to_numpy()
    y_transformed = y.to_numpy()
    return Bunch(data=X_transformed, target=y_transformed)
        
