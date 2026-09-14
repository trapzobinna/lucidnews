import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Settings, List, FileText, Menu, X } from 'lucide-react';

export default function Layout({ children }: { children: React.ReactNode }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);
  const closeMenu = () => setIsMobileMenuOpen(false);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex justify-between w-full sm:w-auto">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Lucid</span>
              </div>
              <div className="flex items-center sm:hidden">
                <button 
                  onClick={toggleMenu}
                  className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none"
                >
                  {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
              </div>
            </div>
            
            <div className="hidden sm:-my-px sm:ml-8 sm:flex sm:space-x-8">
              <NavLink to="/" className={({ isActive }) => 
                `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive ? 'border-indigo-500 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`
              }>
                <FileText className="w-4 h-4 mr-2" />
                Today's Briefing
              </NavLink>
              <NavLink to="/goals" className={({ isActive }) => 
                `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive ? 'border-indigo-500 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`
              }>
                <Settings className="w-4 h-4 mr-2" />
                Goals
              </NavLink>
              <NavLink to="/excluded" className={({ isActive }) => 
                `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive ? 'border-indigo-500 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`
              }>
                <List className="w-4 h-4 mr-2" />
                Excluded
              </NavLink>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="sm:hidden border-t border-gray-200 bg-white">
            <div className="pt-2 pb-3 space-y-1">
              <NavLink 
                to="/" 
                onClick={closeMenu}
                className={({ isActive }) => 
                  `block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${isActive ? 'bg-indigo-50 border-indigo-500 text-indigo-700' : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'}`
                }
              >
                <div className="flex items-center">
                  <FileText className="w-5 h-5 mr-3" />
                  Today's Briefing
                </div>
              </NavLink>
              <NavLink 
                to="/goals" 
                onClick={closeMenu}
                className={({ isActive }) => 
                  `block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${isActive ? 'bg-indigo-50 border-indigo-500 text-indigo-700' : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'}`
                }
              >
                <div className="flex items-center">
                  <Settings className="w-5 h-5 mr-3" />
                  Goals
                </div>
              </NavLink>
              <NavLink 
                to="/excluded" 
                onClick={closeMenu}
                className={({ isActive }) => 
                  `block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${isActive ? 'bg-indigo-50 border-indigo-500 text-indigo-700' : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'}`
                }
              >
                <div className="flex items-center">
                  <List className="w-5 h-5 mr-3" />
                  Excluded
                </div>
              </NavLink>
            </div>
          </div>
        )}
      </nav>

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
