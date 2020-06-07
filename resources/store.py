from flask_restful import Resource

from models.store import StoreModel

EXISTS_ERROR = "{} already exists"
STORE_NOT_FOUND = "Store not found"
SAVE_ERROR = "An error occurred while saving {}"
STORE_DELETED = "Store deleted"


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json(), 200
        return {"message": STORE_NOT_FOUND}, 404

    @classmethod
    def post(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return {"message": EXISTS_ERROR.format(name)}, 400
        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {"message": SAVE_ERROR}, 500

        return store.json(), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {"message": STORE_DELETED}, 200
        return {"message": STORE_NOT_FOUND.format(name)}, 404


class StoreList(Resource):
    @classmethod
    def get(cls):
        return [store.json() for store in StoreModel.find_all()]
