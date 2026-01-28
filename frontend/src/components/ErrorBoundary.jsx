import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.state = { hasError: true, error, errorInfo };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-8">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
            <h1 className="text-3xl font-bold text-red-600 mb-4">Something went wrong</h1>
            <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
              <h2 className="font-semibold text-red-800 mb-2">Error:</h2>
              <pre className="text-sm text-red-700 whitespace-pre-wrap overflow-auto">
                {this.state.error?.toString()}
              </pre>
            </div>
            {this.state.errorInfo && (
              <div className="bg-gray-50 border border-gray-200 rounded p-4">
                <h2 className="font-semibold text-gray-800 mb-2">Component Stack:</h2>
                <pre className="text-xs text-gray-600 whitespace-pre-wrap overflow-auto max-h-64">
                  {this.state.errorInfo.componentStack}
                </pre>
              </div>
            )}
            <button
              onClick={() => window.location.reload()}
              className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
