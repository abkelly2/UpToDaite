import { initializeApp } from "https://www.gstatic.com/firebasejs/10.3.1/firebase-app.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/10.3.1/firebase-firestore.js";
import { marked } from "https://cdn.jsdelivr.net/npm/marked/marked.min.js";

const firebaseConfig = {
  apiKey: "...",
  authDomain: "...",
  projectId: "...",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "..."
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function fetchTodayDigest() {
  const today = new Date().toISOString().split('T')[0];
  const docRef = doc(db, "daily_digests", today);
  const docSnap = await getDoc(docRef);

  if (docSnap.exists()) {
    const data = docSnap.data();
    document.getElementById('title').innerText = data.title;
    document.getElementById('content').innerHTML = marked.parse(data.content);
  } else {
    document.getElementById('title').innerText = "No digest yet";
    document.getElementById('content').innerText = "Check back later.";
  }
}

fetchTodayDigest();
