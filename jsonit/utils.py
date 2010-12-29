import os

from django.http import HttpResponse
from django.template import Context, RequestContext, loader


def ajax_aware_render(request, template_list, context=None, **kwargs):
    """
    Render a template, using a different one automatically for AJAX requests.
    
    :param template_list: Either a template name or a list of template names.
    :param context: Optional extra context to pass to the template.
    
    For AJAX requests, the template list is altered to look for alternate
    templates first and the ``is_ajax`` context variable is set to ``True``.
    
    For example, if ``template_list`` was set to
    ``['custom/login.html', 'login.html']``, then an AJAX request will change
    this to::
    
        ['custom/login.ajax.html', 'login.ajax.html',
         'custom/login.html', 'login.html']
    """
    if not isinstance(context, Context):
        context = RequestContext(request, context)
    if isinstance(template_list, basestring):
        template_list = [template_list]
    if request.is_ajax():
        ajax_template_list = []
        for name in template_list:
            ajax_template_list.append('%s.ajax%s' % os.path.splitext(name))
        template_list = ajax_template_list + list(template_list)
        context['is_ajax'] = True
        context['current_url'] = request.get_full_path()
    template = loader.select_template(template_list)
    return HttpResponse(template.render(context), **kwargs)
