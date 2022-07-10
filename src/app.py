"""Flask Application"""

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from src.services.userServices import Users, User
from src.services.budgetServices import Budgets, Budget
from src.services.categoryServices import Categories, Category
from src.services.incomeExpensesServices import IncomeExpenses, OneIncomeExpense
from src.services.auth import Register, Login


app = Flask(__name__)
api = Api(app)

swagger = Swagger(app)

app.config["JWT_SECRET_KEY"] = "budget-app"
jwt = JWTManager(app)

api.add_resource(Users, "/api/v1/users/")
api.add_resource(User, "/api/v1/users/<int:id>")

api.add_resource(Budgets, "/api/v1/budgets/")
api.add_resource(Budget, "/api/v1/budgets/<int:id>")

api.add_resource(Categories, "/api/v1/categories/")
api.add_resource(Category, "/api/v1/categories/<int:id>")

api.add_resource(IncomeExpenses, "/api/v1/income_expenses/")
api.add_resource(OneIncomeExpense, "/api/v1/income_expenses/<id>")

api.add_resource(Register, "/api/v1/register/<id>", "/api/v1/register/")
api.add_resource(Login, "/api/v1/login/<id>", "/api/v1/login/")
