from flask_restful import Resource
from flask import request, Response, json
from datetime import timedelta, datetime

from connection import getConnectToSQLdb


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
    def get(self, id = None):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True)
            if id:
                query = "SELECT * FROM income_expenses where id = %s"
                cursor.execute(query, [id])
                income_expenses = cursor.fetchall()
                connector.commit()
                return Response(status = 200, response=json.dumps({"message":f"income_expenses with {id} not found"}) if not income_expenses else json.dumps({"income_expenses": income_expenses,"total_income_expenses": len(income_expenses)}))
            else:
                query = "SELECT * FROM income_expenses"
                cursor.execute(query)
                income_expenses = cursor.fetchall()
                if not income_expenses:
                    return Response(status=200, response=json.dumps({"message": "No income_expenses found"}))
                connector.commit()
                return Response(status=200, response=json.dumps({"income_expenses": income_expenses,"total_income_expenses": len(income_expenses)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            [isValid, data ,errorObj] = validateIncomeExpense(request)
            if not isValid: return Response(status= 422, response=json.dumps(errorObj))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM budgets where id = %s"
            cursor.execute(query, [data.get('budget_id')])
            budget = cursor.fetchone()

            if budget is None:
                return Response(status= 422, response=json.dumps({"message":f"No budget found with {data.get('budget_id')}"}))
            
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [data.get('category_id')])
            category = cursor.fetchone()

            if category is None:
                return Response(status= 422, response=json.dumps({"message":f"No category found with {data.get('category_id')}"}))

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
                return Response(status=400, response=json.dumps({"message": "Transaction exist"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Transaction created Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    def put(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            data = request.get_json()
            amount = data.get("amount")
            if "amount" not in data.keys() or not amount:
                return Response(status= 422, response=json.dumps({"message":f"amount is required"}))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expense = cursor.fetchone()

            if not income_expense:
                return Response(status= 422, response=json.dumps({"message":f"Income expenses with {id} not found for update"}))

            query = "UPDATE income_expenses SET amount = %s where id = %s"
            cursor.execute(query, [amount, id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Income expenses updated Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    def delete(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM income_expenses where id = %s"
            cursor.execute(query, [id])
            income_expense = cursor.fetchone()

            if not income_expense:
                return Response(status= 422, response=json.dumps({"message":f"Income expenses with {id} not found for delete"}))

            query = "DELETE FROM income_expenses WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Income expenses deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))