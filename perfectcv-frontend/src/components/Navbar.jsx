import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { FaMoon, FaSun, FaRobot, FaSignOutAlt } from "react-icons/fa";

export default function Navbar({ user, onLogout, darkMode, toggleDarkMode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("hero");

  const navigate = useNavigate();
  const location = useLocation();

  const navLinks = [
    { label: "Home", id: "hero" },
    { label: "About", id: "about" },
    { label: "How It Works", id: "how-it-works" },
    { label: "Testimonials", id: "testimonials" },
    { label: "Contact", id: "contact" },
    { label: "FAQ", id: "faq" },
  ];

  // Scroll spy (only for unauthenticated users on home page)
  useEffect(() => {
    if (!user && location.pathname === "/") {
      const handleScroll = () => {
        const scrollPos = window.scrollY + 120;
        for (let i = navLinks.length - 1; i >= 0; i--) {
          const section = document.getElementById(navLinks[i].id);
          if (section && scrollPos >= section.offsetTop) {
            setActiveSection(navLinks[i].id);
            break;
          }
        }
      };
      window.addEventListener("scroll", handleScroll);
      return () => window.removeEventListener("scroll", handleScroll);
    }
  }, [user, location.pathname]);

  // Reset active section when not on homepage
  useEffect(() => {
    if (location.pathname !== "/") {
      setActiveSection("");
    }
  }, [location.pathname]);

  // Smooth scroll handler
  const handleScrollTo = (e, id) => {
    const section = document.getElementById(id);
    if (location.pathname === "/" && section) {
      e.preventDefault();
      window.scrollTo({
        top: section.offsetTop - 80,
        behavior: "smooth",
      });
      setMenuOpen(false);
    } else {
      e.preventDefault();
      // navigate to the homepage anchor without full reload
      navigate(`/#${id}`);
      setMenuOpen(false);
    }
  };

  return (
    <nav className="sticky top-0 z-50 bg-white dark:bg-gray-900 shadow-md transition-colors">
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-3 flex justify-between items-center">
        {/* Logo */}
        <Link
          to="/"
          className="text-2xl font-bold text-indigo-600 dark:text-indigo-400"
        >
          PerfectCV
        </Link>

        {/* Desktop View */}
  <div className="hidden md:flex items-center gap-6" role="menubar" aria-label="Main navigation">
          {!user ? (
            <>
              {navLinks.map((link) => (
                <button
                  key={link.id}
                  onClick={(e) => handleScrollTo(e, link.id)}
                  className={`relative px-2 py-1 font-medium transition duration-300 group ${
                    location.pathname === "/" && activeSection === link.id
                      ? "text-indigo-600 dark:text-indigo-400"
                      : "text-gray-700 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400"
                  }`}
                >
                  {link.label}
                  <span
                    className={`absolute left-0 -bottom-1 h-0.5 bg-indigo-600 dark:bg-indigo-400 transition-all duration-500 ease-in-out transform origin-left ${
                      location.pathname === "/" && activeSection === link.id
                        ? "scale-x-100 opacity-100"
                        : "group-hover:scale-x-100 group-hover:opacity-100 scale-x-0 opacity-0"
                    }`}
                  ></span>
                </button>
              ))}

              <Link
                to="/login"
                className="px-4 py-1 border border-indigo-600 text-indigo-600 rounded hover:bg-indigo-50 dark:hover:bg-indigo-800 dark:hover:text-white transition"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="px-4 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
              >
                Sign Up
              </Link>

              {/* Dark/Light mode */}
              <button
                onClick={toggleDarkMode}
                className="text-gray-700 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400 transition"
                title="Toggle Dark/Light Mode"
              >
                {darkMode ? <FaSun /> : <FaMoon />}
              </button>
            </>
          ) : (
            <>
              <span className="text-gray-700 dark:text-gray-200 font-medium">
                Hello, {user?.username}
              </span>
              {location.pathname === '/chatbot' ? (
                <Link
                  to="/dashboard"
                  className="flex items-center gap-1 text-gray-700 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400 transition"
                >
                  <FaRobot /> Dashboard
                </Link>
              ) : (
                <Link
                  to="/chatbot"
                  className="flex items-center gap-1 text-gray-700 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400 transition"
                >
                  <FaRobot /> Chatbot
                </Link>
              )}
              <button
                onClick={() => { onLogout && onLogout(); navigate('/'); }}
                className="flex items-center gap-1 bg-red-600 text-white px-4 py-1 rounded hover:bg-red-700 transition"
              >
                <FaSignOutAlt /> Logout
              </button>
              <button
                onClick={toggleDarkMode}
                className="text-gray-700 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400 transition"
                title="Toggle Dark/Light Mode"
              >
                {darkMode ? <FaSun /> : <FaMoon />}
              </button>
            </>
          )}
        </div>

        {/* Mobile View */}
        <div className="md:hidden flex items-center gap-3">
          <button
            onClick={toggleDarkMode}
            className="text-gray-700 dark:text-gray-200 focus:outline-none"
            title="Toggle Dark/Light Mode"
          >
            {darkMode ? <FaSun /> : <FaMoon />}
          </button>

          {user && (
            <button
              onClick={onLogout}
              className="text-red-600 focus:outline-none"
              title="Logout"
            >
              <FaSignOutAlt />
            </button>
          )}

          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="text-gray-700 dark:text-gray-200 focus:outline-none"
            aria-controls="mobile-menu"
            aria-expanded={menuOpen}
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {menuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Dropdown */}
      {menuOpen && (
        <div id="mobile-menu" className="md:hidden bg-white dark:bg-gray-900 shadow-md transition-colors" role="menu">
          {!user ? (
            <>
              {navLinks.map((link) => (
                <button
                  key={link.id}
                  onClick={(e) => handleScrollTo(e, link.id)}
                  className={`block w-full text-left px-4 py-2 transition ${
                    activeSection === link.id
                      ? "text-indigo-600 dark:text-indigo-400 font-semibold"
                      : "text-gray-700 dark:text-gray-200 hover:bg-indigo-50 dark:hover:bg-gray-800"
                  }`}
                >
                  {link.label}
                </button>
              ))}
              <Link to="/login" onClick={() => setMenuOpen(false)} className="block px-4 py-2 text-indigo-600 border border-indigo-600 rounded hover:bg-indigo-50 dark:hover:bg-indigo-800 dark:hover:text-white transition">
                Login
              </Link>
              <Link to="/register" onClick={() => setMenuOpen(false)} className="block px-4 py-2 mt-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition">
                Sign Up
              </Link>
            </>
          ) : (
            <>
              <span className="block px-4 py-2 text-gray-700 dark:text-gray-200 font-medium">
                Hello, <Link to="/dashboard" className="font-semibold hover:underline">{user?.full_name || user?.username}</Link>
              </span>
              {location.pathname === '/chatbot' ? (
                <Link to="/dashboard" onClick={() => setMenuOpen(false)} className="flex items-center gap-1 px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-indigo-50 dark:hover:bg-gray-800 transition">
                  <FaRobot /> Dashboard
                </Link>
              ) : (
                <Link to="/chatbot" onClick={() => setMenuOpen(false)} className="flex items-center gap-1 px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-indigo-50 dark:hover:bg-gray-800 transition">
                  <FaRobot /> Chatbot
                </Link>
              )}
              <button
                onClick={() => {
                  onLogout && onLogout();
                  setMenuOpen(false);
                }}
                className="flex items-center gap-1 w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900 transition"
              >
                <FaSignOutAlt /> Logout
              </button>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
