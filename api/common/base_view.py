from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.middleware import get_user
from django.utils.functional import SimpleLazyObject
from .authenticate_config import authentication_staff
from .cookies_serializer import CookiesSerializer
from .cookies import Cookies


class BaseAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = None
    pagination_class = None
    serializer_many = False

    def check_permissions(self, request):
        pass
        
    def authenticate(self, request):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        auth = JWTAuthentication()
        auth = auth.authenticate(request)
        if auth:
            request.user = auth[0]

    def get_response(self, request=None, results=None, serializer=None, many=False):
        

        if serializer is not None:
            data = {
                'code': 0,
                'msg': 'success',
                'data': results,
            }
            
            if self.pagination_class:
                page = request['page']
                page_size = request['page_size']
        
                offset = page * page_size
                limit = page_size
                total = results.count()
                results = results[offset: offset + limit]

                serializer = serializer(data, many=many)
                data = {
                    'code': 0,
                    'msg': 'success',
                    'data': {
                        'records': serializer.data['data'],
                        'page': page,
                        'page_size': page_size,
                        'total': total
                    }
                }
            else:
                serializer = serializer(data, many=many)
                data = serializer.data
         
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {
                'code': 0,
                'msg': 'success',
                'data': results,
            }

        return Response(data=data, status=status.HTTP_200_OK)

    def dispatch(self, request, *args, **kwargs):
        """
                `.dispatch()` is pretty much the same as Django's regular dispatch,
                but with extra hooks for startup, finalize, and exception handling.
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            authenticated = self.authenticate(request=request)

            serializer = None
            if self.serializer_class is not None:
                serializer = self.serializer_class(
                    data=JSONParser().parse(request), many=self.serializer_many)
                serializer.is_valid(raise_exception=True)
            
            for permission in self.get_permissions():
                if not permission.has_permission(request, self):
                    self.permission_denied(request, message=getattr(permission, 'message', None))
                if serializer:
                    data = serializer.data
                    data.Meta = self.serializer_class.Meta if hasattr(self.serializer_class, 'Meta') else None
                    if not permission.has_object_permission(request, None, data):
                        self.permission_denied(request, message=getattr(permission, 'message', None))
    
            cookies_serializer = CookiesSerializer(data=request.COOKIES)
            cookies_serializer.is_valid(raise_exception=True)
            cookies = Cookies(**cookies_serializer.validated_data)

            response = handler(request, serializer, cookies, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(
            request, response, *args, **kwargs)
        return self.response
