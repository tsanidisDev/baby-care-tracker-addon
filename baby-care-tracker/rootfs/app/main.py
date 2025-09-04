#!/usr/bin/env python3
"""
Baby Care Tracker Add-on
Complete baby care tracking solution with persistent data and analytics
"""

# Monkey patch early to avoid warnings
from gevent import monkey
monkey.patch_all()

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
    import json
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
    from migrations import run_migrations
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

# Application version
APP_VERSION = "1.0.10"
print(f"Baby Care Tracker Add-on version: {APP_VERSION}")

print("Setting up logging...")
logger = setup_logging(CONFIG.get('log_level', 'info'))
logger.info("=== Baby Care Tracker Application Starting ===")
logger.info(f"Version: {APP_VERSION}")
logger.info(f"Configuration: {CONFIG}")

# Initialize Flask app
print("Initializing Flask application...")
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.config['SECRET_KEY'] = 'baby-care-tracker-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Add custom Jinja2 filters
@app.template_filter('tojsonfilter')
def to_json_filter(obj):
    """Convert Python object to JSON for use in templates"""
    return json.dumps(obj, default=str)

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
        # Run database migrations if needed
        logger.info("Checking for database migrations...")
        print("Checking for database migrations...")
        db_path = CONFIG.get('database_path', '/data/baby_care.db')
        try:
            run_migrations(db_path, APP_VERSION)
            logger.info("Database migrations completed")
            print("Database migrations completed")
        except Exception as e:
            logger.error(f"Database migration failed: {e}", exc_info=True)
            print(f"Database migration failed: {e}")
            # Continue anyway
        
        # Initialize database
        logger.info("Initializing database...")
        print("Initializing database...")
        try:
            db = Database(CONFIG)
            logger.info("Database initialized successfully")
            print("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            print(f"Database initialization failed: {e}")
            raise
        
        # Initialize analytics
        logger.info("Initializing analytics...")
        print("Initializing analytics...")
        try:
            analytics = Analytics(db)
            logger.info("Analytics initialized successfully")
            print("Analytics initialized successfully")
        except Exception as e:
            logger.error(f"Analytics initialization failed: {e}", exc_info=True)
            print(f"Analytics initialization failed: {e}")
            # Continue without analytics
            
        # Initialize device manager
        logger.info("Initializing device manager...")
        print("Initializing device manager...")
        try:
            device_manager = DeviceManager(CONFIG)
            logger.info("Device manager initialized successfully")
            print("Device manager initialized successfully")
        except Exception as e:
            logger.error(f"Device manager initialization failed: {e}", exc_info=True)
            print(f"Device manager initialization failed: {e}")
            # Continue without device manager
        
        # Initialize MQTT client
        logger.info("Initializing MQTT client...")
        print("Initializing MQTT client...")
        try:
            mqtt_client = MQTTClient(CONFIG, on_device_event)
            logger.info("MQTT client initialized successfully")
            print("MQTT client initialized successfully")
        except Exception as e:
            logger.error(f"MQTT client initialization failed: {e}", exc_info=True)
            print(f"MQTT client initialization failed: {e}")
            # Continue without MQTT
        
        logger.info("Component initialization completed")
        print("Component initialization completed")
        
    except Exception as e:
        logger.error(f"Critical failure during component initialization: {e}", exc_info=True)
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
        logger.info("Loading analytics page...")
        
        # Initialize with empty data in case methods fail
        feeding_stats = {}
        sleep_stats = {}
        diaper_stats = {}
        growth_data = {}
        
        # Get analytics data with individual error handling
        try:
            feeding_stats = analytics.get_feeding_analytics() if analytics else {}
            logger.info(f"Feeding stats loaded: {len(feeding_stats) if feeding_stats else 0} items")
        except Exception as e:
            logger.error(f"Error loading feeding analytics: {e}")
            feeding_stats = {'error': str(e)}
            
        try:
            sleep_stats = analytics.get_sleep_analytics() if analytics else {}
            logger.info(f"Sleep stats loaded: {len(sleep_stats) if sleep_stats else 0} items")
        except Exception as e:
            logger.error(f"Error loading sleep analytics: {e}")
            sleep_stats = {'error': str(e)}
            
        try:
            diaper_stats = analytics.get_diaper_analytics() if analytics else {}
            logger.info(f"Diaper stats loaded: {len(diaper_stats) if diaper_stats else 0} items")
        except Exception as e:
            logger.error(f"Error loading diaper analytics: {e}")
            diaper_stats = {'error': str(e)}
            
        try:
            growth_data = analytics.get_growth_trends() if analytics else {}
            logger.info(f"Growth data loaded: {len(growth_data) if growth_data else 0} items")
        except Exception as e:
            logger.error(f"Error loading growth trends: {e}")
            growth_data = {'error': str(e)}
        
        logger.info("Analytics page data prepared successfully")
        
        # Prepare comprehensive analytics object with expected structure for template
        analytics_summary = {
            'total_events': db.get_total_events_count() if db else 0,
            'feeding_stats': {
                'total_sessions': feeding_stats.get('total_feedings', 0) if feeding_stats else 0,
                'left_breast_sessions': feeding_stats.get('left_breast_count', 0) if feeding_stats else 0,
                'right_breast_sessions': feeding_stats.get('right_breast_count', 0) if feeding_stats else 0,
                'daily_average': feeding_stats.get('daily_average', 0) if feeding_stats else 0,
                'avg_duration_minutes': 0,  # Not available in current analytics
                'avg_interval_hours': feeding_stats.get('average_interval_hours', 0) if feeding_stats else 0,
                'sessions_per_day': feeding_stats.get('daily_average', 0) if feeding_stats else 0
            },
            'sleep_stats': {
                'total_sessions': sleep_stats.get('total_sleep_sessions', 0) if sleep_stats else 0,
                'avg_duration_hours': sleep_stats.get('average_session_duration', 0) if sleep_stats else 0,
                'total_sleep_hours': sleep_stats.get('total_sleep_hours', 0) if sleep_stats else 0,
                'daily_sleep_average': sleep_stats.get('daily_sleep_average', 0) if sleep_stats else 0
            },
            'diaper_stats': {
                'total_changes': diaper_stats.get('total_changes', 0) if diaper_stats else 0,
                'wet_changes': diaper_stats.get('pee_count', 0) if diaper_stats else 0,
                'dirty_changes': diaper_stats.get('poo_count', 0) if diaper_stats else 0,
                'daily_average': diaper_stats.get('daily_average', 0) if diaper_stats else 0
            },
            'days_with_data': len(growth_data) if isinstance(growth_data, list) else 0
        }
        
        # Prepare chart data for frontend
        chart_data = {
            'feeding_stats': feeding_stats,
            'sleep_stats': sleep_stats,
            'diaper_stats': diaper_stats,
            'growth_data': growth_data
        }
        
        return render_template('analytics.html',
                             feeding_stats=feeding_stats,
                             sleep_stats=sleep_stats,
                             diaper_stats=diaper_stats,
                             growth_data=growth_data,
                             analytics=analytics_summary,
                             chart_data=chart_data)
    except Exception as e:
        logger.error(f"Critical error loading analytics page: {e}", exc_info=True)
        return render_template('error.html', error=str(e)), 500

@app.route('/devices')
def devices_page():
    """Device configuration page"""
    try:
        logger.info("Loading devices page...")
        
        # Initialize with empty data
        available_devices = []
        current_mappings = []
        mqtt_config = {
            'broker': 'core-mosquitto',
            'username': '',
            'connected': False,
            'status': 'Disconnected'
        }
        
        try:
            available_devices = device_manager.discover_devices() if device_manager else []
            logger.info(f"Discovered {len(available_devices)} devices")
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            available_devices = []
            
        try:
            current_mappings = device_manager.get_all_mappings() if device_manager else []
            logger.info(f"Loaded {len(current_mappings)} device mappings")
        except Exception as e:
            logger.error(f"Error loading device mappings: {e}")
            current_mappings = []
            
        try:
            mqtt_config = {
                'broker': CONFIG.get('mqtt_broker', 'core-mosquitto'),
                'username': CONFIG.get('mqtt_username', ''),
                'connected': mqtt_client.is_connected() if mqtt_client else False,
                'status': 'Connected' if (mqtt_client and mqtt_client.is_connected()) else 'Disconnected'
            }
            logger.info(f"MQTT status: {mqtt_config['status']}")
        except Exception as e:
            logger.error(f"Error getting MQTT status: {e}")
        
        logger.info("Devices page data prepared successfully")
        
        return render_template('devices.html',
                             available_devices=available_devices,
                             current_mappings=current_mappings,
                             mqtt_config=mqtt_config)
    except Exception as e:
        logger.error(f"Critical error loading devices page: {e}", exc_info=True)
        return render_template('error.html', error=str(e)), 500

@app.route('/settings')
def settings_page():
    """Settings and configuration page"""
    try:
        logger.info("Loading settings page...")
        
        # Initialize with safe defaults
        current_config = CONFIG if CONFIG else {}
        system_info = {
            'version': APP_VERSION,
            'database_type': 'sqlite',
            'mqtt_connected': False,
            'total_events': 0
        }
        settings = {
            'mqtt_broker': 'core-mosquitto',
            'mqtt_username': '',
            'database_type': 'sqlite',
            'log_level': 'info',
            'analytics_enabled': True,
            'export_enabled': True,
            'timezone': 'UTC'
        }
        
        try:
            system_info = {
                'version': APP_VERSION,
                'database_type': CONFIG.get('database_type', 'sqlite'),
                'mqtt_connected': mqtt_client.is_connected() if mqtt_client else False,
                'total_events': db.get_total_events_count() if db else 0
            }
            logger.info(f"System info loaded: {system_info}")
        except Exception as e:
            logger.error(f"Error loading system info: {e}")
        
        try:
            settings = {
                'mqtt_broker': CONFIG.get('mqtt_broker', 'core-mosquitto'),
                'mqtt_username': CONFIG.get('mqtt_username', ''),
                'database_type': CONFIG.get('database_type', 'sqlite'),
                'log_level': CONFIG.get('log_level', 'info'),
                'analytics_enabled': CONFIG.get('enable_analytics', True),
                'export_enabled': CONFIG.get('export_enabled', True),
                'timezone': CONFIG.get('timezone', 'UTC')
            }
            logger.info(f"Settings loaded: {list(settings.keys())}")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
        
        logger.info("Settings page data prepared successfully")
        
        return render_template('settings.html',
                             config=current_config,
                             system_info=system_info,
                             settings=settings)
    except Exception as e:
        logger.error(f"Critical error loading settings page: {e}", exc_info=True)
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
        logger.info("API: Adding new event...")
        if not db:
            logger.error("Database not initialized")
            return jsonify({'success': False, 'error': 'Database not available'}), 500
            
        data = request.get_json()
        logger.info(f"API: Event data received: {data}")
        
        event_id = db.add_event(
            event_type=data['type'],
            duration=data.get('duration'),
            notes=data.get('notes', ''),
            device_source=data.get('device_source', 'manual')
        )
        
        logger.info(f"API: Event added with ID: {event_id}")
        
        # Emit real-time update
        try:
            socketio.emit('new_event', {
                'id': event_id,
                'type': data['type'],
                'timestamp': datetime.now().isoformat(),
                'device': data.get('device_source', 'manual')
            })
            logger.info("API: Real-time event emitted")
        except Exception as e:
            logger.error(f"Error emitting real-time event: {e}")
        
        return jsonify({'success': True, 'event_id': event_id})
        
    except Exception as e:
        logger.error(f"Error adding event: {e}", exc_info=True)
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

@app.route('/api/devices/discover', methods=['POST'])
def api_discover_devices():
    """Discover available devices"""
    try:
        logger.info("API: Discovering devices...")
        if not device_manager:
            logger.error("Device manager not initialized")
            return jsonify({'success': False, 'error': 'Device manager not available'}), 500
            
        devices = device_manager.discover_devices()
        logger.info(f"API: Discovered {len(devices)} devices")
        
        return jsonify({
            'success': True, 
            'device_count': len(devices),
            'devices': devices
        })
        
    except Exception as e:
        logger.error(f"Error discovering devices: {e}", exc_info=True)
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

@app.route('/api/daily-stats')
def api_daily_stats():
    """Get current daily statistics"""
    try:
        logger.info("API: Getting daily stats...")
        if not analytics:
            logger.error("Analytics not initialized")
            return jsonify({'success': False, 'error': 'Analytics not available'}), 500
            
        daily_stats = analytics.get_daily_stats()
        
        # Add debug information
        debug_info = {
            'stats_calculation_time': datetime.now().isoformat(),
            'has_data': bool(daily_stats),
            'total_events_count': db.get_total_events_count() if db else 0,
            'analytics_available': analytics is not None,
            'database_available': db is not None
        }
        
        logger.info(f"API: Daily stats retrieved: {debug_info}")
        
        return jsonify({
            'success': True, 
            'data': daily_stats,
            'debug': debug_info
        })
        
    except Exception as e:
        logger.error(f"Error getting daily stats: {e}", exc_info=True)
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
            'version': APP_VERSION
        }
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'version': APP_VERSION
        }), 500

@app.route('/api/version')
def get_version():
    """Get application version information"""
    try:
        version_info = {
            'version': APP_VERSION,
            'name': 'Baby Care Tracker',
            'description': 'Complete baby care tracking solution',
            'timestamp': datetime.now().isoformat(),
            'config': {
                'database_type': CONFIG.get('database_type', 'sqlite'),
                'mqtt_enabled': bool(CONFIG.get('mqtt_broker')),
                'analytics_enabled': CONFIG.get('enable_analytics', True)
            }
        }
        return jsonify(version_info)
        
    except Exception as e:
        logger.error(f"Version check error: {e}")
        return jsonify({'error': str(e)}), 500
        
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
        
        # Start socketio server (gevent already patched at startup)
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=8099, 
                    debug=CONFIG.get('debug', False))
                    
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
