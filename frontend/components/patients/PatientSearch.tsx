"use client";

import { useState } from "react";
import { Search } from "lucide-react";

interface PatientSearchProps {
  onSearch: (query: string) => void;
}

export default function PatientSearch({ onSearch }: PatientSearchProps) {
  const [query, setQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSearch} className="relative w-full max-w-md">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
        <Search size={18} />
      </div>
      <input
        type="text"
        className="block w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg leading-5 bg-white placeholder-slate-700 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent sm:text-sm transition-all shadow-sm"
        placeholder="Search patients by name or ID..."
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          // Optional: real-time search
          // onSearch(e.target.value);
        }}
      />
    </form>
  );
}
