from flask import Flask , render_template
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


app = Flask(__name__)

cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'



#app.app_context().push()
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)




# import market.models

# with app.app_context():
#     db.create_all()


#   flask run
#   $env:FLASK_APP=market.py
#   $env:FLASK_DEBUG=1

# if __name__ == "__main__":
#     app.run(debug=True)