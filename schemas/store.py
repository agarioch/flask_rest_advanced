from ma import ma
from models.store import StoreModel
from models.item import ItemModel
from schemas.item import ItemSchema


class StoreSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True)

    class Meta:
        model = StoreModel
        include_relationships = True
        include_fk = True
        load_instance = True

    id = ma.auto_field(dump_only=True)
