import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="error-boundary-fallback" style={{
          padding: '24px',
          textAlign: 'center',
          background: '#fff1f2',
          border: '1px solid #fecaca',
          borderRadius: '12px',
          margin: '20px'
        }}>
          <h3 style={{ color: '#b91c1c', marginBottom: '8px' }}>Something went wrong</h3>
          <p style={{ color: '#7f1d1d', fontSize: '14px' }}>
            This module failed to load, but the rest of the application is still working.
          </p>
          <button 
            className="btn btn-secondary" 
            style={{ marginTop: '16px' }}
            onClick={() => this.setState({ hasError: false })}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
