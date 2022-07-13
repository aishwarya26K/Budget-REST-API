from flask_restx import Resource, Namespace, reqparse
from flask import request, Response, json
from flask_jwt_extended import jwt_required, current_user

from src.utils.connection import getConnectToSQLdb
from src.utils.requestParsers import pagination_parser

api = Namespace('Categories', description='Categories related apis')

parser = pagination_parser.copy()
parser.add_argument('contains', help='filtering category by name only', location='args')

#PUT, POST
category_parser = reqparse.RequestParser()
category_parser.add_argument('category_name', required=True, help='category name required', location='json')

@api.route('/categories')
class Categories(Resource):
    #get all categories by category name only of that particular user
    @jwt_required()
    @api.expect(parser)
    def get(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            user_id = current_user.get("id")
            cursor = connector.cursor(buffered=True, dictionary=True)
            contains = request.args.get('contains')
            page_size = int(request.args.get('page_size',10))
            page_index = int(request.args.get('page_index',1))
            offset_val = (page_index - 1) * page_size

            query = f"SELECT id, name, created_at FROM categories WHERE user_id ={user_id}"
            filter_query = f" AND name like '%{contains}%'"

            pagination_query = f" LIMIT {page_size} OFFSET {offset_val}"

            query = query + filter_query if contains else query
            query = query + pagination_query if page_size or page_index else query
            cursor.execute(query)
            category = cursor.fetchall()
            if not category:
                return Response(status=400, response=json.dumps({"message": "No categories found"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"items": category,"count": len(category)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))
    
    #add category of that particular user
    @jwt_required()
    @api.expect(category_parser)
    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            data = request.get_json()
            category_name = data.get("category_name")
            if "category_name" not in data.keys() or not category_name:
                return Response(status= 400, response=json.dumps({"message":f"Category name is required"}))

            user_id = current_user.get("id")

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM users where id = %s"
            cursor.execute(query, [user_id])
            user = cursor.fetchone()

            if user is None:
                return Response(status= 400, response=json.dumps({"message":f"No user found with {user_id}"}))

            query = "SELECT * FROM categories where user_id = %s AND name = %s"
            cursor.execute(query, [user_id, category_name])
            category = cursor.fetchone()

            if category is None:
                query = '''
                    Insert into categories (name, user_id)
                    VALUES (%s, %s)
                '''
                value = [category_name, user_id]
                cursor.execute(query, value)
            else:
                return Response(status=200, response=json.dumps({"message": f"Category exist with name {category_name}"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category created Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))


@api.route('/categories/<int:id>')
class Category(Resource):
    #get categories by category id of that particular user only
    @jwt_required()
    def get(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchone()
            print(category)
            print(current_user.get("id"))

            if not category:
                return Response(status= 400, response=json.dumps({"message":f"category with {id} not found for retrieve"}))
            
            elif category.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to access category"}))

            query = "SELECT name, created_at FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchall()
            connector.commit()
            return Response(status = 200, response=json.dumps({"items": category,"count": len(category)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))
    
    #update category by category id of that particular user only
    @jwt_required()
    @api.expect(category_parser)
    def put(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            data = request.get_json()
            category_name = data.get("category_name")
            if "category_name" not in data.keys() or not category_name:
                return Response(status= 400, response=json.dumps({"message":f"Category name is required"}))

            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchone()

            if not category:
                return Response(status= 400, response=json.dumps({"message":f"Category with {id} not found for update"}))

            elif category.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to update category"}))

            query = "UPDATE categories SET name = %s where id = %s"
            cursor.execute(query, [category_name, id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category updated Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    #delete category by budget id of that particular user only.
    @jwt_required()
    def delete(self, id):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchone()

            if not category:
                return Response(status= 400, response=json.dumps({"message":f"Category with {id} not found for delete"}))

            elif category.get('user_id') != current_user.get("id"):
                return Response(status= 401, response=json.dumps({"message":f"Unauthorized user to delete category"}))

            query = "DELETE FROM categories WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))