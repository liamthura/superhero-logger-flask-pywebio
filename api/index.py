from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH, start_server
import argparse
from flask import Flask

app = Flask(__name__)
# application = app

@use_scope('ROOT')
def main():
    put_text(f'Hello World')


app.add_url_rule('/', 'webio_view', webio_view(main), methods=['GET', 'POST', 'OPTIONS'])
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    start_server(app, port=args.port)
if __name__ == '__main__':
    app()
    
