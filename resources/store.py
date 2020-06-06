from flask_restful import Resource

from models.store import StoreModel


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json(), 200
        return {"message": "Store not found"}, 404

    def post(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return {"message": "Error, store with name '{}' already exists".format(name)}, 400
        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {"message": "An error occurred while saving the new store"}, 500

        return store.json(), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {"message": "item deleted"}, 200
        return {"message": "Error, store with name '{}' does not exist".format(name)}, 404


class StoreList(Resource):

    def get(self):
        return [store.json() for store in StoreModel.find_all()]
