
# import logging
import sys
from loguru import logger
from flask import Flask, Response, request, jsonify
from secrets import token_hex
import jwt
from time import time
from get_data import list_of_api_keys, list_of_play_tokens

SECRET_JWT_KEY = token_hex(16)  # will replace with a repo secret
EXTRA_TIME_TO_LIVE = 86400
DEBUG_MODE_VERSION = 0

HOST = "localhost"
PORT = 5000

CONSOLE_DEBUG_LEVEL = "DEBUG"
FILE_DEBUG_LEVEL = "DEBUG"


# remove default handlers and add custom ones
logger.remove()
logger.add(
    # sys.stdout,
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
    # "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    "<cyan>{function:>20}</cyan>:<cyan>{line:<4}</cyan> | <level>{message}</level>",
    level=CONSOLE_DEBUG_LEVEL,
)

# logger.add("sever_{time}.log", level="DEBUG", rotation="500 MB")  # , compression="zip", backtrace=True, diagnose=True
logger.add(
    "server.log",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | "
    # "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    "<cyan>{function:>20}</cyan>:<cyan>{line:<4}</cyan> | <level>{message}</level>",
    level=FILE_DEBUG_LEVEL
)  # , compression="zip", backtrace=True, diagnose=True

app = Flask(__name__)


@app.before_request
def before_request():
    api_key = request.headers.get("x-api-key")
    if api_key in list_of_api_keys:
        pass
    elif not api_key or type(api_key) is str:
        logger.error(f"x-api-key header is not valid: {({"api_key": api_key})}")
        return jsonify({"error": "x-api-key header is not valid"}), 401
    else:
        logger.error(f"x-api-key header is not valid: {({"api_key": api_key})}")
        return jsonify({"error": "x-api-key header is not valid"}), 400

    logger.info("got valid header")
    try:
        req_json = request.json
    except:  # noqa E722
        req_json = {}

    logger.debug({"headers": request.headers, "json": req_json})

    # print(request.headers, request.json)


@app.route("/")
def home():
    logger.info("got root API call")

    return jsonify({"message": "API for Clear Skies"}), 200


@app.route("/authn", methods=["POST"])
def authenticate() -> tuple[Response, int]:
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
        play_token_int: int = -1
        encoded_jwt: str = ""
        game_version: int = -1

        play_token = request.json["play_token"]  # type:ignore[index]

        try:
            play_token_int = int(play_token)
        except ValueError:
            logger.error(f"play_token is not valid: {({"play_token": play_token})}")

        if play_token_int in list_of_play_tokens:
            if play_token_int in range(100, 350):
                game_version = 1
            elif play_token_int in range(350, 600):
                game_version = 2
            elif play_token_int in range(600, 850):
                game_version = 3
            elif play_token_int in [0, 999]:
                game_version = DEBUG_MODE_VERSION
        elif not play_token or type(play_token) is str:
            logger.error(f"play_token is not valid: {({"play_token": play_token})}")
            return jsonify({"error": "play_token is not valid"}), 401
        else:
            logger.error(f"play_token is not valid: {({"play_token": play_token})}")
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
        logger.error(f"unhandled exception: {e}")
        return jsonify({"error": "internal server error"}), 500

    finally:
        if encoded_jwt:
            logger.info("authentication success")
            logger.debug({"encoded_jwt": encoded_jwt, "game_version": game_version})
        return jsonify({"jwt": encoded_jwt, "game_version": game_version}), 200


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

    try:
        authorization = request.headers.get("Authorization", "Bearer X")
        authorization_parts = authorization.split()
        if len(authorization_parts) > 1:
            encoded_jwt = authorization_parts[1]
        else:
            encoded_jwt = ""
        if encoded_jwt.count(".") == 2:
            pass
        elif not encoded_jwt or type(encoded_jwt) is str:
            logger.error(f"authorization header is not valid: {({"encoded_jwt": encoded_jwt})}")
            return ({"error": "authorization header is not valid"}), 401
        else:
            logger.error(f"authorization header is not valid: {({"encoded_jwt": encoded_jwt})}")
            return jsonify({"error": "authorization header is not valid"}), 400

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
        logger.info("decode JWT success")
        logger.debug({"decoded_jwt": decoded_jwt})
        # print(decoded_jwt)
    except jwt.InvalidTokenError:
        logger.error(f"failed to decode JWT: {({"encoded_jwt": encoded_jwt})}")
        return jsonify({"error": "failed to decode JWT"}), 400
    except jwt.DecodeError:
        logger.error(f"failed to decode JWT: {({"encoded_jwt": encoded_jwt})}")
        return jsonify({"error": "failed to decode JWT"}), 500

    # TEMPORARY, will replace with functions to update database
    logger.info("got telemetry data")
    logger.debug(request.json["telemetry_data"])

    return jsonify({"message": "telemetry data received"}), 200


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
