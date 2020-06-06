from flask_restful import Resource, reqparse

from models.user import UserModel


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("username", type=str, required=True, help="A username is required")
    parser.add_argument("password", type=str, required=True, help="A password is required")

    def post(self):
        data = UserRegister.parser.parse_args()
        if UserModel.find_by_username(data["username"]):
            return {"message": "Error, username '{}' is already taken".format(data["username"])}, 400
        user = UserModel(**data)
        user.save_to_db()
        return {"message": "User created successfully"}, 201


class UserPasswordReset(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("username", type=str, required=True, help="A username is required")
    parser.add_argument("password", type=str, required=True, help="A password is required")

    def put(self, username):
        data = UserRegister.parser.parse_args()
        user = UserModel.find_by_username(username)
        if user:
            user.password = data["password"]
        else:
            user = UserModel(username, data["password"])

        try:
            user.save_to_db()
        except:
            return {"message": "Error, could not update user credentials"}, 500

        return user.json(), 201


class User(Resource):
    def get(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.json(), 200
        return {"message": "User '{}' not found".format(user_id)}, 404

    def delete(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "Error user id '{}' not found".format(user_id)}, 404
        user.delete_from_db()
        return {"message": "User deleted"}, 200
