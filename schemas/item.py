from ma import ma
from models.item import ItemModel
from models.store import StoreModel


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemModel
        include_relationships = True
        include_fk = True
        load_instance = True

    id = ma.auto_field(dump_only=True)
    store = ma.auto_field(load_only=True)
