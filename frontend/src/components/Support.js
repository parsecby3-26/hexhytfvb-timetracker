import React, { useState } from 'react';
import { supportAPI } from '../services/api';
import useAuthStore from '../stores/authStore';
import { MessageSquare, Send, CheckCircle2, AlertCircle } from 'lucide-react';

const Support = () => {
    const { user, isAuthenticated } = useAuthStore();
    const [formData, setFormData] = useState({
        name: user?.name || '',
        email: user?.email || '',
        category: 'Feedback',
        message: ''
    });
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState({ type: '', message: '' });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setStatus({ type: '', message: '' });

        try {
            await supportAPI.submitFeedback(formData);
            setStatus({ type: 'success', message: 'Thank you! Your feedback has been sent successfully.' });
            setFormData({ 
                name: user?.name || '', 
                email: user?.email || '', 
                category: 'Feedback', 
                message: '' 
            });
        } catch (error) {
            setStatus({ 
                type: 'error', 
                message: error.response?.data?.message || 'Failed to send feedback. Please try again later.' 
            });
        } finally {
            setLoading(false);
        }
    };

    const renderForm = () => (
        <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <div className="card-body">
                {status.message && (
                    <div className={`login-error ${status.type === 'success' ? 'success-message' : ''}`} 
                         style={{ 
                             backgroundColor: status.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                             color: status.type === 'success' ? '#047857' : '#b91c1c',
                             marginBottom: '24px',
                             display: 'flex',
                             alignItems: 'center',
                             gap: '10px'
                         }}>
                        {status.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                        {status.message}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Full Name</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                required
                                className="form-input"
                                placeholder="Your Name"
                            />
                        </div>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Email Address</label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                required
                                className="form-input"
                                placeholder="name@example.com"
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Inquiry Type</label>
                        <select
                            name="category"
                            value={formData.category}
                            onChange={handleChange}
                            className="form-select"
                        >
                            <option value="Feedback">General Feedback</option>
                            <option value="Bug Report">Bug Report</option>
                            <option value="Feature Request">Feature Request</option>
                            <option value="Support">Technical Support</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Message</label>
                        <textarea
                            name="message"
                            value={formData.message}
                            onChange={handleChange}
                            required
                            rows="5"
                            className="form-input"
                            style={{ resize: 'none' }}
                            placeholder="How can we help you?"
                        ></textarea>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn btn-primary"
                        style={{ width: '100%', justifyContent: 'center', padding: '12px' }}
                    >
                        {loading ? (
                            <>
                                <span className="spinner" style={{ width: '18px', height: '18px', borderThickness: '2px' }}></span>
                                <span style={{ marginLeft: '10px' }}>Sending...</span>
                            </>
                        ) : (
                            <>
                                <Send size={18} />
                                <span>Submit Feedback</span>
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );

    if (!isAuthenticated) {
        return (
            <div className="login-container" style={{ padding: '20px' }}>
                <div className="login-card" style={{ maxWidth: '600px', padding: '40px' }}>
                    <div className="login-header">
                        <div className="login-logo">
                            <MessageSquare size={40} style={{ color: 'var(--primary)', marginBottom: '16px' }} />
                        </div>
                        <h2 style={{ fontSize: '24px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '8px' }}>Support & Feedback</h2>
                        <p style={{ color: 'var(--text-secondary)' }}>We'd love to hear from you. Please fill out the form below.</p>
                    </div>
                    {renderForm()}
                    <div style={{ marginTop: '24px', textAlign: 'center' }}>
                        <a href="/" style={{ color: 'var(--primary)', fontWeight: '500', textDecoration: 'none', fontSize: '14px' }}>
                            Back to Sign In
                        </a>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="page-content">
            <header className="header" style={{ marginBottom: '24px', borderRadius: '12px' }}>
                <div className="header-title">
                    <h2>Support & Feedback</h2>
                    <p>Contact our team for any assistance or feedback</p>
                </div>
            </header>
            {renderForm()}
        </div>
    );
};

export default Support;
