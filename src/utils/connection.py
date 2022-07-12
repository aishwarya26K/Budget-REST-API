import mysql.connector
import os
 
def getConnectToSQLdb():
    mydb = None
    try:
        mydb = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        username=os.getenv("MYSQL_USER_NAME"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
        )

        return mydb
    except Exception as e:
        print(str(e))
        mydb.close()

