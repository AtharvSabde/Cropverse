"""
CropVerse Main Application
==========================
Entry point for Firebase Cloud Functions.

This module defines:
- Flask app with all API routes mounted
- CORS configuration for frontend communication
- Scheduled Cloud Functions (daily analytics job)
- Global error handlers
- Health check endpoint

Functions:
- app() - Main Flask application (handles all HTTP requests)
- daily_analytics_job() - Scheduled function (runs daily at midnight)
"""

import os
import logging

from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from firebase_admin import initialize_app, firestore
from firebase_functions import https_fn, scheduler_fn

from utils.logger import setup_logger, get_api_logger
from utils.decorators import log_execution_time



from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# # Initialize Firebase Admin SDK
# initialize_app()
# db = firestore.client()



# Initialize Firebase Admin SDK
import os
from firebase_admin import credentials


# Setup loggers
logger = setup_logger(__name__)
api_logger = get_api_logger()


# Check if running locally or on Cloud Functions
if os.path.exists('serviceAccountKey.json'):
    # Local development - use service account key
    cred = credentials.Certificate('serviceAccountKey.json')
    initialize_app(cred)
    logger.info("Firebase initialized with service account key (local)")
else:
    # Cloud Functions - use default credentials
    initialize_app()
    logger.info("Firebase initialized with default credentials (cloud)")

db = firestore.client()


# Create Flask app
flask_app = Flask(__name__)

# Configure CORS (allow requests from Firebase Hosting and localhost)
CORS(flask_app, resources={
    r"/api/*": {
        "origins": [
            "https://cropverse-*.web.app",
            "https://cropverse-*.firebaseapp.com",
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})


# ============================================================================
# REGISTER ROUTES
# ============================================================================

def register_routes():
    """Register all API route blueprints."""
    from routes.arduino import arduino_bp
    from routes.dashboard import dashboard_bp
    from routes.analytics import analytics_bp
    from routes.chatbot import chatbot_bp
    from routes.settings import settings_bp
    from routes.auth import auth_bp
    
    flask_app.register_blueprint(arduino_bp, url_prefix='/api/arduino')
    flask_app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    flask_app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    flask_app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
    flask_app.register_blueprint(settings_bp, url_prefix='/api/settings')
    flask_app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    logger.info("All routes registered successfully")


register_routes()


# ============================================================================
# HEALTH CHECK & ROOT ENDPOINT
# ============================================================================

@flask_app.route('/')
def root():
    """Root endpoint - API info."""
    return jsonify({
        'service': 'CropVerse API',
        'version': '1.0.0',
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'health': '/health',
            'arduino': '/api/arduino/*',
            'dashboard': '/api/dashboard/*',
            'analytics': '/api/analytics/*',
            'chatbot': '/api/chatbot/*',
            'settings': '/api/settings/*',
            'auth': '/api/auth/*'
        }
    }), 200


@flask_app.route('/health')
@log_execution_time
def health_check():
    """
    Health check endpoint.
    
    Verifies:
    - Flask app is running
    - Firestore connection is working
    - Environment variables are loaded
    
    Returns:
        JSON response with health status
    """
    try:
        # Test Firestore connection
        db.collection('settings').limit(1).get()
        
        # Check critical environment variables
        required_env_vars = ['FIREBASE_PROJECT_ID', 'CLAUDE_API_KEY']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")
            return jsonify({
                'status': 'degraded',
                'message': f'Missing environment variables: {", ".join(missing_vars)}',
                'timestamp': datetime.utcnow().isoformat(),
                'firestore': 'connected',
                'flask': 'running'
            }), 200
        
        logger.info("Health check passed")
        return jsonify({
            'status': 'healthy',
            'message': 'All systems operational',
            'timestamp': datetime.utcnow().isoformat(),
            'firestore': 'connected',
            'flask': 'running',
            'environment': 'configured'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


# ============================================================================
# GLOBAL ERROR HANDLERS
# ============================================================================

@flask_app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    api_logger.warning(f"Bad request: {str(error)}")
    return jsonify({
        'error': 'Bad Request',
        'message': str(error),
        'status_code': 400
    }), 400


@flask_app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    api_logger.warning(f"Unauthorized access attempt: {str(error)}")
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required',
        'status_code': 401
    }), 401


@flask_app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    api_logger.warning(f"Forbidden access attempt: {str(error)}")
    return jsonify({
        'error': 'Forbidden',
        'message': 'Insufficient permissions',
        'status_code': 403
    }), 403


@flask_app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    api_logger.info(f"Resource not found: {request.path}")
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }), 404


