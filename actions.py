from abc import ABC, abstractmethod
import pychromecast
from uuid import UUID

class Action(ABC):
    
    def __init__(self):
        self.prepare()
    
    def prepare(self):
        pass
    
    @abstractmethod
    def run(self):
        pass
    
    def got_overruled(self):
        raise NotImplementedError()

class PrintGreeting(Action):
    
    def run(self):
        print("Hello, snapper!")
    
    def got_overruled(self):
        answer = query_yes_no("Was this a snap?")
        return answer

    @staticmethod
    def query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.
        
        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
                It must be "yes" (the default), "no" or None (meaning
                an answer is required of the user).
        
        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)
        
        while True:
            print(question + prompt)
            choice = input().lower()
            if default is not None and choice == "":
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                print("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

class ToggleChromecast(Action):
    
    def __init__(self, name=None, uuid=None):
        self.name = name
        self.uuid = UUID(uuid) if uuid is not None else None
        self.cast = None
        
        super().__init__()
    
    def discover_chromecast(self):
        result = None
        
        casts, browser = pychromecast.get_chromecasts()
        # select our chromecast
        for cast in casts:
            # filter by name
            if self.name is not None:
                name = cast.cast_info.friendly_name
                if self.name == name:
                    result = cast
                else:
                    result = None
                    continue
                
            # filter by uuid
            if self.uuid is not None:
                if self.uuid == cast.uuid:
                    result = cast
                else:
                    result = None
                    continue
                
        if result is None:
            raise RuntimeError(f"could not find chromecast {self.name} {self.uuid}")
        
        # wait for setting up a session with the found cast
        result.wait()
        
        return result
            
    def prepare(self):
        self.cast = self.discover_chromecast()
    
    def run(self):
        media = self.cast.media_controller
        
        # is there any playback running?
        if media.is_active:
            # is the media actually playing?
            if media.is_playing:
                # yes: pause
                media.pause()
                print("Playback paused.")
            else:
                # no: resume
                media.play()
                print("Playback resumed.")
    
    __call__ = run
        
        
            
            
        
        