import { Link } from 'react-router-dom';
import { FiShoppingCart } from 'react-icons/fi';
import { useCart } from '../../context/CartContext';

export default function ProductCard({ product }) {
  const { addToCart } = useCart();

  const handleQuickAdd = (e) => {
    e.preventDefault();
    addToCart(product, 1);
  };

  return (
    <Link
      to={`/products/${product.id}`}
      className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition group"
    >
      {/* Image */}
      <div className="aspect-square bg-gray-100 overflow-hidden relative">
        {product.images?.[0]?.image_url ? (
          <img
            src={product.images[0].image_url}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="text-4xl">👕</span>
          </div>
        )}

        {/* Stock Badge */}
        {product.stock_quantity === 0 && (
          <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
            Out of Stock
          </div>
        )}

        {product.stock_quantity > 0 && product.stock_quantity <= 5 && (
          <div className="absolute top-2 right-2 bg-orange-500 text-white text-xs px-2 py-1 rounded">
            Only {product.stock_quantity} left
          </div>
        )}

        {/* Quick Add Button */}
        {product.stock_quantity > 0 && (
          <button
            onClick={handleQuickAdd}
            className="absolute bottom-2 right-2 bg-white p-2 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition hover:bg-primary hover:text-white"
            title="Quick Add to Cart"
          >
            <FiShoppingCart className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Details */}
      <div className="p-4">
        <h3 className="font-medium text-gray-900 line-clamp-2 mb-2 h-12">
          {product.name}
        </h3>

        <div className="flex items-center justify-between mb-2">
          <span className="text-xl font-bold text-primary">
            ₹{parseFloat(product.display_price).toLocaleString()}
          </span>

          {product.average_rating > 0 && (
            <div className="flex items-center text-sm">
              <span className="text-yellow-500">⭐</span>
              <span className="ml-1 text-gray-600">
                {product.average_rating} ({product.total_reviews})
              </span>
            </div>
          )}
        </div>

        <p className="text-xs text-gray-500">{product.shop_name}, {product.shop_city}</p>

        {/* Sizes */}
        {product.sizes?.length > 0 && (
          <div className="flex gap-1 mt-2 flex-wrap">
            {product.sizes.slice(0, 4).map((size) => (
              <span key={size} className="text-xs border border-gray-300 px-2 py-1 rounded">
                {size}
              </span>
            ))}
            {product.sizes.length > 4 && (
              <span className="text-xs text-gray-500">+{product.sizes.length - 4}</span>
            )}
          </div>
        )}
      </div>
    </Link>
  );
}