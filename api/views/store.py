import typing
import pydantic

from api.models.store import Store
from api.models.user import User

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from uuid import UUID
from shared.view_tools import exceptions
from shared.view_tools import body_tools
from shared.view_tools.paths import Api


store_api = Api("store/", name="Store")

class CreateStoreInput(pydantic.BaseModel):
    store_name: str
    store_description: str

@store_api.endpoint("create", method="POST",permission=IsAuthenticated)
@body_tools.validate(CreateStoreInput)
def create_store(request: Request) -> Response:
    data: CreateStoreInput = body_tools.get_validated_body(request)
    user: User = typing.cast(request.user, User)

    store = Store.objects.create(store_name=data.store_name, store_description=data.store_description, owner=user,)

    return Response(status=status.HTTP_201_CREATED)

class UpdateStoreInput(pydantic.BaseModel):
    store_name: str | None
    store_description: str | None

@store_api.endpoint("update<id>", method="PATCH", permission=IsAuthenticated)
@body_tools.validate(UpdateStoreInput)
def update_store(request: Request, id: str) -> Response:
    data: UpdateStoreInput = body_tools.get_validated_body(request)
    if not data.store_name and not data.store_description:
        raise exceptions.ApiException("Pass in atlest one")
    
    checkUUID(id=id, value="Store")
    
    try:
        store: Store = Store.objects.get(id=id)
        
        if data.store_name:
            store.name = data.store_name
            store.save()
        
        if data.store_description:
            store.description = data.store_description
            store.save()
        return Response(store.serialize())
    
    except Store.DoesNotExist:
        raise exceptions.ResourceNotFound("Store does not exist")
    

@store_api.endpoint("delete<id>", method="DELETE", permission=IsAuthenticated)
def delete_store(request: Request, id: str) -> Response:
    checkUUID(id=id,value="Store")

    try:
        store: Store = Store.objects.get(id=id)
        store.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    except Store.DoesNotExist:
        raise exceptions.ResourceNotFound("Store does not exist")


@store_api.endpoint("get", method="POST",permission=IsAuthenticated)
def get_stores(request: Request) -> Response:
    user: User = typing.cast(request.user, User)
    stores = Store.objects.filter(owner=user)
    return Response([
        store.serialize() for store in stores
    ])
            
def checkUUID(id: str, value: str):
    try:
        UUID(id)
    except ValueError:
        raise exceptions.ApiException(f"Invalid {value} Id")

