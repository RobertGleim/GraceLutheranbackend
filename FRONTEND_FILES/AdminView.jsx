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
