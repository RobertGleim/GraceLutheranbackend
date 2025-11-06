# Backend API Testing Guide

## Test the Pastor Messages API

### 1. Start your Flask backend
```bash
python flask_app.py
```

### 2. Test Public Endpoints (No Auth Required)

#### Get All Messages
```bash
curl -X GET http://localhost:5000/pastor-messages
```

#### Get Active Message
```bash
curl -X GET http://localhost:5000/pastor-messages/active
```

---

### 3. Test Admin Endpoints (Auth Required)

First, you need to:
1. Create an admin user
2. Login to get a token
3. Use that token for admin requests

#### Step 3.1: Create an Admin User

```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@gracelutheran.com",
    "password": "admin123",
    "role": "admin"
  }'
```

#### Step 3.2: Login to Get Token

```bash
curl -X POST http://localhost:5000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gracelutheran.com",
    "password": "admin123"
  }'
```

**Save the token from the response!** It will look like:
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {...}
}
```

#### Step 3.3: Create a Pastor Message

Replace `YOUR_TOKEN_HERE` with your actual token:

```bash
curl -X POST http://localhost:5000/pastor-messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Welcome Message",
    "message": "Dear congregation, I hope this message finds you well. This week we reflect on faith and community...",
    "is_active": true
  }'
```

#### Step 3.4: Update a Message

Replace `MESSAGE_ID` with the actual ID and `YOUR_TOKEN_HERE` with your token:

```bash
curl -X PUT http://localhost:5000/pastor-messages/MESSAGE_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Updated Welcome Message",
    "message": "This is an updated message from the pastor...",
    "is_active": true
  }'
```

#### Step 3.5: Activate a Message

```bash
curl -X PATCH http://localhost:5000/pastor-messages/MESSAGE_ID/activate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Step 3.6: Delete a Message

```bash
curl -X DELETE http://localhost:5000/pastor-messages/MESSAGE_ID \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Using Postman (Easier!)

If you prefer Postman:

### 1. Import the Collection

Use the existing `postman/Grace Lutheran.postman_collection.json`

### 2. Add Pastor Messages Requests

Create a new folder "Pastor Messages" with these requests:

**GET All Messages**
- Method: GET
- URL: {{base_url}}/pastor-messages

**GET Active Message**
- Method: GET
- URL: {{base_url}}/pastor-messages/active

**CREATE Message**
- Method: POST
- URL: {{base_url}}/pastor-messages
- Headers: Authorization: Bearer {{token}}
- Body (JSON):
```json
{
  "title": "Weekly Message",
  "message": "Your message content here...",
  "is_active": true
}
```

**UPDATE Message**
- Method: PUT
- URL: {{base_url}}/pastor-messages/1
- Headers: Authorization: Bearer {{token}}
- Body (JSON):
```json
{
  "title": "Updated Title",
  "message": "Updated content...",
  "is_active": true
}
```

**DELETE Message**
- Method: DELETE
- URL: {{base_url}}/pastor-messages/1
- Headers: Authorization: Bearer {{token}}

**ACTIVATE Message**
- Method: PATCH
- URL: {{base_url}}/pastor-messages/1/activate
- Headers: Authorization: Bearer {{token}}

---

## Expected Responses

### Success Responses:

**Create (201):**
```json
{
  "message": "Pastor message created successfully.",
  "data": {
    "id": 1,
    "title": "Welcome Message",
    "message": "Dear congregation...",
    "is_active": true
  }
}
```

**Update (200):**
```json
{
  "message": "Pastor message updated successfully.",
  "data": {...}
}
```

**Delete (200):**
```json
{
  "message": "Pastor message deleted successfully."
}
```

### Error Responses:

**401 Unauthorized:**
```json
{
  "message": "Token is missing!"
}
```

**403 Forbidden:**
```json
{
  "message": "Admin access required!"
}
```

**404 Not Found:**
```json
{
  "message": "Pastor message not found."
}
```
