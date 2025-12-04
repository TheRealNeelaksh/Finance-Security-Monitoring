import { useState, useEffect } from 'react';
import apiClient from '../api/axiosClient';
import { 
  Shield, Bell, Settings, LayoutDashboard, AlertTriangle, 
  MapPin, Smartphone, Activity, CheckCircle, XCircle, AlertOctagon, ThumbsUp, ThumbsDown
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';
import './Dashboard.css';

// --- HELPER: Process History for Real-Time Graph ---
const processRealTimeData = (historyLog) => {
  if (!historyLog || historyLog.length === 0) {
    // Placeholder to keep graph looking good when empty
    return [
      { time: 'Start', normal: 0, suspicious: 0 },
      { time: 'Live', normal: 0, suspicious: 0 }
    ];
  }

  const groups = {};

  // Process logs (Reverse so oldest appear first on the left)
  [...historyLog].reverse().forEach(log => {
    // Extract time string (e.g. "Dec 03, 10:45 AM") -> "10:45 AM"
    // We split by comma to get the time part
    const timeParts = log.time.split(', ');
    const timeLabel = timeParts.length > 1 ? timeParts[1] : log.time; 

    if (!groups[timeLabel]) {
      groups[timeLabel] = { time: timeLabel, normal: 0, suspicious: 0 };
    }

    // Count: Green vs Red
    if (log.status === 'Success' || log.status === 'Verified Safe') {
      groups[timeLabel].normal += 1;
    } else {
      groups[timeLabel].suspicious += 1;
    }
  });

  return Object.values(groups);
};

const Dashboard = () => {
  // ----------------------------
  // 1. STATE MANAGEMENT
  // ----------------------------
  const [history, setHistory] = useState([]);
  const [alerts, setAlerts] = useState([]); 

  // ----------------------------
  // 2. WEBSOCKET CONNECTION
  // ----------------------------
  useEffect(() => {
    // Dynamic URL for Local/Vercel
    const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
    const wsUrl = baseUrl.replace("http", "ws"); 
    
    let ws = new WebSocket(`${wsUrl}/ws/alerts`);

    ws.onopen = () => console.log("✅ WebSocket Connected");
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "CRITICAL_ALERT") {
          // Prevent duplicates (debounce 500ms)
          const newAlertId = Date.now();
          setAlerts(prev => {
            const recent = prev.find(a => newAlertId - a.id < 500);
            if (recent) return prev;
            return [{ id: newAlertId, msg: data.message }, ...prev];
          });
          
          setTimeout(() => setAlerts(prev => prev.filter(a => a.id !== newAlertId)), 5000);
          fetchHistory(); 
        }
      } catch (e) { console.error("WS Error", e); }
    };

    return () => { if (ws.readyState === 1) ws.close(); };
  }, []);

  // ----------------------------
  // 3. ROBUST DATA POLLING
  // ----------------------------
  const fetchHistory = async () => {
    try {
      const res = await apiClient.get('/security/history');
      if (Array.isArray(res.data)) {
        setHistory(res.data);
      } else {
        setHistory([]); 
      }
    } catch (err) { console.error("API Error", err); }
  };

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 2000);
    return () => clearInterval(interval);
  }, []);

  // ----------------------------
  // 4. ACTIONS
  // ----------------------------
  const handleVerify = async (logId, action) => {
    try {
      await apiClient.post('/security/feedback', { log_id: logId, action: action });
      fetchHistory();
    } catch (err) { alert("Feedback Failed"); }
  };

  const openSimulator = () => {
    window.open('/login', 'BankSimulator', 'toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=400,height=750');
  };

  // ----------------------------
  // 5. DYNAMIC CALCULATIONS
  // ----------------------------
  const safeHistory = Array.isArray(history) ? history : [];

  // A. Safety Score
  const latestLog = safeHistory.length > 0 ? safeHistory[0] : null;
  const latestRisk = latestLog ? latestLog.risk_score : 0; 
  const safePercentage = Math.round((1 - latestRisk) * 100); 
  const gaugeColor = safePercentage > 80 ? '#05cd99' : safePercentage > 50 ? '#ffb547' : '#ee5d50';

  const donutData = [
    { name: 'Safe', value: safePercentage },
    { name: 'Risk', value: 100 - safePercentage }
  ];

  // B. Real Counters
  const failedCount = safeHistory.filter(h => h.status === 'Blocked' || h.status === 'Suspicious').length;
  const uniqueDevices = new Set(safeHistory.map(h => h.device)).size;
  const activeThreats = safeHistory.filter(h => h.risk_score > 0.8 && !h.user_feedback).length;

  // C. REAL-TIME GRAPH DATA (This is the fix)
  const trendData = processRealTimeData(safeHistory);

  // ----------------------------
  // 6. UI RENDER
  // ----------------------------
  return (
    <div className="dashboard-container">
      
      <div className="toast-container">
        {alerts.map(alert => (
          <div key={alert.id} className="toast">
            <AlertOctagon color="#ee5d50" size={24} />
            <div className="toast-content">
              <h4>Security Alert</h4>
              <p>{alert.msg}</p>
            </div>
          </div>
        ))}
      </div>

      <nav className="navbar">
        <div className="brand">
          <Shield size={28} className="brand-icon" />
          <span>SecureWatch <span className="brand-accent">AI</span></span>
        </div>
        <div className="nav-links">
          <div className="nav-item active"><LayoutDashboard size={18}/> Dashboard</div>
          <div className="nav-item launch-btn" onClick={openSimulator}>
            <Smartphone size={16}/> Launch App
          </div>
          <div className="nav-item"><Settings size={18}/> Settings</div>
        </div>
      </nav>

      <div className="stats-grid">
        {/* RISK CARD */}
        <div className="card risk-card">
          <div className="card-header">
            <h3>Account Safety Score</h3>
            <Activity size={18} color="#a3aed0"/>
          </div>
          <div className="donut-layout">
            <div className="donut-wrapper">
               <PieChart width={140} height={140}>
                  <Pie 
                    data={donutData} innerRadius={55} outerRadius={70} 
                    startAngle={90} endAngle={-270} dataKey="value" stroke="none"
                  >
                    <Cell fill={gaugeColor} /> 
                    <Cell fill="#f4f7fe" />
                  </Pie>
               </PieChart>
               <div className="risk-label">
                  <h2 style={{color: gaugeColor}}>{safePercentage}%</h2>
                  <span style={{color: '#a3aed0', fontSize:'12px'}}>Safe</span>
               </div>
            </div>
            
            <div className="risk-details">
              <div className="metric">
                <div className="metric-text"><span>Failed Attempts</span><strong>{failedCount}</strong></div>
                <div className="bar-bg"><div className="bar-fill" style={{width: `${Math.min(failedCount * 5, 100)}%`, background:'#ee5d50'}}></div></div>
              </div>
              <div className="metric">
                <div className="metric-text"><span>Active Devices</span><strong>{uniqueDevices}</strong></div>
                <div className="bar-bg"><div className="bar-fill" style={{width: `${Math.min(uniqueDevices * 10, 100)}%`, background:'#ffb547'}}></div></div>
              </div>
            </div>
          </div>
        </div>

        {/* ALERTS CARD */}
        <div className="card alert-card">
          <div className="alert-badge-wrapper">
             <div className="pulse-circle" style={{background: activeThreats > 0 ? '#fff5f5' : '#e6fdf5'}}>
                {activeThreats > 0 ? <AlertTriangle size={32} color="#ee5d50" /> : <CheckCircle size={32} color="#05cd99"/>}
             </div>
             {activeThreats > 0 && <div className="alert-count">{activeThreats}</div>}
          </div>
          <h3>{activeThreats > 0 ? "Threats Detected" : "System Secure"}</h3>
          <p className="sub-text">Real-time threat monitoring active</p>
          <div className="mini-alert-list">
            {activeThreats > 0 ? (
              <div className="mini-alert">
                <XCircle size={14} color="#ee5d50"/>
                <span>Unusual login from {latestLog?.location}</span>
              </div>
            ) : (
              <div className="mini-alert success">
                <CheckCircle size={14} color="#05cd99"/>
                <span>No active threats found</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* REAL-TIME GRAPH */}
      <div className="card chart-section">
        <div className="section-title"><Activity size={20} color="#4318ff"/> Live Traffic Analysis</div>
        <div style={{ width: '100%', height: 220 }}>
          <ResponsiveContainer>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e0e5f2"/>
              {/* NOTE: dataKey is now "time" (e.g. 10:45 AM) instead of "day" */}
              <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#a3aed0', fontSize: 12}} dy={10}/>
              <YAxis axisLine={false} tickLine={false} tick={{fill: '#a3aed0', fontSize: 12}}/>
              <Tooltip contentStyle={{borderRadius: '10px', border: 'none', boxShadow: '0 10px 20px rgba(0,0,0,0.1)'}}/>
              <Line type="monotone" dataKey="normal" stroke="#05cd99" strokeWidth={3} dot={{r:4}} name="Safe" />
              <Line type="monotone" dataKey="suspicious" stroke="#ee5d50" strokeWidth={3} dot={{r:4}} name="Threats" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* TABLE */}
      <div className="card">
        <div className="section-title">Live Transaction Monitor</div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Location</th>
                <th>Device</th>
                <th>Risk Score</th>
                <th>Analysis (Reason)</th> 
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {safeHistory.map((row) => (
                <tr key={row.id}>
                  <td style={{fontWeight:'500'}}>{row.time}</td>
                  <td><div className="icon-text"><MapPin size={14} color="#a3aed0"/> {row.location}</div></td>
                  <td><div className="icon-text"><Smartphone size={14} color="#a3aed0"/> {row.device}</div></td>
                  <td>
                    <div className="risk-pill" style={{
                      color: row.risk_score > 0.8 ? '#ee5d50' : row.risk_score > 0.5 ? '#ffb547' : '#05cd99',
                      background: row.risk_score > 0.8 ? '#fff5f5' : row.risk_score > 0.5 ? '#fffbf0' : '#e6fdf5'
                    }}>
                      {(row.risk_score * 100).toFixed(0)}%
                    </div>
                  </td>
                  <td style={{fontSize:'13px', fontWeight:'600', color: row.risk_score > 0.5 ? '#ee5d50' : '#a3aed0'}}>
                      {row.reason || "Standard Login"}
                  </td>
                  <td>
                    <span className={`status-badge ${row.status === 'Verified Safe' ? 'verified' : row.status.includes('Block') ? 'blocked' : 'success'}`}>
                       {row.status}
                    </span>
                  </td>
                  <td>
                    {row.user_feedback ? (
                      <span className="feedback-text">{row.user_feedback}</span>
                    ) : (
                      <div className="action-buttons">
                        <button className="btn-icon safe" onClick={() => handleVerify(row.id, 'verify_safe')} title="Verify Safe"><ThumbsUp size={16}/></button>
                        <button className="btn-icon fraud" onClick={() => handleVerify(row.id, 'confirm_fraud')} title="Confirm Fraud"><ThumbsDown size={16}/></button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default Dashboard;