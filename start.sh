export FLASK_APP=__init__.py

cd /home/pi/Desktop/mal-time ; /usr/bin/env authbind --deep /usr/local/opt/python-3.9.0/bin/python3.9 -m flask run --port=443 --host=0.0.0.0 --cert=ssl/final.crt --key=ssl/key.key --with-threads --lazy-loader 