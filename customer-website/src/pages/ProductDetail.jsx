import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FiStar, FiShoppingCart, FiArrowLeft } from 'react-icons/fi';
import { apiService } from '../services/api';
import { useCart } from '../context/CartContext';
import toast from 'react-hot-toast';

export default function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedSize, setSelectedSize] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [quantity, setQuantity] = useState(1);
  const { addToCart } = useCart();

  useEffect(() => {
    loadProduct();
    loadReviews();
  }, [id]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProduct(id);
      setProduct(data.product);
      
      // Auto-select first size and color
      if (data.product.sizes?.length > 0) setSelectedSize(data.product.sizes[0]);
      if (data.product.colors?.length > 0) setSelectedColor(data.product.colors[0]);
    } catch (error) {
      console.error('Error loading product:', error);
      toast.error('Failed to load product');
    } finally {
      setLoading(false);
    }
  };

  const loadReviews = async () => {
    try {
      const data = await apiService.getProductReviews(id, { page_size: 10 });
      setReviews(data.reviews || []);
    } catch (error) {
      console.error('Error loading reviews:', error);
    }
  };

  const handleAddToCart = () => {
    if (product.sizes?.length > 0 && !selectedSize) {
      toast.error('Please select a size');
      return;
    }
    if (product.colors?.length > 0 && !selectedColor) {
      toast.error('Please select a color');
      return;
    }
    if (quantity > product.stock_quantity) {
      toast.error('Not enough stock available');
      return;
    }

    addToCart(product, quantity, selectedSize, selectedColor);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500 text-lg">Product not found</p>
        <Link to="/products" className="mt-4 text-primary hover:underline inline-block">
          Back to Products
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <Link to="/" className="hover:text-primary">Home</Link>
        <span>/</span>
        <Link to="/products" className="hover:text-primary">Products</Link>
        <span>/</span>
        <span className="text-gray-900">{product.name}</span>
      </div>

      {/* Product Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Images */}
        <div className="space-y-4">
          {/* Main Image */}
          <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
            {product.images?.length > 0 ? (
              <img
                src={product.images[selectedImage]?.image_url}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                <span className="text-6xl">👕</span>
              </div>
            )}
          </div>

         {/* Thumbnails */}
          {product.images?.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {product.images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(index)}
                  className={`aspect-square rounded-lg overflow-hidden border-2 ${
                    selectedImage === index ? 'border-primary' : 'border-gray-200'
                  }`}
                >
                  <img
                    src={image.image_url}
                    alt={`${product.name} ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>

            {/* Rating */}
            {product.average_rating > 0 && (
              <div className="flex items-center gap-2 text-sm">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <FiStar
                      key={i}
                      className={`h-4 w-4 ${
                        i < Math.floor(product.average_rating)
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-gray-600">
                  {product.average_rating} ({product.total_reviews} reviews)
                </span>
              </div>
            )}
          </div>

          {/* Price */}
          <div className="flex items-baseline gap-3">
            <span className="text-4xl font-bold text-primary">
              ₹{parseFloat(product.display_price).toLocaleString()}
            </span>
            <span className="text-sm text-gray-500">Incl. all taxes</span>
          </div>

          {/* Shop */}
          <div className="border-t border-b border-gray-200 py-4">
            <p className="text-sm text-gray-600">Sold by</p>
            <Link
              to={`/products?shop=${product.shop_details.id}`}
              className="font-medium text-primary hover:underline"
            >
              {product.shop_details.name}
            </Link>
            <p className="text-sm text-gray-500">{product.shop_details.city}</p>
          </div>

          {/* Stock Status */}
          <div>
            {product.stock_quantity === 0 ? (
              <p className="text-red-600 font-medium">Out of Stock</p>
            ) : product.stock_quantity <= 5 ? (
              <p className="text-orange-600 font-medium">
                Only {product.stock_quantity} left in stock!
              </p>
            ) : (
              <p className="text-green-600 font-medium">In Stock</p>
            )}
          </div>

          {/* Sizes */}
          {product.sizes?.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Size <span className="text-red-500">*</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {product.sizes.map((size) => (
                  <button
                    key={size}
                    onClick={() => setSelectedSize(size)}
                    className={`px-4 py-2 border-2 rounded-lg font-medium transition ${
                      selectedSize === size
                        ? 'border-primary bg-primary text-white'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Colors */}
          {product.colors?.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Color <span className="text-red-500">*</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {product.colors.map((color) => (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(color)}
                    className={`px-4 py-2 border-2 rounded-lg font-medium transition ${
                      selectedColor === color
                        ? 'border-primary bg-primary text-white'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-10 h-10 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                -
              </button>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-20 text-center border border-gray-300 rounded-lg px-3 py-2"
                min="1"
                max={product.stock_quantity}
              />
              <button
                onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                className="w-10 h-10 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                +
              </button>
            </div>
          </div>

          {/* Add to Cart Button */}
          <button
            onClick={handleAddToCart}
            disabled={product.stock_quantity === 0}
            className={`w-full py-4 rounded-lg font-medium text-white flex items-center justify-center gap-2 transition ${
              product.stock_quantity === 0
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-primary hover:bg-primary-dark'
            }`}
          >
            <FiShoppingCart className="h-5 w-5" />
            {product.stock_quantity === 0 ? 'Out of Stock' : 'Add to Cart'}
          </button>

          {/* Product Details */}
          {(product.material || product.brand) && (
            <div className="border-t border-gray-200 pt-6 space-y-2">
              {product.material && (
                <div className="flex">
                  <span className="w-24 text-gray-600">Material:</span>
                  <span className="font-medium">{product.material}</span>
                </div>
              )}
              {product.brand && (
                <div className="flex">
                  <span className="w-24 text-gray-600">Brand:</span>
                  <span className="font-medium">{product.brand}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Description */}
      {product.description && (
        <div className="border-t border-gray-200 pt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Description</h2>
          <p className="text-gray-600 whitespace-pre-line">{product.description}</p>
        </div>
      )}

      {/* Reviews */}
      {reviews.length > 0 && (
        <div className="border-t border-gray-200 pt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Customer Reviews ({product.total_reviews})
          </h2>

          <div className="space-y-6">
            {reviews.map((review) => (
              <div key={review.id} className="border-b border-gray-200 pb-6">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <FiStar
                        key={i}
                        className={`h-4 w-4 ${
                          i < review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="font-medium text-gray-900">{review.customer_name}</span>
                  {review.is_verified_purchase && (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                      Verified Purchase
                    </span>
                  )}
                </div>
                <p className="text-gray-600">{review.review_text}</p>
                <p className="text-sm text-gray-400 mt-2">
                  {new Date(review.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}