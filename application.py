import os
from flask import Flask

application = Flask(__name__)

@application.route("/")
def test_env_variable():
    return "Hello World"

#with application.app_context():
#    db.create_all()

#if __name__=='__main__':
#    application.run(debug=True, host="0.0.0.0", port=int(os.envion.get("PORT",8080)))
