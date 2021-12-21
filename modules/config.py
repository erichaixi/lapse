from datetime import datetime
import json

class Config:
    slots = {
        'input folder': None,
        'output folder': None,
        'length': None,

        'output file': None,
        'output height': 1080,
        'output width': 1920,
    }

    def __init__(self, args=None):
        self.d = {}
        for key in self.slots:
            self.d[key] = self.slots[key]

        if args:
            for key in args:
                self.d[key] = args[key]
                
        currDatetime = datetime.now()
        dt_string = currDatetime.strftime("%d-%m-%Y %H-%M-%S")
        self.d['output file'] = dt_string

    def __getitem__(self, key):
        print(key)
        return self.d[key]

    def __setitem__(self, key, val):
        self.d[key] = val

    def __contains__(self, key):
        return key in self.d

    def toJson(self):
        return json.dumps(self.d)