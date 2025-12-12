import { useState } from 'react';
import apiClient from '../api/axiosClient';
import './LoginPage.css';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState(null);
  
  // --- EMAIL STATE ---
  const [sendEmail, setSendEmail] = useState(false);
  const [alertEmail, setAlertEmail] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setStatus('analyzing');

    // Standard User Payload
    // The Python script handles the attacks, but this UI can also trigger them if needed.
    // For now, we default to "Safe" unless you change the logic.
    const payload = {
      user_id: email || "demo_user",
      features: [0.1, 0.1, 0.1, 0.1], // Safe trigger
      sequence_data: [[1], [2], [3], [4], [1], [2], [3], [4], [1], [2]],
      
      // ✨ SEND THIS TO BACKEND
      target_email: sendEmail ? alertEmail : null
    };

    try {
      const res = await apiClient.post('/security/analyze-login', payload);
      
      // Trigger dashboard refresh
      try { await apiClient.get('/security/history'); } catch(e) {}

      if (res.data.verdict === 'BLOCK') {
        setStatus('blocked');
      } else if (res.data.verdict === 'MFA_CHALLENGE') {
        setStatus('mfa');
      } else {
        setStatus('success');
      }
      
    } catch (err) {
      console.error(err);
      alert("System Error. Please try again.");
      setStatus(null);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div style={{marginBottom: '20px'}}>
           <div style={{width:'50px', height:'50px', background:'#4f46e5', borderRadius:'50%', margin:'0 auto 15px auto', display:'flex', alignItems:'center', justifyContent:'center'}}>
             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
           </div>
           <h2>Secure Bank</h2>
           <p style={{color:'#64748b', fontSize:'14px', margin:0}}>Welcome back, please login</p>
        </div>
        
        {status === 'blocked' ? (
          <div className="error-msg">
            <h3 style={{margin:'0 0 5px 0'}}>🚫 Access Denied</h3>
            Your account has been flagged for suspicious activity.<br/>
            {sendEmail && <span style={{fontSize:'12px', marginTop:'5px', display:'block'}}>Alert sent to {alertEmail}</span>}
          </div>
        ) : status === 'mfa' ? (
          <div className="warning-msg">⚠️ <b>Verify Identity</b><br/>Unusual activity detected.</div>
        ) : status === 'success' ? (
          <div className="success-msg">✅ <b>Success</b><br/>Redirecting...</div>
        ) : (
          <form onSubmit={handleLogin}>
            <input 
              type="text" 
              placeholder="Email Address" 
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

            {/* --- EMAIL ALERT TOGGLE --- */}
            <div style={{textAlign: 'left', marginTop: '15px', padding: '10px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0'}}>
                <label style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer', color: '#475569', fontWeight: 600}}>
                    <input 
                        type="checkbox" 
                        checked={sendEmail} 
                        onChange={e => setSendEmail(e.target.checked)} 
                    />
                    📩 Send Security Alert?
                </label>
                
                {sendEmail && (
                    <input 
                        type="email" 
                        placeholder="Enter email for alert..." 
                        value={alertEmail}
                        onChange={e => setAlertEmail(e.target.value)}
                        style={{marginTop: '8px', width: '100%', boxSizing: 'border-box', fontSize: '13px', padding: '8px'}}
                    />
                )}
            </div>

            <button style={{marginTop: '15px', background: '#4f46e5', width:'100%', color:'white', padding:'10px', borderRadius:'6px', border:'none', cursor:'pointer', fontWeight:'bold'}}>
              {status === 'analyzing' ? 'Verifying...' : 'Sign In'}
            </button>
          </form>
        )}
        <p style={{marginTop:'20px', fontSize:'12px', color:'#94a3b8'}}>Protected by SecureWatch AI</p>
      </div>
    </div>
  );
};

export default LoginPage;