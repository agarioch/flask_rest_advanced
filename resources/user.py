from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_raw_jwt,
    get_jwt_identity,
)
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp

from blacklist import BLACKLIST
from models.user import UserModel

BLANK_ERROR = "{} cannot be left blank"
EXISTS_ERROR = "{} already exists"
USER_NOT_FOUND = "User {} not found"
USER_CREATED = "User created successfully"
USER_DELETED = "User deleted"
SAVE_ERROR = "An error occurred while saving {}"
INVALID_CREDENTIALS = "Invalid credentials"
USER_LOGGED_OUT = "User {} successfully logged out"

parser = reqparse.RequestParser()
parser.add_argument(
    "username", type=str, required=True, help=BLANK_ERROR.format("username")
)
parser.add_argument(
    "password", type=str, required=True, help=BLANK_ERROR.format("password")
)


class UserRegister(Resource):
    @classmethod
    def post(cls):
        data = parser.parse_args()
        if UserModel.find_by_username(data["username"]):
            return (
                {"message": EXISTS_ERROR.format(data["username"])},
                400,
            )
        user = UserModel(**data)
        user.save_to_db()
        return {"message": USER_CREATED}, 201


class UserPasswordReset(Resource):
    @classmethod
    def put(cls, username: str):
        data = parser.parse_args()
        user = UserModel.find_by_username(username)
        if user:
            user.password = data["password"]
        else:
            user = UserModel(username, data["password"])

        try:
            user.save_to_db()
        except:
            return {"message": SAVE_ERROR.format(username)}, 500

        return user.json(), 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.json(), 200
        return {"message": USER_NOT_FOUND.format(user_id)}, 404

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND.format(user_id)}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = parser.parse_args()
        user = UserModel.find_by_username(data["username"])

        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": USER_LOGGED_OUT.format(user_id)}, 200
