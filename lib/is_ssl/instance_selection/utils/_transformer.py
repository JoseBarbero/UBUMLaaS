import numpy as np
from sklearn.utils import Bunch


def transform(X, y):
    X_transformed = X.to_numpy()
    
    if -1 in y:
        print('\n\n\n\n Semi Supervised\n\n\n\n')
        print(X_transformed)
        print(type(X_transformed), end='\n\n\n')
        print(y)
        print(type(y), end='\n\n\n')
        labeled_indexes = np.where(y != -1)
        return Bunch(
            data=X_transformed[labeled_indexes],
            target=y[labeled_indexes]
        )
    else:
        return Bunch(data=X, target=y)
        
