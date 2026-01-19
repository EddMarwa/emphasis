import React, { useState } from 'react';
import { Menu, X, User, LogOut, Settings } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Header = ({ user, onLogout }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const navigate = useNavigate();
  
  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    navigate('/login');
  };
  
  return (
    <header className="sticky top-0 z-40 bg-gradient-header text-white shadow-lg">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-3 group">
            <div className="w-10 h-10 bg-gradient-button-primary rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-cyan-glow transition-all duration-300">
              <span className="text-xl font-bold">Q</span>
            </div>
            <span className="text-xl font-bold">Quantum Capital</span>
          </Link>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <Link to="/dashboard" className="hover:text-electric-cyan transition-colors duration-200 font-medium">
              Dashboard
            </Link>
            <Link to="/funds" className="hover:text-electric-cyan transition-colors duration-200 font-medium">
              Funds
            </Link>
            <Link to="/referrals" className="hover:text-electric-cyan transition-colors duration-200 font-medium">
              Referrals
            </Link>
            <Link to="/training" className="hover:text-electric-cyan transition-colors duration-200 font-medium">
              Training
            </Link>
            {user?.isAdmin && (
              <Link to="/admin" className="hover:text-electric-cyan transition-colors duration-200 font-medium">
                Admin
              </Link>
            )}
          </div>
          
          {/* User Menu */}
          <div className="hidden md:flex items-center gap-4">
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-button-primary rounded-full flex items-center justify-center border-2 border-electric-cyan">
                  <User size={16} />
                </div>
                <span className="font-medium">{user?.username || 'User'}</span>
              </button>
              
              {userMenuOpen && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setUserMenuOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-quantum-lg overflow-hidden animate-slide-up z-20">
                    <div className="p-2">
                      <div className="px-4 py-2 border-b border-gray-200">
                        <p className="text-sm font-semibold text-text-dark">{user?.username || 'User'}</p>
                        <p className="text-xs text-text-gray">{user?.email || ''}</p>
                      </div>
                      <button
                        onClick={() => {
                          setUserMenuOpen(false);
                          navigate('/profile');
                        }}
                        className="w-full flex items-center gap-3 px-4 py-2 text-sm text-text-dark hover:bg-gray-100 transition-colors"
                      >
                        <Settings size={16} />
                        Settings
                      </button>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <LogOut size={16} />
                        Logout
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
          
          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
        
        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-white/20 pt-4 animate-slide-up">
            <div className="flex flex-col gap-3">
              <Link
                to="/dashboard"
                className="px-4 py-2 hover:bg-white/10 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Dashboard
              </Link>
              <Link
                to="/funds"
                className="px-4 py-2 hover:bg-white/10 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Funds
              </Link>
              <Link
                to="/referrals"
                className="px-4 py-2 hover:bg-white/10 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Referrals
              </Link>
              <Link
                to="/training"
                className="px-4 py-2 hover:bg-white/10 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Training
              </Link>
              {user?.isAdmin && (
                <Link
                  to="/admin"
                  className="px-4 py-2 hover:bg-white/10 rounded-lg transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Admin
                </Link>
              )}
              <div className="border-t border-white/20 pt-3 mt-2">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2 hover:bg-white/10 rounded-lg transition-colors text-left"
                >
                  <LogOut size={18} />
                  Logout
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;

