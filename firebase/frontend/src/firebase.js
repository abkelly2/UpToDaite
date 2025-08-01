// src/firebase.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyAr8HgijA9HDTC9cl1rVpRd_g9lx4ApOTU",
  authDomain: "uptodaite.firebaseapp.com",
  projectId: "uptodaite",
  storageBucket: "uptodaite.firebasestorage.app",
  messagingSenderId: "714763767580",
  appId: "1:714763767580:web:0fc64318a054b9298cb4d9",
  measurementId: "G-YKLXFMK8S3"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export { db };
