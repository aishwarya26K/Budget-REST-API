from flask_restx import Resource, Namespace, reqparse
from flask import request, Response, json
from flask_jwt_extended import jwt_required

from src.utils.connection import getConnectToSQLdb

api = Namespace('IncomeExpense', description='IncomeExpense related apis')

parser = reqparse.RequestParser()
parser.add_argument('contains', help='filtering transaction by name only', location='args')

#POST
income_expenses_parser = reqparse.RequestParser()
income_expenses_parser.add_argument('trans_name', required=True, help='transaction name required', location='json')
income_expenses_parser.add_argument('amount', required=True, help='amount required', location='json')
income_expenses_parser.add_argument('budget_id',required=True, help='budget id required', location='json')
income_expenses_parser.add_argument('is_expense',required=True, help='is_expense id required', location='json')
income_expenses_parser.add_argument('category_id',required=True, help='category id required', location='json')

#PUT
income_put_parser = reqparse.RequestParser()
income_expenses_parser.add_argument('amount',required=True, help='amount required', location='json')


def validateIncomeExpense(request):
    required_fields = ["trans_name", "amount","budget_id","is_expense", "category_id"]

    data = request.get_json()
    error_fields = {}
    actual_data = { field:value for field,value in data.items() }
    
    for field in required_fields:
        if field not in data or not data.get(field):
            error_fields[field] = f"{field} is required"

    if error_fields:
        return [False , actual_data, {"message": error_fields}]    
    
    return [True, actual_data, {}]

class IncomeExpenses(Resource):
    @jwt_required()
    @api.expect(parser)
    def get(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            contains = request.args.get('contains')
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM income_expenses "
            filter_query = f"WHERE name like '%{contains}%'"
            query = query + filter_query if contains else query
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

    @jwt_required()
    @api.expect(income_expenses_parser)
    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateIncomeExpense(request)
            if not isValid: return Response(status= 400, response=json.dumps(errorObj))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM budgets where id = %s"
            cursor.execute(query, [data.get('budget_id')])
            budget = cursor.fetchone()

            if budget is None:
                return Response(status= 400, response=json.dumps({"message":f"No budget found with {data.get('budget_id')}"}))
            
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [data.get('category_id')])
            category = cursor.fetchone()

            if category is None:
                return Response(status= 400, response=json.dumps({"message":f"No category found with {data.get('category_id')}"}))

            query = "SELECT * FROM income_expenses where category_id = %s AND budget_id = %s"
            cursor.execute(query, [data.get('category_id'), data.get('budget_id')])
            income_expense = cursor.fetchone()

            if income_expense is None:
                query = '''
                    Insert into income_expenses (name, category_id, budget_id, amount, is_expense)
                    VALUES (%s, %s, %s, %s, %s)
                '''
                value = (data.get('trans_name'), data.get('category_id'), data.get('budget_id'), data.get('amount'), data.get('is_expense'))
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


class OneIncomeExpense(Resource):
    @jwt_required()
    def get(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expenses = cursor.fetchall()
            connector.commit()
            return Response(status = 200, response=json.dumps({"message":f"income_expenses with {id} not found"}) if not income_expenses else json.dumps({"items": income_expenses,"count": len(income_expenses)}))
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

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expense = cursor.fetchone()

            if not income_expense:
                return Response(status= 400, response=json.dumps({"message":f"Income expenses with {id} not found for update"}))

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
            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expense = cursor.fetchone()

            if not income_expense:
                return Response(status= 400, response=json.dumps({"message":f"Income expenses with {id} not found for delete"}))

            query = "DELETE FROM income_expenses WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Income expenses deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))