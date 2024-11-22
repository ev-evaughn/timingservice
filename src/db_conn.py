import MySQLdb as mariadb
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

host = os.environ.get("DBHOST")
user = os.environ.get("DBUSER")
password = os.environ.get("DBPASS")
db = os.environ.get("DBNAME")

def query(sql : str) -> dict:
  con = mariadb.connect(host, user, password, db)
  cursor = con.cursor(mariadb.cursors.DictCursor)
  cursor.execute(sql)
  con.commit()
  return cursor.fetchall()