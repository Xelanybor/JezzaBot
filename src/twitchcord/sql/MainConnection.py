from logging import exception
import pyodbc
import os

class mainConnection:
    """An sql connection to the JezzaBot database."""
    __DEFAULT_DATABASE = "A:\Coding Projects\JezzaBot\src\twitchcord\sql\JezzaBot.accdb"

    def __init__(self, databaseName = __DEFAULT_DATABASE):
        self.__DATABASE = databaseName
        self.__connection = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=A:\Coding Projects\JezzaBot\src\twitchcord\sql\JezzaBot.accdb;")

    def close(self):
        """Destroy the databse connection."""
        self.__connection.close()

    def get(self, sql: str, *params):
        """Execute an sql statement and return a list of Row objects."""
        cursor = self.__connection.cursor()
        cursor.execute(sql, *params)
        output = cursor.fetchall()
        cursor.close()
        return output

    def execute(self, sql: str, *params) -> None:
        """Execute an sql statement and return nothing."""
        cursor = self.__connection.cursor()
        try:
            cursor.execute(sql, *params)
            cursor.commit()
        except pyodbc.ProgrammingError as msg:
            raise msg
        except:
            pass
        finally:
            cursor.close()

    def addLinkedAccount(self, twitchID: str, discordID: str):
        try:
            self.execute(
                f"INSERT INTO Users (TwitchUser, DiscordUser) VALUES (?, ?)",
                [twitchID, discordID]
            )
        except pyodbc.ProgrammingError as msg:
            raise msg

    def getAccounts(self):
        return self.get("SELECT * FROM Users")

if __name__ == "__main__":
    print(os.getcwd())
    conn = mainConnection()
    # print(conn.getAccounts())
    conn.addLinkedAccount("twitchTest", "discordTest#1234")