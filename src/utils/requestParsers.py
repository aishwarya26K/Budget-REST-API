from flask_restx import reqparse

#pagination parser
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page_index', help='Page number', type=int, location='args')
pagination_parser.add_argument('page_size', help='No. of items in each page',type=int, location='args')