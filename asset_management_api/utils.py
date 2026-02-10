# utils.py

import requests

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def get_location_from_ip(ip):
    # Ignore local IPs
    if not ip or ip in ("127.0.0.1", "::1"):
        return {}

    try:
        response = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=5
        )

        if response.status_code != 200:
            return {}

        data = response.json()

        return {
            "ip": ip,
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }

    except requests.RequestException:
        return {}


# import requests 

# def get_ip(request):     #a function that takes Django request object.
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')     #Checks if request contains header:
#                                                                    #This header contains the real client IP.
#     if x_forwarded_for:                             #If header exists:     
#         ip = x_forwarded_for.split(',')[0].strip()          #.split(',') → breaks a string into a list using comma,
#                                                     #[0] → takes first element from that list, Used to extract first IP address from multiple IPs
#                                                     #It may contain multiple IPs:
#                                                     #"8.8.8.8, 192.168.1.1"
#                                                     #We take the first IP → real client IP
    
    
#     else:                                           
#         ip = request.META.get('REMOTE_ADDR')        #request.META.get() is used in Django to read information from the HTTP request headers and server environment       
#                                                     #it tells you:who sent the request,from where using, which browser,which method (GET/POST) and much more.
    
#     print("ip is ----->",ip)
#     return ip

# def get_location_from_ip(ip):
#     try:
#         response = requests.get(
#             f"https://ipapi.co/{ip}/json/",
#             timeout=5
#         )

#         if response.status_code != 200:
#             return {}

#         data = response.json()

#         return {
#             "ip": ip,
#             "city": data.get("city"),
#             "region": data.get("region"),
#             "country": data.get("country_name"),
#             "latitude": data.get("latitude"),
#             "longitude": data.get("longitude"),
#         }

#     except Exception as e:
#         print("Geo-IP error:", e)
#         return {}






