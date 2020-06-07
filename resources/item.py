from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity

from models.item import ItemModel

BLANK_ERROR = "{} cannot be left blank"
EXISTS_ERROR = "{} already exists"
ITEM_NOT_FOUND = "Item not found"
SAVE_ERROR = "An error occurred while saving {}"
ITEM_DELETED = "Item deleted"


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    )

    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return {"message": EXISTS_ERROR.format("item")}, 400
        data = Item.parser.parse_args()
        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message", SAVE_ERROR.format("item")}, 500

        return item.json(), 201

    @classmethod
    @jwt_required
    def put(cls, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
            item.store_id = data["store_id"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()
        return item.json(), 200

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
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {"items": items}, 200
        return (
            {
                "items": [item["name"] for item in items],
                "message": "Not logged in - only returning item names",
            },
            200,
        )
