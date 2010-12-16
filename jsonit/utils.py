import os

from django.http import HttpResponse
from django.template import RequestContext, loader


def ajax_aware_render(request, template_list, extra_context=None, **kwargs):
    if isinstance(template_list, basestring):
        template_list = [template_list]
    if request.is_ajax():
        new_template_list = []
        for name in template_list:
            new_template_list.append('%s.ajax.%s' % os.path.splitext(name))
            new_template_list.append(name)
        template_list = new_template_list
    c = RequestContext(request, extra_context)
    t = loader.select_template(template_list)
    return HttpResponse(t.render(c), **kwargs)
