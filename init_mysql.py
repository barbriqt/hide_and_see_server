from getpass import getpass
import configparser
import mysql.connector


# get config from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

ip = config.get('MySQL', 'Ip')
db_name = config.get('MySQL', 'Database Name')
user = config.get('MySQL', 'User')
password = config.get('MySQL', 'Password')

# connect to mysql server
connection = mysql.connector.connect(
    host = ip,
    user = "root",
    password = getpass("MySQL root Pass: ")
)

db = connection.cursor()

# delete existing user and database
db.execute(f"DROP DATABASE IF EXISTS {db_name}")
db.execute(f"DROP USER IF EXISTS '{user}'@'{ip}'")

# create new database and tables
db.execute(f"CREATE DATABASE {db_name}")
db.execute(f"USE {db_name}")
db.execute("""
    CREATE TABLE locations (
        Username varchar(255),
        Location varchar(255),
        Address varchar(255),
        Time datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (Username)
    )
    """
)
db.execute("""
    CREATE TABLE settings (
        Setting varchar(255),
        Value varchar(255)
    )
    """
)

# create new user
db.execute(f"CREATE USER IF NOT EXISTS '{user}'@'{ip}' IDENTIFIED BY '{password}'")
db.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{user}'@'{ip}'")

# close the connection
connection.commit()
db.close()
connection.close()