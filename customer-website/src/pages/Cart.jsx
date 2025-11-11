import { Link, useNavigate } from 'react-router-dom';
import { FiTrash2, FiShoppingBag } from 'react-icons/fi';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';

export default function Cart() {
  const { cart, updateQuantity, removeFromCart, totals, clearCart } = useCart();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleCheckout = () => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/checkout');
      return;
    }
    navigate('/checkout');
  };

  if (cart.length === 0) {
    return (
      <div className="text-center py-16">
        <FiShoppingBag className="h-24 w-24 text-gray-300 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
        <p className="text-gray-600 mb-6">Add some products to get started!</p>
        <Link
          to="/products"
          className="inline-block bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-dark transition"
        >
          Browse Products
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
        <button
          onClick={clearCart}
          className="text-red-600 hover:text-red-700 text-sm"
        >
          Clear Cart
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-4">
          {cart.map((item) => (
            <div
              key={`${item.id}-${item.size}-${item.color}`}
              className="bg-white rounded-lg border border-gray-200 p-4 flex gap-4"
            >
              {/* Image */}
              <div className="w-24 h-24 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden">
                {item.image ? (
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    👕
                  </div>
                )}
              </div>

              {/* Details */}
              <div className="flex-1">
                <div className="flex justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{item.name}</h3>
                    <p className="text-sm text-gray-500">{item.shopName}</p>
                    {item.size && (
                      <p className="text-sm text-gray-600 mt-1">Size: {item.size}</p>
                    )}
                    {item.color && (
                      <p className="text-sm text-gray-600">Color: {item.color}</p>
                    )}
                  </div>
                  <button
                    onClick={() => removeFromCart(item.id, item.size, item.color)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <FiTrash2 className="h-5 w-5" />
                  </button>
                </div>

                <div className="flex justify-between items-center mt-4">
                  {/* Quantity */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => updateQuantity(item.id, item.size, item.color, item.quantity - 1)}
                      className="w-8 h-8 border border-gray-300 rounded hover:bg-gray-100"
                    >
                      -
                    </button>
                    <span className="w-12 text-center">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, item.size, item.color, item.quantity + 1)}
                      disabled={item.quantity >= item.stock}
                      className="w-8 h-8 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50"
                    >
                      +
                    </button>
                  </div>

                  {/* Price */}
                  <div className="text-right">
                    <p className="text-lg font-bold text-primary">
                      ₹{(item.price * item.quantity).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">
                      ₹{item.price} × {item.quantity}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-20">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>

            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal ({cart.length} items)</span>
                <span>₹{totals.subtotal.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>COD Fee</span>
                <span>₹{totals.codFee}</span>
              </div>
              <div className="border-t border-gray-200 pt-3 flex justify-between text-lg font-bold">
                <span>Total</span>
                <span className="text-primary">₹{totals.total.toLocaleString()}</span>
              </div>
            </div>

            <button
              onClick={handleCheckout}
              className="w-full bg-primary text-white py-4 rounded-lg font-medium hover:bg-primary-dark transition"
            >
              Proceed to Checkout
            </button>

            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                💰 <strong>Cash on Delivery Available</strong>
                <br />
                Pay when you receive your order
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}