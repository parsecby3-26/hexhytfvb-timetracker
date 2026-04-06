import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { authAPI } from '../services/api';

const VerifyEmail = () => {
    const [status, setStatus] = useState('verifying'); // verifying, success, error
    const [message, setMessage] = useState('Verifying your email address...');
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        const verify = async () => {
            const query = new URLSearchParams(location.search);
            const token = query.get('token');

            if (!token) {
                setStatus('error');
                setMessage('Invalid or missing verification token.');
                return;
            }

            try {
                await authAPI.verifyEmail(token);
                setStatus('success');
                setMessage('Your email has been successfully verified! You can now log in.');
                
                // Auto redirect to login after 5 seconds
                setTimeout(() => {
                    navigate('/');
                }, 5000);
            } catch (error) {
                setStatus('error');
                setMessage(error.response?.data?.detail || 'Verification failed. The link may be expired or invalid.');
            }
        };

        verify();
    }, [location, navigate]);

    return (
        <div className="auth-container">
            <motion.div 
                className="auth-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <div className="auth-header">
                    <div className="auth-logo">
                        <span className="logo-icon">✓</span>
                    </div>
                    <h2>Email Verification</h2>
                </div>

                <div className={`status-message ${status}`} style={{
                    padding: '20px',
                    borderRadius: '8px',
                    textAlign: 'center',
                    marginTop: '20px',
                    backgroundColor: status === 'success' ? '#ecfdf5' : status === 'error' ? '#fef2f2' : '#f0f9ff',
                    color: status === 'success' ? '#065f46' : status === 'error' ? '#991b1b' : '#075985',
                    border: `1px solid ${status === 'success' ? '#10b981' : status === 'error' ? '#ef4444' : '#0ea5e9'}`
                }}>
                    {status === 'verifying' && <div className="spinner-small" style={{ margin: '0 auto 15px' }}></div>}
                    <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>{message}</p>
                </div>

                <div style={{ marginTop: '30px', textAlign: 'center' }}>
                    <Link to="/" className="btn-primary" style={{ textDecoration: 'none', display: 'inline-block' }}>
                        Go to Login
                    </Link>
                </div>

                {status === 'success' && (
                    <p style={{ marginTop: '20px', fontSize: '14px', color: '#64748b', textAlign: 'center' }}>
                        Redirecting to login in 5 seconds...
                    </p>
                )}
            </motion.div>
        </div>
    );
};

export default VerifyEmail;
