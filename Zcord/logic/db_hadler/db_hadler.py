from getpass import getpass
from mysql.connector import connect, Error

class db_hadler:
    """
    Объект работающий с БД

    Пример инициализации:
    db = db_hadler("IP-ADDRESS", "USER-NAME", "PAROL", "DATABASE-NAME")

    Содержит 2 метода:

    ( 1 )
    def getDataFromTableColumn(self, tableName:str, column:str) -> list ---> возвращает list с данными, взятые
                                                                                            из колонки column таблицы tableName
    Пример:
    db.getDataFromTableColumn("NAME-TABLE", "COLUMN-NAME")

    ( 2 )
    def insertDataInTable(self, tableName:str, columns:str, dataToInsert:str) -> bool ---> возвращет True, если данные dataToInsert
                                                                                            были добавлены в таблтцу table Name с колонками columns
    Пример:
    db.insertDataInTable("TABLE-NAME", "(COL1, COL2, COL3, COL4)", "(5, 'data2', 'data3', 'data4')")
    """
    def __init__(self, host, user, password, databaseName):
        self.__connection = connect(
                host=host,
                user=user,
                password= password,
                database=databaseName
        )



    def getDataFromTableColumn(self, tableName:str, column:str) -> list:
        try:
            cursor = self.__connection.cursor()
            cursor.execute(f"SELECT {column} FROM {tableName}")
            return list(map(lambda x: list(x),  cursor.fetchall()))
        except Error as e:
            print(e)
            return []

    def insertDataInTable(self, tableName:str, columns:str, dataToInsert:str) -> bool:
        try:
            cursor = self.__connection.cursor()
            cursor.execute(f"INSERT INTO {tableName} {columns} VALUES {dataToInsert};")
            cursor.close()
            self.__connection.commit()
            return True
        except Error as e:
            print(e)
            return False


db = db_hadler("127.0.0.1", "Dmitry", "gfggfggfg3D-", "zcord")










