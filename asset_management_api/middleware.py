from .utils import get_location_from_ip, get_ip

class LocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_ip(request)
        location = get_location_from_ip(ip)

        request.ip = ip
        request.location = location

        response = self.get_response(request)
        return response
    
   