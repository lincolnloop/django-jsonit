import datetime
import json

from django.conf import settings
from django.contrib.messages.storage.base import Message
from django.utils.functional import Promise


def encode_message(message):
    return {'tags': message.tags, 'message': message.message}


class JsonitEncoder(json.JSONEncoder):
    default_encoders = {
        Promise: unicode,
        Message: encode_message,
        datetime.datetime: lambda d: d.isoformat(),
        datetime.date: lambda d: d.isoformat(),
    }

    def __init__(self, *args, **kwargs):
        """
        In addition to the standard JSONEncoder constructor arguments, this
        class uses the following keyword arguments::

        :param extra_encoders: A dictionary of extra encoders to help convert
            objects into JSON. Each key should be a class and each value a
            conversion function for objects of that class.
        """
        self.encoders = self.default_encoders.copy()
        extra_encoders = kwargs.pop('extra_encoders', None)
        if extra_encoders:
            self.encoders.update(extra_encoders)
        super(JsonitEncoder, self).__init__(*args, **kwargs)

    def default(self, o):
        for cls, func in self.encoders.iteritems():
            if isinstance(o, cls):
                return func(o)
        super(JsonitEncoder, self).default(o)


def encode(object, encoders=None):
    """
    Encode an object into a JSON representation.

    :param object: The object to encode.
    :param encoders: An optional dictionary of encoders to help convert
        objects.

    All other parameters are passed to the standard JSON encode.
    """
    indent = settings.DEBUG and 2 or None
    return JsonitEncoder(indent=indent, extra_encoders=encoders).encode(object)
