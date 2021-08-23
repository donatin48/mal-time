from flask import Flask , render_template , request , redirect , send_from_directory, jsonify 
from flask import json as JSON
from flask.helpers import url_for
from flask_talisman import Talisman
from jikanpy import Jikan
from datetime import date, datetime
import sqlite3
from flask import g
from datetime import datetime 
import time as te
csp = {
   'default-src': [
      '\'self\''
   ],
   'img-src': [
      'google.com data:',
      '\'self\'',
      '*.myanimelist.net',
      'https://cdn.myanimelist.net/images/userimages/*'
   ],
   'script-src': [
       '\'self\'',
       'https://cdnjs.cloudflare.com',
   ]
}
DATABASE = 'db.db'


app = Flask(__name__,template_folder="templates",static_folder="static")
Talisman(app,force_https=True,force_https_permanent=True,content_security_policy=csp)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
jikan = Jikan()

def db_len_users():
   return query_db('''SELECT "seq" FROM "main"."sqlite_sequence" WHERE "name"= 'users' ''',one=True)["seq"]

@app.route('/', methods=['GET'])
@app.route('/index/', methods=['GET'])
def index():
   users = db_len_users()
   return render_template("index.html",users=users)

def db_connection():
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
     cur = db_connection().cursor().execute(query, args)
     rv = cur.fetchall()
     cur.close()
     return (rv[0] if rv else None) if one else rv

def query_commit(query, args=()):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(query,args)
    conn.commit()
    cur.close()

def db_create_user(username,mal_id):
   conn = db_connection()
   cur = conn.cursor()
   print(str(username))
   cur.execute('''INSERT INTO "main"."users"("mal_id","username") VALUES (?,?); ''',(int(mal_id),str(username))) 
   # cur.execute(f'''INSERT INTO "main"."anime"("mal_id") VALUES (?); ''',(int(mal_id),)) 
   # cur.execute(f'''INSERT INTO "main"."anime"("mal_id","days_watched","mean_score","watching","completed","on_hold","dropped","plan_to_watch","rewatched","episodes_watched") VALUES (?,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL); ''',int(mal_id)) 
   print("succes")
   conn.commit()
   cur.close()


def time():
   return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/user/<username>/refresh/', methods=['GET'])
def userefresh(username):
   try:
      user = jikan.user(username)
   except:
      return jsonify(status=400,message="username not found",error=None), 400


   id = user["user_id"]
   if query_db('''SELECT mal_id FROM "main"."users" WHERE "mal_id" = ? and "username" = ?''',args=[id,username],one=True):  # already in db : update lastscrap
      query_commit('''UPDATE "main"."users" SET "last_scrap"= datetime() WHERE "mal_id" = ? ''',[id])
   elif query_db('''SELECT mal_id FROM "main"."users" WHERE "mal_id" = ?''',args=[id],one=True):   # need to change username 
      query_commit('''UPDATE "main"."users" SET "username"= ? WHERE "mal_id"= ? ''',[username,id])	
      query_commit('''UPDATE "main"."users" SET "last_scrap"= datetime() WHERE "mal_id" = ? ''',[id])	 
   else:
      query_commit('''INSERT INTO "main"."users"("mal_id","username") VALUES (?,?)''',[id,username])   # new user
   # add anime stats data
   query_commit('''
   INSERT INTO "main"."anime"("mal_id","days_watched","mean_score","watching","completed","on_hold","dropped","plan_to_watch","rewatched","episodes_watched") VALUES (?,?,?,?,?,?,?,?,?,?)''',
   [user["user_id"],user["anime_stats"]["days_watched"],user["anime_stats"]["mean_score"],user["anime_stats"]["watching"],user["anime_stats"]["completed"],user["anime_stats"]["on_hold"],user["anime_stats"]["dropped"],user["anime_stats"]["plan_to_watch"],user["anime_stats"]["rewatched"],user["anime_stats"]["episodes_watched"]]
   )
   return redirect(f"https://lelab.ml/user/{username}/", code=302)


@app.route('/alldb/')
def func_name():
    a = ""
    for user in query_db('select * from anime where mal_id = 8473021 '):
        a += f"{list(user)}<br>"
    return a

def UserExistUsername(username):
   data = query_db('''SELECT mal_id FROM "main"."users" WHERE username = ? ''',args=[username],one=True)
   if not data :
      return False
   else :
      return True

def UserExist(id):
   data = query_db('''SELECT mal_id FROM "main"."users" WHERE mal_id = ? ''',args=[id],one=True)
   if not data :
      return False
   else :
      return True

