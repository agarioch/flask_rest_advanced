## Store API

Endpoint | Method | Body | Description |
---- | ---- | ---- | ---- |
/item/{name} | GET | - | Get item by name |
/item/{name} | POST | {"price": X, store_id: X} | Create item with name & price |
/item/{name} | PUT | {"price": X, store_id: X} | Update item with price X |
/item/{name} | DELETE | - | Delete item with name |
/items | GET | - | Get list of all items |
/store{name} | GET | - | Get named store and child items |
/store{name} | POST | - | Create new store with name |
/store{name} | DELETE | - | Delete store with name |
/stores | GET | - | Get all stores and items |
 