import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { Eye, EyeOff, ShieldCheck, Check, X } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const { login, verifyFirstLogin, loading, error, clearError } = useAuthStore();
  const [step, setStep] = useState('LOGIN'); // 'LOGIN' or 'OTP'
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  
  const [otpData, setOtpData] = useState({
    otp: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  // Password Validation Check
  const isPasswordStrong = (pwd) => {
    return (
      pwd.length >= 8 &&
      /[A-Z]/.test(pwd) &&
      /\d/.test(pwd) &&
      /[!@#$%^&*(),.?":{}|<>]/.test(pwd)
    );
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    clearError();
    const result = await login(formData.email, formData.password);
    
    if (result === 'otp_required') {
      setStep('OTP');
    } else if (result === true) {
      navigate('/dashboard');
    }
  };

  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    clearError();
    setPasswordError('');
    
    if (otpData.newPassword !== otpData.confirmPassword) {
      setPasswordError("Passwords do not match");
      return;
    }
    
    if (!isPasswordStrong(otpData.newPassword)) {
      setPasswordError("Password does not meet strong security requirements.");
      return;
    }

    const success = await verifyFirstLogin(formData.email, otpData.otp, otpData.newPassword);
    if (success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card" style={{ maxWidth: step === 'OTP' ? '480px' : '420px', transition: 'all 0.3s' }}>
        <div className="login-header">
          <div className="login-logo">
            <svg width="180" height="44" viewBox="0 0 180 44" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginBottom: '16px' }}>
              <rect width="44" height="44" rx="10" fill="url(#grad)"/>
              <text x="22" y="30" textAnchor="middle" fill="white" fontSize="22" fontWeight="bold" fontFamily="monospace">hx</text>
              <text x="68" y="30" fill="#7c3aed" fontSize="18" fontWeight="700" fontFamily="'Inter', sans-serif">hexhytfvb</text>
              <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="44" y2="44" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#7c3aed"/>
                  <stop offset="1" stopColor="#4f46e5"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="login-subtitle">
            {step === 'LOGIN' ? 'Sign in to TimeTracker' : 'First-Time Security Setup'}
          </div>
        </div>

        {error && (
          <div className="login-error" style={{ marginBottom: '20px' }}>
            {error}
          </div>
        )}
        {passwordError && (
          <div className="login-error" style={{ marginBottom: '20px', backgroundColor: 'rgba(245, 158, 11, 0.1)', color: '#b45309', borderLeft: '4px solid #f59e0b' }}>
            {passwordError}
          </div>
        )}

        {step === 'LOGIN' ? (
          <form className="login-form" onSubmit={handleLoginSubmit}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  style={{ paddingRight: '48px' }}
                />
                <button
                  type="button"
                  className="btn-icon"
                  style={{
                    position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)'
                  }}
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <Link to="/forgot-password" style={{ fontSize: '12px', color: 'var(--primary)', marginTop: '8px', display: 'block', textDecoration: 'none' }}>
                Forgot password?
              </Link>
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading} style={{ width: '100%', marginTop: '10px' }}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        ) : (
          <form className="login-form" onSubmit={handleOtpSubmit}>
            <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: 'rgba(13, 148, 136, 0.1)', borderRadius: '8px', color: 'var(--primary-dark)', fontSize: '14px', display: 'flex', gap: '12px', alignItems: 'center' }}>
              <ShieldCheck size={24} />
              <div>We've sent a 6-digit verification code to <strong>{formData.email}</strong>. Please enter it below to set your permanent password.</div>
            </div>

            <div className="form-group">
              <label className="form-label">6-Digit OTP Code</label>
              <input
                type="text"
                className="form-input"
                placeholder="000000"
                maxLength={6}
                value={otpData.otp}
                onChange={(e) => setOtpData({ ...otpData, otp: e.target.value })}
                required
                style={{ fontSize: '24px', letterSpacing: '8px', textAlign: 'center', fontFamily: 'monospace' }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">New Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showNewPassword ? 'text' : 'password'}
                  className="form-input"
                  placeholder="Enter new password"
                  value={otpData.newPassword}
                  onChange={(e) => setOtpData({ ...otpData, newPassword: e.target.value })}
                  required
                  style={{ paddingRight: '48px' }}
                />
                <button
                  type="button"
                  className="btn-icon"
                  style={{
                    position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)'
                  }}
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <ul style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '12px', listStyle: 'none', padding: 0 }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '6px', color: otpData.newPassword.length >= 8 ? 'var(--success)' : 'inherit' }}>
                  {otpData.newPassword.length >= 8 ? <Check size={14} /> : <X size={14}/>} At least 8 characters
                </li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /[A-Z]/.test(otpData.newPassword) ? 'var(--success)' : 'inherit' }}>
                  {/[A-Z]/.test(otpData.newPassword) ? <Check size={14} /> : <X size={14}/>} One uppercase letter
                </li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /\d/.test(otpData.newPassword) ? 'var(--success)' : 'inherit' }}>
                  {/\d/.test(otpData.newPassword) ? <Check size={14} /> : <X size={14}/>} One number
                </li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /[!@#$%^&*(),.?":{}|<>]/.test(otpData.newPassword) ? 'var(--success)' : 'inherit' }}>
                  {/[!@#$%^&*(),.?":{}|<>]/.test(otpData.newPassword) ? <Check size={14} /> : <X size={14}/>} One special character
                </li>
              </ul>
            </div>

            <div className="form-group">
              <label className="form-label">Confirm New Password</label>
              <input
                type={showNewPassword ? 'text' : 'password'}
                className="form-input"
                placeholder="Repeat new password"
                value={otpData.confirmPassword}
                onChange={(e) => setOtpData({ ...otpData, confirmPassword: e.target.value })}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading || otpData.otp.length < 6} style={{ width: '100%', marginTop: '10px' }}>
              {loading ? 'Verifying...' : 'Set Password & Login'}
            </button>
          </form>
        )}

        {step === 'LOGIN' && (
          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <p className="text-secondary text-sm">
              Don't have an account?{' '}
              <Link to="/register" style={{ color: 'var(--primary)', fontWeight: 500 }}>
                Register here
              </Link>
              {' | '}
              <Link to="/support" style={{ color: 'var(--primary)', fontWeight: 500 }}>
                Support & Feedback
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;