from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity
from marshmallow import ValidationError

from models.item import ItemModel
from schemas.item import ItemSchema

EXISTS_ERROR = "{} already exists"
ITEM_NOT_FOUND = "Item not found"
SAVE_ERROR = "An error occurred while saving {}"
ITEM_DELETED = "Item deleted"

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return {"message": EXISTS_ERROR.format("item")}, 400
        item_json = request.get_json()
        item_json["name"] = name

        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.messages, 500

        try:
            item.save_to_db()
        except:
            return {"message": SAVE_ERROR}

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def put(cls, name: str):
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = item_json["price"]
            item.store_id = item_json["store_id"]
        else:
            item_json["name"] = name
            try:
                item_schema.load(item_json)
            except ValidationError as err:
                return err.messages, 400

        item.save_to_db()

        return item_schema.dump(item), 200

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}, 200
        return (
            {"message": ITEM_NOT_FOUND},
            404,
        )


class ItemList(Resource):
    @classmethod
    @jwt_optional
    def get(cls):
        user_id = get_jwt_identity()
        items = item_list_schema.dump(ItemModel.find_all())
        if user_id:
            return {"items": items}, 200
        return (
            {
                "items": [item["name"] for item in items],
                "message": "Not logged in - only returning item names",
            },
            200,
        )
