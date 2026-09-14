import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Filter, EyeOff } from 'lucide-react';

export default function Excluded() {
  const [excluded, setExcluded] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get('/admin/excluded')
      .then(res => setExcluded(res))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <header className="mb-8 border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight flex items-center">
          <EyeOff className="w-8 h-8 mr-3 text-gray-400" />
          Excluded Stories
        </h1>
        <p className="mt-2 text-gray-600">
          Transparency view. Here is what we filtered out today and why.
        </p>
      </header>

      {loading ? (
        <p className="text-gray-500">Loading excluded articles...</p>
      ) : excluded.length === 0 ? (
        <div className="text-center py-12">
          <Filter className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No articles were excluded recently.</p>
        </div>
      ) : (
        <div className="space-y-12">
          {(() => {
            const grouped = excluded.reduce((acc, item) => {
              const cat = item.category || 'Uncategorized';
              if (!acc[cat]) acc[cat] = [];
              acc[cat].push(item);
              return acc;
            }, {} as Record<string, any[]>);

            const categories = Object.keys(grouped).sort((a, b) => {
              if (a === 'Uncategorized') return 1;
              if (b === 'Uncategorized') return -1;
              return a.localeCompare(b);
            });

            return categories.map(cat => (
              <div key={cat} className="space-y-4">
                <h2 className={`text-xl font-bold border-b pb-2 ${cat === 'Uncategorized' ? 'text-gray-400 border-gray-100' : 'text-gray-800 border-gray-200'}`}>
                  {cat}
                </h2>
                <div className="space-y-4">
                  {grouped[cat].map((item: any, idx: number) => (
                    <div key={idx} className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm opacity-75 hover:opacity-100 transition-opacity">
                      <h3 className="font-bold text-gray-900 mb-1">
                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline">{item.title}</a>
                      </h3>
                      <p className="text-sm text-gray-500 mb-3">{item.source}</p>
                      
                      <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-700">
                        <span className="font-semibold block mb-1">Why was this excluded?</span>
                        <ul className="list-disc list-inside space-y-1">
                          {item.relevance_score < 0.3 && (
                            <li>Low relevance to your goals ({item.relevance_score.toFixed(2)})</li>
                          )}
                          {item.credibility_score < 0.6 && (
                            <li>Low credibility score ({item.credibility_score.toFixed(2)})</li>
                          )}
                          {item.credibility_reasons.map((reason: string, rIdx: number) => (
                            <li key={rIdx} className="text-gray-500">{reason}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ));
          })()}
        </div>
      )}
    </div>
  );
}
