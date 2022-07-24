# Family Budget REST API Application

This is a REST API application for managing family budgets.

## App
https://budget-rest-api-jpakotmwxa-uc.a.run.app/

## Installation
1. Clone this repository.
```bash
git clone https://github.com/aishwarya26K/Budget-REST-API.git
cd Budget-REST-API
```
2. Install the package manager Pip and then install Pipenv.

```bash
pip install pipenv
```
3. Install the project dependencies.
```bash
pipenv install
```
4. Start the development environment.
```bash
$env:FLASK_ENV = "development"
flask run
```
5. You should see the following after `flask run`
```bash
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
```
You are ready !!


## API
The APIs are build for five use cases, they are:
  - [Authorization](#authorization)
  - [Users](#users) :lock:
  - [Budgets](#budgets) :lock:
  - [Categories](#categories) :lock:
  - [Income Expenses](#income-expenses) :lock:

## Authorization
Purpose: This usecase is mainly for registering a new user and logging a user.

### Login
  - POST /api/v1/login
  - The user who is logged in will receive a access token and with that access token only it can access all the APIs.
##### [ Note - The access token is valid for 15 mins ]
### Register
  - POST /api/v1/register

## Users
Purpose: This section of APIs are to be used for handling user related details.
  - POST /api/v1/users
  - GET /api/v1/users
  - PUT /api/v1/users/{id}
  - DELETE /api/v1/users/{id}
  - GET /api/v1/users/{id}

## Budgets
Purpose: This section of APIs are to be used by logged-in users to add a budget, retrieve budgets or budget, and update or delete a budget.
  - POST /api/v1/budgets
  - GET /api/v1/budgets]
  - PUT /api/v1/budgets/{id}
  - DELETE /api/v1/budgets/{id}
  - GET /api/v1/budgets/{id}

## Categories
Purpose: This section of APIs are to be used by logged-in users to add a category, retrieve categories or category, and update or delete a category.
  - POST /api/v1/categories
  - GET /api/v1/categories
  - PUT /api/v1/categories/{id}
  - DELETE /api/v1/categories/{id}
  - GET /api/v1/categories/{id}

## Income Expenses
Purpose: This section of APIs are to be used by logged-in users to add income expense, retrieve income expense or income expenses, and update or delete an income expense.
  - POST /api/v1/income_expenses
  - GET /api/v1/income_expenses
  - PUT /api/v1/income_expenses/{id}
  - DELETE /api/v1/income_expenses/{id}
  - GET /api/v1/income_expenses/{id}

## Technology Stacks
- Python 3.9.2
- Flask 2.1.2
- MySQL 
- Google Cloud Run (for deployment)
