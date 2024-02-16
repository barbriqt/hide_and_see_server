import http.server
import configparser
from urllib.parse import *
import mysql.connector
import json

def connect_mysql(config):
    connection = mysql.connector.connect(
        host = config.get("mysql", "ip"),
        user = config.get("mysql", "user"),
        password = config.get("mysql", "password"),
        database = config.get("mysql", "db_name")
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
            radius = post_params.get('radius', 0)[0]    #default radius je 0 (nema ga)
            timeInterval = post_params.get('timeInterval', 300)[0]  #default timeIntercal je 5 minuta (300s)
            
            connection = connect_mysql(config)
            db = connection.cursor()

            if username == '':
                self.send_response(400)
            
            else:
                # ovo brise sve postojece igre!!!
                db.execute("TRUNCATE TABLE locations")
                db.execute(f"INSERT INTO locations (Username) VALUES ('{username}')")
                db.execute(f"INSERT INTO settings (Radius, Timeinterval) VALUES ('{radius}, '{timeInterval}')")
                self.send_response(200)
            
            connection.commit()
            db.close()
            connection.close()



        elif (self.path == "/join_game"):
            username = post_params.get('username', [''])[0]
            
            connection = connect_mysql(config)
            db = connection.cursor()

            #self note: proveri ako user vec postoji i salji status 4xx ak da
            if username == '':
                self.send_response(400)
            
            else:
                db.execute(f"INSERT INTO locations (Username) VALUES ('{username}')")
                self.send_response(200)
            
            connection.commit()
            db.close()
            connection.close()




        elif (self.path == "/update"):
            username = post_params.get('username', [''])[0]
            location = post_params.get('location', [''])[0]
            address = post_params.get('address', [''])[0]

            connection = connect_mysql(config)
            db = connection.cursor()

            if username == '':
                self.send_response(400)
            
            else:
                db.execute(f"UPDATE locations SET Location='{location}', Address='{address}' WHERE Username='{username}'")
                self.send_response(200)

            connection.commit()
            db.close()
            connection.close()



        else:
            self.send_response(404)
        self.end_headers()
    

    def do_GET(self):
        global config

        if self.path == "/locations":
            connection = connect_mysql(config)
            db = connection.cursor()

            body = []

            db.execute("SELECT Username, Location, Address FROM locations")
            for (username, location, address) in db:
                player={
                    "username": username,
                    "location": location,
                    "address": address
                }
                body.append(player)

            json_str_body = json.dumps(body)
            self.wfile.write(json_str_body.encode("utf-8"))



        elif self.path == "/settings":
             # ovo stoji za get settings funkciju kad zatreba
            """
            db.execute("SELECT * FROM settings")
            for (radius, timeInterval) in db:
                body["settings"]["radius"] = radius
                body["settings"]["timeInterval"] = timeInterval
            """
            
        else:
            self.send_response(404)
        self.end_headers()


config = configparser.ConfigParser()
config.read('config.ini')


server_adress = ("0.0.0.0", 8000)
httpd = http.server.HTTPServer(server_adress, MyHandler)
httpd.serve_forever()