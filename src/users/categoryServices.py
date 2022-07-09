from flask_restful import Resource
from flask import request, Response, json
from datetime import timedelta, datetime

from connection import getConnectToSQLdb


class Category(Resource):
    def get(self, id = None):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            cursor = connector.cursor(buffered=True)
            if id:
                query = "SELECT * FROM categories where id = %s"
                cursor.execute(query, [id])
                category = cursor.fetchall()
                connector.commit()
                return Response(status = 200, response=json.dumps({"message":f"category with {id} not found"}) if not category else json.dumps({"categories": category,"total_categories": len(category)}))
            else:
                query = "SELECT * FROM categories"
                cursor.execute(query)
                categories = cursor.fetchall()
                if not categories:
                    return Response(status=200, response=json.dumps({"message": "No categories found"}))
                connector.commit()
                return Response(status=200, response=json.dumps({"categories": categories,"total_categories": len(categories)}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))

    def post(self):
        cursor = None
        connector = getConnectToSQLdb()
        try:
            data = request.get_json()
            category_name = data.get("category_name")
            if "category_name" not in data.keys() or not category_name:
                return Response(status= 422, response=json.dumps({"message":f"Category name is required"}))

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
                return Response(status=400, response=json.dumps({"message": "Category exist"}))
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category created Successfully"}))
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
            category_name = data.get("category_name")
            if "category_name" not in data.keys() or not category_name:
                return Response(status= 422, response=json.dumps({"message":f"Category name is required"}))

            cursor = connector.cursor(buffered=True)
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchone()

            if not category:
                return Response(status= 422, response=json.dumps({"message":f"category with {id} not found for update"}))

            query = "UPDATE categories SET name = %s where id = %s"
            cursor.execute(query, [category_name, id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category updated Successfully"}))
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
            query = "SELECT * FROM categories where id = %s"
            cursor.execute(query, [id])
            category = cursor.fetchone()

            if not category:
                return Response(status= 422, response=json.dumps({"message":f"category with {id} not found for delete"}))

            query = "DELETE FROM categories WHERE id = %s"
            cursor.execute(query, [id])
            connector.commit()
            return Response(status=200, response=json.dumps({"message": "Category deleted Successfully"}))
        except Exception as e:
            cursor and cursor.close()
            connector and connector.rollback()
            connector and connector.close()
            return Response(status = 500, response=json.dumps({"message": str(e)}))