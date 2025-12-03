import { useState } from 'react';
import apiClient from '../api/axiosClient';
import './LoginPage.css';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState(null);
  const [scenario, setScenario] = useState('safe'); // 'safe', 'context', 'bot', 'ring'

  const handleLogin = async (e) => {
    e.preventDefault();
    setStatus('analyzing');

    let payload = {
      user_id: email || "demo_user",
      features: [0.1, 0.1, 0.1, 0.1], // Default Safe
      sequence_data: [[1], [2], [3], [4], [1], [2], [3], [4], [1], [2]] 
    };

    // --- 1. CONTEXT ATTACK (Triggers Isolation Forest) ---
    if (scenario === 'context') {
      payload.features = [100.0, -99.0, 50.0, 20.0]; 
    }

    // --- 2. BOT ATTACK (Triggers LSTM) ---
    if (scenario === 'bot') {
      payload.features = [0.5, 0.5, 0.5, 0.5]; // Neutral features
      // Repetitive action '1' triggers the backend override
      payload.sequence_data = [[1], [1], [1], [1], [1], [1], [1], [1], [1], [1]];
    }

    // --- 3. FRAUD RING ATTACK (Triggers Network Graph) ---
    if (scenario === 'ring') {
      payload.features = [0.5, 0.5, 0.5, 0.5]; // Neutral features
      payload.user_id = "user_101"; 
    }

    try {
      const res = await apiClient.post('/security/analyze-login', payload);
      
      // Refresh Dashboard History
      await apiClient.get('/security/history');

      if (res.data.verdict === 'BLOCK') {
        setStatus('blocked');
      } else if (res.data.verdict === 'MFA_CHALLENGE') {
        setStatus('mfa');
      } else {
        setStatus('success');
      }
    } catch (err) {
      alert("Server Error");
      setStatus(null);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>🏦 Secure Bank Login</h2>
        
        {status === 'blocked' ? (
          <div className="error-msg">🚫 <b>ACCESS DENIED</b><br/>High Risk Activity Detected.</div>
        ) : status === 'mfa' ? (
          <div className="warning-msg">⚠️ <b>Identity Verification</b><br/>Unusual behavior detected.</div>
        ) : status === 'success' ? (
          <div className="success-msg">✅ <b>Login Successful</b><br/>Welcome back.</div>
        ) : (
          <form onSubmit={handleLogin}>
            <input 
              type="text" 
              placeholder="Username" 
              value={email} 
              onChange={e=>setEmail(e.target.value)}
              required 
            />
            <input 
              type="password" 
              placeholder="Password" 
              value={password}
              onChange={e=>setPassword(e.target.value)}
              required
            />
            
            {/* SCENARIO SELECTOR */}
            <div style={{background: '#f1f5f9', padding: '15px', borderRadius: '8px', marginTop: '10px'}}>
              <p style={{fontSize: '12px', fontWeight: 'bold', color: '#64748b', margin: '0 0 10px 0'}}>DEMO SIMULATION MODE:</p>
              
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px'}}>
                <button type="button" 
                  onClick={() => setScenario('safe')}
                  style={{background: scenario==='safe'?'#10b981':'#e2e8f0', color: scenario==='safe'?'white':'#64748b', fontSize:'12px', padding:'8px'}}
                >
                  ✅ Normal User
                </button>
                <button type="button" 
                  onClick={() => setScenario('context')}
                  style={{background: scenario==='context'?'#f59e0b':'#e2e8f0', color: scenario==='context'?'white':'#64748b', fontSize:'12px', padding:'8px'}}
                >
                  🌍 Impossible Travel
                </button>
                <button type="button" 
                  onClick={() => setScenario('bot')}
                  style={{background: scenario==='bot'?'#8b5cf6':'#e2e8f0', color: scenario==='bot'?'white':'#64748b', fontSize:'12px', padding:'8px'}}
                >
                  🤖 Bot Script
                </button>
                <button type="button" 
                  onClick={() => setScenario('ring')}
                  style={{background: scenario==='ring'?'#ef4444':'#e2e8f0', color: scenario==='ring'?'white':'#64748b', fontSize:'12px', padding:'8px'}}
                >
                  🕸️ Fraud Ring
                </button>
              </div>
            </div>

            <button style={{marginTop: '20px', background: '#4318ff'}}>
              {status === 'analyzing' ? 'Running AI Models...' : 'Sign In'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default LoginPage;