import mysql.connector
import os

def getConnectToSQLdb():
    mydb = None
    UNIX_SOCKET = os.getenv("MYSQL_UNIX_SOCKET")
    try:
        if UNIX_SOCKET:
            mydb = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                username=os.getenv("MYSQL_USER_NAME"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DB"),
                unix_socket=UNIX_SOCKET
            )
        else:
            mydb = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                username=os.getenv("MYSQL_USER_NAME"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DB"),
            )

        return mydb
    except Exception as e:
        print(str(e))
        if mydb:
            mydb.close()
            
