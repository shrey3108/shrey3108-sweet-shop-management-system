import React, { useState } from 'react';

function SweetCard({ sweet, isAdmin, onEdit, onDelete, onPurchase }) {
  const [purchaseQty, setPurchaseQty] = useState(1);
  const [loading, setLoading] = useState(false);

  const handlePurchase = async () => {
    if (purchaseQty < 1 || purchaseQty > sweet.quantity) return;
    
    setLoading(true);
    try {
      await onPurchase(sweet.id, purchaseQty);
      setPurchaseQty(1);
    } catch (error) {
      // Error handled by parent
    } finally {
      setLoading(false);
    }
  };

  const isOutOfStock = sweet.quantity === 0;

  return (
    <div className="sweet-card">
      <div className="sweet-card-header">
        <h3>{sweet.name}</h3>
        <span className="sweet-category">{sweet.category}</span>
      </div>

      <div className="sweet-card-body">
        <div className="sweet-info">
          <p className="sweet-price">${sweet.price.toFixed(2)}</p>
          <p className={`sweet-stock ${isOutOfStock ? 'out-of-stock' : ''}`}>
            Stock: {sweet.quantity}
            {isOutOfStock && ' (Out of Stock)'}
          </p>
        </div>

        {!isAdmin && (
          <div className="purchase-section">
            <div className="quantity-control">
              <button
                onClick={() => setPurchaseQty(Math.max(1, purchaseQty - 1))}
                disabled={isOutOfStock || loading}
              >
                -
              </button>
              <input
                type="number"
                value={purchaseQty}
                onChange={(e) => setPurchaseQty(Math.max(1, parseInt(e.target.value) || 1))}
                min="1"
                max={sweet.quantity}
                disabled={isOutOfStock || loading}
              />
              <button
                onClick={() => setPurchaseQty(Math.min(sweet.quantity, purchaseQty + 1))}
                disabled={isOutOfStock || loading}
              >
                +
              </button>
            </div>
            <button
              className="btn-purchase"
              onClick={handlePurchase}
              disabled={isOutOfStock || loading}
            >
              {loading ? 'Purchasing...' : 'Purchase'}
            </button>
          </div>
        )}

        {isAdmin && (
          <div className="admin-actions">
            <button
              className="btn-edit"
              onClick={() => onEdit(sweet)}
            >
              Edit
            </button>
            <button
              className="btn-delete"
              onClick={() => onDelete(sweet.id)}
            >
              Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default SweetCard;
