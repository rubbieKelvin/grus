import pydantic

from uuid import UUID
from decimal import Decimal

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from shared.view_tools import body_tools
from shared.view_tools.paths import Api
from shared.view_tools.exceptions import ApiException, ResourceNotFound

from api.models.item import Item
from api.models.store import Store

from utils.typecheck import validateUUID


item_api = Api("item/", name="Items")


class CreateItemInput(pydantic.BaseModel):
    name: str
    brand: str | None
    category: str | None
    purchase_price: Decimal
    selling_price: Decimal
    quantity: int


@item_api.endpoint("create/<id>", method="POST", permission=IsAuthenticated)
@body_tools.validate(CreateItemInput)
def create_item(request: Request, id: str) -> Response:
    data: CreateItemInput = body_tools.get_validated_body(request)
    validateUUID(id,"Invalid store id")
    try:
        store = Store.objects.get(id=id)
        item=  Item.objects.create(
            name=data.name,
            brand=data.brand,
            category=data.category,
            purchase_price=data.purchase_price,
            selling_price=data.selling_price,
            quantity=data.quantity,
            store=store
        )
    except Store.DoesNotExist:
        raise ResourceNotFound("Store does not exist")
    return Response(item.serialize(), status=status.HTTP_201_CREATED)


@item_api.endpoint_class("<item_id>", permission=IsAuthenticated)
class ItemGetUpdateDelete:
    def check_item_id(self, item_id: str) -> str:
        try:
            UUID(item_id)
        except ValueError:
            raise ApiException("Invalid item Id")
        return item_id

    def get(self, request: Request, item_id: str) -> Response:
        item_id = self.check_item_id(item_id=item_id)
        item = Item.objects.get(id=item_id)
        return Response(item.serialize())

    class UpdateItemInput(pydantic.BaseModel):
        name: str | None = None
        brand: str | None = None
        category: str | None = None
        purchase_price: Decimal | None = None
        selling_price: Decimal | None = None
        quantity: int | None = None

    @body_tools.validate(UpdateItemInput)
    def patch(self, request: Request, item_id: str) -> Response:
        data: ItemGetUpdateDelete.UpdateItemInput = body_tools.get_validated_body(
            request=request
        )
        try:
            item = Item.objects.get(id=item_id)

            if not any(
                [
                    getattr(data, i)
                    for i in [
                        "name",
                        "brand",
                        "category",
                        "purchase_price",
                        "selling_price",
                        "quantity",
                    ]
                ]
            ):
                raise ApiException("Provide at least one parameter to be update")

            if data.name:
                item.name = data.name
            if data.brand:
                item.brand = data.brand
            if data.category:
                item.category = data.category
            if data.purchase_price:
                item.purchase_price = data.purchase_price
            if data.selling_price:
                item.selling_price = data.selling_price
            if data.quantity:
                item.quantity = data.quantity
            item.save()
        except Item.DoesNotExist:
            raise ResourceNotFound("Item does not exist")
        return Response(item.serialize())

    def delete(self, request: Request, item_id: str) -> Response:
        item_id = self.check_item_id(item_id=item_id)
        try:
            item: Item = Item.objects.get(id=item_id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Item.DoesNotExist:
            raise ResourceNotFound("Item does not exist")


@item_api.endpoint("getList/<store_id>", method="GET", permission=IsAuthenticated)
def getItems(request: Request, store_id: str) -> Response:
    validateUUID(store_id, "Invalid Store id")

    try:
        store = Store.objects.get(id=store_id)
        items = Item.objects.filter(store=store)
    except Store.DoesNotExist:
        raise ApiException("Invalid Store Id")

    return Response([item.serialize() for item in items])
