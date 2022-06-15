import sys

from flask_script import Manager
from application.config import create_app

app = create_app()
# CSRFProtect(app)

manage = Manager(app=app)

# @app.after_request
# def after_request(response):
#     csrf_token = generate_csrf()
#     response.set_cookie('csrf_token', csrf_token)
#     return response


if __name__ == '__main__':
    manage.run()
