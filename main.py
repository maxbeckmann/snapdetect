import typer
from audio import AudioInputDevice, list_available_devices, AudioSnippet
from actions import ToggleChromecast, PrintGreeting
import benchmark as train
from sklearn import svm
import data
import joblib
import classifier
import time, math

app = typer.Typer()

@app.command()
def list_devices():
    for id, device in list_available_devices():
        print("Input Device id ", id, " - ", device.get('name'))

@app.command()
def listen(device_id: int, learn: bool = False, cast: str = None, record: bool = False):
    if cast is None:
        if learn:
            action = None
        else:
            action = PrintGreeting()
    else:
        action = ToggleChromecast(cast)
        print(f"In control of {cast}")
        
    audio = AudioInputDevice(device_id)
    clf = classifier.SimpleSVMClassifier.restore("model.joblib")
    
    try:
        print("listening for a snap")
        for snippet in audio.listen():
            prep = train.preprocessor_abs_hfft(snippet)
            if clf.is_match(prep):
                action.run()
                if record:
                    AudioSnippet(snippet).write_to_wav("rec")
                
    except KeyboardInterrupt:
        print("Stopping.")


@app.command()
def record(device_id: int, dir: str = "rec", seconds: float = 1.0, delay: int = 0):
    if delay > 0:
        print(f"Waiting {delay} seconds...")
        time.sleep(delay)
    
    audio = AudioInputDevice(device_id)
    print(f"Recording for {seconds} seconds, yielding {math.ceil(seconds / audio.snippet_type.DURATION)} snippets")
    for i, snippet in enumerate(audio.listen(), start=1):
        AudioSnippet(snippet).write_to_wav(dir)
        if i * audio.snippet_type.DURATION >= seconds:
            break
        
@app.command()
def train_model():
    clf = svm.SVC()
    train_data = list(data.load(preprocess=train.preprocessor_abs_hfft))
    clf = train.train(clf, train_data)
    joblib.dump(clf, "model.joblib")

if __name__ == "__main__":
    app()