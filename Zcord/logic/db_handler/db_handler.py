from getpass import getpass
from mysql.connector import connect, Error

class db_handler:
    """
    Родительский класс для объектов, описывающих взаимодействие с таблицами

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
    def __init__(self, host, user, password, databaseName, tableName):
        self._host = host
        self._user = user
        self._password = password
        self._database_name = databaseName

        self._tableName = tableName



    def getDataFromTableColumn(self, column:str) -> list:
        connection = connect(
                host=self._host,
                user=self._user,
                password= self._password,
                database=self._database_name
        )

        try:
            cursor = connection.cursor()

            cursor.execute(f"SELECT {column} FROM {self._tableName}")

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


#db = db_hadler("127.0.0.1", "Dmitry", "gfggfggfg3D-", "zcord")










