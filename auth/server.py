import psycopg, jwt, datetime, os
from flask import Flask, request

server = Flask(__name__)

# PostgreSQL Configuration
server.config["POSTGRES_HOST"] = os.environ.get("POSTGRES_HOST")
server.config["POSTGRES_DB"] = os.environ.get("POSTGRES_DB")
server.config["POSTGRES_USER"] = os.environ.get("POSTGRES_USER")
server.config["POSTGRES_PASSWORD"] = os.environ.get("POSTGRES_PASSWORD")
server.config["POSTGRES_PORT"] = os.environ.get("POSTGRES_PORT")


# Database connection function
def get_db_connection():
    return psycopg.connect(
        dbname=server.config["POSTGRES_DB"],
        user=server.config["POSTGRES_USER"],
        password=server.config["POSTGRES_PASSWORD"],
        host=server.config["POSTGRES_HOST"],
        port=server.config["POSTGRES_PORT"]
    )

@server.route('/login', methods=['POST'])
def login():
      auth = request.authorization
      if not auth:
           return "missing credentials", 401
      
      #check db for username and password
      conn = get_db_connection()
      cursor = conn.cursor()
      res = cursor.execute("""
        SELECT email, password FROM users WHERE email=%s
      """, (auth.username,)
      )

      user_row = cursor.fetchone()

      if user_row:
           email, password = user_row

           if auth.username != email or auth.password != password:
                  return "invalid credentials", 401
           else:
                return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
      else:
           return "invalid credentials", 401
      
     
def createJWT(username, secret, is_admin):
     return jwt.encode(
          {
               "username": username,
               "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
               "iat": datetime.datetime.now(tz=datetime.timezone.utc),
               "admin": is_admin
          },
          secret,
          algorithm="HS256"
     )

if __name__ == "__main__":
     server.run(host="0.0.0.0", port=5000)

@server.route("/validate", methods=["POST"])
def validate():
     encoded_JWT = request.headers["Authorization"]

     if not encoded_JWT:
          return "missing credentials", 401
     
     encoded_JWT = encoded_JWT.split(" ")[1]

     try:
          decoded = jwt.decode(encoded_JWT, os.environ.get["JWT_SECRET"], algorithms=["HS256"])
     except:
          return "not authorized", 403
     
     return decoded, 200

