from flask import Flask
from models import *

app = Flask(__name__)
def setup_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///db.sqlite3"
    db.init_app(app)
    #Pending here is sqlite
    app.app_context().push()  #direct access to other modules
    app.debug= True
    print("Started ....")

setup_app()    
 
# from config import *
# from models import *
from routes import *

if __name__=='__main__':
    app.run(debug=True)


     