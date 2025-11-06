import React, { useState, useEffect } from 'react';
import './Homeview.css';

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

  return (
    <div className="home-view">
      {/* Your existing hero section and other content here */}
      
      {/* Pastor Message Sidebar - Updated to fetch from API */}
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
      
      {/* Rest of your home view content */}
    </div>
  );
};

export default HomeView;
