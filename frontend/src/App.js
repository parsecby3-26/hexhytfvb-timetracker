import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import useAuthStore from './stores/authStore';
import Login from './components/Login';
import Register from './components/Register';
import ForgotPassword from './components/ForgotPassword';
import ResetPassword from './components/ResetPassword';
import VerifyEmail from './components/VerifyEmail';
import Dashboard from './components/Dashboard';
import Timesheets from './components/Timesheets';
import Approvals from './components/Approvals';
import Projects from './components/Projects';
import Reports from './components/Reports';
import UserProvisioning from './components/UserProvisioning';
import Layout from './components/Layout';
import Support from './components/Support';
import ErrorBoundary from './components/ErrorBoundary';

const pageVariants = {
  initial: { opacity: 0, y: 10 },
  in: { opacity: 1, y: 0 },
  out: { opacity: 0, y: -10 }
};

const pageTransition = {
  type: "tween",
  ease: "anticipate",
  duration: 0.3
};

const AnimatedPage = ({ children }) => {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
      style={{ width: '100%', height: '100%' }}
    >
      {children}
    </motion.div>
  );
};

const AnimatedRoutes = ({ isAuthenticated }) => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <AnimatedPage><Login /></AnimatedPage>
            )
          }
        />
        <Route path="/register" element={<AnimatedPage><Register /></AnimatedPage>} />
        <Route path="/verify-email" element={<AnimatedPage><VerifyEmail /></AnimatedPage>} />
        <Route path="/forgot-password" element={<AnimatedPage><ForgotPassword /></AnimatedPage>} />
        <Route path="/reset-password" element={<AnimatedPage><ResetPassword /></AnimatedPage>} />
        <Route path="/support" element={<AnimatedPage><Support /></AnimatedPage>} />
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <Layout>
                <AnimatePresence mode="wait">
                  <Routes location={location} key={location.pathname}>
                    <Route path="/dashboard" element={<ErrorBoundary><AnimatedPage><Dashboard /></AnimatedPage></ErrorBoundary>} />
                    <Route path="/timesheets" element={<ErrorBoundary><AnimatedPage><Timesheets /></AnimatedPage></ErrorBoundary>} />
                    <Route path="/approvals" element={<ErrorBoundary><AnimatedPage><Approvals /></AnimatedPage></ErrorBoundary>} />
                    <Route path="/projects" element={<ErrorBoundary><AnimatedPage><Projects /></AnimatedPage></ErrorBoundary>} />
                    <Route path="/reports" element={<ErrorBoundary><AnimatedPage><Reports /></AnimatedPage></ErrorBoundary>} />
                    <Route path="/users" element={<ErrorBoundary><AnimatedPage><UserProvisioning /></AnimatedPage></ErrorBoundary>} />
                  </Routes>
                </AnimatePresence>
              </Layout>
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
      </Routes>
    </AnimatePresence>
  );
};

function App() {
  const { isAuthenticated, fetchCurrentUser, token } = useAuthStore();
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    const init = async () => {
      if (token) {
        await fetchCurrentUser();
      }
      setInitializing(false);
    };
    init();
  }, [token, fetchCurrentUser]);

  if (initializing) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <AnimatedRoutes isAuthenticated={isAuthenticated} />
    </BrowserRouter>
  );
}

export default App;



