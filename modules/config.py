from datetime import datetime

class Config:
    slots = [
        'input folder',
        'output folder',
        'length',

        'output file',
        'output height',
        'output width',
    ]

    def __init__(self, args):
        self.d = {}

        for key in args:
            self.d[key] = args[key]
                
        currDatetime = datetime.now()
        dt_string = currDatetime.strftime("%d-%m-%Y %H-%M-%S")
        self.d['output file'] = dt_string

        self.d['output height'] = 1080
        self.d['output width'] = 1920

        # Confirm all slots are filled
        for slot in self.slots:
            assert slot in self.d

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key, val):
        self.d[key] = val