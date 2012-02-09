import os

from jsonit.http import JSONFormResponse, JSONResponse


class AJAXTemplateResponseMixin(object):
    """
    A mixin usually used with a Django's ``TemplateResponseMixin`` that extends
    the template list for AJAX requests.

    For an AJAX request the template list is altered to look for alternate
    templates first and the ``is_ajax`` context variable is set to ``True``.
    The format of the names of these alternate templates are defined in the
    :attr:`ajax_template_format` attribute.

    For example, if a view was going to pick a template from
    ``['custom/login.html', 'login.html']``, then an AJAX request will change
    the template list to::

        ['custom/login.ajax.html', 'login.ajax.html',
         'custom/login.html', 'login.html']

    For views which use :meth:`get_context_data`, two extra context variables
    are added for AJAX requests:

    ``is_ajax``
        Set to ``True``

    ``current_url``
        The current URL, useful for explicitly setting HTML form actions.
    """
    ajax_template_format = '%(name)s.ajax%(ext)s'

    def get_template_names(self, *args, **kwargs):
        """
        Returns a list of template names to be used for the request. Must
        return a list. May not be called if render_to_response is overridden.
        """
        template_list = super(AJAXTemplateResponseMixin, self)\
                                        .get_template_names(*args, **kwargs)
        if self.request.is_ajax():
            ajax_template_list = []
            for template_name in template_list:
                name, ext = os.path.splitext(template_name)
                ajax_template_list.append(self.ajax_template_format %
                                          {'name': name, 'ext': ext})
            template_list = ajax_template_list + list(template_list)
        return template_list

    def get_context_data(self, *args, **kwargs):
        data = super(AJAXTemplateResponseMixin, self).get_context_data(*args,
                                                                    **kwargs)
        if self.request.is_ajax():
            data['is_ajax'] = True
            data['current_url'] = self.request.get_full_path()
        return data


class JSONResponseMixin(object):
    """
    A mixin for views which may want to return a JSON response for AJAX
    initiated requests.

    The :attr:`json_success` attribute is used as the JSON response success
    value (defaults to ``True``).
    """
    json_success = True

    def get_json_response(self, response, details=None, redirect=None):
        """
        Override a standard response for AJAX initiated requests, instead
        returning a JSON response.

        :param response: The standard response to return if this is not an AJAX
            initiated request.
        :param details: A dictionary of extra JSON details to return.
        :param redirect: The URL to send along as part of successful JSON
            responses.
        :param forms: The forms to pass to the :class:`JSONFormResponse`. If no
            forms are provided (more specifically, if :meth:`get_forms` doesn't
            return any) then a :class:`JSONResponse` will be used instead.
        """
        if not self.request.is_ajax():
            return response
        kwargs = {'details': details}
        if self.json_success is not None:
            kwargs['success'] = self.json_success
        if redirect is not None:
            kwargs['redirect'] = redirect
        forms = self.get_forms()
        if forms:
            json_response_class = JSONFormResponse
            kwargs['forms'] = forms
        else:
            json_response_class = JSONResponse
        return json_response_class(self.request, **kwargs)

    def get_forms(self):
        return []


class AJAXMixin(AJAXTemplateResponseMixin, JSONResponseMixin):
    """
    A mixin that will look for AJAX alternatives to templates and that provides
    helper methods for creating JSON responses.

    AJAX POST requests will receive a JSON response.

    If the :attr:`ajax_redirect` attribute is set to ``True`` (default), a
    successful JSON response will include the redirection URL.
    """
    ajax_redirect = True

    def post(self, request, *args, **kwargs):
        """
        If the request was AJAX initiated, return a :class:`JSONFormResponse`.
        """
        response = super(AJAXMixin, self).post(request, *args, **kwargs)
        if not request.is_ajax():
            return response
        if self.ajax_redirect and str(response.status_code) in ('301', '302'):
            kwargs['redirect'] = response['Location']
        return self.get_json_response(response, **kwargs)


class AJAXFormMixin(AJAXMixin):
    """
    A mixin for Django generic form views which will return a
    :class:`JSONFormResponse` for AJAX initiated ``POST`` requests (and also
    look for alternate AJAX versions of templates).
    """

    def get_forms(self):
        forms = super(AJAXFormMixin, self).get_forms()
        form_class = self.get_form_class()
        forms.append(self.get_form(form_class))
        return forms


# Legacy name
AJAXFormView = AJAXFormMixin
