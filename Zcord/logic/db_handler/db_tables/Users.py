from logic.db_handler.db_handler import db_handler

class Users(db_handler):
    def __init__(self, host, user, password, databaseName, tableName):
        super().__init__(host, user, password, databaseName, tableName)




