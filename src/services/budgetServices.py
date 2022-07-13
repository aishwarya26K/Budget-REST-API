from flask_restx import Resource, Namespace, reqparse
from flask import request, Response, json
from flask_jwt_extended import jwt_required, current_user

from src.utils.connection import getConnectToSQLdb
from src.utils.requestParsers import pagination_parser

api = Namespace('Budgets', description='Budgets related apis')

parser = pagination_parser.copy()
parser.add_argument('contains', help='filtering budget by name only', location='args')

#PUT POST
budget_parser = reqparse.RequestParser()
budget_parser.add_argument('budget_name', required=True, help='budget name required', location='json')


@api.route("/budgets")
class Budgets(Resource):
    #get all budget by budget name only of that particular user
    @jwt_required()
    @api.expect(parser)
    def get(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            user_id = current_user.get("id")
            contains = request.args.get('contains')
            page_size = int(request.args.get('page_size',10))
            page_index = int(request.args.get('page_index',1))
            offset_val = (page_index - 1) * page_size

            cursor = connector.cursor(buffered=True, dictionary=True)
            query = f"SELECT id, name, created_at FROM budgets WHERE user_id = {user_id} "
            filter_query = f"AND name like '%{contains}%'"

            pagination_query = f" LIMIT {page_size} OFFSET {offset_val}"

            query = query + filter_query if contains else query
            query = query + pagination_query if page_size or page_index else query
            cursor.execute(query)
            budgets = cursor.fetchall()
            if not budgets:
                return Response(status=400, response=json.dumps({"message": "No budgets found"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"items": budgets,"count": len(budgets)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))
    
    #add budget of that particular user
    @jwt_required()
    @api.expect(budget_parser)
    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            data = request.get_json()
            budget_name = data.get("budget_name")
            if "budget_name" not in data.keys() or not budget_name:
                return Response(status= 400, response=json.dumps({"message":f"Budget name is required"}))

            user_id = current_user.get("id")

            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM users where id = %s"
            cursor.execute(query, [user_id])
            user = cursor.fetchone()

            if user is None:
                return Response(status= 400, response=json.dumps({"message":f"No user found with {user_id}"}))

            query = "SELECT * FROM budgets where user_id = %s AND name = %s"
            cursor.execute(query, [user_id, budget_name])
            budget = cursor.fetchone()
            if budget is None:
                query = '''
                    Insert into budgets (name, user_id)
                    VALUES (%s, %s)
                '''
                value = (budget_name, user_id)
                cursor.execute(query, value)
            else:
                return Response(status=200, response=json.dumps({"message": f"Budget exist with name {budget_name}"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Budget created Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

@api.route("/budgets/<int:id>")
class Budget(Resource):
    #get budgets by budget id of that particular user only
    @jwt_required()
    def get(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM budgets where id = %s"
            cursor.execute(query, [id])
            budget = cursor.fetchone()

            if not budget:
                return Response(status= 400, response=json.dumps({"message":f"Budget with {id} not found for retrieve"}))
            
            elif budget.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to access budget"}))

            query = "SELECT name, created_at FROM budgets where id = %s"
            cursor.execute(query, [id])
            budget = cursor.fetchall()
            connector.commit()
            return Response(status = 200, response=json.dumps({"items": budget,"count": len(budget)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    #update budget by budget id of that particular user only
    @jwt_required()
    @api.expect(budget_parser)
    def put(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            data = request.get_json()
            budget_name = data.get("budget_name")
            if "budget_name" not in data.keys() or not budget_name:
                return Response(status= 400, response=json.dumps({"message":f"Budget name is required"}))

            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM budgets where id = %s"
            cursor.execute(query, [id])
            budget = cursor.fetchone()

            if not budget:
                return Response(status= 400, response=json.dumps({"message":f"Budget with {id} not found for update"}))

            elif budget.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to update budget"}))

            query = "UPDATE budgets SET name = %s where id = %s"
            cursor.execute(query, [budget_name, id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Budget updated Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    #delete budget by budget id of that particular user only.
    @jwt_required()
    def delete(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM budgets where id = %s"
            cursor.execute(query, [id])
            budget = cursor.fetchone()

            if not budget:
                return Response(status= 400, response=json.dumps({"message":f"Budget with {id} not found for delete"}))

            elif budget.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to delete budget"}))

            query = "DELETE FROM budgets WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Budget deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))