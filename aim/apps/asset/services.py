from rest_framework import status

from .models import AssetType, Asset, AssetStatus
from aim.apps.common.base_service import BaseService, ServiceException
from aim.apps.common.cookies import Cookies


# Asset services
from ..trading.models import RegisterBuy, RegisterBuyStatus, RegisterSell, RegisterSellStatus


class AssetCreateService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        return Asset.objects.create(created_by=cookies.id, update_by=cookies.id, **kwargs)


class AssetFilterService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        asset = Asset(**kwargs)
        q = Asset.objects.filter(is_deleted=False)

        if asset.name is not None:
            q = q.filter(name__icontains=asset.name)

        if asset.address is not None:
            q = q.filter(address__icontains=asset.address)

        if asset.description is not None:
            q = q.filter(description__icontains=asset.description)

        if asset.asset_type_id is not None:
            q = q.filter(asset_type_id=asset.asset_type_id)

        if asset.asset_status_id is not None:
            q = q.filter(asset_status_id=asset.asset_status_id)

        return q.order_by('-created_at')


class AssetGetService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        try:
            return Asset.objects.get(**kwargs)
        except Asset.DoesNotExist as e:
            self.exception = e
            self.status = status.HTTP_404_NOT_FOUND
            raise ServiceException


class AssetUpdateService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        try:
            id = kwargs.pop('id', None)
            Asset.objects.filter(pk=id).update(update_by=cookies.id, **kwargs)
        except Asset.DoesNotExist as e:
            self.exception = e
            self.status = status.HTTP_404_NOT_FOUND
            raise ServiceException


class AssetDeleteService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        try:
            id = kwargs.pop('id', None)
            return Asset.objects.filter(pk=id).update(is_deleted=True, update_by=cookies.id)
        except Asset.DoesNotExist as e:
            self.exception = e
            self.status = status.HTTP_404_NOT_FOUND
            raise ServiceException


class AssetGetNewService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        new_register_buys = RegisterBuy.objects.filter(register_buy_status=RegisterBuyStatus.NEW, is_deleted=False)
        asset_id_list = list(map(lambda r: r.asset_id, new_register_buys))
        q = Asset.objects.filter(is_deleted=False, asset_status_id=1).exclude(id__in=asset_id_list)

        return q.order_by('-created_at')


class AssetGetBuyingService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        new_register_buys = RegisterBuy.objects.filter(register_buy_status=RegisterBuyStatus.NEW, is_deleted=False)
        asset_id_list = list(map(lambda r: r.asset_id, new_register_buys))
        q = Asset.objects.filter(is_deleted=False, asset_status_id=1, id__in=asset_id_list)

        return q.order_by('-created_at')


class AssetGetOwningService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        register_sells = RegisterSell.objects.filter(is_deleted=False).exclude(
            register_sell_status=RegisterSellStatus.APPROVED)
        asset_id_list = list(map(lambda r: r.asset_id, register_sells))
        q = Asset.objects.filter(is_deleted=False, asset_status_id=2).exclude(id__in=asset_id_list)

        return q.order_by('-created_at')


class AssetGetTransferringService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        register_sells = RegisterSell.objects.filter(is_deleted=False).exclude(
            register_sell_status=RegisterSellStatus.APPROVED)
        asset_id_list = list(map(lambda r: r.asset_id, register_sells))
        q = Asset.objects.filter(is_deleted=False, asset_status_id=2, id__in=asset_id_list)

        return q.order_by('-created_at')


# Asset type services
class AssetTypeGetAllService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        return AssetType.objects.filter(is_deleted=False)


class AssetTypeGetService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        try:
            return AssetType.objects.get(**kwargs)
        except AssetType.DoesNotExist as e:
            self.exception = e
            self.status = status.HTTP_404_NOT_FOUND
            raise ServiceException


# Asset type services
class AssetStatusGetAllService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        return AssetStatus.objects.filter(is_deleted=False).order_by('id')


class AssetStatusGetService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        try:
            return AssetStatus.objects.get(**kwargs)
        except AssetStatus.DoesNotExist as e:
            self.exception = e
            self.status = status.HTTP_404_NOT_FOUND
            raise ServiceException
