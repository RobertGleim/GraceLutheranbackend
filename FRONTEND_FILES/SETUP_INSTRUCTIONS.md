# Admin Portal Setup Instructions

This admin portal allows admins to manage the "Message from the Pastor" section with full CRUD functionality.

## 📋 What Was Created

### Backend Changes (Already in workspace):
1. ✅ **app/models.py** - PastorMessage model (already existed)
2. ✅ **app/blueprints/pastor_messages/routes.py** - Added GET all messages route and admin_required decorators
3. ✅ **app/__init__.py** - Registered pastor_messages blueprint
4. ✅ **app/utils/auth.py** - admin_required decorator (already existed)

### Frontend Files (Copy to your Frontend folder):
1. **frontend_files/AdminView.jsx** - Complete admin portal component
2. **frontend_files/AdminView.css** - Styling for admin portal
3. **frontend_files/HomeView.jsx** - Updated to fetch and display active pastor message
4. **frontend_files/.env.example** - Environment variables template

---

## 🚀 Step-by-Step Setup

### Backend Setup (Already Done ✅)

The backend is ready! All necessary changes have been made to:
- Register the pastor_messages blueprint
- Add GET all messages endpoint
- Secure admin routes with admin_required decorator
- Fix field names in update route

### Frontend Setup (You need to do this)

#### 1. Copy Frontend Files

Copy these files from `Backend/frontend_files/` to your frontend project:

```bash
# From Backend/frontend_files/
cp AdminView.jsx ../Frontend/Grace_Lutheran/src/views/
cp AdminView.css ../Frontend/Grace_Lutheran/src/views/
cp HomeView.jsx ../Frontend/Grace_Lutheran/src/views/
```

#### 2. Update Your .env File

In `Frontend/Grace_Lutheran/.env`, add:

```env
VITE_API_URL=http://localhost:5000
```

For production, change to your deployed backend URL.

#### 3. Update Your Routes (App.jsx or wherever you define routes)

Add the admin route to your React Router:

```jsx
import AdminView from './views/AdminView';

// In your routes:
<Route path="/admin" element={<AdminView />} />
```

#### 4. Update Navigation (NavBar.jsx)

Add a link to the admin portal (only show if user is admin):

```jsx
// In your NavBar component
const user = JSON.parse(localStorage.getItem('user') || '{}');

{user.role === 'admin' && (
  <Link to="/admin">Admin Portal</Link>
)}
```

---

## 🔧 API Endpoints Reference

### Public Endpoints:
- **GET** `/pastor-messages/active` - Get the currently active message
- **GET** `/pastor-messages` - Get all messages

### Admin-Only Endpoints (Require admin token):
- **POST** `/pastor-messages` - Create new message
- **PUT** `/pastor-messages/:id` - Update message
- **DELETE** `/pastor-messages/:id` - Delete message
- **PATCH** `/pastor-messages/:id/activate` - Set message as active

---

## 👨‍💻 How to Use the Admin Portal

### 1. Login as Admin

First, create an admin user or update an existing user's role to 'admin' in your database:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
```

### 2. Access Admin Portal

Navigate to `/admin` in your application (e.g., http://localhost:5173/admin)

### 3. Create a Message

1. Fill in the form at the top:
   - **Title**: Enter a title for the message
   - **Message**: Enter the pastor's message
   - **Set as Active**: Check to make this the active message (will deactivate others)
2. Click "Create Message"

### 4. Edit a Message

1. Find the message in the list below
2. Click the "Edit" button
3. Update the form that appears at the top
4. Click "Update Message"

### 5. Activate a Message

- Click the "Activate" button on any inactive message
- This will make it the active message shown on the home page

### 6. Delete a Message

- Click the "Delete" button
- Confirm the deletion in the popup

---

## 🎨 Features

### Admin Portal Features:
- ✅ **Create** new pastor messages
- ✅ **Read** all messages (list view)
- ✅ **Update** existing messages
- ✅ **Delete** messages (with confirmation)
- ✅ **Activate** messages (only one can be active at a time)
- ✅ Form validation
- ✅ Loading states
- ✅ Error handling
- ✅ Success notifications
- ✅ Responsive design

### Home Page Features:
- ✅ Displays active pastor message
- ✅ Falls back to Lorem Ipsum if no active message
- ✅ Automatic loading state
- ✅ Error handling

---

## 🔐 Security Notes

- All admin endpoints require authentication with admin role
- Token is stored in localStorage after login
- Token is sent in Authorization header as Bearer token
- Non-admin users will get 403 Forbidden errors

---

## 🐛 Troubleshooting

### "Token is missing" error:
- Make sure you're logged in
- Check that token is in localStorage: `localStorage.getItem('token')`

### "Admin access required" error:
- Your user role must be 'admin'
- Update in database: `UPDATE users SET role = 'admin' WHERE id = YOUR_USER_ID;`

### CORS errors:
- Make sure CORS is enabled in backend (already done in flask_app.py)
- Check that VITE_API_URL in .env matches your backend URL

### No messages showing on home page:
- Create a message in admin portal
- Make sure "Set as Active" is checked
- Check browser console for errors

---

## 📝 Code Quality Notes

This code is written in a bootcamp-friendly style with:
- Clear variable names
- Comments explaining each function
- Basic error handling with try/catch
- Simple state management with useState
- Standard fetch API calls
- No complex libraries or patterns
- Readable CSS with clear class names

---

## 🎓 Learning Points

This project demonstrates:
1. **Full CRUD Operations** - Create, Read, Update, Delete
2. **REST API Design** - Proper HTTP methods (GET, POST, PUT, DELETE, PATCH)
3. **Authentication & Authorization** - Token-based auth with role checking
4. **React Hooks** - useState, useEffect
5. **Forms & Input Handling** - Controlled components
6. **Async/Await** - Modern JavaScript promises
7. **Error Handling** - Try/catch blocks
8. **Responsive Design** - Mobile-friendly CSS
9. **User Experience** - Loading states, confirmations, notifications

---

## 📞 Need Help?

If you run into issues:
1. Check the browser console for errors
2. Check the backend terminal for errors
3. Verify your .env file has the correct API_URL
4. Make sure backend is running on the correct port
5. Verify you're logged in as an admin user

Happy coding! 🎉
