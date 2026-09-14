import React from 'react';
import CredibilityBadge from './CredibilityBadge';
import GoalTag from './GoalTag';
import { ExternalLink, Calendar } from 'lucide-react';
import { format, parseISO } from 'date-fns';

interface ArticleCardProps {
  item: {
    article: { title: string; url: string; published_at: string | null };
    source: { name: string; category: string };
    score: { credibility_score: number; relevance_score: number; credibility_reasons: string; relevance_match_type?: string; matched_keyword?: string };
    summary: string;
  };
  index: number;
}

export default function ArticleCard({ item, index }: ArticleCardProps) {
  const { article, source, score, summary } = item;
  
  const formattedDate = article.published_at 
    ? format(parseISO(article.published_at), 'MMM d, yyyy')
    : 'Unknown date';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200 mb-6">
      <div className="p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start mb-4 gap-2 sm:gap-4">
          <div className="flex gap-2 flex-wrap">
            <CredibilityBadge score={score.credibility_score} />
            <GoalTag 
              relevanceScore={score.relevance_score} 
              matchType={score.relevance_match_type}
              matchedKeyword={score.matched_keyword}
            />
          </div>
          <span className="text-sm text-gray-500 font-medium bg-gray-50 px-2 py-1 rounded">#{index + 1}</span>
        </div>
        
        <h2 className="text-xl font-bold text-gray-900 mb-2 leading-tight">
          <a href={article.url} target="_blank" rel="noopener noreferrer" className="hover:text-indigo-600 transition-colors">
            {article.title}
          </a>
        </h2>
        
        <p className="text-gray-600 mb-4 leading-relaxed">
          {summary}
        </p>
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between text-sm text-gray-500 border-t border-gray-100 pt-4 gap-3 sm:gap-0">
          <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-4">
            <span className="font-medium text-gray-700">{source.name}</span>
            <span className="flex items-center"><Calendar className="w-3 h-3 mr-1" /> {formattedDate}</span>
          </div>
          <a href={article.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium">
            Read Source <ExternalLink className="w-3 h-3 ml-1" />
          </a>
        </div>
      </div>
    </div>
  );
}
