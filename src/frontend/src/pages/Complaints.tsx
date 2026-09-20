import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, MapPin, AlertTriangle, Calendar } from 'lucide-react';
import { complaintApi } from '../services/api';
import { Complaint } from '../types/complaint';

const Complaints: React.FC = () => {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    complaintApi.list()
      .then(items => setComplaints(items.sort((a: Complaint, b: Complaint) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Civic Complaints</h1>
          <p className="text-slate-500">Manage and track reported civic issues</p>
        </div>
        <Link
          to="/complaints/new"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          New Complaint
        </Link>
      </div >

      {loading ? (
        <div className="text-center py-12 text-slate-500">Loading complaints...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="p-4 font-semibold text-slate-600 text-sm">Complaint #</th>
                <th className="p-4 font-semibold text-slate-600 text-sm">Issue Type</th>
                <th className="p-4 font-semibold text-slate-600 text-sm">Location</th>
                <th className="p-4 font-semibold text-slate-600 text-sm">Status</th>
                <th className="p-4 font-semibold text-slate-600 text-sm">Created</th>
                <th className="p-4 font-semibold text-slate-600 text-sm">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {complaints.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50 transition-colors">
                  <td className="p-4 font-bold text-slate-900">{c.complaint_number}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
                      {c.issue_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-slate-600">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" /> {c.address || 'No address'}
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium
                      ${c.status === 'OPEN' ? 'bg-blue-100 text-blue-700' :
                        c.status === 'VERIFIED_RESOLVED' ? 'bg-green-100 text-green-700' :
                        'bg-orange-100 text-orange-700'}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-slate-500">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" /> {new Date(c.created_at).toLocaleString()}
                    </div>
                  </td>
                  <td className="p-4">
                    <Link
                      to={`/complaints/${c.id}`}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
              {complaints.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-slate-500 italic">
                    No complaints found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Complaints;
