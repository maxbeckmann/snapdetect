import pyaudio
import types
import numpy as np
import wave
from pathlib import Path
import hashlib
#import queue

class AudioSnippet(list):
    
    DURATION = 0.250 # ms
    SAMPLERATE = 44100
    SAMPLETYPE = np.int16
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        assert len(self) == self.desired_len()
    
    @classmethod
    def desired_len(cls):
        return int(cls.DURATION * cls.SAMPLERATE)
    
    def write_to_wav(self, path: Path):
        bin_frames = np.asarray(self, dtype=self.SAMPLETYPE).tostring()
        
        m = hashlib.sha256()
        m.update(bin_frames)
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / f"{str(m.hexdigest())}.wav"
        
        with wave.open(str(file_path),'wb') as obj:
            obj.setnchannels(1)
            obj.setsampwidth(2)
            obj.setframerate(self.SAMPLERATE)
            obj.writeframes(bin_frames)

class AudioInputDevice:
    def __init__(self, device_id, snippet_type = AudioSnippet):
        self.device_id = device_id
        self.channels = 1
        self.snippet_type = snippet_type
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.keep_listening = None
    
    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        
    def listen(self):
        self.stream = self.audio.open(
            rate=self.snippet_type.SAMPLERATE,
            format=pyaudio.paInt16,
            channels=self.channels,
            input=True,
            input_device_index=self.device_id,
        )        
        
        self.keep_listening = True
        while self.keep_listening:
            frames = np.array([], dtype=np.int16)
            desired_frames = self.snippet_type.desired_len()
            while len(frames) < (desired_frames * 2):
                data = self.stream.read(desired_frames, exception_on_overflow = False)
                print(len(data))
                a = np.fromstring(data,dtype=np.int16)[0::self.channels]
                frames = np.concatenate((frames, a))
            yield frames[:desired_frames]#AudioSnippet(frames[:desired_frames])
            frames = frames[desired_frames:]
        
        self.stop_stream()
        
    def terminate(self):
        if self.stream is not None:
            self.stop_stream()
        self.p.terminate()

#import sounddevice as sd

# class SounddeviceAudioInputDevice:
#     def __init__(self, device_id, snippet_type = AudioSnippet):
#         self.device_id = device_id
#         self.channels = 1
#         self.snippet_type = snippet_type
#         self.keep_listening = None
#         
#     def listen(self):
#         q = queue.Queue()
#         def callback(indata, frames, time, status):
#             """This is called (from a separate thread) for each audio block."""
#             indata = indata[:, 0]
#             print(status)
#             if any(indata):
#                 print(len(indata))
#                 q.put(indata)
#             else:
#                 print('no input')
#             
#         desired_frames = self.snippet_type.desired_len()
#         with sd.InputStream(samplerate=self.snippet_type.SAMPLERATE, dtype=np.int16, device=self.device_id, blocksize=desired_frames,
#         channels=1, callback=callback) as stream:
#             self.keep_listening = True
#             while self.keep_listening:
#                 frames = np.array([], dtype=np.int16)
#                 desired_frames = self.snippet_type.desired_len()
#                 while len(frames) < (desired_frames * 2):
#                     data = q.get()
#                     frames = np.concatenate((frames, data))
#                 yield frames[:desired_frames]#AudioSnippet(frames[:desired_frames])
#                 frames = frames[desired_frames:]
#             
#     def terminate(self):
#         pass
# 
def list_available_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
            
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            yield i, p.get_device_info_by_host_api_device_index(0, i)