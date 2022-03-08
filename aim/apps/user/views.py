"""
Definition of staff view.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from aim.apps.common.authenticate_config import authentication_staff
from aim.apps.common.authenticate_config import authentication_staff
from aim.apps.user.user_service import UserService


@csrf_exempt
def user_login(request):
    """
    Check user login
    :param request:
    :return:
    """
    user_service = UserService()

    response = user_service.user_login(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
def get_list_group_user(request):
    """
    Get list group user
    :param request:
    :return:
    """
    user_service = UserService()

    response = user_service.get_list_group_user(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('search_user')
def search_user(request):
    """
    Search user
    :param request:
    :return:
    """
    user_service = UserService()

    response = user_service.search_user(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('add_user')
def add_user(request):
    """
    Add user
    :param request:
    :return:
    """
    user_service = UserService()

    response = user_service.add_user(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('get_user_detail')
def get_user_detail(request, id):
    """
    Get user detail
    :param request:
    :param id:
    :return:
    """
    user_service = UserService()

    response = user_service.get_user_detail(request, id)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('update_user')
def update_user(request):
    """
    Update user
    :param request:
    :return:
    """
    user_service = UserService()

    response = user_service.update_user(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('delete_user')
def delete_user(request, id):
    """
    Delete user
    :param request:
    :param id:
    :return:
    """
    user_service = UserService()

    response = user_service.delete_user(request, id)

    return JsonResponse(response.__dict__, status=response.status)


# @csrf_exempt
# def update_pass(request):
#     """
#     Update new pass word
#     :param request:
#     :return:
#     """
#     user_service = UserService()
#
#     response = user_service.update_pass(request)
#
#     return JsonResponse(response.__dict__, status=response.status)
#
#
# @csrf_exempt
# def active_pass(request):
#     """
#     Active customer pass
#     :param request:
#     :return:
#     """
#     user_service = UserService()
#
#     response = user_service.active_user_pass(request)
#
#     return JsonResponse(response.__dict__, status=response.status)
#
#
# @csrf_exempt
# @authentication_user('change_pass_user')
# def change_pass_user(request):
#     """
#     Update new pass word
#     :param request:
#     :return:
#     """
#     user_service = UserService()
#
#     response = user_service.change_pass(request)
#
#     return JsonResponse(response.__dict__, status=response.status)



