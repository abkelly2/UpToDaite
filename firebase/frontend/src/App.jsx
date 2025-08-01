import { useEffect, useState } from 'react';
import { db } from './firebase';
import { collection, doc, getDoc } from 'firebase/firestore';
import ReactMarkdown from 'react-markdown';
import './App.css';

export default function App() {
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBriefing = async () => {
      try {
        const today     = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);

        const dateStr = `${yesterday.getMonth() + 1}-${yesterday.getDate()}-${yesterday.getFullYear()}`;
        console.log("🔥 Asking for briefing under collection:", dateStr);
          
        const dayRef = doc(db, dateStr, 'metadata');
        const daySnap = await getDoc(dayRef);
        console.log("📄 daySnap.exists() =", daySnap.exists());
  
        if (!daySnap.exists()) {
          setError('No briefing available for today yet.');
          setLoading(false);
          return;
        }

        const data = daySnap.data();
        if (!data.briefing) {
          setError('Briefing is being generated. Please check back soon.');
          setLoading(false);
          return;
        }

        setBriefing(data.briefing);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching briefing:', err);
        setError('Failed to load today\'s briefing. Please try again later.');
        setLoading(false);
      }
    };

    fetchBriefing();
  }, []);

  if (loading) {
    return (
      <div className="container loading">
        <div className="spinner"></div>
        <p>Loading today's AI briefing...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container error">
        <h2>⚠️</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="container">
      <header>
        <h1>Daily AI Briefing</h1>
        <p className="date">
          {new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </p>
      </header>
      
      <main className="content">
        <ReactMarkdown>{briefing}</ReactMarkdown>
      </main>
      
      <footer>
        <p>Updates daily with the latest in AI Products, News, and Research</p>
      </footer>
    </div>
  );
}
