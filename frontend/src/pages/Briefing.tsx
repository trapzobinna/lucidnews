import { useEffect, useState, useRef } from 'react';
import { apiClient } from '../api/client';
import ArticleCard from '../components/ArticleCard';
import { Sparkles, Loader2, AlertCircle } from 'lucide-react';

interface ProgressState {
  is_running: boolean;
  stage: string;
  progress: number;
  error: string | null;
}

export default function Briefing() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  
  const [pipelineState, setPipelineState] = useState<ProgressState | null>(null);
  const [pipelineConflict, setPipelineConflict] = useState(false);
  const pollingInterval = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchBriefing = () => {
    setLoading(true);
    apiClient.get('/briefings/today')
      .then(res => setData(res))
      .catch(err => setFetchError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchBriefing();
    return () => stopPolling();
  }, []);

  const stopPolling = () => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }
  };

  const pollProgress = () => {
    if (pollingInterval.current) return;
    
    pollingInterval.current = setInterval(async () => {
      try {
        const res = await apiClient.get('/admin/pipeline-progress');
        setPipelineState(res);
        
        if (res.stage === "Error") {
          stopPolling();
        } else if (res.progress === 100 || !res.is_running) {
          stopPolling();
          if (res.progress === 100) {
            // Pipeline finished, fetch new briefing
            setTimeout(() => {
              setPipelineState(null);
              fetchBriefing();
            }, 1500); // little delay to show 100%
          }
        }
      } catch (err) {
        console.error("Failed to fetch pipeline progress", err);
      }
    }, 1500);
  };

  const runPipeline = async () => {
    setPipelineConflict(false);
    try {
      await apiClient.post('/admin/run-pipeline', {});
      // Success, start polling
      setPipelineState({ is_running: true, stage: "Starting", progress: 0, error: null });
      pollProgress();
    } catch (err: any) {
      if (err.response?.status === 409) {
        setPipelineConflict(true);
        pollProgress(); // Start polling to show current progress
      } else {
        alert("Error triggering pipeline: " + err);
      }
    }
  };

  if (loading && !pipelineState?.is_running) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mb-4" />
        <p className="text-gray-500">Curating your briefing...</p>
      </div>
    );
  }

  // If no data and not running, OR if pipeline is actively running/errored, show the dashboard card
  if (fetchError || !data || pipelineState?.is_running || pipelineState?.stage === "Error") {
    return (
      <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-gray-200 px-6 max-w-2xl mx-auto mt-10">
        <Sparkles className="w-12 h-12 text-indigo-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {pipelineState?.is_running ? "Curating Today's Briefing..." : "No Briefing Yet"}
        </h2>
        
        {(!pipelineState || (!pipelineState.is_running && pipelineState.stage !== "Error")) && (
          <>
            <p className="text-gray-500 mb-6">Today's pipeline hasn't run or no articles met your criteria.</p>
            {pipelineConflict && (
              <div className="mb-4 text-sm text-amber-600 bg-amber-50 p-2 rounded inline-block">
                A pipeline is already running in the background.
              </div>
            )}
            <br/>
            <button 
              onClick={runPipeline}
              className="inline-flex items-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
            >
              Run Pipeline Now
            </button>
          </>
        )}

        {(pipelineState?.is_running || pipelineState?.stage === "Error") && (
          <div className="mt-8 text-left max-w-md mx-auto">
            <div className="flex justify-between text-sm font-medium mb-2">
              <span className={pipelineState.stage === "Error" ? "text-red-600" : "text-indigo-600"}>
                {pipelineState.stage === "Error" ? "Pipeline Failed" : pipelineState.stage}
              </span>
              <span className="text-gray-500">{pipelineState.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div 
                className={`h-2.5 rounded-full transition-all duration-500 ease-out ${pipelineState.stage === "Error" ? "bg-red-500" : "bg-indigo-600"}`}
                style={{ width: `${pipelineState.progress}%` }}
              ></div>
            </div>
            
            {pipelineState.stage === "Error" && (
              <div className="mt-4 p-4 bg-red-50 rounded-lg flex items-start text-sm text-red-700">
                <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                <p className="break-all">{pipelineState.error}</p>
              </div>
            )}
            
            {pipelineState.stage === "Error" && (
              <div className="mt-6 text-center">
                <button 
                  onClick={runPipeline}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                >
                  Retry Pipeline
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <header className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Today's Briefing</h1>
          <p className="mt-2 text-gray-600">
            The most credible, relevant stories for your goals. No infinite scroll.
          </p>
        </div>
        <button 
          onClick={runPipeline}
          className="w-full sm:w-auto justify-center inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          Re-run Pipeline
        </button>
      </header>

      <div className="space-y-6">
        {data.items.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Articles Found</h3>
            <p className="text-gray-500">
              We scoured the internet, but no highly credible stories matched your goals today.
            </p>
          </div>
        ) : (
          data.items.map((item: any, idx: number) => (
            <ArticleCard key={idx} item={item} index={idx} />
          ))
        )}
      </div>

      <div className="mt-12 text-center py-8 border-t border-gray-200">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 mb-4">
          <Sparkles className="w-5 h-5 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900">You're caught up!</h3>
        <p className="text-gray-500 mt-1">That's everything you need to know today. See you tomorrow.</p>
      </div>
    </div>
  );
}
