import os

def getAPiVersion():
    return "api/v1"

def getDocPath(methodName):
   return os.path.join(os.getcwd(), "docs", getAPiVersion(), methodName)
