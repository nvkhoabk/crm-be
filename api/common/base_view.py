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
        request.user = SimpleLazyObject(lambda: get_user(request))

        return None

    def get_response(self, request=None, results=None, serializer=None, many=False):
        if self.pagination_class is not None:
            try:
                results = self.pagination_class.paginate_queryset(
                    results, request)
                serializer = serializer(results, many=many)
                return self.pagination_class.get_paginated_response(serializer.data)
            except AttributeError as e:
                return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)

        if serializer is not None:
            data = {
                'code': 0,
                'msg': 'success',
                'data': results,
            }
            if many:
                print(results)
                print(serializer(data, many=many))
            serializer = serializer(data, many=many)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

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
            for permission in self.get_permissions():
                if not permission.has_permission(request, self):
                    self.permission_denied(request, message=getattr(permission, 'message', None))

            cookies_serializer = CookiesSerializer(data=request.COOKIES)
            cookies_serializer.is_valid(raise_exception=True)
            cookies = Cookies(**cookies_serializer.validated_data)

            if self.serializer_class is not None:
                serializer = self.serializer_class(
                    data=JSONParser().parse(request), many=self.serializer_many)
                serializer.is_valid(raise_exception=True)
                response = handler(request, serializer,
                                   cookies, *args, **kwargs)
            else:
                response = handler(request, None, cookies, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(
            request, response, *args, **kwargs)
        return self.response
