import datetime
from unittest import TestCase

from django.contrib import messages
from django.contrib.messages.constants import DEFAULT_TAGS
from django.contrib.messages.storage import base as messages_base
from django.contrib.messages.storage.session import SessionStorage
from django.http import HttpRequest
from django.utils.functional import lazy
from django.utils import six

from jsonit.http import JSONResponse
from jsonit.encoder import encode


class BaseTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'


class JSONResponseTest(BaseTest):

    def setUp(self):
        self.request = HttpRequest()
        self.request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

    def test_success(self):
        response = JSONResponse(self.request)
        self.assertEqual(
            response.content,
            '{"messages": [], "details": {}, "success": true}'
        )

    def test_not_success(self):
        response = JSONResponse(self.request, success=False)
        self.assertEqual(
            response.content,
            '{"messages": [], "details": {}, "success": false}'
        )

    def test_details(self):
        response = JSONResponse(self.request, details={'test': 1})
        self.assertEqual(
            response.content,
            '{"messages": [], "details": {"test": 1}, "success": true}'
        )


class MessageTest(BaseTest):

    def setUp(self):
        super(MessageTest, self).setUp()
        self.request.session = {}
        self._old_LEVEL_TAGS = messages_base.LEVEL_TAGS
        messages_base.LEVEL_TAGS = DEFAULT_TAGS
        self.request._messages = SessionStorage(self.request)

    def tearDown(self):
        messages_base.LEVEL_TAGS = self._old_LEVEL_TAGS

    def test_messages(self):
        messages.info(self.request, 'Hello')
        response = JSONResponse(self.request)
        self.assertEqual(
            response.content,
            '{"messages": [{"message": "Hello", "class": "info"}], '
            '"details": {}, "success": true}'
        )


class EncoderTest(TestCase):

    def test_lazy(self):
        test_msg = lazy(lambda: 'Test!', six.text_type)
        self.assertEqual(encode(test_msg()), '"Test!"')

    def test_datetime(self):
        self.assertEqual(encode(datetime.datetime(1980, 1, 1, 12, 0, 5)),
                         '"1980-01-01T12:00:05"')

    def test_date(self):
        self.assertEqual(encode(datetime.date(1980, 1, 1)),
                         '"1980-01-01"')

    def test_custom_encoder(self):
        encode_dt = lambda d: d.strftime('%d %b %Y')
        self.assertEqual(encode(datetime.datetime(1980, 1, 1),
                                encoders=[(datetime.datetime, encode_dt)]),
                         u'"01 Jan 1980"')
