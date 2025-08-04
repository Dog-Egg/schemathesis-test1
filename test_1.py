from flask import Flask, request
import schemathesis


app = Flask(__name__)


@app.route("/users/<int:user_id>")
def get_user(user_id):
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or token != "secret-token":
        return {"error": "Unauthorized"}, 401
    return {"user_id": user_id}


@app.route("/openapi.json")
def openapi():
    return {
        "openapi": "3.0.3",
        "info": {"version": "0.1", "title": "Test API"},
        "paths": {
            "/users/{user_id}": {
                "get": {
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            },
                        },
                        "401": {
                            "description": "Unauthorized",
                        },
                        "404": {"description": "Not Found"},
                    },
                    "security": [{"MyBearer": []}],
                }
            }
        },
        "components": {
            "securitySchemes": {
                "MyBearer": {"type": "http", "scheme": "bearer"},
            }
        },
    }


schema = schemathesis.openapi.from_wsgi("/openapi.json", app)


@schema.parametrize()
def test_api(case):
    case.call_and_validate(headers={"Authorization": "Bearer secret-token"})
