# 🔧 FRONTEND UPDATE GUIDE

## Step-by-Step Instructions to Update Your Frontend

Follow these steps exactly to integrate the admin portal with your existing frontend.

---

## STEP 1: Update .env File

**File:** `Frontend/.env`

**Action:** Add this line at the end of the file:

```env
VITE_API_URL=http://localhost:5000
```

If you're deploying to production, change to your deployed backend URL:
```env
VITE_API_URL=https://your-backend-url.com
```

---

## STEP 2: Replace AdminView.jsx

**File:** `Frontend/src/views/AdminView.jsx`

**Action:** Replace the ENTIRE contents of the file with the code from:
`Backend/frontend_files/AdminView.jsx`

Or copy this complete file content:

```jsx
import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import './AdminView.css';

const AdminView = () => {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  
  // State for all pastor messages
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // State for form (create/edit)
  const [isEditing, setIsEditing] = useState(false);
  const [currentMessageId, setCurrentMessageId] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    is_active: false
  });

  // Get API URL from environment or use default
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  // Check if user is admin
  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/login');
    }
  }, [user, navigate]);

  // Get token from localStorage
  const getToken = () => {
    return localStorage.getItem('token');
  };

  // Fetch all messages
  const fetchMessages = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_URL}/pastor-messages`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch messages');
      }

      const data = await response.json();
      setMessages(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching messages:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load messages when component mounts
  useEffect(() => {
    fetchMessages();
  }, []);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Handle create new message
  const handleCreate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const token = getToken();
    if (!token) {
      setError('You must be logged in as admin to create messages');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/pastor-messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to create message');
      }

      setSuccess('Message created successfully!');
      setFormData({ title: '', message: '', is_active: false });
      fetchMessages(); // Refresh the list
    } catch (err) {
      setError(err.message);
      console.error('Error creating message:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle update message
  const handleUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const token = getToken();
    if (!token) {
      setError('You must be logged in as admin to update messages');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/pastor-messages/${currentMessageId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to update message');
      }

      setSuccess('Message updated successfully!');
      setIsEditing(false);
      setCurrentMessageId(null);
      setFormData({ title: '', message: '', is_active: false });
      fetchMessages(); // Refresh the list
    } catch (err) {
      setError(err.message);
      console.error('Error updating message:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete message
  const handleDelete = async (messageId) => {
    if (!window.confirm('Are you sure you want to delete this message?')) {
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    const token = getToken();
    if (!token) {
      setError('You must be logged in as admin to delete messages');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/pastor-messages/${messageId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to delete message');
      }

      setSuccess('Message deleted successfully!');
      fetchMessages(); // Refresh the list
    } catch (err) {
      setError(err.message);
      console.error('Error deleting message:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle activate message
  const handleActivate = async (messageId) => {
    setLoading(true);
    setError('');
    setSuccess('');

    const token = getToken();
    if (!token) {
      setError('You must be logged in as admin to activate messages');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/pastor-messages/${messageId}/activate`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to activate message');
      }

      setSuccess('Message activated successfully!');
      fetchMessages(); // Refresh the list
    } catch (err) {
      setError(err.message);
      console.error('Error activating message:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle edit button click
  const handleEditClick = (message) => {
    setIsEditing(true);
    setCurrentMessageId(message.id);
    setFormData({
      title: message.title,
      message: message.message,
      is_active: message.is_active
    });
    // Scroll to form
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Handle cancel edit
  const handleCancelEdit = () => {
    setIsEditing(false);
    setCurrentMessageId(null);
    setFormData({ title: '', message: '', is_active: false });
  };

  return (
    <div className="admin-view">
      <div className="admin-container">
        <h1>Admin Portal - Pastor Messages</h1>
        
        {/* Success/Error Messages */}
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {/* Create/Edit Form */}
        <div className="form-section">
          <h2>{isEditing ? 'Edit Message' : 'Create New Message'}</h2>
          <form onSubmit={isEditing ? handleUpdate : handleCreate}>
            <div className="form-group">
              <label htmlFor="title">Title:</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
                placeholder="Enter message title"
              />
            </div>

            <div className="form-group">
              <label htmlFor="message">Message:</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleInputChange}
                required
                placeholder="Enter pastor's message"
                rows="10"
              />
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                />
                Set as Active Message
              </label>
            </div>

            <div className="form-buttons">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Saving...' : (isEditing ? 'Update Message' : 'Create Message')}
              </button>
              {isEditing && (
                <button type="button" className="btn btn-secondary" onClick={handleCancelEdit}>
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Messages List */}
        <div className="messages-section">
          <h2>All Pastor Messages</h2>
          {loading && <p>Loading messages...</p>}
          
          {!loading && messages.length === 0 && (
            <p className="no-messages">No messages found. Create your first message above!</p>
          )}

          <div className="messages-grid">
            {messages.map((msg) => (
              <div key={msg.id} className={`message-card ${msg.is_active ? 'active' : ''}`}>
                <div className="message-header">
                  <h3>{msg.title}</h3>
                  {msg.is_active && <span className="active-badge">ACTIVE</span>}
                </div>
                <div className="message-content">
                  <p>{msg.message}</p>
                </div>
                <div className="message-actions">
                  <button 
                    className="btn btn-edit" 
                    onClick={() => handleEditClick(msg)}
                    disabled={loading}
                  >
                    Edit
                  </button>
                  {!msg.is_active && (
                    <button 
                      className="btn btn-activate" 
                      onClick={() => handleActivate(msg.id)}
                      disabled={loading}
                    >
                      Activate
                    </button>
                  )}
                  <button 
                    className="btn btn-delete" 
                    onClick={() => handleDelete(msg.id)}
                    disabled={loading}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminView;
```

---

## STEP 3: Replace AdminView.css

**File:** `Frontend/src/views/AdminView.css`

**Action:** Replace the ENTIRE contents with the code from:
`Backend/frontend_files/AdminView.css`

Or copy the complete CSS from that file.

---

## STEP 4: Update HomeView.jsx

**File:** `Frontend/src/views/HomeView.jsx`

**Action:** Find the pastor message section and update it to fetch from API.

Look for the section with `className="pastor-message-sidebar"` and replace it with this updated version:

Add these imports at the top:
```jsx
import React, { useState, useEffect } from 'react';
```

Add this state and useEffect after your component declaration:
```jsx
const HomeView = () => {
  const [pastorMessage, setPastorMessage] = useState(null);
  const [loadingMessage, setLoadingMessage] = useState(true);

  // Get API URL from environment or use default
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  // Fetch the active pastor message
  useEffect(() => {
    const fetchActivePastorMessage = async () => {
      try {
        const response = await fetch(`${API_URL}/pastor-messages/active`);
        
        if (response.ok) {
          const data = await response.json();
          setPastorMessage(data);
        } else {
          // No active message found, that's okay
          setPastorMessage(null);
        }
      } catch (err) {
        console.error('Error fetching pastor message:', err);
      } finally {
        setLoadingMessage(false);
      }
    };

    fetchActivePastorMessage();
  }, []);

  // ... rest of your component
```

Then replace the pastor message div with:
```jsx
<div className="pastor-message-sidebar scrollable-sidebar">
  <h2>Message from the Pastor</h2>
  <br />
  
  {loadingMessage && <p>Loading message...</p>}
  
  {!loadingMessage && pastorMessage ? (
    <div className="pastor-message-content">
      <h3>{pastorMessage.title}</h3>
      <p>{pastorMessage.message}</p>
    </div>
  ) : (
    !loadingMessage && (
      <p>
        Lorem ipsum dolor sit amet consectetur adipisicing elit. Provident
        odit impedit ratione dolore. Deserunt deleniti minus nostrum,
        voluptatibus magnam nesciunt temporibus. Necessitatibus facere animi
        vel in veniam nostrum nam tempora hic molestias possimus culpa
        tenetur assumenda, quidem, repellat sit officia iste, ullam adipisci
        sapiente similique amet! Minima omnis numquam corporis placeat. Sunt
        tempora illo maiores voluptatibus fugit dicta atque nostrum
        molestias. Autem, totam quod, ratione doloribus nihil aspernatur
        voluptatibus repellat aliquid, odio dolorum natus et quos. Aut,
        mollitia quibusdam maiores ipsam ipsa veniam eum ipsum repudiandae
        reprehenderit iste aspernatur et quia commodi at numquam voluptatem
        adipisci. Dolor corporis pariatur architecto?
      </p>
    )
  )}
</div>
```

---

## STEP 5: Update App.jsx (If needed)

**File:** `Frontend/src/App.jsx`

**Action:** Make sure the AdminView route is already included. If not, add it:

```jsx
import AdminView from './views/AdminView';

// In your routes:
<Route path="/admin" element={<AdminView />} />
```

---

## STEP 6: Update NavBar.jsx (Optional - Add Admin Link)

**File:** `Frontend/src/components/navbar/NavBar.jsx`

**Action:** Add a link to the admin portal that only shows for admin users.

Add this import if not already present:
```jsx
import { useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
```

Inside your NavBar component:
```jsx
const { user } = useContext(AuthContext);
```

Add this link in your navigation menu (wherever appropriate):
```jsx
{user && user.role === 'admin' && (
  <Link to="/admin" className="nav-link">
    Admin Portal
  </Link>
)}
```

---

## STEP 7: Verify Your Changes

### Backend Check:
1. Make sure backend is running: `python flask_app.py`
2. Test endpoint: Visit `http://localhost:5000/pastor-messages/active`

### Frontend Check:
1. Start frontend: `npm run dev`
2. Check `.env` has `VITE_API_URL=http://localhost:5000`
3. Login as admin
4. Navigate to `/admin`
5. Try creating a message
6. Go to home page and verify it shows

---

## 🎯 Quick Test Checklist

- [ ] `.env` file updated with `VITE_API_URL`
- [ ] `AdminView.jsx` replaced with new version
- [ ] `AdminView.css` replaced with new version
- [ ] `HomeView.jsx` updated to fetch pastor message
- [ ] Backend is running
- [ ] Frontend is running
- [ ] Admin user exists in database
- [ ] Can login as admin
- [ ] Can access `/admin` route
- [ ] Can create a message
- [ ] Can edit a message
- [ ] Can delete a message
- [ ] Can activate a message
- [ ] Home page shows active message

---

## 🚨 Common Issues

**Issue: "Cannot find module './AdminView.css'"**
- Make sure you copied AdminView.css to the views folder

**Issue: "AuthContext is not defined"**
- Make sure you have the import: `import { AuthContext } from '../contexts/AuthContext';`

**Issue: "user is undefined"**
- Check that AuthContext is properly set up and providing user data

**Issue: Messages not showing on home page**
- Check browser console for errors
- Verify VITE_API_URL in .env
- Make sure at least one message is marked as active

**Issue: CORS errors**
- Backend already has CORS enabled
- Make sure you're using the correct API URL

---

## 📞 Need Help?

If something doesn't work:
1. Check browser console (F12) for errors
2. Check backend terminal for errors
3. Verify all files were updated correctly
4. Make sure backend is running on port 5000
5. Make sure .env file is in the root of Frontend folder

Good luck! 🚀
