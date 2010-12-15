from jsonit.http import JSONResponse


class JSONExceptionMiddleware(object):
    """
    Django middleware which catches any exception for AJAX requests.
    
    These exceptions will be returned using a JSONResponse rather than letting
    the exception propogate.
    """

    def process_exception(self, request, exception):
        """
        Intercept exceptions for AJAX requests. 
        """
        if request.is_ajax():
            return JSONResponse(exception=exception)
