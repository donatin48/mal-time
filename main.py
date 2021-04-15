from flask import Flask , render_template , request , redirect , send_from_directory
from flask_talisman import Talisman

# import requests
# from bs4 import BeautifulSoup

app = Flask(__name__,template_folder="templates",static_folder="static")
Talisman(app,force_https=True,force_https_permanent=True)

@app.route('/', methods=['GET','POST'])
@app.route('/index/', methods=['GET', 'POST'])
def index():
   return render_template("index.html")

@app.route('/users/<username>/', methods=['GET', 'POST'])
def users(username):

   return render_template("profile.html",username=username)




@app.route('/users/<username>/json', methods=['GET', 'POST'])
def json(username):
   return '{%s : "" }' %username

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
   return send_from_directory(app.static_folder, request.path[1:])

@app.before_request
def before_request():
   if request.url.startswith('http://'):
      url = request.url.replace('http://', 'https://', 1)
      code = 301
      return redirect(url, code=code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)