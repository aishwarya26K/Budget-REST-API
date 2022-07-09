from flask import Flask
from flask_restful import Api
import os
import sys

project_root = os.path.dirname(os.path.realpath(os.path.join(__file__)))
sys.path.append(os.path.join(project_root, "src", "users"))


from userServices import Users
from budgetServices import Budgets
from categoryServices import Category
from incomeExpensesServices import IncomeExpenses


app = Flask(__name__)
api = Api(app)

api.add_resource(Users, "/api/v1/users/<id>", "/api/v1/users/")
api.add_resource(Budgets, "/api/v1/budgets/<id>", "/api/v1/budgets/")
api.add_resource(Category, "/api/v1/categories/<id>", "/api/v1/categories/")
api.add_resource(IncomeExpenses, "/api/v1/income_expenses/<id>", "/api/v1/income_expenses/")

if __name__ == '__main__':
    app.run(debug=True)