from solomon_model_router import ModelRouter
from solomon_mnemosyne_db import SolomonMnemosyneDB

db = SolomonMnemosyneDB()
router = ModelRouter(db)
print("Router instantiated successfully")
