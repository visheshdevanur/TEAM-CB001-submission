import React, { useEffect, useState } from 'react';
import { Bell } from 'lucide-react';
import { notificationApi } from '../services/api';

const NotificationPanel: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const load = () => notificationApi.mine().then(setItems).catch(() => setItems([]));
  useEffect(() => { load(); const timer = window.setInterval(load, 30000); return () => window.clearInterval(timer); }, []);
  const unread = items.filter(item => !item.is_read).length;
  const read = async (id: number) => { await notificationApi.markRead(id); load(); };
  return <section className="bg-white border rounded-xl p-5"><div className="flex justify-between items-center"><h2 className="font-bold flex gap-2"><Bell className="w-5 h-5 text-blue-600"/> Notifications</h2>{unread > 0 && <span className="rounded-full bg-red-600 text-white text-xs px-2 py-0.5">{unread} new</span>}</div>{items.length ? <div className="mt-4 max-h-80 space-y-3 overflow-y-auto pr-2" aria-label="Notification list">{items.map(item => <button key={item.id} onClick={() => void read(item.id)} className={`w-full text-left border rounded-lg p-3 ${item.is_read ? 'bg-white' : item.kind === 'RESOLVED' ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'}`}><p className="font-semibold text-sm">{item.title}</p><p className="mt-1 text-sm text-slate-600">{item.message}</p><p className="mt-1 text-xs text-slate-400">{new Date(item.created_at).toLocaleString()}</p></button>)}</div> : <p className="mt-3 text-sm text-slate-500">No notifications yet.</p>}</section>;
};
export default NotificationPanel;
