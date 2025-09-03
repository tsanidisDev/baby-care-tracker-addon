#!/usr/bin/env python3
"""
Baby Care Tracker Add-on
Complete baby care tracking solution with persistent data and analytics
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime

print("=== Baby Care Tracker Python Application Starting ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Environment variables:")
for key, value in os.environ.items():
    if 'MQTT' in key or 'DATABASE' in key or 'LOG' in key:
        print(f"  {key}={value}")

try:
    print("Importing Flask modules...")
    from flask import Flask, render_template, request, jsonify, send_file
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit
    print("Flask modules imported successfully")
except ImportError as e:
    print(f"ERROR importing Flask modules: {e}")
    sys.exit(1)

try:
    print("Importing application modules...")
    from database import Database
    from mqtt_client import MQTTClient
    from analytics import Analytics
    from device_manager import DeviceManager
    from utils import setup_logging, load_config
    print("Application modules imported successfully")
except ImportError as e:
    print(f"ERROR importing application modules: {e}")
    print("Checking if modules exist...")
    import glob
    py_files = glob.glob("*.py")
    print(f"Python files in current directory: {py_files}")
    sys.exit(1)

# Configuration
print("Loading configuration...")
CONFIG = load_config()
print(f"Configuration loaded: {CONFIG}")

print("Setting up logging...")
logger = setup_logging(CONFIG.get('log_level', 'info'))
logger.info("=== Baby Care Tracker Application Starting ===")
logger.info(f"Configuration: {CONFIG}")

# Initialize Flask app
print("Initializing Flask application...")
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.config['SECRET_KEY'] = 'baby-care-tracker-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
print("Flask application initialized")

# Global components
db = None
mqtt_client = None
analytics = None
device_manager = None

def initialize_components():
    """Initialize all application components"""
    global db, mqtt_client, analytics, device_manager
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        print("Initializing database...")
        db = Database(CONFIG)
        logger.info("Database initialized successfully")
        print("Database initialized successfully")
        
        # Initialize MQTT client
        logger.info("Initializing MQTT client...")
        mqtt_client = MQTTClient(CONFIG, on_device_event)
        
        # Initialize analytics
        logger.info("Initializing analytics...")
        analytics = Analytics(db)
        
        # Initialize device manager
        logger.info("Initializing device manager...")
        device_manager = DeviceManager(CONFIG)
        
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        sys.exit(1)

def on_device_event(device_id, event_type, data):
    """Handle device events from MQTT"""
    try:
        # Check if this device is mapped to a baby care action
        mapping = device_manager.get_mapping(device_id, event_type)
        if mapping:
            # Log the baby care event
            event_id = db.add_event(
                event_type=mapping['baby_care_action'],
                device_source=device_id,
                trigger_data=data
            )
            
            # Emit real-time update to web clients
            socketio.emit('new_event', {
                'id': event_id,
                'type': mapping['baby_care_action'],
                'timestamp': datetime.now().isoformat(),
                'device': device_id
            })
            
            logger.info(f"Logged baby care event: {mapping['baby_care_action']} from {device_id}")
            
    except Exception as e:
        logger.error(f"Error handling device event: {e}")

# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def dashboard():
    """Main dashboard"""
    try:
        recent_events = db.get_recent_events(limit=10)
        daily_stats = analytics.get_daily_stats()
        device_mappings = device_manager.get_all_mappings()
        
        return render_template('dashboard.html',
                             recent_events=recent_events,
                             daily_stats=daily_stats,
                             device_mappings=device_mappings)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/analytics')
def analytics_page():
    """Analytics and reports page"""
    try:
        # Get analytics data
        feeding_stats = analytics.get_feeding_analytics()
        sleep_stats = analytics.get_sleep_analytics()
        diaper_stats = analytics.get_diaper_analytics()
        growth_data = analytics.get_growth_trends()
        
        return render_template('analytics.html',
                             feeding_stats=feeding_stats,
                             sleep_stats=sleep_stats,
                             diaper_stats=diaper_stats,
                             growth_data=growth_data)
    except Exception as e:
        logger.error(f"Error loading analytics: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/devices')
def devices_page():
    """Device configuration page"""
    try:
        available_devices = device_manager.discover_devices()
        current_mappings = device_manager.get_all_mappings()
        
        return render_template('devices.html',
                             available_devices=available_devices,
                             current_mappings=current_mappings)
    except Exception as e:
        logger.error(f"Error loading devices page: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/settings')
def settings_page():
    """Settings and configuration page"""
    try:
        current_config = CONFIG
        system_info = {
            'version': '2.0.0',
            'database_type': CONFIG.get('database_type', 'sqlite'),
            'mqtt_connected': mqtt_client.is_connected() if mqtt_client else False,
            'total_events': db.get_total_events_count() if db else 0
        }
        
        return render_template('settings.html',
                             config=current_config,
                             system_info=system_info)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return render_template('error.html', error=str(e)), 500

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/events', methods=['GET'])
def api_get_events():
    """Get events with optional filtering"""
    try:
        event_type = request.args.get('type')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        events = db.get_events(event_type=event_type, limit=limit, offset=offset)
        return jsonify({'success': True, 'events': events})
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events', methods=['POST'])
def api_add_event():
    """Add a new baby care event"""
    try:
        data = request.get_json()
        event_id = db.add_event(
            event_type=data['type'],
            duration=data.get('duration'),
            notes=data.get('notes', ''),
            device_source=data.get('device_source', 'manual')
        )
        
        # Emit real-time update
        socketio.emit('new_event', {
            'id': event_id,
            'type': data['type'],
            'timestamp': datetime.now().isoformat(),
            'device': data.get('device_source', 'manual')
        })
        
        return jsonify({'success': True, 'event_id': event_id})
        
    except Exception as e:
        logger.error(f"Error adding event: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device-mappings', methods=['GET'])
def api_get_device_mappings():
    """Get all device mappings"""
    try:
        mappings = device_manager.get_all_mappings()
        return jsonify({'success': True, 'mappings': mappings})
        
    except Exception as e:
        logger.error(f"Error getting device mappings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device-mappings', methods=['POST'])
def api_add_device_mapping():
    """Add a new device mapping"""
    try:
        data = request.get_json()
        mapping_id = device_manager.add_mapping(
            device_id=data['device_id'],
            trigger_type=data['trigger_type'],
            baby_care_action=data['baby_care_action']
        )
        
        return jsonify({'success': True, 'mapping_id': mapping_id})
        
    except Exception as e:
        logger.error(f"Error adding device mapping: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device-mappings/<int:mapping_id>', methods=['DELETE'])
def api_delete_device_mapping(mapping_id):
    """Delete a device mapping"""
    try:
        device_manager.delete_mapping(mapping_id)
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error deleting device mapping: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/feeding')
def api_feeding_analytics():
    """Get feeding analytics"""
    try:
        stats = analytics.get_feeding_analytics()
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        logger.error(f"Error getting feeding analytics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/sleep')
def api_sleep_analytics():
    """Get sleep analytics"""
    try:
        stats = analytics.get_sleep_analytics()
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        logger.error(f"Error getting sleep analytics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/<format>')
def api_export_data(format):
    """Export data in various formats"""
    try:
        if format not in ['csv', 'json', 'pdf']:
            return jsonify({'success': False, 'error': 'Invalid format'}), 400
            
        file_path = analytics.export_data(format)
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected' if db and db.is_healthy() else 'disconnected',
            'mqtt': 'connected' if mqtt_client and mqtt_client.is_connected() else 'disconnected',
            'version': '2.0.0'
        }
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# ============================================================================
# SOCKETIO EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'status': 'Connected to Baby Care Tracker'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('get_live_stats')
def handle_get_live_stats():
    """Send live statistics to client"""
    try:
        stats = analytics.get_live_stats()
        emit('live_stats', stats)
    except Exception as e:
        logger.error(f"Error getting live stats: {e}")
        emit('error', {'message': str(e)})

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

def background_tasks():
    """Run background tasks"""
    while True:
        try:
            # Cleanup old data if configured
            if CONFIG.get('auto_cleanup', False):
                db.cleanup_old_data(days=CONFIG.get('cleanup_days', 365))
            
            # Generate daily reports if enabled
            if CONFIG.get('daily_reports', False):
                analytics.generate_daily_report()
            
            # Sleep for an hour
            time.sleep(3600)
            
        except Exception as e:
            logger.error(f"Background task error: {e}")
            time.sleep(60)  # Wait a minute before retrying

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    print("=== Main function starting ===")
    logger.info("Starting Baby Care Tracker Add-on v2.0.0")
    print("Starting Baby Care Tracker Add-on v2.0.0")
    
    try:
        # Initialize all components
        print("Initializing components...")
        logger.info("Initializing components...")
        initialize_components()
        print("Components initialized successfully")
        logger.info("Components initialized successfully")
        
        # Start background tasks thread
        print("Starting background tasks thread...")
        logger.info("Starting background tasks thread...")
        background_thread = threading.Thread(target=background_tasks, daemon=True)
        background_thread.start()
        print("Background tasks thread started")
        logger.info("Background tasks thread started")
        
        # Start the web server
        print("Starting web server on port 8099...")
        logger.info("Starting web server on port 8099...")
        print(f"Debug mode: {CONFIG.get('debug', False)}")
        print("Web server is about to start...")
        
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=8099, 
                    debug=CONFIG.get('debug', False),
                    allow_unsafe_werkzeug=True)
                    
    except Exception as e:
        print(f"CRITICAL ERROR in main(): {e}")
        logger.error(f"CRITICAL ERROR in main(): {e}")
        import traceback
        traceback.print_exc()
        print("Application failed to start")
        sys.exit(1)

if __name__ == '__main__':
    print("=== __main__ block executing ===")
    main()
