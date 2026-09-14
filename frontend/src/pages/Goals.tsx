import React, { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Target, Plus, Trash2 } from 'lucide-react';

export default function Goals() {
  const [goals, setGoals] = useState<any[]>([]);
  const [newGoal, setNewGoal] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchGoals = () => {
    apiClient.get('/goals/')
      .then(res => setGoals(res))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGoal.trim()) return;
    
    apiClient.post('/goals/', { goal_text: newGoal.trim() })
      .then(() => {
        setNewGoal("");
        fetchGoals();
      });
  };

  const handleDelete = (id: number) => {
    apiClient.delete(`/goals/${id}`)
      .then(() => fetchGoals());
  };

  return (
    <div>
      <header className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Your Goals</h1>
        <p className="mt-2 text-gray-600">
          Define what matters to you. Lucid uses these to find relevant stories.
        </p>
      </header>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-8">
        <div className="p-6">
          <form onSubmit={handleAdd} className="flex flex-col sm:flex-row gap-4">
            <input 
              type="text" 
              value={newGoal}
              onChange={(e) => setNewGoal(e.target.value)}
              placeholder="e.g. Cybersecurity startups, AI engineering roles..." 
              className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
            />
            <button type="submit" className="w-full sm:w-auto justify-center inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
              <Plus className="w-4 h-4 mr-2" />
              Add Goal
            </button>
          </form>
        </div>
      </div>

      <div className="space-y-4">
        {loading ? (
          <p className="text-gray-500">Loading goals...</p>
        ) : goals.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
            <Target className="w-10 h-10 text-gray-400 mx-auto mb-3" />
            <h3 className="text-sm font-medium text-gray-900">No goals set</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating a goal above.</p>
          </div>
        ) : (
          goals.map(goal => (
            <div key={goal.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex justify-between items-center">
              <div className="flex items-center">
                <Target className="w-5 h-5 text-indigo-500 mr-3" />
                <span className="font-medium text-gray-900">{goal.goal_text}</span>
              </div>
              <button onClick={() => handleDelete(goal.id)} className="text-gray-400 hover:text-red-600 transition-colors">
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
