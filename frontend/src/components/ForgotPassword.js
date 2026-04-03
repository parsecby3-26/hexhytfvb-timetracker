import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import { Mail, ArrowLeft } from 'lucide-react';

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const response = await authAPI.requestPasswordReset(email);
      if (response.status === 200 || response.status === 201) {
        setSuccess(true);
        setEmail('');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send reset link. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div style={{ marginBottom: '16px' }}>
            <Mail size={32} color="var(--primary)" />
          </div>
          <h2 style={{ marginBottom: '8px' }}>Reset Password</h2>
          <div className="login-subtitle">Enter your email to receive a password reset link</div>
        </div>

        {error && (
          <div className="login-error" style={{ marginBottom: '20px' }}>
            {error}
          </div>
        )}

        {success ? (
          <div style={{
            padding: '16px',
            borderRadius: '8px',
            background: 'rgba(34, 197, 94, 0.1)',
            border: '1px solid rgba(34, 197, 94, 0.3)',
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            <div style={{ color: 'var(--success)', fontWeight: 500, marginBottom: '8px' }}>
              ✓ Reset link sent!
            </div>
            <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Check your email for a password reset link. If you don't see it, check your spam folder.
            </div>
            <button
              onClick={() => navigate('/login')}
              className="btn btn-primary btn-block"
              style={{ width: '100%' }}
            >
              Back to Login
            </button>
          </div>
        ) : (
          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={loading}
              style={{ width: '100%', marginTop: '10px' }}
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
        )}

        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <Link
            to="/login"
            style={{
              color: 'var(--primary)',
              fontWeight: 500,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            <ArrowLeft size={16} />
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
