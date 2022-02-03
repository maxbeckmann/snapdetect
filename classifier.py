from abc import ABC, abstractmethod, abstractclassmethod
from pathlib import Path
import random
import joblib

class Classifier(ABC):
    @abstractmethod
    def store(self, model_path: Path):
        pass
    
    @abstractclassmethod
    def restore(cls, model_path: Path):
        pass
    
    @abstractmethod
    def train(self, labled_samples):
        pass
    
    @abstractmethod
    def is_match(self, sample) -> bool:
        pass


class SimpleSVMClassifier(Classifier):
    
    def __init__(self):
        self.clf = None
    
    def store(self, model_path: Path):
        joblib.dump(self.clf, str(model_path))
    
    @classmethod
    def restore(cls, model_path: Path):
        result = cls()
        result.clf = joblib.load(str(model_path))
        return result
    
    def train(self, data):
        data = random.shuffle(random)
        y, X = zip(*data)
        self.clf.fit(X, y)
    
    def is_match(self, sample) -> bool:
        return self.clf.predict([sample])[0]