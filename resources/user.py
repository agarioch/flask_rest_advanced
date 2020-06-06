from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_raw_jwt, get_jwt_identity
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp

from blacklist import BLACKLIST
from models.user import UserModel

parser = reqparse.RequestParser()
parser.add_argument("username", type=str, required=True, help="A username is required")
parser.add_argument("password", type=str, required=True, help="A password is required")


class UserRegister(Resource):

    def post(self):
        data = parser.parse_args()
        if UserModel.find_by_username(data["username"]):
            return {"message": "Error, username '{}' is already taken".format(data["username"])}, 400
        user = UserModel(**data)
        user.save_to_db()
        return {"message": "User created successfully"}, 201


class UserPasswordReset(Resource):
    def put(self, username):
        data = parser.parse_args()
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


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        user = UserModel.find_by_username(data["username"])

        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}

        return {"message": "Invalid credentials"}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": "User <id={}> successfully logged out".format(user_id)}, 200
