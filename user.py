from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, inspect
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for the entire app, allowing requests from your specific frontend
CORS(app)

# Configuration for multiple databases
app.config['SQLALCHEMY_BINDS'] = {
    'db_user': 'mysql://admin:Cloud998134@cloudpp1.cv478kobasse.us-east-1.rds.amazonaws.com/user_db',
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "somethingunique"

db = SQLAlchemy(app)

# Define models, binding each to its respective database
class User(db.Model):
    __bind_key__ = 'db_user'
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)

def table_exists(engine, table_name):
    inspector = inspect(engine)
    return inspector.has_table(table_name)

with app.app_context():
    engines = {
        'db_user': db.get_engine(bind='db_user'),
    }
    
    # Check and create tables for each bind
    for bind_key, engine in engines.items():
        metadata = MetaData()
        metadata.reflect(bind=engine)
        if not table_exists(engine, 'user') and bind_key == 'db_user':
            User.__table__.create(bind=engine)

@app.route('/')
def index():
    return "Welcome to the Multi-DB Flask App"

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    new_user = User(name=name, age=age)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{'id': user.id, 'name': user.name, 'age': user.age} for user in users]
    return jsonify(users_list), 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({'id': user.id, 'name': user.name, 'age': user.age}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.json
    user = User.query.get(id)
    if user:
        user.name = data.get('name', user.name)
        user.age = data.get('age', user.age)
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

# Handle preflight OPTIONS request
@app.route('/users', methods=['OPTIONS'])
@app.route('/users/<int:id>', methods=['OPTIONS'])
def handle_options():
    return jsonify({'message': 'OK'}), 200, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
