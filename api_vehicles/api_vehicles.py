import textwrap
from functools import wraps
from flask import Flask, request, jsonify
from jsonschema import validate, ValidationError
app = Flask(__name__)

API_KEY = 'aW50ZWdyYXRpb24xOnJpZGVyeV9wYXNzd29yZA=='


def requires_auth(f):
    """
    Decorator function to require API key authentication.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('X-API-key', None)
        if not auth or auth != API_KEY:
            return jsonify({
                "message": "Unauthorized - Valid API Key Required",
            }), 401
        return f(*args, **kwargs)
    return wrapper


@app.route('/vehicles', methods=['POST'])
@requires_auth
def create_vehicles():
    """
    Endpoint to create vehicles. Validates and processes the input data.

    Returns:
        tuple: JSON response and status code.
    """
    data = request.get_json()

    # Check if data is a list
    if not isinstance(data, list):
        return jsonify({
            "message": "The received data is not a list."
        }), 400

    vehicle_ids = []
    for vehicle in data:
        try:
            # Validate each vehicle against the schema
            validate(instance=vehicle, schema=get_vehicle_schema())
            # Simulation of vehicle creation in the API for testing purposes
            print(textwrap.dedent(f"""\n
                Vehicle ID: {vehicle.get('id')}
                Driver: {vehicle.get('partner').get('name')}
                Data: {vehicle}
            \n"""))
            vehicle_ids.append(vehicle['id'])

        except ValidationError as e:
            return jsonify({
                "message": f"Vehicle validation error: {str(e)}"
            }), 400

    return jsonify({
        "message": "Vehicles successfully created.",
        "vehicle_ids": vehicle_ids,
    }), 201


def get_vehicle_schema():
    """
    Returns the schema definition for a vehicle object.
    """
    return {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "partner": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "vat": {"type": ["string", "boolean"]},
                    "mobile": {"type": ["string", "boolean"]},
                    "email": {"type": ["string", "boolean"]}
                },
                "required": ["id", "name"]
            },
            "vehicle_model": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "brand": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        },
                        "required": ["id", "name"]
                    },
                    "type": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        },
                        "required": ["id", "name"]
                    }
                },
                "required": ["id", "name", "brand", "type"]
            },
            "vehicle_services": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    },
                    "required": ["id", "name"]
                }
            },
            "color": {"type": "string"},
            "plate": {"type": "string"},
            "description": {"type": ["string", "boolean"]},
            "doors": {"type": "integer"},
            "seats": {"type": "integer"},
            "year": {"type": ["string", "boolean"]},
            "registration_date": {"type": "string"},
            "transmission": {"type": ["string"]}
        },
        "required": [
            "id", "partner", "vehicle_model",
            "color", "plate", "doors", "seats", "year",
            "registration_date", "transmission"
        ]
    }


if __name__ == '__main__':
    app.run(debug=True, port=5000)
