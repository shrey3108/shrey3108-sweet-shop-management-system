import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { clearAuth, getUser, getSweets, searchSweets, createSweet, updateSweet, deleteSweet, purchaseSweet } from '../api';
import SweetCard from '../components/SweetCard';
import SweetForm from '../components/SweetForm';

function Dashboard() {
  const navigate = useNavigate();
  const user = getUser();
  const isAdmin = user?.role === 'ADMIN';

  const [sweets, setSweets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingSweet, setEditingSweet] = useState(null);

  // Fetch sweets on mount
  useEffect(() => {
    fetchSweets();
  }, []);

  const fetchSweets = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getSweets();
      setSweets(data);
    } catch (err) {
      setError('Failed to load sweets');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      fetchSweets();
      return;
    }

    setLoading(true);
    setError('');
    try {
      const data = await searchSweets({ name: searchQuery });
      setSweets(data);
    } catch (err) {
      setError('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    fetchSweets();
  };

  const handleAddSweet = () => {
    setEditingSweet(null);
    setShowForm(true);
  };

  const handleEditSweet = (sweet) => {
    setEditingSweet(sweet);
    setShowForm(true);
  };

  const handleFormSubmit = async (sweetData) => {
    try {
      if (editingSweet) {
        await updateSweet(editingSweet.id, sweetData);
      } else {
        await createSweet(sweetData);
      }
      setShowForm(false);
      setEditingSweet(null);
      fetchSweets();
    } catch (err) {
      throw err;
    }
  };

  const handleDeleteSweet = async (id) => {
    if (!window.confirm('Are you sure you want to delete this sweet?')) {
      return;
    }

    try {
      await deleteSweet(id);
      fetchSweets();
    } catch (err) {
      alert('Failed to delete sweet');
    }
  };

  const handlePurchase = async (id, quantity) => {
    try {
      await purchaseSweet(id, quantity);
      fetchSweets();
      alert('Purchase successful!');
    } catch (err) {
      alert(err.message || 'Purchase failed');
      throw err;
    }
  };

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="header-left">
          <h1>Sweet Shop</h1>
          <p className="user-info">
            {user?.email} • <span className="user-role">{user?.role}</span>
          </p>
        </div>
        <button onClick={handleLogout} className="btn-secondary">
          Logout
        </button>
      </div>

      <div className="dashboard-controls">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search sweets by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="btn-search">
            Search
          </button>
          {searchQuery && (
            <button type="button" className="btn-clear" onClick={handleClearSearch}>
              Clear
            </button>
          )}
        </form>

        {isAdmin && (
          <button className="btn-add" onClick={handleAddSweet}>
            + Add Sweet
          </button>
        )}
      </div>

      <div className="dashboard-content">
        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">Loading sweets...</div>
        ) : sweets.length === 0 ? (
          <div className="no-sweets">
            <p>No sweets found.</p>
            {isAdmin && <p>Click "Add Sweet" to get started!</p>}
          </div>
        ) : (
          <div className="sweets-grid">
            {sweets.map((sweet) => (
              <SweetCard
                key={sweet.id}
                sweet={sweet}
                isAdmin={isAdmin}
                onEdit={handleEditSweet}
                onDelete={handleDeleteSweet}
                onPurchase={handlePurchase}
              />
            ))}
          </div>
        )}
      </div>

      {showForm && (
        <SweetForm
          sweet={editingSweet}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setShowForm(false);
            setEditingSweet(null);
          }}
        />
      )}
    </div>
  );
}

export default Dashboard;
