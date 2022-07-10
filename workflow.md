## Routes:
1. users/
    - post (create a user)
     - add verification
        - confirm password === pasword and emai should not be exist in DB
    - if verified then create a user and send response
    - get/<int id>
        - if id is passed fetch the details of the current user id
        - if id is None then return all the users

    - patch/<int id>
     - must get an id if not throw 422 bad request
     - if has id update the data according to the payload
     
    - delete/ <int id>
     - id is required. if not id thwrow 422 error
     - if id then delete the user

authentication:
    - create users/authenticationService.py
    - install flask-jwt-extended
    - authenticationservice.py
        - two methods to authenticate
        - register
            - validate all the required fields. and create user
        - login
            - 
authorization:
    -done

api/v1/<model>?contains=

eg: api/v1/users/?contains="r"

