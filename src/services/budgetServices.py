from flask_restful import Resource
from flask import request, Response, json
from flask_jwt_extended import jwt_required

from src.utils.connection import getConnectToSQLdb


def validateBudget(request):
    required_fields = ["budget_name", "user_id"]

    data = request.get_json()
    error_fields = {}
    actual_data = { field:value for field,value in data.items() }
    
    for field in required_fields:
        if field not in data or not data.get(field):
            error_fields[field] = f"{field} is required"

    if error_fields:
        return [False , actual_data, {"message": error_fields}]    
    
    return [True, actual_data, {}]

class Budgets(Resource):
    @jwt_required()
    def get(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            contains = request.args.get('contains')
            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM budgets "
            filter_query = f"WHERE name like '%{contains}%'"
            query = query + filter_query if contains else query
            cursor.execute(query)
            budgets = cursor.fetchall()
            if not budgets:
                return Response(status=200, response=json.dumps({"message": "No budgets found"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"items": budgets,"count": len(budgets)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))
    
    @jwt_required()
    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateBudget(request)
            if not isValid: return Response(status= 422, response=json.dumps(errorObj))

            user_id = data.get('user_id')
            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users where id = %s"
            cursor.execute(query, [user_id])
            user = cursor.fetchone()

            if user is None:
                return Response(status= 422, response=json.dumps({"message":f"No user found with {user_id}"}))
            
            query = "SELECT * FROM budgets where user_id = %s"
            cursor.execute(query, [user_id])
            budget = cursor.fetchone()

            if budget is None:
                query = '''
                    Insert into budgets (name, user_id)
                    VALUES (%s, %s)
                '''
                value = (data.get('budget_name'),user_id)
                cursor.execute(query, value)
            else:
                return Response(status=400, response=json.dumps({"message": "Budget exist"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Budget created Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))


class Budget(Resource):
    @jwt_required()
    def get(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM budgets where id = %s"
            cursor.execute(query, [id])
            budget = cursor.fetchall()
            connector.commit()
            return Response(status = 200, response=json.dumps({"message":f"budget with {id} not found"}) if not budget else json.dumps({"items": budget,"count": len(budget)}))
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
            data = request.get_json()
            budget_name = data.get("budget_name")
            if "budget_name" not in data.keys() or not budget_name:
                return Response(status= 422, response=json.dumps({"message":f"Budget name is required"}))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM budgets where id = %s"
            cursor.execute(query, [id])
            budget = cursor.fetchone()

            if not budget:
                return Response(status= 422, response=json.dumps({"message":f"Budget with {id} not found for update"}))

            query = "UPDATE budgets SET name = %s where id = %s"
            cursor.execute(query, [budget_name, id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Budget updated Successfully"}))
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
            query = "SELECT * FROM budgets where id = %s"
            cursor.execute(query, [id])
            budget = cursor.fetchone()

            if not budget:
                return Response(status= 422, response=json.dumps({"message":f"budget with {id} not found for delete"}))

            query = "DELETE FROM budgets WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Budget deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))