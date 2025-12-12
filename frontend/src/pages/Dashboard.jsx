import { useState, useEffect } from 'react';
import apiClient from '../api/axiosClient';
import { 
  Shield, Bell, Settings, LayoutDashboard, AlertTriangle, 
  MapPin, Smartphone, Activity, CheckCircle, XCircle, AlertOctagon, ThumbsUp, ThumbsDown, FileText, Globe
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';
import AttackMap from '../components/AttackMap'; // Ensure you created this file in previous steps
import './Dashboard.css';

// --- HELPER: Process History for Real-Time Graph ---
const processRealTimeData = (historyLog) => {
  if (!historyLog || !Array.isArray(historyLog) || historyLog.length === 0) {
    return [
      { time: 'Start', normal: 0, suspicious: 0 },
      { time: 'Live', normal: 0, suspicious: 0 }
    ];
  }

  const groups = {};

  // Process logs (Reverse so oldest appear first on the left)
  [...historyLog].reverse().forEach(log => {
    // Extract time string (e.g. "Dec 03, 10:45 AM") -> "10:45 AM"
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
  // 2. WEBSOCKET CONNECTION (Robust)
  // ----------------------------
  useEffect(() => {
    // Dynamic URL for Local/Vercel
    const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
    // Remove trailing slash if exists to prevent double slash errors
    const cleanBaseUrl = baseUrl.replace(/\/$/, "");
    const wsUrl = cleanBaseUrl.replace(/^http/, "ws"); 
    
    console.log(`🔌 Connecting to WebSocket: ${wsUrl}/ws/alerts`);
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
          
          // Auto-remove alert after 5 seconds
          setTimeout(() => setAlerts(prev => prev.filter(a => a.id !== newAlertId)), 5000);
          
          // Refresh table immediately
          fetchHistory(); 
        }
      } catch (e) { console.error("WS Parse Error", e); }
    };

    return () => { if (ws.readyState === 1) ws.close(); };
  }, []);

  // ----------------------------
  // 3. SAFE DATA POLLING
  // ----------------------------
  const fetchHistory = async () => {
    try {
      const res = await apiClient.get('/security/history');
      if (Array.isArray(res.data)) {
        setHistory(res.data);
      } else {
        setHistory([]); // Safety fallback
      }
    } catch (err) { console.error("API Error", err); }
  };

  useEffect(() => {
    fetchHistory();
    // Poll every 1s for "Live" feel during demo
    const interval = setInterval(fetchHistory, 1000); 
    return () => clearInterval(interval);
  }, []);

  // ----------------------------
  // 4. HANDLERS (PDF, Verify, Simulator)
  // ----------------------------
  const handleDownloadReport = async (logId) => {
      try {
          const response = await apiClient.get(`/security/report/${logId}`, { responseType: 'blob' });
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `Forensic_Report_${logId.substring(0,5)}.pdf`);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
      } catch (e) { alert("Error generating PDF. Check backend logs."); }
  };

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
  // 5. DYNAMIC METRICS
  // ----------------------------
  const safeHistory = Array.isArray(history) ? history : [];
  const latestLog = safeHistory[0]; // Most recent log
  const trendData = processRealTimeData(safeHistory);
  
  // Risk Calculations
  const latestRisk = latestLog ? latestLog.risk_score : 0; 
  const riskPercent = Math.round(latestRisk * 100);
  const safePercent = 100 - riskPercent;
  
  // Colors
  const gaugeColor = safePercent > 80 ? '#05cd99' : safePercent > 50 ? '#ffb547' : '#ee5d50';
  const donutData = [{ name: 'Safe', value: safePercent }, { name: 'Risk', value: riskPercent }];

  return (
    <div className="dashboard-container">
      
      {/* ALERTS POPUP */}
      <div className="toast-container">
        {alerts.map((alert, i) => (
          <div key={i} className="toast">
            <AlertOctagon color="#ee5d50" size={24} />
            <div><h4>Security Alert</h4><p>{alert.msg}</p></div>
          </div>
        ))}
      </div>

      {/* NAVBAR */}
      <nav className="navbar">
        <div className="brand"><Shield size={28} color="#4318ff"/> SecureWatch AI</div>
        <div className="nav-links">
            <div className="nav-item active">Dashboard</div>
            <div className="nav-item launch-btn" onClick={openSimulator}>
                <Smartphone size={16}/> Launch App
            </div>
            <div className="nav-item"><Settings size={18}/> Settings</div>
        </div>
      </nav>

      {/* --- ROW 1: RISK STATUS & MAP --- */}
      <div className="stats-grid">
        
        {/* LEFT: RISK GAUGE & AI ANALYSIS */}
        <div className="card risk-card">
          <div className="card-header">
            <h3>Security Status</h3>
            <Activity size={18} color="#a3aed0"/>
          </div>
          
          <div className="donut-layout">
            <div className="donut-wrapper">
               <PieChart width={140} height={140}>
                  <Pie data={donutData} innerRadius={55} outerRadius={70} startAngle={90} endAngle={-270} dataKey="value" stroke="none">
                    <Cell fill={gaugeColor} /> 
                    <Cell fill="#f4f7fe" />
                  </Pie>
               </PieChart>
               <div className="risk-label">
                  <h2 style={{color: gaugeColor}}>{safePercent}%</h2>
                  <span style={{color: '#a3aed0', fontSize:'12px'}}>Safe</span>
               </div>
            </div>
            
            {/* GEN AI BOX */}
            <div className="ai-summary-box" style={{flex: 1, marginLeft: '20px', background: '#f8fafc', padding: '15px', borderRadius: '12px', borderLeft: '4px solid #4318ff'}}>
               <h4 style={{margin: '0 0 8px 0', fontSize:'14px', display:'flex', alignItems:'center', gap:'6px', color:'#4318ff'}}>
                 <Activity size={14}/> AI Forensic Analysis
               </h4>
               <p style={{margin:0, fontSize:'12px', color: '#475569', lineHeight: '1.5'}}>
                 {latestLog?.ai_summary || "System monitoring active. No anomalies detected in current session traffic."}
               </p>
            </div>
          </div>
        </div>

        {/* RIGHT: WAR ROOM MAP */}
        <div className="card map-card" style={{padding: 0, overflow: 'hidden', minHeight: '300px'}}>
           <div style={{padding: '15px', borderBottom:'1px solid #eee', display:'flex', gap:'10px', alignItems:'center', background:'#fff', position:'relative', zIndex:10}}>
              <Globe size={18} color="#4318ff"/> 
              <strong>Global Threat Map</strong>
           </div>
           <div style={{height: '100%'}}>
              {/* Requires AttackMap.jsx component */}
              <AttackMap logs={safeHistory} />
           </div>
        </div>
      </div>

      {/* --- ROW 2: LIVE GRAPH --- */}
      <div className="card chart-section">
        <div className="section-title"><Activity size={20} color="#4318ff"/> Live Traffic Analysis</div>
        <div style={{ width: '100%', height: 220 }}>
          <ResponsiveContainer>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e0e5f2"/>
              <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#a3aed0', fontSize: 12}} dy={10}/>
              <YAxis axisLine={false} tickLine={false} tick={{fill: '#a3aed0', fontSize: 12}}/>
              <Tooltip contentStyle={{borderRadius: '10px', border: 'none', boxShadow: '0 10px 20px rgba(0,0,0,0.1)'}}/>
              <Line type="monotone" dataKey="normal" stroke="#05cd99" strokeWidth={3} dot={{r:4}} name="Safe" />
              <Line type="monotone" dataKey="suspicious" stroke="#ee5d50" strokeWidth={3} dot={{r:4}} name="Threats" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* --- ROW 3: DETAILED TABLE --- */}
      <div className="card">
        <div className="section-title">Live Transaction Monitor</div>
        <div className="table-container">
          <table>
            <thead>
              <tr><th>Timestamp</th><th>Loc</th><th>Device</th><th>Score</th><th>Reason</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {safeHistory.map((row) => (
                <tr key={row.id}>
                  <td style={{fontWeight:'500', fontSize:'13px'}}>{row.time}</td>
                  <td><div className="icon-text"><MapPin size={14} color="#a3aed0"/> {row.location}</div></td>
                  <td style={{fontSize:'13px', color:'#64748b'}}>{row.device}</td>
                  
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
                    <div style={{display:'flex', gap:'10px'}}>
                        {/* 1. DOWNLOAD PDF */}
                        <button className="btn-icon" onClick={() => handleDownloadReport(row.id)} title="Download Report">
                            <FileText size={16} color="#4318ff"/>
                        </button>
                        
                        {/* 2. VERIFY BUTTONS (Only show if not verified yet) */}
                        {!row.user_feedback && (
                            <>
                            <button className="btn-icon" onClick={() => handleVerify(row.id, 'verify_safe')} title="Verify Safe"><ThumbsUp size={16} color="green"/></button>
                            <button className="btn-icon" onClick={() => handleVerify(row.id, 'confirm_fraud')} title="Confirm Fraud"><ThumbsDown size={16} color="red"/></button>
                            </>
                        )}
                    </div>
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