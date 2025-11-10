import { auth } from '../config/firebase';
import {
  RecaptchaVerifier,
  signInWithPhoneNumber,
  signOut
} from 'firebase/auth';
import { apiService } from './api';

export const authService = {
  // Setup invisible reCAPTCHA
  setupRecaptcha: (buttonId) => {
    if (!window.recaptchaVerifier) {
      window.recaptchaVerifier = new RecaptchaVerifier(auth, buttonId, {
        size: 'invisible',
        callback: () => {
          console.log('reCAPTCHA solved');
        }
      });
    }
  },

  // Send OTP
  sendOTP: async (phoneNumber) => {
    const appVerifier = window.recaptchaVerifier;
    const confirmationResult = await signInWithPhoneNumber(auth, phoneNumber, appVerifier);
    return confirmationResult;
  },

  // Verify OTP and register/login
  verifyOTP: async (confirmationResult, otp, userData) => {
    const result = await confirmationResult.confirm(otp);
    const firebaseToken = await result.user.getIdToken();

    // Register/login with backend
    const response = await apiService.register({
      phone_number: result.user.phoneNumber,
      full_name: userData.fullName,
      user_type: 'customer',
      firebase_id_token: firebaseToken
    });

    // Save auth data
    localStorage.setItem('authToken', response.token);
    localStorage.setItem('user', JSON.stringify(response.user));

    return response;
  },

  // Logout
  logout: async () => {
    await signOut(auth);
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  },

  // Get current user
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // Check if authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('authToken');
  }
};