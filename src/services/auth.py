from flask_restx import Resource, Namespace, reqparse
from flask import request, Response, json
from flask_jwt_extended import create_access_token

from src.utils.connection import getConnectToSQLdb

api = Namespace('Auth', description='Auth related apis')

register_parser = reqparse.RequestParser()
register_parser.add_argument('name', required=True, help='name required', location='json')
register_parser.add_argument('email', required=True, help='email required', location='json')
register_parser.add_argument('password',required=True, help='password required', location='json')
register_parser.add_argument('confirm_password', required=True, help='confirm password required', location='json')

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', required=True, help='email required', location='json')
login_parser.add_argument('password',required=True, help='password required', location='json')

def validateUser(request,req_type):
    required_fields_register = ["name", "email", "password", "confirm_password"]
    required_fields_login = ["email", "password"]

    data = request.get_json()
    error_fields = {}
    actual_data = { field:value for field,value in data.items() }
    
    if req_type == "Register":
        for field in required_fields_register:
            if field not in data or not data.get(field):
                error_fields[field] = f"{field} is required"

        if error_fields:
            return [False , actual_data, {"message": error_fields}]
        
        if actual_data.get("password") != actual_data.get("confirm_password"):
            return [False, actual_data, {"message": "password mismatch"}]

    elif req_type == "Login":
        for field in required_fields_login:
            if field not in data or not data.get(field):
                error_fields[field] = f"{field} is required"

        if error_fields:
            return [False , actual_data, {"message": error_fields}]
    
    
    return [True, actual_data, {}]

@api.route('/login')
class Login(Resource):
    @api.doc(security=[])
    @api.expect(login_parser)
    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateUser(request, "Login")
            if not isValid: return Response(status= 400, response=json.dumps(errorObj))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users where email = %s and password = %s"

            cursor.execute(query, [data.get("email"), data.get("password")])
            user = cursor.fetchone()
            connector.commit()

            if user is None:
                return Response(status=401, response=json.dumps({"message": "User doesn't exist. Please register."}))
            else:
                access_token = create_access_token(identity=data.get("email"))  #default expires in 15mins
                return Response(status=200, response=json.dumps({"message": "login successfully","access_token":access_token}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

@api.route('/register')
class Register(Resource):
    @api.doc(security=[], )
    @api.expect(register_parser)
    def post(self, **args):
        cursor = None
        connector = getConnectToSQLdb()
        print(args, request)
        try:
            [isValid, data ,errorObj] = validateUser(request, "Register")
            if not isValid: return Response(status= 422, response=json.dumps(errorObj))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users where email = %s"

            cursor.execute(query, [data.get("email")])
            user = cursor.fetchone()

            if user is None:
                query = '''
                    Insert into users (full_name, email, password)
                    VALUES (%s, %s, %s)
                '''
                value = (data["name"], data["email"], data["password"])

                cursor.execute(query, value)
            else:
                return Response(status=400, response=json.dumps({"message": "user exist"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Created Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))