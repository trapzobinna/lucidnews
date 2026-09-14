
import { ShieldCheck, ShieldAlert, Shield } from 'lucide-react';

export default function CredibilityBadge({ score }: { score: number }) {
  let colorClass = "bg-gray-100 text-gray-800 border-gray-200";
  let Icon = Shield;
  let label = "Neutral";

  if (score >= 0.8) {
    colorClass = "bg-green-50 text-green-700 border-green-200";
    Icon = ShieldCheck;
    label = "High Trust";
  } else if (score >= 0.6) {
    colorClass = "bg-blue-50 text-blue-700 border-blue-200";
    Icon = Shield;
    label = "Standard";
  } else {
    colorClass = "bg-red-50 text-red-700 border-red-200";
    Icon = ShieldAlert;
    label = "Low Trust";
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClass}`} title={`Score: ${score.toFixed(2)}`}>
      <Icon className="w-3 h-3 mr-1" />
      {label}
    </span>
  );
}
