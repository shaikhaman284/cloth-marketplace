import { useState, useEffect } from 'react';
import { apiService } from '../../services/api';

export default function FilterSidebar({ filters, onFilterChange }) {
  const [categories, setCategories] = useState([]);
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const data = await apiService.getCategories();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const handleCategoryChange = (categoryId) => {
    const newCategories = filters.categories?.includes(categoryId)
      ? filters.categories.filter(id => id !== categoryId)
      : [...(filters.categories || []), categoryId];

    onFilterChange({ ...filters, categories: newCategories });
  };

  const handlePriceChange = () => {
    onFilterChange({
      ...filters,
      min_price: priceRange.min,
      max_price: priceRange.max
    });
  };

  const clearFilters = () => {
    setPriceRange({ min: '', max: '' });
    onFilterChange({});
  };

  const activeFilterCount =
    (filters.categories?.length || 0) +
    (filters.min_price ? 1 : 0) +
    (filters.max_price ? 1 : 0);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-lg">Filters</h3>
        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            className="text-sm text-primary hover:underline"
          >
            Clear All ({activeFilterCount})
          </button>
        )}
      </div>

      {/* Categories */}
      <div>
        <h4 className="font-medium mb-3">Categories</h4>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {categories.map((category) => (
            <label key={category.id} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.categories?.includes(category.id) || false}
                onChange={() => handleCategoryChange(category.id)}
                className="rounded text-primary focus:ring-primary"
              />
              <span className="text-sm text-gray-700">{category.name}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Price Range */}
      <div>
        <h4 className="font-medium mb-3">Price Range</h4>
        <div className="flex gap-2 items-center">
          <input
            type="number"
            placeholder="Min"
            value={priceRange.min}
            onChange={(e) => setPriceRange({ ...priceRange, min: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-1 focus:ring-primary focus:border-primary"
          />
          <span className="text-gray-500">-</span>
          <input
            type="number"
            placeholder="Max"
            value={priceRange.max}
            onChange={(e) => setPriceRange({ ...priceRange, max: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-1 focus:ring-primary focus:border-primary"
          />
        </div>
        <button
          onClick={handlePriceChange}
          className="w-full mt-2 bg-primary text-white py-2 rounded hover:bg-primary-dark transition text-sm"
        >
          Apply
        </button>
      </div>

      {/* Stock Filter */}
      <div>
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.in_stock || false}
            onChange={(e) => onFilterChange({ ...filters, in_stock: e.target.checked })}
            className="rounded text-primary focus:ring-primary"
          />
          <span className="text-sm text-gray-700">In Stock Only</span>
        </label>
      </div>
    </div>
  );
}