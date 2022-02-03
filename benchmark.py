import data
from sklearn import svm, neighbors
import numpy as np
import typer
import random

app = typer.Typer()

def train(clf, data):
    random.shuffle(data)
    y, X = zip(*data)
    clf.fit(X, y)
    return clf

def test(clf, data):
    y, X = zip(*data)
    predictions = clf.predict(X)
    return zip(y, predictions)

def is_match(clf, sample) -> bool:
    return clf.predict([sample])[0]

def train_and_test(clf, in_data):
    train_data, test_data = in_data
    
    train(clf, train_data)
    results = test(clf, test_data)

    false_positives = 0
    false_negatives = 0
    true_positives = 0
    true_negatives = 0

    for label, prediction in results:
        if label == True:
            if prediction == True:
                true_positives += 1
            else:
                false_negatives += 1
        else:
            if prediction == True:
                false_positives += 1
            else:
                true_negatives += 1

    correct_classifications = true_positives + true_negatives
    wrong_classification = false_positives + false_negatives

    print("n="+str(len(test_data)))
    print("correct: " + str(correct_classifications / len(test_data))) # always false: 0,6147
    print("false positives: " + str(false_positives / len(test_data)))
    print("false negatives: " + str(false_negatives / len(test_data)))

def preprocessor_abs_hfft(data):
    res = np.abs(np.fft.hfft(data))
    return res

@app.command()
def plain():
    print("plain")
    train_and_test(svm.SVC(), data.split(data.load()))

@app.command()
def fft():
    print("with hfft")
    train_and_test(svm.SVC(), data.split(data.load(preprocessor_abs_hfft)))

if __name__ == "__main__":
    app()