from flask_restx import Resource, Namespace, reqparse
from flask import request, Response, json
from flask_jwt_extended import jwt_required, current_user

from src.utils.connection import getConnectToSQLdb
from src.utils.requestParsers import pagination_parser

api = Namespace('IncomeExpense', description='IncomeExpense related apis')

parser = pagination_parser.copy()
parser.add_argument('contains', help='filtering transaction by name only', location='args')

#POST
income_expenses_parser = reqparse.RequestParser()
income_expenses_parser.add_argument('trans_name', required=True, help='transaction name required', location='json')
income_expenses_parser.add_argument('amount',type=int, required=True, help='amount required', location='json')
income_expenses_parser.add_argument('budget_id',type=int,required=True, help='budget id required', location='json')
income_expenses_parser.add_argument('is_expense', type=bool, help='is_expense', location='json')
income_expenses_parser.add_argument('category_id',type=int, help="category id can't be zero", location='json')

#PUT
income_put_parser = reqparse.RequestParser()
income_put_parser.add_argument('amount',type=int, required=True, help='amount required', location='json')


def validateIncomeExpense(request):
    required_fields = ["trans_name", "amount","budget_id"]

    data = request.get_json()
    error_fields = {}
    actual_data = { field:value for field,value in data.items() }
    
    for field in required_fields:
        if field not in data or not data.get(field):
            error_fields[field] = f"{field} is required"

    if error_fields:
        return [False , actual_data, {"message": error_fields}]    
    
    return [True, actual_data, {}]

@api.route("/income_expenses")
class IncomeExpenses(Resource):
    #get all Income Expenses by transaction name only of that particular user
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
            query = f"SELECT name, created_at, amount FROM income_expenses WHERE user_id = {user_id} "
            filter_query = f"AND name like '%{contains}%'"

            pagination_query = f" LIMIT {page_size} OFFSET {offset_val}"

            query = query + filter_query if contains else query
            query = query + pagination_query if page_size or page_index else query
            cursor.execute(query)
            income_expenses = cursor.fetchall()
            if not income_expenses:
                return Response(status=400, response=json.dumps({"message": "No income_expenses found"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"items": income_expenses,"count": len(income_expenses)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))
    
    #add income expenses of that particular user
    @jwt_required()
    @api.expect(income_expenses_parser)
    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateIncomeExpense(request)
            if not isValid: return Response(status= 400, response=json.dumps(errorObj))

            user_id = current_user.get("id")

            category_id = data.get('category_id')
            budget_id = data.get('budget_id')
            trans_name = data.get('trans_name')

            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM budgets where id = %s AND user_id = %s"
            cursor.execute(query, [budget_id, user_id])
            budget = cursor.fetchone()

            if budget is None:
                return Response(status= 400, response=json.dumps({"message":f"No budget found with {data.get('budget_id')}"}))

            if category_id:
                query = "SELECT * FROM categories where id = %s AND user_id = %s"
                cursor.execute(query, [category_id, user_id])
                category = cursor.fetchone()
                if category is None:
                    return Response(status= 400, response=json.dumps({"message":f"No category found with {category_id}"}))

            query = f"SELECT * FROM income_expenses where user_id ={user_id} AND budget_id = {budget_id} AND name = '{trans_name}'"
            category_query = f" AND category_id = {category_id}"
            query = query + category_query if category_id else query
            cursor.execute(query)
            income_expense = cursor.fetchone()

            if income_expense is None:
                query = '''
                    Insert into income_expenses (name, category_id, budget_id, amount, is_expense, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                '''
                value = (trans_name, category_id, budget_id, data.get('amount'), data.get('is_expense'), user_id)
                cursor.execute(query, value)
            else:
                return Response(status=200, response=json.dumps({"message": "Transaction exist"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Transaction created Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))


@api.route("/income_expenses/<int:id>")
class OneIncomeExpense(Resource):
    @jwt_required()
    def get(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expenses = cursor.fetchone()

            if not income_expenses:
                return Response(status= 400, response=json.dumps({"message":f"income_expenses with {id} not found for retrieve"}))
            
            elif income_expenses.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to access income_expenses"}))

            query = "SELECT name, created_at, amount  FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expenses = cursor.fetchone()
            connector.commit()
            return Response(status = 200, response=json.dumps({"items": income_expenses,"count": len(income_expenses)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    @jwt_required()
    @api.expect(income_put_parser)
    def put(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            data = request.get_json()
            amount = data.get("amount")
            if "amount" not in data.keys() or not amount:
                return Response(status= 400, response=json.dumps({"message":f"amount is required"}))

            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expense = cursor.fetchone()

            if not income_expense:
                return Response(status= 400, response=json.dumps({"message":f"income_expense with {id} not found for update"}))

            elif income_expense.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to update income_expense"}))

            query = "UPDATE income_expenses SET amount = %s where id = %s"
            cursor.execute(query, [amount, id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Income expenses updated Successfully"}))
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
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expense = cursor.fetchone()

            if not income_expense:
                return Response(status= 400, response=json.dumps({"message":f"income_expense with {id} not found for delete"}))

            elif income_expense.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to delete income_expense"}))

            query = "DELETE FROM income_expenses WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Income expenses deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))