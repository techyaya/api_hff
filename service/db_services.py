
import pyodbc
from dotenv import load_dotenv
import os
load_dotenv()

def get_connection():
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.getenv("server")};"
        f"DATABASE={os.getenv("database")};"
        f"UID={os.getenv("user")};"
        f"PWD={os.getenv("password")};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes"
    )


    #print("server : " , os.getenv("server"))
    #print("database : " , os.getenv("database"))
    #print("utilisateur : " , os.getenv("user"))
    #print("password: " , os.getenv("password"))


    return pyodbc.connect(connection_string) 


def get_connection_informix():
    connection_string = (
        "DRIVER={IBM INFORMIX ODBC DRIVER (64-bit)};"
        f"HOST={os.getenv("host_informix")};"
        f"SERVICE={os.getenv("service")};"
        f"SERVER={os.getenv("server_informix")};"
        "PROTOCOL=onsoctcp;"
        f"DATABASE={os.getenv("database_informix")};"
        f"UID={os.getenv("user_informix")};"
        f"PWD={os.getenv("pwd_informix")};"
    )
   
    return pyodbc.connect(connection_string)