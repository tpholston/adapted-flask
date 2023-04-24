import os
from project import application, db

with application.app_context():
    db.create_all()

if __name__=='__main__':
    application.run(debug=True, host="0.0.0.0", port=int(os.envion.get("PORT",8080)))
