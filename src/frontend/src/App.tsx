import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, ClipboardList } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Complaints from './pages/Complaints';
import ComplaintDetail from './pages/ComplaintDetail';
import ComplaintCreate from './pages/ComplaintCreate';
import Landing from './pages/Landing';
import Access from './pages/Access';
import PublicPortal from './pages/PublicPortal';
import WorkerPortal from './pages/WorkerPortal';
import PortalComplaintDetail from './pages/PortalComplaintDetail';
import NotificationPanel from './components/NotificationPanel';

const App: React.FC = () => {
  const location = useLocation();
  const mccView = location.pathname.startsWith('/mcc') || location.pathname.startsWith('/complaints') || location.pathname.startsWith('/verification');
  const portalView = location.pathname === '/public' || location.pathname === '/worker';
  const landingView = location.pathname === '/';
  const authView = location.pathname.startsWith('/access/');
  return (
    <div className="min-h-screen flex flex-col">
      {mccView && <nav className="app-nav">
        <div className="app-nav-inner">
          <Link to="/" className="app-brand"><span className="app-brand-mark">MD</span><span><small>MYSURU CITY CORPORATION</small><strong>Mysuru<span>Drishti</span></strong></span></Link>
          <div className="app-nav-links">
            <Link to="/mcc"><LayoutDashboard className="w-4 h-4" />Dashboard</Link>
            <Link to="/complaints"><ClipboardList className="w-4 h-4" />Complaints</Link>
          </div>
        </div>
      </nav>}
      <main className={`flex-1 ${landingView || authView ? '' : 'app-workspace'}`}>
        {portalView && <div className="max-w-6xl mx-auto mb-6"><NotificationPanel /></div>}
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/access/:role" element={<Access />} />
          <Route path="/public" element={<PublicPortal />} />
          <Route path="/worker" element={<WorkerPortal />} />
          <Route path="/:role/complaints/:id" element={<PortalComplaintDetail />} />
          <Route path="/mcc" element={<Dashboard />} />
          <Route path="/complaints" element={<Complaints />} />
          <Route path="/complaints/new" element={<ComplaintCreate />} />
          <Route path="/complaints/:id" element={<ComplaintDetail />} />
        </Routes>
      </main>
      {mccView && <footer className="app-footer">
        &copy; 2026 MysuruDrishti <span>Municipal Resolution Verification Platform</span>
      </footer>}
    </div>
  );
};

export default App;
