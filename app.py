from app import app
from app import spider
import time

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 7777,  debug=True, use_reloader=False)
