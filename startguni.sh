gunicorn --workers 4 --bind 0.0.0.0:5000 --certfile=ssl/final.crt --keyfile=ssl/key.key __init__:app
