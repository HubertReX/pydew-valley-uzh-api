from flask import Flask, request, jsonify
from secrets import token_hex
import jwt
from time import time
from get_data import list_of_api_keys, list_of_play_tokens

app = Flask(__name__)

SECRET_JWT_KEY = token_hex(16) # will replace with a repo secret
EXTRA_TIME_TO_LIVE = 86400


@app.before_request
def details():
    api_key = request.headers.get("x-api-key")
    if api_key in list_of_api_keys:
        pass
    elif not api_key or type(api_key) != str:
        return jsonify({"error": "x-api-key header is not valid"}), 401
    else:
        return jsonify({"error": "x-api-key header is not valid"}), 400

    print(request.headers, request.json)


@app.route("/")
def home():
    return jsonify({"message": "API for Clear Skies"}), 200


@app.route("/authn", methods=["POST"])
def authenticate():
    """
    Trade a play token for a JWT token to interact with backend API

    HEADER:
    ```
    x-api-key: YOUR_API_KEY
    ```

    PAYLOAD:
    ```
    {
        "play_token": YOUR_PLAY_TOKEN
    }
    ```
    """

    try:
        play_token = request.json["play_token"]
        if play_token in list_of_play_tokens:
            pass
        elif not play_token or type(play_token) != str:
            return jsonify({"error": "play_token is not valid"}), 401
        else:
            return jsonify({"error": "play_token is not valid"}), 400

        current_time = time()
        encoded_jwt = jwt.encode(
            payload={
                "nbf": int(current_time),
                "exp": int(current_time + EXTRA_TIME_TO_LIVE)
            },
            key=SECRET_JWT_KEY,
            algorithm="HS256"
        )

    except Exception as e:
        print(e)
        return 500

    finally:
        return jsonify({"token": encoded_jwt}), 200


@app.route("/telemetry", methods=["POST"])
def telemetry():
    """
    Sends player decision data to the backend to be stored in a database.

    HEADER:
    ```
    x-api-key: YOUR_API_KEY
    Authorization: YOUR_JWT_TOKEN
    ```

    PAYLOAD:
    ```
    {
        insert JSON data here
    }
    ```
    """

    encoded_jwt = request.headers.get("Authorization").split()[1]
    if encoded_jwt.count(".") == 2:
        pass
    elif not encoded_jwt or type(encoded_jwt) != str:
        return jsonify({"error": "authorization header is not valid"}), 401
    else:
        return jsonify({"error": "authorization header is not valid"}), 400

    try:
        decoded_jwt = jwt.decode(
            jwt=encoded_jwt,
            key=SECRET_JWT_KEY,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "require": ["exp"],
                "verify_exp": True
            }
        )
        print(decoded_jwt)
    except jwt.InvalidTokenError:
        return jsonify({"error": "failed to decode JWT"}), 400
    except jwt.DecodeError:
        return jsonify({"error": "failed to decode JWT"}), 500

    # TEMPORARY, will replace with functions to update database
    print("lalala i am updating the database with this data =", request.json["telemetry_data"])

    return jsonify({"message": "telemetry data received"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
