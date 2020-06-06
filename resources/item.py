from flask_restful import Resource, reqparse

from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help="Price cannot be left empty"
    )

    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {"message": "Item not found"}, 404

    def post(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return {"message": "Error, item already exists"}, 400
        data = Item.parser.parse_args()
        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message", "An error occurred while saving the new item"}, 500

        return item.json(), 201

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()
        return item.json(), 200

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": "item deleted"}, 200
        return {"message": "Error, item with name '{}' does not exist".format(name)}, 404


class ItemList(Resource):

    def get(self):
        return [item.json() for item in ItemModel.find_all()]
