import os
import jwt

jwt_secret = os.getenv('JWT_SECRET_KEY')
jwt_algorithm = 'HS256'
jwt_sec_expires = 600


def encode_jwt(payload):
    return jwt.encode(
        payload=payload,
        key=jwt_secret,
        algorithm=jwt_algorithm
    )


def decode_jwt(payload):
    try:
        return jwt.decode(
            jwt=payload,
            key=jwt_secret,
            algorithms=jwt_algorithm
        )
    except Exception as e:
        print(e)
        return None
