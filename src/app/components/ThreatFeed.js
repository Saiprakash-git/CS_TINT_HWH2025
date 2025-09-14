'use client';

import { ShieldAlert, Clock, Bug } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ThreatFeed({ threats }) {
  // utility for severity badge colors
  const badgeColor = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'critical':
        return 'bg-red-500/20 text-red-400 border-red-500/40';
      case 'high':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40';
      case 'low':
        return 'bg-green-500/20 text-green-400 border-green-500/40';
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/40';
    }
  };

  return (
    <div className="mt-6 bg-gray-900/60 backdrop-blur-md rounded-2xl shadow-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <ShieldAlert className="text-red-400" size={22} />
        <h2 className="text-xl font-semibold text-white">
          Real-Time Threat Feed
        </h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-gray-300">
          <thead>
            <tr className="bg-gray-800/70 text-gray-200">
              <th className="p-3 font-medium">Threat</th>
              <th className="p-3 font-medium">Severity</th>
              <th className="p-3 font-medium">Published</th>
              <th className="p-3 font-medium">Summary</th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {threats.map((t) => (
                <motion.tr
                  key={t.id}
                  className="border-b border-gray-700 hover:bg-gray-800/40 transition-colors"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.4 }}
                >
                  <td className="p-3 flex items-center gap-2">
                    <Bug className="text-gray-400" size={16} />
                    <span className="font-medium">{t.id}</span>
                  </td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-1 text-xs rounded-full border ${badgeColor(
                        t.severity
                      )}`}
                    >
                      {t.severity}
                    </span>
                  </td>
                  <td className="p-3 flex items-center gap-1">
                    <Clock size={14} className="text-gray-400" />
                    {new Date(t.published).toLocaleString()}
                  </td>
                  <td
                    className="p-3 max-w-xs truncate"
                    title={t.description}
                  >
                    {t.description || 'No description'}
                  </td>
                </motion.tr>
              ))}
            </AnimatePresence>
          </tbody>
        </table>
      </div>
    </div>
  );
}
