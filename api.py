from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

'''
__name__ argument is passed to the Flask class when creating an instance of the Flask application.
This helps with -
1. Resource Identification: The __name__ variable helps Flask to identify the root path of the application. 
2. Debugging and Logging: Flask uses the __name__ attribute for debugging purposes and to identify the name of the application in log messages. 
This is particularly useful when multiple Flask applications are running on the same server
'''
app = Flask(__name__)

'''
configure the Flask application to use a SQLite database.
app.config - dictionary-like object that stores configuration variables for the Flask application.
This line sets the configuration for the Flask application to use a SQLite database.
Database file named database.db will be created in the current directory.
''' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

'''initializes an instance of the SQLAlchemy class to handle database operations.

SQLAlchemy is an ORM (Object-Relational Mapping) library that provides a high-level interface for interacting with databases.
db is the variable that holds the instance of the SQLAlchemy class.
app is the Flask application instance that is passed to SQLAlchemy to bind it to the Flask app.
'''
db = SQLAlchemy(app)

'''
This line initializes an instance of the Api class from the Flask-RESTful extension to create RESTful APIs.
Api is a class that helps in creating RESTful APIs with Flask.
api is the variable that holds the instance of the Api class.
app is the Flask application instance that is passed to Api to bind it to the Flask app.
'''
api = Api(app)

# defines a class named UserModel that inherits from db.Model. 
# This means UserModel is a model class that represents a table in the database
class UserModel(db.Model):
    # Column Definitions:
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    # This method defines how instances of the UserModel class will be represented as strings.
    def __repr__(self):
        return f'User: {self.last_name}, {self.first_name} has email: {self.email}'

# RequestParser - module provided by the Flask-RESTful extension that helps in parsing and validating request arguments.
# It creates a request parser to handle and validate incoming request arguments and provides custom error messages for each argument if they are not provided in the request.
user_args = reqparse.RequestParser()
user_args.add_argument('email', type=str, required=True, help="Email can't be blank")
user_args.add_argument('first_name', type=str, required=True, help="Forname can't be blank")
user_args.add_argument('last_name', type=str, required=True, help="Surname can't be blank")

userFields = {
    'id': fields.Integer,
    'email': fields.String,
    'first_name': fields.String,
    'last_name': fields.String
}

'''
defines a class named Users that inherits from the Resource class.
Resource is a class provided by the Flask-RESTful extension that represents an abstract RESTful resource.
The get method is used to handle GET requests to the resource.
'''
class Users(Resource):
    # The @marshal_with decorator is used to specify that the response should be serialized using the userFields dictionary. 
    # This means that only the fields defined in userFields will be included in the response.
    @marshal_with(userFields)
    def get(self):
        # queries the database to retrieve all records from the UserModel table.
        users = UserModel.query.all()
        return users
    
    @marshal_with(userFields)
    def post(self):
        # parses the arguments from the incoming POST request using user_args which is defined above in the code and specifies the expected arguments and their types.
        args = user_args.parse_args()
        # creates a new instance of the UserModel class using the parsed arguments (email, first_name, last_name)
        user = UserModel(email=args['email'],
                         first_name=args['first_name'],
                         last_name=args['last_name'])
        # adds the newly created user object to the current database session.
        db.session.add(user)
        # commits the current transaction, saving the new user record to the database.
        db.session.commit()
        users = UserModel.query.all()
        # returns the list of users along with the HTTP status code 201 Created
        return users, 201
    
class User(Resource):
    @marshal_with(userFields)
    def get(self, email):
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            abort(404, "User Not Found!")  
        return user
        
    @marshal_with(userFields)
    def delete(self, email):
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            abort(404, "User Not Found!")  
        # If the user is found, this line deletes the user from the database session.
        db.session.delete(user)
        db.session.commit()
        return f'user: {email} deleted!!', 204
    
    @marshal_with(userFields)
    def patch(self, email):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            abort(404, "User Not Found!") 
        # If the user is found, this line updates the user’s first_name/last_name with the value provided in the request arguments. 
        user.first_name = args['first_name'] 
        user.last_name = args['last_name']
        db.session.commit()
        return user


# This method is used to add a resource to the api which is the instance of the Api class from the Flask-RESTful extension.
# When a client makes a GET request to '/api/users/', the get method of the Users resource will be called, and it will return the list of users from the database.
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<string:email>')

# it's a decorator that tells Flask to execute the following function when a request is made to the root URL ('/').
@app.route('/')
def home():
    return '<h>Hello World!</h1>'

if __name__ == '__main__':
    app.run(debug=True)
