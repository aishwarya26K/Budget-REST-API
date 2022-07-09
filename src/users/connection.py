import mysql.connector
 
def getConnectToSQLdb():
    mydb = None
    try:
        mydb = mysql.connector.connect(
        host="localhost",
        username="root",
        password="",
        database="budget"
        )

        return mydb
    except Exception as e:
        print(str(e))
        mydb.close()

