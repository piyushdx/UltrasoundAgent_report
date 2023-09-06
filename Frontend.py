from flask import Flask, render_template
import os
import threading
import re
from config import config, environment, ip_config

# ===================================================================================================
IP = ip_config[environment]
response_port = config['BotApplication']['Backend']  # response API

with open("ChatBotUI/static/js/script_base.js", "r", encoding='utf-8') as f:
    js_code= f.read()

js_code = re.sub('"http://127.0.0.1:1563/"', f'"http://{IP}:{response_port}/"', js_code)
with open("ChatBotUI/static/js/script.js", "w") as f:
    f.write(js_code)
    f.close()
# ===================================================================================================


TEMPLATE_DIR = os.path.abspath('ChatBotUI/templates')
STATIC_DIR = os.path.abspath('ChatBotUI/static')

# app = Flask(__name__) # to make the app run without any
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

@app.route('/')
def index():
    return "check /UltraBot"

@app.route('/UltraBot')
def UltraBot():
    return render_template('UltraBot_index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config['BotApplication']['Frontend'])

