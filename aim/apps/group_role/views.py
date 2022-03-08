"""
    Define of role views
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aim.apps.group_role.group_role_service import RoleService
from aim.apps.common.authenticate_config import authentication_staff


@csrf_exempt
@authentication_staff('list_role')
def list_role(request):
    """
    list role
    :param request:
    :return:
    """
    role_service = RoleService()

    response = role_service.list(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('get_list_screen')
def get_list_screen(request):
    """
    Get list screen
    :param request:
    :return:
    """
    role_service = RoleService()

    response = role_service.get_list_screen(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('detail_group_role')
def detail_group_role(request, id):
    """
    Detail role
    :param request:
    :return:
    """
    role_service = RoleService()

    response = role_service.detail_group_role(request, id)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('add_group_role')
def add_group_role(request):
    """
    Add group role
    :param request:
    :return:
    """
    role_service = RoleService()

    response = role_service.add_group_role(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('update_group_role')
def update_group_role(request):
    """
    Update role
    :param request:
    :return:
    """
    role_service = RoleService()

    response = role_service.update_group_role(request)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('delete_group_role')
def delete_group_role(request, id):
    """
    Delete group role
    :param request:
    :return:
    """
    role_service = RoleService()

    response = role_service.delete_group_role(request, id)

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
@authentication_staff('get_group_role_option')
def get_group_role_option(request):
    """
    Get group role option
    :param request:
    :return:
    """
    role_service = RoleService()

    response = role_service.get_group_role_option(request)

    return JsonResponse(response.__dict__, status=response.status)
