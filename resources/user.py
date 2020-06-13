from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_raw_jwt,
    get_jwt_identity,
)
from flask_restful import Resource
from werkzeug.security import safe_str_cmp
from marshmallow import ValidationError

from blacklist import BLACKLIST
from models.user import UserModel
from schemas.user import UserSchema

BLANK_ERROR = "{} cannot be left blank"
EXISTS_ERROR = "{} already exists"
USER_NOT_FOUND = "User {} not found"
USER_CREATED = "User created successfully"
USER_DELETED = "User deleted"
SAVE_ERROR = "An error occurred while saving {}"
INVALID_CREDENTIALS = "Invalid credentials"
USER_LOGGED_OUT = "User {} successfully logged out"
NOT_CONFIRMED_ERROR = "Please confirm registration at {}"
USER_CONFIRMED = "User activated successfully"

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return (
                {"message": EXISTS_ERROR.format(user.username)},
                400,
            )
        user.save_to_db()
        return {"message": USER_CREATED}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            return user_schema.dump(user), 200
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
        user_data = user_schema.load(request.get_json())
        user = UserModel.find_by_username(user_data.username)

        if user and safe_str_cmp(user.password, user_data.password):
            if user.activated:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return (
                    {"access_token": access_token, "refresh_token": refresh_token},
                    200,
                )
            return {"message": NOT_CONFIRMED_ERROR.format(user.username)}, 400
        return {"message": INVALID_CREDENTIALS}, 401


class UserConfirm(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND.format(user_id)}, 400
        user.activated = True
        user.save_to_db()
        return {"message": USER_CONFIRMED}, 200


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": USER_LOGGED_OUT.format(user_id)}, 200
