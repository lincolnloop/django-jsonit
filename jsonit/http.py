"""
A JSON response always returns a JSON-encoded dictionary. The dictionary
will always contain the following three keys:

success
    True or False

details
    A dictionary containing any success / failure details.

messages
    A list of message dictionaries. Each message dictionary contains a
    ``class`` (a string of HTML classes) and a ``message`` key.

An example success::

    {
        'success': True,
        'details': {},
        'messages': [
            {'class': '', 'message': 'some message'},
        ]
    }

If an exception is passed (via the ``exception`` parameter), ``details`` and
``messages`` will be emptied, ``success`` will be set to ``False``, and an
``exception`` key will be added to the response::

An example exception::

    {
        'success': False,
        'details': {},
        'messages': [],
        'exception': 'error message'
    }

If the project's ``DEBUG`` setting is ``False``, exception will just be set to
``True``.
"""
from django import http
from django.contrib import messages

from jsonit.encoder import encode


class JSONResponse(http.HttpResponse):
    """
    Return a JSON encoded HTTP response.
    """

    def __init__(self, request, details=None, success=True, exception=None):
        """
        :param request: The current ``HTTPRequest``. Required so that any
            ``django.contrib.messages`` can be retrieved.
        :param details: An optional dictionary of extra details to be encoded
            as part of the response.
        :param success: Whether the request was considered successful. Defaults
            to ``True``.
        :param exception: Used to build an exception JSON response. Not
            usually needed unless the need to handle exceptions manually
            arises. See the :class:`JSONExceptionMiddleware` to handle AJAX
            exceptions automatically.
        :returns: An HTTPResponse containing a JSON encoded dictionary with a
            content type of ``application/json``.
        """
        self.request = request
        self.success = success
        self.details = details or {}
        assert isinstance(self.details, dict)
        super(JSONResponse, self).__init__(content=self.build_json(exception),
                                           content_type='application/json')

    def build_json(self, exception=None):
        content = {
            'success': self.success,
            'details': self.details,
            'messages': [],
        }
        if exception is not None:
            content['success'] = False
            content['details'] = {}
            if hasattr(exception, 'message'):
                exception = exception.message
            else:
                exception = '%s: %s' % (_('Internal error'), exception)
            content['exception'] = exception
        elif self.request:
            content['messages'] = self.get_messages()
        try:
            return encode(content)
        except Exception, e:
            if exception is not None:
                raise
            return self.build_json(e)

    def get_messages(self):
        return list(messages.get_messages(self.request))


class JSONFormResponse(JSONResponse):
    """
    Return a JSON response, handling form errors.
    
    Accepts a ``forms`` keyword argument which should be a list of forms to
    be validated.
    
    If any of the forms contain errors, a ``form_errors`` key
    will be added to the ``details`` dictionary, containing the HTML ids of
    fields and a list of messages for each.

    The ``__all__`` key is used for any form-wide error messages.

    An example failure::
    
        {
            'success': False,
            'details': {
                'form_errors': {
                    '__all__': ['some error'],
                    'some_field_id': ['some error'],
                }
            },
            'messages': [
                {'class': 'error', 'message': 'some message'},
                {'class': '', 'message': 'some message'},
            ]
        }
    """

    def __init__(self, *args, **kwargs):
        """
        In addition to the standard :class:`JSONResponse` arguments, one
        additional keyword argument is available.
        
        :param forms: A list of forms to validate against.
        """
        self.forms = kwargs.pop('forms')
        super(JSONFormResponse, self).__init__(*args, **kwargs)

    def build_json(self, *args, **kwargs):
        """
        Check for form errors before building the JSON dictionary. 
        """
        self.get_form_errors()
        return super(JSONFormResponse, self).build_json(*args, **kwargs)

    def get_form_errors(self):
        """
        Validate the forms, adding the ``form_errors`` key to :attr:`details`
        containing any form errors.
        
        If any of the forms do not validate, :attr:`success` will be set to
        ``False``.
        """
        forms = self.forms or ()
        for form in forms:
            for field, errors in form.errors.items():
                self.success = False
                if field is not '__all__':
                    field = form[field].auto_id
                if field:
                    form_errors = self.details.setdefault('form_errors', {})
                    error_list = form_errors.setdefault(field, [])
                    error_list.extend(errors)
