
import { Target } from 'lucide-react';

export default function GoalTag({ relevanceScore, matchType, matchedKeyword }: { relevanceScore: number, matchType?: string, matchedKeyword?: string }) {
  if (relevanceScore < 0.3) return null;
  
  let label = "Relevant";
  if (relevanceScore > 0.6) label = "Highly Relevant";
  
  const isKeyword = matchType === 'keyword';
  
  return (
    <span 
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${isKeyword ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-purple-50 text-purple-700 border-purple-200'}`}
      title={`Score: ${relevanceScore.toFixed(2)}`}
    >
      <Target className="w-3 h-3 mr-1" />
      {isKeyword ? `Matched: ${matchedKeyword} (keyword)` : `Matched: ${label} (semantic)`}
    </span>
  );
}
