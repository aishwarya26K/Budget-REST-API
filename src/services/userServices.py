from flask_restx import Resource, Namespace, reqparse
from flask import request, Response, json
from flask_jwt_extended import jwt_required

from src.utils.connection import getConnectToSQLdb
from src.utils.requestParsers import pagination_parser

api = Namespace('Users', description='Users related apis')

parser = pagination_parser.copy()
parser.add_argument('contains', help='filtering users by name only', location='args')

#PUT
users_parser = reqparse.RequestParser()
users_parser.add_argument('name', required=True, help='name required', location='json')
users_parser.add_argument('email', required=True, help='email required', location='json')
users_parser.add_argument('password',required=True, help='password required', location='json')

#POST
users_post_parser = users_parser.copy()
users_post_parser.add_argument('confirm_password', required=True, help='confirm password required', location='json')

def validateUser(request,req_type):
    required_fields = ["name", "email", "password", "confirm_password"]
    required_fields_update = ["name","email", "password"]

    data = request.get_json()
    error_fields = {}
    actual_data = { field:value for field,value in data.items() }
    
    if req_type == "POST":
        for field in required_fields:
            if field not in data or not data.get(field):
                error_fields[field] = f"{field} is required"

        if error_fields:
            return [False , actual_data, {"message": error_fields}]
        
        if actual_data.get("password") != actual_data.get("confirm_password"):
            return [False, actual_data, {"message": "password mismatch"}]

    elif req_type == "PUT":
        for field in required_fields_update:
            if field not in data or not data.get(field):
                error_fields[field] = f"{field} is required"

        if error_fields:
            return [False , actual_data, {"message": error_fields}]
    
    return [True, actual_data, {}]


@api.route("/users")
class Users(Resource):
    #get all users by name only
    @jwt_required()
    @api.expect(parser)
    def get(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            contains = request.args.get('contains')
            page_size = int(request.args.get('page_size',10))
            page_index = int(request.args.get('page_index',1))
            offset_val = (page_index - 1) * page_size

            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT id, full_name, email, created_at FROM users "
            filter_query = f"WHERE full_name like '%{contains}%'"

            pagination_query = f" LIMIT {page_size} OFFSET {offset_val}"

            query = query + filter_query if contains else query
            query = query + pagination_query if page_size or page_index else query
            cursor.execute(query)
            users = cursor.fetchall()
            if not users:
                return Response(status=400, response=json.dumps({"message": "No users found"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"items": users,"count": len(users)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    #add new user data
    @jwt_required()
    @api.expect(users_post_parser)
    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateUser(request, "POST")
            if not isValid: return Response(status= 400, response=json.dumps(errorObj))

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
                return Response(status=200, response=json.dumps({"message": "user exist"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Created Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

@api.route("/users/<int:id>")
class User(Resource):
    #get user by id only
    @jwt_required()
    def get(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT full_name, email, created_at FROM users where id = %s"
            cursor.execute(query, [id])
            user = cursor.fetchall()
            connector.commit()
            return Response(status = 200, response=json.dumps({"message":f"user with {id} not found"}) if not user else json.dumps({"items": user,"count": len(user)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    #update user by id only
    @jwt_required()
    @api.expect(users_parser)
    def put(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateUser(request, "PUT")
            if (not isValid): return Response(status= 400, response=json.dumps(errorObj))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users where id = %s"
            cursor.execute(query, [id])
            user = cursor.fetchone()

            if not user:
                return Response(status= 400, response=json.dumps({"message":f"User with {id} not found for update"}))

            query = "UPDATE users SET full_name = %s, email = %s, password = %s where id = %s"
            cursor.execute(query, [data.get("name"), data.get("email"), data.get("password"), id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Updated Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    #delete user by id only
    @jwt_required()
    def delete(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users where id = %s"
            cursor.execute(query, [id])
            user = cursor.fetchone()

            if not user:
                return Response(status= 400, response=json.dumps({"message":f"User with {id} not found for delete"}))

            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))
