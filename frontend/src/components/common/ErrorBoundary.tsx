import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorCount: number;
}

/**
 * ErrorBoundary component that catches JavaScript errors anywhere in the child
 * component tree, logs those errors, and displays a fallback UI.
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to console
    console.error('ErrorBoundary caught an error:', error);
    console.error('Error info:', errorInfo);

    // Update state with error info
    this.setState((prevState) => ({
      errorInfo,
      errorCount: prevState.errorCount + 1,
    }));

    // Call optional error callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // You can also log to an error reporting service here
    // e.g., logErrorToService(error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  handleReportBug = (): void => {
    const { error } = this.state;
    const errorInfo = this.state.errorInfo;
    const bugReport = `
## Error Report

**Error Message:**
${error?.message || 'Unknown error'}

**Stack Trace:**
\`\`\`
${error?.stack || 'No stack trace available'}
\`\`\`

**Component Stack:**
\`\`\`
${errorInfo?.componentStack || 'No component stack available'}
\`\`\`

**Browser:** ${navigator.userAgent}
**URL:** ${window.location.href}
**Time:** ${new Date().toISOString()}
    `.trim();

    // Copy to clipboard
    navigator.clipboard.writeText(bugReport).then(() => {
      alert('Error report copied to clipboard. Please paste it in your bug report.');
    }).catch(() => {
      // Fallback for browsers that don't support clipboard API
      console.log('Bug Report:', bugReport);
      alert('Please check the console for the error report.');
    });
  };

  render(): ReactNode {
    const { hasError, error, errorCount } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <div className="fixed inset-0 bg-gray-900 flex items-center justify-center z-50">
          <div className="max-w-2xl w-full mx-4 p-8 bg-gray-800 rounded-xl shadow-2xl border border-gray-700">
            {/* Header */}
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-red-500/20 rounded-full">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  Something went wrong
                </h1>
                <p className="text-gray-400 text-sm mt-1">
                  An unexpected error occurred in the application
                </p>
              </div>
            </div>

            {/* Error Details */}
            <div className="mb-6 p-4 bg-gray-900/50 rounded-lg border border-gray-700">
              <p className="text-red-400 font-mono text-sm break-all">
                {error?.message || 'Unknown error'}
              </p>
              {errorCount > 1 && (
                <p className="text-yellow-400 text-sm mt-2">
                  This error has occurred {errorCount} times
                </p>
              )}
            </div>

            {/* Stack Trace (Collapsible) */}
            {error?.stack && (
              <details className="mb-6">
                <summary className="cursor-pointer text-gray-400 hover:text-gray-300 text-sm flex items-center gap-2">
                  <Bug className="w-4 h-4" />
                  View technical details
                </summary>
                <pre className="mt-3 p-4 bg-gray-900/50 rounded-lg border border-gray-700 overflow-auto max-h-48 text-xs text-gray-500 font-mono">
                  {error.stack}
                </pre>
              </details>
            )}

            {/* Actions */}
            <div className="flex flex-wrap gap-3">
              <button
                onClick={this.handleRetry}
                className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors font-medium"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>
              <button
                onClick={this.handleGoHome}
                className="flex items-center gap-2 px-5 py-2.5 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors font-medium"
              >
                <Home className="w-4 h-4" />
                Go Home
              </button>
              <button
                onClick={this.handleReportBug}
                className="flex items-center gap-2 px-5 py-2.5 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors font-medium"
              >
                <Bug className="w-4 h-4" />
                Copy Bug Report
              </button>
            </div>

            {/* Help Text */}
            <p className="mt-6 text-gray-500 text-sm">
              If this problem persists, please try refreshing the page or contact support.
            </p>
          </div>
        </div>
      );
    }

    return children;
  }
}

/**
 * Higher-order component that wraps a component with an ErrorBoundary.
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) {
  const WithErrorBoundary = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  WithErrorBoundary.displayName = `WithErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return WithErrorBoundary;
}

/**
 * Hook to manually trigger error boundary from functional components.
 * Usage: const throwError = useErrorBoundary();
 *        throwError(new Error('Something went wrong'));
 */
export function useErrorBoundary() {
  const [, setError] = React.useState<Error | null>(null);

  const triggerError = (error: Error) => {
    setError(() => {
      throw error;
    });
  };

  return triggerError;
}

export default ErrorBoundary;
