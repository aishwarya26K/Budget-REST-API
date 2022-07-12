from flask_restx import Api

from src.services.auth import api as authNS
from src.services.userServices import api as UsersNS
from src.services.categoryServices import api as CategoriesNS
from src.services.budgetServices import api as BudgetNS
from src.services.incomeExpensesServices import api as incomeExpensesNS

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    title='Family Budget API',
    version='1.0',
    description='REST API for managing family budget',
    authorizations=authorizations,
    security='apikey'
    # All API metadatas
)
API_V1 = "/api/v1"
api.add_namespace(authNS, path=API_V1)
api.add_namespace(UsersNS, path=API_V1)
api.add_namespace(CategoriesNS, path=API_V1)
api.add_namespace(BudgetNS, path=API_V1)
api.add_namespace(incomeExpensesNS, path=API_V1)