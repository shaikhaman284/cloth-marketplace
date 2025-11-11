import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiService } from '../services/api';
import ProductCard from '../components/products/ProductCard';
import FilterSidebar from '../components/products/FilterSidebar';
import { FiFilter } from 'react-icons/fi';
import toast from 'react-hot-toast';

export default function Products() {
  const [searchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('newest');

  useEffect(() => {
    // Load filters from URL
    const urlFilters = {
      search: searchParams.get('search') || '',
      category: searchParams.get('category') ? [parseInt(searchParams.get('category'))] : [],
      shop: searchParams.get('shop') || '',
    };
    setFilters(urlFilters);
  }, [searchParams]);

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, sortBy]);

  const loadProducts = async () => {
    try {
      setLoading(true);

      const params = {
        sort: sortBy,
        page_size: 20,
      };

      if (filters.search) params.search = filters.search;
      if (filters.categories?.length > 0) params.category = filters.categories[0];
      if (filters.shop) params.shop = filters.shop;
      if (filters.min_price) params.min_price = filters.min_price;
      if (filters.max_price) params.max_price = filters.max_price;

      const data = await apiService.getProducts(params);
      console.log('Products API Response:', data);

      // Handle nested response structure: results.products
      const productsList = data?.results?.products || data?.products || [];
      console.log('Extracted products:', productsList);
      setProducts(productsList);
    } catch (error) {
      console.error('Error loading products:', error);
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600 mt-1">
            {loading ? 'Loading...' : `${products.length} products found`}
          </p>
        </div>

        <div className="flex gap-3 w-full md:w-auto">
          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="flex-1 md:flex-none px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="newest">Newest First</option>
            <option value="price_low">Price: Low to High</option>
            <option value="price_high">Price: High to Low</option>
            <option value="popular">Most Popular</option>
          </select>

          {/* Mobile Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="md:hidden flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <FiFilter />
            Filters
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-col md:flex-row gap-6">
        {/* Filters - Desktop */}
        <aside className="hidden md:block w-64 flex-shrink-0">
          <FilterSidebar filters={filters} onFilterChange={handleFilterChange} />
        </aside>

        {/* Filters - Mobile */}
        {showFilters && (
          <div className="md:hidden">
            <FilterSidebar filters={filters} onFilterChange={handleFilterChange} />
          </div>
        )}

        {/* Products Grid */}
        <div className="flex-1">
          {loading ? (
            <div className="flex justify-center items-center min-h-[400px]">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-gray-500 text-lg">No products found</p>
              <button
                onClick={() => setFilters({})}
                className="mt-4 text-primary hover:underline"
              >
                Clear filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}