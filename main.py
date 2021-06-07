from flask import Flask , render_template , request , redirect , send_from_directory, jsonify 
from flask import json as JSON
from flask.helpers import url_for
from flask_talisman import Talisman
import logging
from jikanpy import Jikan
from datetime import datetime
import sqlite3
from flask import g
csp = {
   'default-src': [
      '\'self\''
   ],
   'img-src': [
      '\'self\'',
      '*.myanimelist.net',
      'https://cdn.myanimelist.net/images/userimages/*'
   ]
}
DATABASE = 'db.db'
app = Flask(__name__,template_folder="templates",static_folder="static")
Talisman(app,force_https=True,force_https_permanent=True,content_security_policy=csp)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
jikan = Jikan()

@app.route('/', methods=['GET','POST'])
@app.route('/index/', methods=['GET', 'POST'])
def index():
   return render_template("index.html")

def get_db():
   db = getattr(g, '_database', None)
   if db is None:
      db = g._database = sqlite3.connect(DATABASE)
   db.row_factory = sqlite3.Row
   return db

@app.teardown_appcontext
def close_connection(exception):
   db = getattr(g, '_database', None)
   if db is not None:
      db.close()

def query_db(query, args=(), one=False):
    cur = get_db().cursor().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def db_len_users():
   return query_db("select count(*) from users")

def db_create_user(username,mal_id):
   cur = get_db().cursor()
   print(str(username))
   cur.execute(f'''INSERT INTO users("id","mal_id","username") 
   VALUES (?,{int(mal_id)},"{str(username)}"); ''')
   cur.execute(f'''INSERT INTO "main"."anime"("id","user_id","anime") 
   VALUES (?,0,NULL); ''')
   print("test")

@app.route('/db')
def db():
   l = []
   for row in query_db("select count(*) from users"):
      l += list(row)
   return str(l)

def time():
   return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def dbr():
   with open("static/db.json") as f:
      return JSON.load(f)

def dbc(len,user):
   feeds = dbr()
   feeds["users"][user["user_id"]] = {"id":len,"username":user["username"],"mal-time creation":time()}
   with open("static/db.json","w+") as f:
      print("sucessfull created")
      return JSON.dump(feeds,f, indent=4, separators=(',', ': '))


@app.route('/user/<username>/', methods=['GET', 'POST'])
def user(username):
   try:
      user = jikan.user(username)
      if not user["image_url"]:
        user["image_url"] = url_for('static',filename='nonepicture.png')
   except:
        return jsonify(status=400,message="username not found",error=None), 400
   else:
      users = dbr()
      create = False
      for c in users["users"]:
         if int(c) == int(user["user_id"]):
               print("login...")
               create = True
               break
      if create == False:
         print(f"New user : {username}")
         # db_create_user(username,user["user_id"])
         dbc(len(users["users"]),user)
   return render_template("profile.html",username=username,user=user)

@app.route('/api/<username>', methods=['GET', 'POST'])
def json(username):
   # user = jikan.user(username)
   return jsonify(dbr()["users"])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/favicon.ico')
@app.route('/robots.txt')
@app.route('/sitemap.xml')
async def static_from_root():
   return send_from_directory(app.static_folder, request.path[1:])

@app.before_request
async def before_request():
   if request.url.startswith('http://'):
      url = request.url.replace('http://', 'https://', 1)
      code = 301
      return redirect(url, code=code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)