@app.route('/user/<username>/', methods=['GET'])
def user(username):
   existingUser = UserExistUsername(username)
   user = {}
   if not existingUser :
      user["image_url"] = url_for('static',filename='nonepicture.png')
      return render_template("profile.html",username=username,user=user,new=True)

   id = query_db('''SELECT mal_id FROM "main"."users" WHERE username = ? ''',args=[username],one=True)[0]
   user["image_url"] = f"https://cdn.myanimelist.net/images/userimages/{id}.jpg"

   return render_template("profile.html",username=username,user=user,new=False)

@app.route('/about/')
def about():
    return render_template('about.html')


def jsonError(user,data):
    if not data : data = {}
    if not user:
        return jsonify(status=404,message="not found"), 404
    else:
        d = []
        for item in data:
            d.append({k: item[k] for k in item.keys()})
        return jsonify(user=dict(user),data=d)

@app.cli.command()
def scheduled():
    finaltime = datetime.now()
    print("\n")
    print(f"----- {finaltime} Start -----")
    for user in query_db('''SELECT username,mal_id FROM users'''):
        print(f"[{datetime.now()}] --> {user['username']} ",end="")
        for c in range(3):
            try:
                jikan_user = jikan.user(user["username"])
            except Exception as inst:
                print(f"{inst.args} error retrying ",end="")
                te.sleep(20)
                if c == 3 : jikan_user = None
                continue
            break
        if not jikan_user : continue
        time0 = te.time()
        print(f"finished   [{datetime.now()}]")
        if query_db('''SELECT mal_id FROM "main"."users" WHERE "mal_id" = ? and "username" = ?''',args=[user["mal_id"],user["username"]],one=True):  # already in db : update lastscrap
            query_commit('''UPDATE "main"."users" SET "last_scrap"= datetime() WHERE "mal_id" = ? ''',[user["mal_id"]])
        elif query_db('''SELECT mal_id FROM "main"."users" WHERE "mal_id" = ?''',args=[user["mal_id"]],one=True):   # need to change username 
            query_commit('''UPDATE "main"."users" SET "username"= ? WHERE "mal_id"= ? ''',[user["username"],user["mal_id"]])
            query_commit('''UPDATE "main"."users" SET "last_scrap"= datetime() WHERE "mal_id" = ? ''',[user["mal_id"]])
        query_commit('''
        INSERT INTO "main"."anime"("mal_id","days_watched","mean_score","watching","completed","on_hold","dropped","plan_to_watch","rewatched","episodes_watched") VALUES (?,?,?,?,?,?,?,?,?,?)''',
        [jikan_user["user_id"],jikan_user["anime_stats"]["days_watched"],jikan_user["anime_stats"]["mean_score"],jikan_user["anime_stats"]["watching"],jikan_user["anime_stats"]["completed"],jikan_user["anime_stats"]["on_hold"],jikan_user["anime_stats"]["dropped"],jikan_user["anime_stats"]["plan_to_watch"],jikan_user["anime_stats"]["rewatched"],jikan_user["anime_stats"]["episodes_watched"]]
        )
        cal = te.time() - time0
        print(f"[{datetime.now()}] query finished in {round(cal,3)} wait {round(4-cal)}")
        if cal < 4 :
            te.sleep(4-cal)

    print(f"----- {datetime.now()} Finished in {datetime.now() - finaltime} -----")

@app.route('/api/v1/username/<username>', methods=['GET', 'POST'])
def jsonUsername(username):
	user = query_db('select * from users where username = ?',[username], one=True)
	if not user :
		return jsonify(status=404,message="username not found in db"), 404
	data = query_db('select * from anime where mal_id = ?',[user["mal_id"]], one=False)
	return jsonError(user,data)

@app.route('/api/v1/mal_id/<mal_id>', methods=['GET', 'POST'])
def jsonMalId(mal_id):
   user = query_db('select * from users where mal_id = ?',[mal_id], one=True)
   data = query_db('select * from anime where mal_id = ?',[mal_id], one=False)
   return jsonError(user,data)

@app.route('/api/v1/id/<id>', methods=['GET', 'POST'])
def jsonId(id):
	user = query_db('select * from users where id = ?',[id], one=True)
	if not user :
		return jsonify(status=404,message="id not found in db"), 404
	data = query_db('select * from anime where mal_id = ?',[user["mal_id"]], one=False)
	return jsonError(user,data)

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
   # elif request.url.endswith("refresh/"):
   #    g.request_start_time = time.time()
   #    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)