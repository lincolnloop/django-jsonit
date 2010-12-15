from functools import wraps

from jsonit.http import JSONResponse


def catch_ajax_exceptions(func):
    """
    Catches exceptions which occur when using an AJAX request. 
    
    These exceptions will be returned using a :class:`JSONResponse` rather than
    letting the exception propogate.
    """
    
    @wraps(func)
    def dec(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception, e:
            if request.is_ajax():
                return JSONResponse(exception=e)
            raise

    return dec
