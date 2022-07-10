from flask_restful import Resource
from flask import request, Response, json
from flask_jwt_extended import jwt_required

from src.utils.connection import getConnectToSQLdb


def validateUser(request,req_type):
    required_fields = ["name", "email", "password", "confirm_password"]
    required_fields_update = ["email", "password", "confirm_password"]

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
        
        if actual_data.get("password") != actual_data.get("confirm_password"):
            return [False, actual_data, {"message": "password mismatch"}]
    
    
    return [True, actual_data, {}]

class Users(Resource):
    @jwt_required()
    def get(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            contains = request.args.get('contains')
            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users "
            filter_query = f"WHERE full_name like '%{contains}%'"
            query = query + filter_query if contains else query
            cursor.execute(query)
            users = cursor.fetchall()
            if not users:
                return Response(status=200, response=json.dumps({"message": "No users found"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"items": users,"count": len(users)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    #creating new user data
    @jwt_required()
    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateUser(request, "POST")
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


class User(Resource):
    @jwt_required()
    def get(self, id):
        """
        get users details
        ---
        parameters:
          - in: path
            name: id
            type: integer
            required: true
          - in: query
            name: contains
            type: string
            required: false
        responses:
          200:
            description: returns user details 
            schema:
              id: User
              properties:
                users:
                    type: array
                    items:
                        type: object
                        properties: 
                            full_name:
                                type: string
                                description: The name of the user
                            email:
                                type: string
                                description: The email of the user
                            created_at:
                                type: string
                                description: timestamp of when a user is created
                total_users:
                    type: integer 
          
                
        """
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users where id = %s"
            cursor.execute(query, [id])
            user = cursor.fetchall()
            connector.commit()
            return Response(status = 200, response=json.dumps({"message":f"user with {id} not found"}) if not user else json.dumps({"items": user,"count": len(user)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    @jwt_required()
    def put(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateUser(request, "PUT")
            if (not isValid): return Response(status= 422, response=json.dumps(errorObj))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users where id = %s"
            cursor.execute(query, [id])
            user = cursor.fetchone()

            if not user:
                return Response(status= 422, response=json.dumps({"message":f"User with {id} not found for update"}))

            query = "UPDATE users SET email = %s, password = %s where id = %s"
            cursor.execute(query, [data.get("email"), data.get("password"), id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Updated Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

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
                return Response(status= 422, response=json.dumps({"message":f"User with {id} not found for delete"}))

            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))