import { createContext, useContext, useState, useEffect } from 'react';
import toast from 'react-hot-toast';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) throw new Error('useCart must be used within CartProvider');
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);

  // Load cart from localStorage
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }
  }, []);

  // Save cart to localStorage
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  // Add to cart
  const addToCart = (product, quantity = 1, size = '', color = '') => {
    const existingIndex = cart.findIndex(
      item => item.id === product.id && item.size === size && item.color === color
    );

    if (existingIndex >= 0) {
      const newCart = [...cart];
      newCart[existingIndex].quantity += quantity;
      setCart(newCart);
      toast.success('Cart updated');
    } else {
      setCart([...cart, {
        id: product.id,
        name: product.name,
        price: product.display_price,
        image: product.images?.[0]?.image_url || '',
        shopId: product.shop?.id,
        shopName: product.shop_name,
        size,
        color,
        quantity,
        stock: product.stock_quantity
      }]);
      toast.success('Added to cart');
    }
  };

  // Update quantity
  const updateQuantity = (productId, size, color, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId, size, color);
      return;
    }

    const newCart = cart.map(item =>
      item.id === productId && item.size === size && item.color === color
        ? { ...item, quantity: newQuantity }
        : item
    );
    setCart(newCart);
  };

  // Remove from cart
  const removeFromCart = (productId, size, color) => {
    setCart(cart.filter(
      item => !(item.id === productId && item.size === size && item.color === color)
    ));
    toast.success('Removed from cart');
  };

  // Clear cart
  const clearCart = () => {
    setCart([]);
    localStorage.removeItem('cart');
  };

  // Calculate totals
  const totals = {
    subtotal: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0),
    codFee: 50,
    get total() {
      return this.subtotal + this.codFee;
    }
  };

  const value = {
    cart,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    totals,
    itemCount: cart.reduce((sum, item) => sum + item.quantity, 0)
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};