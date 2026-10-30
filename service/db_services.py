
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