# CodeAthon REST API

## Project Overview

This project is a REST API developed using Python, Flask, and MongoDB. It manages organisations and their employees and implements JWT-based authentication and role-based access control (RBAC).

## Technologies Used

* **Python**: Backend programming
* **Flask**: REST API development
* **MongoDB**: NoSQL database
* **PyMongo**: MongoDB integration
* **PyJWT**: JWT authentication
* **bcrypt**: Password hashing
* **python-dotenv**: Environment variable management
* **Postman**: API testing

## Features

* User registration and login
* Secure password hashing
* JWT token generation and verification
* Organisation CRUD operations
* Employee CRUD operations
* Relationship between employees and organisations
* Role-based permissions for viewers, editors, and admins
* Input validation and appropriate HTTP status codes

## Project Structure

```text
codeathon/
├── app.py
├── database.py
├── auth_utils.py
├── permissions.py
├── set_user_role.py
├── requirements.txt
└── routes/
    ├── auth_routes.py
    ├── organisation_routes.py
    └── employee_routes.py
```

## Setup Instructions

### 1. Clone or download the project

Open the project folder in VS Code.

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```dotenv
MONGO_URI=mongodb://127.0.0.1:27017/
MONGO_DB=CodeAthonDB
JWT_SECRET=your_long_random_secret
```

Replace the example secret with a secure random value. Ensure MongoDB is installed and running.

### 5. Start the application

```bash
python app.py
```

The API runs locally at `http://127.0.0.1:5000` by default.

## Main Endpoints

 GET    : '/'                   - Check API availability           
 GET    : '/health'             - Check database connectivity      
 POST   : '/register'           - Register a user                  
 POST   : '/login'              - Log in and obtain a JWT          
 POST   : '/organisations'      - Create an organisation           
 GET    : '/organisations'      - List organisations               
 GET    : '/organisations/<id>' - Retrieve one organisation        
 PUT    : '/organisations/<id>' - Update organisation details      
 PATCH  : '/organisations/<id>' - Partially update an organisation 
 
 DELETE : '/organisations/<id>' - Delete an organisation           
 POST   : '/employees'          - Create an employee               
 GET    : '/employees'          - List employees                   
 GET    : '/employees/<id>'     - Retrieve one employee            
 PUT    : '/employees/<id>'     - Update employee details          
 PATCH  : '/employees/<id>'     - Partially update an employee     
 DELETE : '/employees/<id>'     - Delete an employee               

## Authentication

Register a user and log in to obtain an access token. For protected endpoints, configure the request's Authorization header in Postman:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Role-Based Access Control

The current implementation uses these roles:

* **Viewer**: Read-only access
* **Editor**: Create, read, and update access
* **Admin**: Create, read, update, and delete access

Privileged roles are assigned through the local administrative script.

## Testing

Use Postman to test successful requests, invalid inputs, missing or invalid tokens, insufficient permissions, and missing records.

## Database

The application uses the 'CodeAthonDB' database with 'organisations', 'employees', and 'users' collections.

## Security Notes

* Passwords are stored as bcrypt hashes.
* JWTs have an expiration time.
* The .env file must not be committed to version control.
* The development server should not be used as a production server.
