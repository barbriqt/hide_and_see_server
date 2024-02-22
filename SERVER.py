import http.server
import configparser
from urllib.parse import *
import mysql.connector
import json
import init_mysql

config = configparser.ConfigParser()



def connect_mysql(config):
    connection = mysql.connector.connect(
        host = config.get("MySQL", "Ip"),
        user = config.get("MySQL", "User"),
        password = config.get("MySQL", "Password"),
        database = config.get("MySQL", "Database Name")
    )
    return connection


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        global config


        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        post_params = parse_qs(body.decode('utf-8'))



        if (self.path == "/new_game"):
            username = post_params.get('username', [''])[0]
            start_loc = post_params.get('startLoc', [''])[0]
            radius = post_params.get('radius', [''])[0]
            timeInterval = post_params.get('timeInterval', [''])[0]
            
            connection = connect_mysql(config)
            db = connection.cursor()

            if '' in (username, start_loc, radius, timeInterval):
                self.send_response(400)
                self.end_headers()
            
            else:
                self.send_response(200)
                self.end_headers()

                # ovo brise sve postojece igre!!!
                db.execute("TRUNCATE TABLE locations")
                db.execute("TRUNCATE TABLE settings")

                db.execute(f"INSERT INTO locations (Username) VALUES ('{username}')")
                db.execute(f"INSERT INTO settings (setting, value) VALUES ('startLoc', '{start_loc}')")
                db.execute(f"INSERT INTO settings (setting, value) VALUES ('radius', '{radius}')")
                db.execute(f"INSERT INTO settings (setting, value) VALUES ('timeInterval', '{timeInterval}')")
                db.execute(f"INSERT INTO settings (setting, value) VALUES ('seeker', '{username}')")

                body = {}
                db.execute("SELECT * FROM settings")
                for (setting, value) in db:
                    body[setting] = value
                json_str_body = json.dumps(body) + "\n"
                self.wfile.write(json_str_body.encode("utf-8"))

                print(f"User {username} created a game\n")
            
            connection.commit()
            db.close()
            connection.close()



        elif (self.path == "/join_game"):
            username = post_params.get('username', [''])[0]
            
            connection = connect_mysql(config)
            db = connection.cursor()

            db.execute(f"SELECT * FROM locations WHERE Username = '{username}'")
            rows = db.fetchall()

            if username == '' or rows != []:
                self.send_response(400)
                self.end_headers()

            else:
                self.send_response(200)
                self.end_headers()
                db.execute(f"INSERT INTO locations (Username) VALUES ('{username}')")

                body = {}
                db.execute("SELECT * FROM settings")
                for (setting, value) in db:
                    body[setting] = value
                json_str_body = json.dumps(body) + "\n"
                self.wfile.write(json_str_body.encode("utf-8"))

                print(f"User {username} joined the game\n")
            
            connection.commit()
            db.close()
            connection.close()



        elif (self.path == "/locations"):
            username = post_params.get('username', [''])[0]
            location = post_params.get('location', [''])[0]
            address = post_params.get('address', [''])[0]

            connection = connect_mysql(config)
            db = connection.cursor()

            db.execute(f"SELECT * FROM locations WHERE Username = '{username}'")
            rows = db.fetchall()

            if ('' in (username, location)) or rows == []:
                self.send_response(400)
                self.end_headers()
            
            else:
                self.send_response(200)
                self.end_headers()
                db.execute(f"UPDATE locations SET Location='{location}', Address='{address}' WHERE Username='{username}'")

                print(f"Location recieved for user {username}\n")
                

            connection.commit()
            db.close()
            connection.close()



        else:
            self.send_response(404)
            self.end_headers()
    

    def do_GET(self):
        global config

        if self.path == "/locations":
            self.send_response(200)
            self.end_headers()

            connection = connect_mysql(config)
            db = connection.cursor()

            body = {}

            db.execute("SELECT Username, Location, Address FROM locations")
            rows = db.fetchall()
            
            for (username, location, address) in rows:
                body[username] = {
                    "location": location,
                    "address": address
                }

            json_str_body = json.dumps(body) + "\n"
            self.wfile.write(json_str_body.encode("utf-8"))

            connection.commit()
            db.close()
            connection.close()

            print("Locations fetched\n")


        
        else:
            self.send_response(404)
            self.end_headers()




def testMySQLConnection():
    global config
    try:
        connection = connect_mysql(config)
        db = connection.cursor()
        connection.commit()
        db.close()
        connection.close()
    except:
        init_mysql.init()

def main():
    global config
    config.read('config.ini')
    testMySQLConnection()

    server_adress = ("0.0.0.0", 8000)
    httpd = http.server.HTTPServer(server_adress, MyHandler)
    httpd.serve_forever()


if __name__=='__main__':
    main()