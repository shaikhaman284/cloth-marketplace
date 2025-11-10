import { useState, useEffect } from 'react';
import { FiX } from 'react-icons/fi';

export default function WelcomePopup() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const hasSeenWelcome = localStorage.getItem('hasSeenWelcome');
    if (!hasSeenWelcome) {
      setShow(true);
    }
  }, []);

  const handleClose = () => {
    localStorage.setItem('hasSeenWelcome', 'true');
    setShow(false);
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6 relative">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <FiX className="h-6 w-6" />
        </button>

        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Welcome to ClothMarket! 🎉
          </h2>

          <div className="text-left space-y-3 mb-6">
            <p className="text-gray-600">
              This is a <span className="font-semibold">beta testing platform</span> connecting you with local cloth shops in Amravati.
            </p>

            <div className="bg-blue-50 p-3 rounded">
              <p className="text-sm text-blue-800">
                <strong>What we offer:</strong>
              </p>
              <ul className="text-sm text-blue-700 mt-2 space-y-1">
                <li>✓ Browse products from verified local shops</li>
                <li>✓ Cash on Delivery (COD) available</li>
                <li>✓ Home delivery in Amravati</li>
                <li>✓ Support local businesses</li>
              </ul>
            </div>

            <p className="text-sm text-gray-500">
              Your feedback helps us improve! 🙏
            </p>
          </div>

          <button
            onClick={handleClose}
            className="w-full bg-primary text-white py-3 rounded-lg font-medium hover:bg-primary-dark transition"
          >
            Start Shopping
          </button>
        </div>
      </div>
    </div>
  );
}