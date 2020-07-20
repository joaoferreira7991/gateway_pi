import json
import datetime

class DateTimeEncoder(json.JSONEncoder):
    # Override the default method
    def default(self, obj):
        # If object is of datetime then
        # transform its values into a dictionary.
        if isinstance(obj, datetime.datetime):
            return {
                '__type__' : 'datetime',
                'year' : obj.year,
                'month' : obj.month,
                'day' : obj.day,
                'hour' : obj.hour,
                'minute' : obj.minute,
                'second' : obj.second,
                'microsecond' : obj.microsecond                
            }

class DateTimeDecoder(json.JSONDecoder):
    
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.decode_datetime,
                                *args, **kwargs)

    def decode_datetime(self, o):
        if '__type__' not in o:
            return o

        type = o.pop('__type__')
        try:
            obj = datetime.datetime(**o)
            return obj
        except:
            o['__type__'] = type
            return o
        