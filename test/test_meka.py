from skmultilearn.dataset import load_dataset

X_train, y_train, _, _ = load_dataset('scene', 'train')
X_test,  y_test, _, _ = load_dataset('scene', 'test')

from skmultilearn.ext import Meka

meka = Meka(
        meka_classifier = "meka.classifiers.multilabel.BR", # Binary Relevance
        weka_classifier = "weka.classifiers.bayes.NaiveBayesMultinomial", # with Naive Bayes single-label classifier
        
)
meka.fit(X_train, y_train)
predictions = meka.predict(X_test)


from sklearn.metrics import hamming_loss

print(hamming_loss(y_test, predictions))
print("Correct")