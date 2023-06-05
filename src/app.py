"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, FavoritesUser, FavoritesPeople, FavoritesPlanets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


#  Listar todos los usuarios del blog
@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.all()
    response_user = [user.serialize() for user in users]
    response_body = {
        "msg": "Users list"
    }

    return jsonify(response_user), 200 

# solicitud de un solo usuario
@app.route('/user/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify({"msg":"User does not exist"}), 404
    

    response_body = {
        "result": user.serialize()
    }

    return jsonify(response_body), 200



#  Listar todos los registros de people en la base de datos
@app.route('/people', methods=['GET'])
def get_people():
    characters = People.query.all()
    response_people = [people.serialize() for people in characters]
    response_body = {
        "msg": "People list"
    }

    return jsonify(response_people), 200



# Listar la información de una sola people
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):
    one_character = People.query.filter_by(id=people_id).first()

    if one_character is None:
        return jsonify({"msg":"Character does not exist"}), 404

    response_body = {
        "result": one_character.serialize()
    }

    return jsonify(response_body), 200


#  Listar los registros de planets en la base de datos
@app.route('/planet', methods=['GET'])
def get_planet():
    planets = Planet.query.all()
    response_planet = [planet.serialize() for planet in planets]
    response_body = {
        "msg": "Planet list"
    }

    return jsonify(response_planet), 200

#  Listar la información de un solo planet
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    one_planet = Planet.query.filter_by(id=planet_id).first()

    if one_planet is None:
        return jsonify({"msg":"Planet does not exist"}), 404

    response_body = {
        "result": one_planet.serialize()
    }

    return jsonify(response_body), 200

#  Listar todos los favoritos que pertenecen al usuario actual.
@app.route('/favoritesUser', methods=['GET'])
def get_favorites_users():
    favorites_users = FavoritesUser.query.all()
    favorites_users = [favorite.serialize() for favorite in favorites_users]

    response = {
        "msg": "Favorites list"
    }
    
    return jsonify(favorites_users), 200


#   Añade un nuevo character favorito al usuario actual con el people = people_id.
@app.route('/FavoritesPeople/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    request_body = request.json
    user_id = request_body.get("user_id")
    name = request_body.get("name")

    if not user_id or not name:
        return jsonify({"msg": "Missing required fields"}), 400

    favorites_people = FavoritesPeople(user_id=user_id, name=name)
    db.session.add(favorites_people)
    db.session.commit()

    response = {
        "msg": "Favorite character successfully created"
    }
    return jsonify(response), 200

#   Añade un nuevo planeta favorito al usuario actual con el people = people_id.
@app.route('/FavoritesPlanets/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):

    request_body = request.json
    user_id = request_body.get("user_id")
    name = request_body.get("name")

    if not user_id or not name:
        return jsonify({"msg": "Missing required fields"}), 400

    favorites_planet = FavoritesPlanets(user_id=user_id, name=name)
    db.session.add(favorites_planet)
    db.session.commit()

    response = {
        "msg": "Favorite planet successfully created"
    }
    return jsonify(response), 200


#   Elimina un planet favorito con el id = planet_id`.
@app.route('/FavoritesPlanets/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    FavoritesPlanets.query.filter_by(id=planet_id).delete()
    db.session.commit()

    response = {
        "msg": "Favourite planet successfully delete"
    }
    return jsonify(response), 200

#   Elimina una people favorita con el id = people_id.
@app.route('/FavoritesPeople/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):

    FavoritesPeople.query.filter_by(id=people_id).delete()
    db.session.commit()

    response = {
        "msg": "Favourite people successfully delete"
    }
    return jsonify(response), 200
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
