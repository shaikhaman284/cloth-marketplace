import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDdhaZbbq2lE_IREvhXbDqXIsw1DQvzZ-Q",
  authDomain: "clothmarket-de8e9.firebaseapp.com",
  projectId: "clothmarket-de8e9",
  storageBucket: "clothmarket-de8e9.firebasestorage.app",
  messagingSenderId: "1002114406517",
  appId: "1:1002114406517:web:7c579738cdeb73b411003c",
  measurementId: "G-VJXH6WF5YX"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);