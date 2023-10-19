from rest_framework.request import Request
from rest_framework.response import Response
from shared.view_tools import body_tools
from shared.view_tools.paths import Api
from uuid import UUID
from shared.view_tools.exceptions import ApiException
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from api.models.item import Item
from api.sr import ItemSerializer
import pydantic

item_api = Api("item/", name="Items")


class CreateItemInput(pydantic.BaseModel):
    name: str
    brand: str | None
    category: str | None
    purchase_price: Decimal
    selling_price: Decimal
    quantity: int

class UpdateItemInput(pydantic.BaseModel):
    name: str | None
    brand: str | None
    category: str | None
    purchase_price: Decimal | None
    selling_price: Decimal | None
    quantity: int | None


def create_item(request: Request) -> Response:
    return Response()


@item_api.endpoint_class("<item_id>", permission=IsAuthenticated)
class ItemCreateUpdateDelete:
    def check_item_id(self, item_id: str) -> str:
        try:
            UUID(item_id)
        except ValueError:
            raise ApiException("Invalid item_id string")
        return item_id
    
    def get(self, request: Request, item_id: str) -> Response:
        item_id= self.check_item_id(item_id=item_id)
        item = Item.objects.get(id=item_id)
        sr = ItemSerializer(item, request)
        return Response(sr())
    
    @body_tools.validate(UpdateItemInput)
    def update(self, request: Request, item_id: str) -> Response:
        data: UpdateItemInput = body_tools.get_validated_body(request=request)

        item = Item.objects.get(id=item_id)
        if (not data.name and not data.brand and not data.category and not data.purchase_price and not data.selling_price and not data.quantity):
            raise ApiException("Provide atlest one parameter to be update")
        
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
        return Response()

    def delete(self, request: Request, item_id: str) -> Response:

        return Response()
