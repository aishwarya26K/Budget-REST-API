from flask_restx import Resource, Namespace, reqparse
from flask import request, Response, json
from flask_jwt_extended import jwt_required

from src.utils.connection import getConnectToSQLdb

api = Namespace('Categories', description='Categories related apis')

parser = reqparse.RequestParser()
parser.add_argument('contains', help='filtering category by name only', location='args')

#PUT, POST
category_parser = reqparse.RequestParser()
category_parser.add_argument('category_name', required=True, help='category name required', location='json')


class Categories(Resource):
    @jwt_required()
    @api.expect(parser)
    def get(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            contains = request.args.get('contains')
            query = "SELECT * FROM categories "
            filter_query = f"WHERE name like '%{contains}%'"
            query = query + filter_query if contains else query
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

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM categories where name = %s"
            cursor.execute(query, [category_name])
            category = cursor.fetchone()

            if category is None:
                query = '''
                    Insert into categories (name)
                    VALUES (%s)
                '''
                value = [category_name]
                cursor.execute(query, value)
            else:
                return Response(status=200, response=json.dumps({"message": "Category exist"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category created Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))


class Category(Resource):
    @jwt_required()
    def get(self, id ):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchall()
            connector.commit()
            return Response(status = 200, response=json.dumps({"message":f"category with {id} not found"}) if not category else json.dumps({"items": category,"count": len(category)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))
    
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

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchone()

            if not category:
                return Response(status= 400, response=json.dumps({"message":f"category with {id} not found for update"}))

            query = "UPDATE categories SET name = %s where id = %s"
            cursor.execute(query, [category_name, id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category updated Successfully"}))
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
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchone()

            if not category:
                return Response(status= 400, response=json.dumps({"message":f"category with {id} not found for delete"}))

            query = "DELETE FROM categories WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))