@flask_app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle 429 Too Many Requests errors."""
    api_logger.warning(f"Rate limit exceeded: {request.remote_addr}")
    return jsonify({
        'error': 'Too Many Requests',
        'message': 'Rate limit exceeded. Please try again later.',
        'status_code': 429
    }), 429


@flask_app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    api_logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred. Please try again later.',
        'status_code': 500
    }), 500


@flask_app.errorhandler(Exception)
def handle_exception(error):
    """Handle all uncaught exceptions."""
    api_logger.error(f"Uncaught exception: {str(error)}", exc_info=True)
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500


# ============================================================================
# REQUEST/RESPONSE LOGGING
# ============================================================================

@flask_app.before_request
def log_request():
    """Log all incoming requests."""
    api_logger.info(
        f"Request: {request.method} {request.path} "
        f"from {request.remote_addr}"
    )


@flask_app.after_request
def log_response(response):
    """Log all outgoing responses."""
    api_logger.info(
        f"Response: {request.method} {request.path} "
        f"-> {response.status_code}"
    )
    return response


# ============================================================================
# FIREBASE CLOUD FUNCTIONS EXPORTS
# ============================================================================

@https_fn.on_request(
    timeout_sec=300,
    memory=512,
    min_instances=0,
    max_instances=10
)
def app(req: https_fn.Request) -> https_fn.Response:
    """
    Main HTTP Cloud Function.
    
    This function handles all API requests by routing them through Flask.
    Firebase automatically calls this function for any HTTP request.
    
    Configuration:
    - Timeout: 300 seconds (5 minutes)
    - Memory: 512 MB
    - Min instances: 0 (scales to zero when not in use)
    - Max instances: 10 (auto-scales under load)
    
    Args:
        req: Firebase HTTP request object
        
    Returns:
        Firebase HTTP response object
    """
    with flask_app.request_context(req.environ):
        return flask_app.full_dispatch_request()


@scheduler_fn.on_schedule(
    schedule="0 0 * * *",  # Every day at midnight UTC
    timezone="UTC",
    memory=256,
    timeout_sec=540
)
def daily_analytics_job(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled Cloud Function - Daily Analytics Summary.
    
    This function runs automatically every day at midnight UTC.
    It calculates analytics for the previous day and stores the summary
    in the analytics_summary collection.
    
    What it does:
    1. Gets yesterday's date
    2. Queries all sensor readings from yesterday
    3. Calculates aggregated statistics (avg, min, max)
    4. Counts alerts for the day
    5. Saves summary to Firestore
    
    Schedule: Daily at 00:00 UTC (5:30 AM IST)
    Memory: 256 MB
    Timeout: 540 seconds (9 minutes)
    
    Args:
        event: Scheduled event object (contains schedule_time)
    """
    try:
        from services.analytics_service import calculate_daily_summary
        
        # Calculate for yesterday (since job runs at midnight)
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        
        logger.info(f"Starting daily analytics job for date: {yesterday}")
        
        # Calculate and save summary
        summary = calculate_daily_summary(yesterday)
        
        if summary:
            logger.info(
                f"Daily analytics job completed successfully. "
                f"Summary: {summary.get('alert_count', 0)} alerts, "
                f"avg temp: {summary.get('avg_temperature', 0):.1f}°C"
            )
        else:
            logger.warning(f"No data available for {yesterday}")
            
    except Exception as e:
        logger.error(
            f"Daily analytics job failed for {yesterday}: {str(e)}", 
            exc_info=True
        )
        # Don't re-raise - we don't want the job to be marked as failed
        # It will retry automatically next day


# ============================================================================
# DEVELOPMENT SERVER (for local testing only)
# ============================================================================

if __name__ == '__main__':
    """
    Local development server.
    
    This runs only when you execute 'python main.py' directly.
    Firebase Cloud Functions don't use this - they call the app() function.
    
    Usage:
        python main.py
        
    Then access: http://localhost:8080
    """
    print("=" * 60)
    print("🌱 CropVerse API - Development Server")
    print("=" * 60)
    print("📍 Running at: http://localhost:8080")
    print("📍 Health check: http://localhost:8080/health")
    print("📍 API docs: http://localhost:8080/")
    print("=" * 60)
    
    flask_app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )