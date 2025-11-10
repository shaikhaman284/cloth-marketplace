import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiSearch, FiArrowRight } from 'react-icons/fi';
import { apiService } from '../services/api';
import WelcomePopup from '../components/common/WelcomePopup';
import toast from 'react-hot-toast';

export default function Home() {
  const [categories, setCategories] = useState([]);
  const [shops, setShops] = useState([]);
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load categories, shops, and featured products
      const [categoriesRes, shopsRes, productsRes] = await Promise.all([
        apiService.getCategories(),
        apiService.getShops(),
        apiService.getProducts({ page_size: 8, sort: 'newest' })
      ]);

      setCategories(categoriesRes.categories || []);
      setShops(shopsRes.shops || []);
      setFeaturedProducts(productsRes.products || []);
    } catch (error) {
      console.error('Error loading home data:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-16">
      <WelcomePopup />

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary to-indigo-600 text-white rounded-2xl p-8 md:p-12">
        <div className="max-w-3xl">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Shop Your Favorite Local Clothes Online
          </h1>
          <p className="text-lg mb-8 text-indigo-100">
            Discover the best cloth shops in Amravati. Browse, order, and get delivery at your doorstep.
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="flex-1 relative">
              <FiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search for clothes, brands..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-white"
              />
            </div>
            <button
              type="submit"
              className="bg-white text-primary px-8 py-4 rounded-lg font-medium hover:bg-gray-100 transition"
            >
              Search
            </button>
          </form>
        </div>
      </section>

      {/* Categories */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Shop by Category</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {categories.map((category) => (
            <Link
              key={category.id}
              to={`/products?category=${category.id}`}
              className="bg-white p-6 rounded-lg border-2 border-gray-200 hover:border-primary hover:shadow-lg transition text-center group"
            >
              <div className="text-4xl mb-3">👕</div>
              <h3 className="font-medium text-gray-900 group-hover:text-primary">
                {category.name}
              </h3>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Shops */}
      {shops.length > 0 && (
        <section>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Verified Shops</h2>
            <Link to="/shops" className="text-primary hover:underline flex items-center gap-1">
              View All <FiArrowRight />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {shops.slice(0, 3).map((shop) => (
              <Link
                key={shop.id}
                to={`/products?shop=${shop.id}`}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition"
              >
                <div className="h-40 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                  {shop.shop_image_url ? (
                    <img
                      src={shop.shop_image_url}
                      alt={shop.shop_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-6xl">🏪</span>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-lg text-gray-900">{shop.shop_name}</h3>
                  <p className="text-sm text-gray-500">{shop.city}</p>
                  <p className="text-sm text-gray-600 mt-2">
                    {shop.product_count} Products
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Featured Products */}
      {featuredProducts.length > 0 && (
        <section>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Latest Products</h2>
            <Link to="/products" className="text-primary hover:underline flex items-center gap-1">
              View All <FiArrowRight />
            </Link>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <Link
                key={product.id}
                to={`/products/${product.id}`}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition group"
              >
                <div className="aspect-square bg-gray-100 overflow-hidden">
                  {product.images?.[0]?.image_url ? (
                    <img
                      src={product.images[0].image_url}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      No Image
                    </div>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-medium text-gray-900 line-clamp-2 mb-2">
                    {product.name}
                  </h3>
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-primary">
                      ₹{product.display_price}
                    </span>
                    {product.average_rating > 0 && (
                      <span className="text-sm text-gray-600">
                        ⭐ {product.average_rating}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{product.shop_name}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="bg-gray-100 rounded-2xl p-8 md:p-12 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to Shop?
        </h2>
        <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
          Browse our collection of products from verified local shops in Amravati.
          Cash on Delivery available!
        </p>
        <Link
          to="/products"
          className="inline-block bg-primary text-white px-8 py-4 rounded-lg font-medium hover:bg-primary-dark transition"
        >
          Browse All Products
        </Link>
      </section>
    </div>
  );
}