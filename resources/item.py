from typing import Dict, List
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, fresh_jwt_required
from marshmallow import ValidationError
from models.item import ItemModel
from schemas.item import ItemSchema

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)

NAME_ALREADY_EXISTS = "An item with name {} already exists."
ERROR_INSERTING = "An error ocurred while inserting the item"
ITEM_NOT_FOUND = "Item not found"
ITEM_DELETED = "Item deleted"


class Item(Resource):
    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str) -> None:
        if ItemModel.find_by_name(name):
            return ({"message": NAME_ALREADY_EXISTS.format(name)}, 400)

        item_json = request.get_json()
        item_json["name"] = name

        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.messages, 400

        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return item_schema.dump(item), 201

    @jwt_required
    def delete(self, name: str) -> None:
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}
        return {"message": ITEM_NOT_FOUND}

    @classmethod
    def put(cls, name: str) -> None:
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item is None:
            item_json["name"] = name
            try:
                item = item_schema.load(item_json)
            except ValidationError as err:
                return err.messages, 400
        else:
            item.price = item_json["price"]

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
