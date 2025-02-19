from getpass import getpass
from mysql.connector import connect, Error

class db_handler:
    """
    Родительский класс для объектов, описывающих взаимодействие с таблицами

    Пример инициализации:
    db = db_hadler("IP-ADDRESS", "USER-NAME", "PAROL", "DATABASE-NAME")

    Содержит 2 метода:

    ( 1 )
    def getDataFromTableColumn(self, column:str) -> list ---> возвращает list с данными, взятые
                                                                                            из колонки column таблицы tableName
    Пример:
    db.getDataFromTableColumn("COLUMN-NAME")

    ( 2 )
    def insertDataInTable(self, tableName:str, columns:str, dataToInsert:str) -> bool ---> возвращет True, если данные dataToInsert
                                                                                            были добавлены в таблтцу table Name с колонками columns
    Пример:
    db.insertDataInTable("(COL1, COL2, COL3, COL4)", "(5, 'data2', 'data3', 'data4')")
    """
    def __init__(self, host, user, password, databaseName, tableName):
        self._host = host
        self._user = user
        self._password = password
        self._database_name = databaseName

        self._tableName = tableName



    def getDataFromTableColumn(self, column:str, condition:str = "") -> list:
        connection = connect(
                host=self._host,
                user=self._user,
                password= self._password,
                database=self._database_name
        )

        try:
            cursor = connection.cursor()

            cursor.execute(f"SELECT {column} FROM {self._tableName} {condition}")

            result = list(map(lambda x: list(x),  cursor.fetchall()))

            cursor.close()
            connection.close()

            return result

        except Error as e:
            print(e)
            return []

    def insertDataInTable(self, columns:str, dataToInsert:str) -> bool:
        connection = connect(
                host=self._host,
                user=self._user,
                password= self._password,
                database=self._database_name
        )

        try:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO {self._tableName} {columns} VALUES {dataToInsert};")

            cursor.close()
            connection.commit()
            return True
        except Error as e:
            print(e)
            return False

    def getCertainRow(self, column:str, value:str, columns:str, condition:str="1=1"):
        connection = connect(
            host=self._host,
            user=self._user,
            password= self._password,
            database=self._database_name
        )

        try:
            cursor = connection.cursor()

            cursor.execute(f"SELECT {columns} FROM {self._tableName} where {column} = '{value}' AND {condition}")


            result = list(map(lambda x: list(x),  cursor.fetchall()))

            cursor.close()
            connection.close()
            return result
        except Error as e:
            print(e)
            return []

    def checkIfUhique(self, column:str, columnToCheck:str):
        connection = connect(
            host=self._host,
            user=self._user,
            password= self._password,
            database=self._database_name
        )

        try:
            cursor = connection.cursor()

            cursor.execute(f"SELECT {columnToCheck} AS col FROM {self._tableName} WHERE {columnToCheck} != '{column}';")


            result = list(map(lambda x: list(x),  cursor.fetchall()))

            cursor.close()
            connection.close()

            if len(result) == 0:
                return True

            return False
        except Error as e:
            print(e)
            return False

    def UpdateRequest(self, columnToChange:str, newValue:str, condition:str = "") -> bool:
        connection = connect(
            host=self._host,
            user=self._user,
            password= self._password,
            database=self._database_name
        )

        try:
            cursor = connection.cursor()

            cursor.execute(f"UPDATE {self._tableName} SET {columnToChange} = {newValue} {condition}")

            connection.commit()

            cursor.close()
            connection.close()

            return True
        except Error as e:
            print(e)
            return False


    def DeleteRequest(self, columnToDeleteFrom:str, CheckValue:str) -> bool:
        connection = connect(
            host=self._host,
            user=self._user,
            password= self._password,
            database=self._database_name
        )

        try:
            cursor = connection.cursor()

            cursor.execute(f"DELETE FROM {self._tableName} WHERE {columnToDeleteFrom} = {CheckValue} LIMIT 1")

            connection.commit()

            cursor.close()
            connection.close()

            return True
        except Error as e:
            print(e)
            return False





#db = db_hadler("127.0.0.1", "Dmitry", "gfggfggfg3D-", "zcord")










