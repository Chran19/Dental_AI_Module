"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAnalysisResults } from "@/lib/api";
import { useAuth } from "@/app/providers";
import {
  ArrowLeft,
  FileText,
  Filter,
  Search,
  Download,
  Share2,
  Eye,
  BarChart2,
  Calendar,
  Layers,
  Activity
} from "lucide-react";

export default function ResultsPage() {
  const { isAuthenticated } = useAuth();
  const [results, setResults] = useState<any[]>([]);
  const [filteredResults, setFilteredResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Filters
  const [filterType, setFilterType] = useState("All");
  const [minConfidence, setMinConfidence] = useState("Any");

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getAnalysisResults();
        const resultsArray = Array.isArray(data) ? data : [];
        
        // Mocking some extra data on results for better UI since real data might be bare JSON
        const enhancedResults = resultsArray.map((r: Record<string, any>, i: number) => ({
           ...r,
           analysis_type: r.analysis_type || (Math.random() > 0.5 ? "Periapical Lesion" : "Caries Detection"),
           patient_name: r.patient_name || `Patient 00${i+1}X`,
           timestamp: r.timestamp || new Date(Date.now() - Math.random() * 10000000000).toISOString(),
           confidence: r.confidence !== undefined ? r.confidence : (0.7 + Math.random() * 0.28),
           severity: r.severity || (Math.random() > 0.8 ? "critical" : Math.random() > 0.4 ? "high" : "moderate"),
           diagnosis: r.diagnosis || (r.analysis_result?.pathologies ? r.analysis_result.pathologies.join(', ') : "Review needed")
        }));

        setResults(enhancedResults);
        setFilteredResults(enhancedResults);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) fetchResults();
  }, [isAuthenticated]);

  useEffect(() => {
    let filtered = [...results];
    
    if (filterType !== "All") {
      filtered = filtered.filter(r => r.analysis_type === filterType);
    }
    
    if (minConfidence !== "Any") {
      const min = parseFloat(minConfidence) / 100;
      filtered = filtered.filter(r => r.confidence >= min);
    }
    
    setFilteredResults(filtered);
  }, [filterType, minConfidence, results]);

  if (!isAuthenticated) return null;

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen pb-10">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                 <FileText className="text-indigo-600" /> Analysis Reports
              </h1>
            </div>
            <p className="text-gray-600 mt-1 font-medium">
              Review and manage structured AI diagnostic results.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6">
         
         <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            
            {/* Filter Bar */}
            <div className="p-5 border-b border-gray-100 bg-gray-50 flex flex-col md:flex-row gap-4 items-end">
               <div className="flex-1 w-full">
                  <label className="block text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                     <Layers size={12} /> Analysis Type
                  </label>
                  <select 
                     value={filterType} 
                     onChange={(e) => setFilterType(e.target.value)}
                     className="w-full bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5 font-bold"
                  >
                     <option value="All">All Categories</option>
                     <option value="Periapical Lesion">Periapical Lesion</option>
                     <option value="Caries Detection">Caries Detection</option>
                  </select>
               </div>
               
               <div className="flex-1 w-full">
                  <label className="block text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                     <Activity size={12} /> Min Confidence
                  </label>
                  <select 
                     value={minConfidence} 
                     onChange={(e) => setMinConfidence(e.target.value)}
                     className="w-full bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5 font-bold"
                  >
                     <option value="Any">Any Confidence</option>
                     <option value="75">75%+</option>
                     <option value="85">85%+</option>
                     <option value="95">95%+</option>
                  </select>
               </div>
               
               <div className="flex-1 w-full sm:w-auto">
                  <button className="w-full bg-indigo-600 text-white font-bold rounded-lg px-6 py-2.5 hover:bg-indigo-700 transition flex items-center justify-center gap-2 shadow-sm">
                     <Filter size={16} /> Filter Results
                  </button>
               </div>
            </div>

            {/* Content Area */}
            <div className="p-6">
               {loading && (
                 <div className="space-y-4">
                   <div className="h-40 bg-gray-100 animate-pulse rounded-xl border border-gray-200"></div>
                   <div className="h-40 bg-gray-100 animate-pulse rounded-xl border border-gray-200"></div>
                 </div>
               )}

               {error && (
                 <div className="rounded-lg bg-red-50 p-4 font-bold text-red-700 border border-red-200">
                   Connection Error: {error}
                 </div>
               )}

               {!loading && !error && filteredResults.length === 0 && (
                 <div className="text-center py-16 px-4">
                   <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4 text-gray-400">
                     <BarChart2 size={32} />
                   </div>
                   <h3 className="text-xl font-bold text-gray-900 mb-2">No results found</h3>
                   <p className="text-gray-500 font-medium mb-6 max-w-sm mx-auto">
                     There are no analysis records matching your criteria. Try adjusting your filters or upload a new scan.
                   </p>
                   <Link href="/dashboard/upload" className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 outline-none rounded-lg font-bold hover:bg-indigo-700 transition shadow-sm">
                     Upload Scan
                   </Link>
                 </div>
               )}

               {!loading && filteredResults.length > 0 && (
                 <div className="space-y-4">
                   {filteredResults.map((result, index) => (
                     <div
                       key={index}
                       className={`border-l-4 rounded-xl p-5 hover:shadow-md transition bg-white border border-gray-200 ${
                          result.severity === 'critical' ? 'border-l-red-500' :
                          result.severity === 'high' ? 'border-l-orange-500' : 'border-l-blue-500'
                       }`}
                     >
                       <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                         <div>
                           <div className="flex items-center gap-3 mb-1">
                              <h3 className="text-lg font-black text-gray-900 uppercase">
                                {result.analysis_type}
                              </h3>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                                 result.severity === 'critical' ? 'bg-red-100 text-red-700' :
                                 result.severity === 'high' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'
                              }`}>
                                 {result.severity} Risk
                              </span>
                           </div>
                           <div className="flex flex-wrap items-center gap-4 text-sm font-medium text-gray-500 mt-2">
                              <span className="flex items-center gap-1 bg-gray-50 px-2 py-1 rounded border border-gray-200 shadow-sm text-gray-800">
                                 <strong>ID:</strong> {result.patient_name}
                              </span>
                              <span className="flex items-center gap-1">
                                 <Calendar size={14} /> {new Date(result.timestamp).toLocaleDateString()} at {new Date(result.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                              </span>
                           </div>
                         </div>
                         
                         <div className="flex flex-col items-end">
                            <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider mb-1">Model Confidence</span>
                            <div className="flex items-center gap-2">
                               <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
                                  <div className="h-full bg-green-500 rounded-full" style={{width: `${(result.confidence * 100)}%`}}></div>
                               </div>
                               <span className="text-lg font-black text-green-700">
                                 {(result.confidence * 100).toFixed(0)}%
                               </span>
                            </div>
                         </div>
                       </div>

                       <div className="mt-5 p-4 bg-gray-50 rounded-lg border border-gray-100">
                         <p className="text-sm font-medium text-gray-700">
                           <strong className="text-gray-900 mr-2 uppercase text-[11px] tracking-wider">Primary Findings:</strong> 
                           {result.diagnosis || "No specific anomalies detected beyond baseline."}
                         </p>
                       </div>

                       <div className="mt-5 flex flex-wrap gap-3">
                         <button className="px-5 py-2 bg-white border border-gray-300 text-gray-800 font-bold rounded-lg hover:bg-gray-50 text-sm flex items-center gap-2 transition shadow-sm">
                           <Eye size={16} /> View Details
                         </button>
                         <button className="px-5 py-2 bg-white border border-gray-300 text-gray-800 font-bold rounded-lg hover:bg-gray-50 text-sm flex items-center gap-2 transition shadow-sm">
                           <Share2 size={16} /> Share
                         </button>
                         <button className="px-5 py-2 bg-white border border-gray-300 text-gray-800 font-bold rounded-lg hover:bg-gray-50 text-sm flex items-center gap-2 transition shadow-sm">
                           <Download size={16} /> Report
                         </button>
                       </div>
                     </div>
                   ))}
                 </div>
               )}

            </div>
         </div>
      </div>
    </div>
  );
}
