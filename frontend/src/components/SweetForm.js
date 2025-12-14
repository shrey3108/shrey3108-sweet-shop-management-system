import React, { useState, useEffect } from 'react';

function SweetForm({ sweet, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    price: '',
    quantity: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isEditMode = !!sweet;

  useEffect(() => {
    if (sweet) {
      setFormData({
        name: sweet.name,
        category: sweet.category,
        price: sweet.price.toString(),
        quantity: sweet.quantity.toString(),
      });
    }
  }, [sweet]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    const price = parseFloat(formData.price);
    const quantity = parseInt(formData.quantity);

    if (price <= 0) {
      setError('Price must be greater than 0');
      return;
    }

    if (quantity < 0) {
      setError('Quantity cannot be negative');
      return;
    }

    setLoading(true);

    try {
      const sweetData = {
        name: formData.name.trim(),
        category: formData.category.trim(),
        price: price,
        quantity: quantity,
      };

      await onSubmit(sweetData);
    } catch (err) {
      setError(err.message || 'Failed to save sweet');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sweet-form-overlay">
      <div className="sweet-form-container">
        <div className="sweet-form-header">
          <h2>{isEditMode ? 'Edit Sweet' : 'Add New Sweet'}</h2>
          <button className="close-btn" onClick={onCancel}>×</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="e.g., Chocolate Bar"
            />
          </div>

          <div className="form-group">
            <label htmlFor="category">Category</label>
            <input
              type="text"
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
              placeholder="e.g., Chocolate, Candy, Gummies"
            />
          </div>

          <div className="form-group">
            <label htmlFor="price">Price ($)</label>
            <input
              type="number"
              id="price"
              name="price"
              value={formData.price}
              onChange={handleChange}
              required
              step="0.01"
              min="0.01"
              placeholder="0.00"
            />
          </div>

          <div className="form-group">
            <label htmlFor="quantity">Quantity</label>
            <input
              type="number"
              id="quantity"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              required
              min="0"
              placeholder="0"
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn-cancel" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SweetForm;
