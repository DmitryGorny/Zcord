from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError, ProgrammingError

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

    _engine = None
    _session_factory = None
    def __init__(self, host, user, password, databaseName, tableName):
        self._host = host
        self._user = user
        self._password = password
        self._database_name = databaseName
        self._tableName = tableName

        if db_handler._engine is None:
            db_handler._engine = create_engine(
                f'mysql://{user}:{password}@{host}/{databaseName}',
                pool_size=10,
                max_overflow=5,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True
            )
            db_handler._session_factory = scoped_session(sessionmaker(bind=db_handler._engine))

    def get_session(self):
        """Создает новую сессию для текущего потока."""
        return db_handler._session_factory()

    def getDataFromTableColumn(self, column:str, condition:str = "") -> list:
        session = self.get_session()
        try:
            result = session.execute(text(f"SELECT {column} FROM {self._tableName} {condition}"))

            result = list(map(lambda x: list(x),  result.fetchall()))

            return result

        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return []
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return []
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return []
        finally:
            db_handler._session_factory.remove()

    def insertDataInTable(self, columns:str, dataToInsert:str) -> bool:
        session = self.get_session()
        try:
            session.execute(text(f"INSERT INTO {self._tableName} {columns} VALUES {dataToInsert};"))
            session.commit()
            return True
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return False
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return False
        finally:
            db_handler._session_factory.remove()

    def getCertainRow(self, column:str, value:str, columns:str, condition:str="1=1"):
        session = self.get_session()
        try:
            res = session.execute(text(f"SELECT {columns} FROM {self._tableName} where {column} = '{value}' AND {condition}"))

            result = list(map(lambda x: list(x),  res.fetchall()))

            return result
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return []
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return []
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return []
        finally:
            db_handler._session_factory.remove()

    def checkIfUhique(self, column:str, columnToCheck:str):
        session = self.get_session()
        try:
            res = session.execute(text(f"SELECT {columnToCheck} AS col FROM {self._tableName} WHERE {columnToCheck} != '{column}';"))

            result = list(map(lambda x: list(x),  res.fetchall()))

            if len(result) == 0:
                return True

            return False
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return False
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return False
        finally:
            db_handler._session_factory.remove()

    def UpdateRequest(self, columnToChange:str, newValue:str, condition:str = "") -> bool:
        session = self.get_session()
        try:
            session.execute(text(f"UPDATE {self._tableName} SET {columnToChange} = {newValue} {condition}"))

            session.commit()

            return True
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return False
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return False
        finally:
            db_handler._session_factory.remove()


    def DeleteRequest(self, columnToDeleteFrom:str, CheckValue:str, condition:str = "") -> bool:
        session = self.get_session()
        try:
            session.execute(text(f"DELETE FROM {self._tableName} WHERE {columnToDeleteFrom} = {CheckValue} {condition} LIMIT 1"))

            session.commit()

            return True
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return False
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return False
        finally:
            db_handler._session_factory.remove()

    def insertDataInTablePacket(self, columns:str, dataToInsert:list) -> bool:
        """
        Метод для пактеной отсылке данных в БД
        dataToInsert - Массив с даннми типа ['(val1, val2)', '(val3, val4)']
        """
        session = self.get_session()
        try:
            session.execute(text(f"INSERT INTO {self._tableName} {columns} VALUES {','.join(dataToInsert)};"))
            session.commit()
            return True
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return False
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return False
        finally:
            db_handler._session_factory.remove()
    def getAI_Id(self):
        session = self.get_session()
        try:
            res = session.execute(text(f"SELECT max(`id`) from {self._tableName};"))
            result = list(map(lambda x: list(x),  res.fetchall()))
            if result[0][0] is None:
                return [[1]]
            return result
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return [[1]]
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return [[1]]
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return [[1]]
        finally:
            db_handler._session_factory.remove()

    def packetUpdate(self, columnToUpdate:str, ArrayOfValues:list) -> bool:
        session = self.get_session()
        try:
            for valueInd in range(len(ArrayOfValues)):
                session.execute(text(f"UPDATE {self._tableName} SET {columnToUpdate} = {ArrayOfValues[valueInd][0]} {ArrayOfValues[valueInd][1]};"))
                session.commit()
            return True
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
        except IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
            return False
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе: {e}")
            return False
        finally:
            db_handler._session_factory.remove()











