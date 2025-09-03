#!/usr/bin/env python3
"""
MQTT Client for Baby Care Tracker
Handles MQTT communication for device events and Home Assistant integration
"""

import json
import logging
import threading
import time
from typing import Callable, Dict, Any, Optional
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class MQTTClient:
    """MQTT client for handling device events and Home Assistant integration"""
    
    def __init__(self, config: Dict[str, Any], event_callback: Callable):
        self.config = config
        self.event_callback = event_callback
        self.client = None
        self.connected = False
        self.reconnect_delay = 5
        self.max_reconnect_delay = 300
        
        self._initialize_client()
        self._connect()
    
    def _initialize_client(self):
        """Initialize MQTT client"""
        try:
            self.client = mqtt.Client(client_id="baby_care_tracker")
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            self.client.on_subscribe = self._on_subscribe
            
            # Set authentication if provided
            username = self.config.get('mqtt_username')
            password = self.config.get('mqtt_password')
            
            if username and password:
                self.client.username_pw_set(username, password)
                logger.info("MQTT authentication configured")
            
            # Set TLS if needed (for external MQTT brokers)
            if self.config.get('mqtt_tls', False):
                self.client.tls_set()
                logger.info("MQTT TLS enabled")
            
        except Exception as e:
            logger.error(f"Failed to initialize MQTT client: {e}")
            raise
    
    def _connect(self):
        """Connect to MQTT broker"""
        try:
            broker = self.config.get('mqtt_broker', 'core-mosquitto')
            port = self.config.get('mqtt_port', 1883)
            
            # Handle different broker formats
            if '://' in broker:
                # Remove protocol if present
                broker = broker.split('://')[-1]
            
            if ':' in broker:
                # Extract port if included in broker string
                broker, port = broker.split(':')
                port = int(port)
            
            logger.info(f"Connecting to MQTT broker: {broker}:{port}")
            self.client.connect(broker, port, 60)
            
            # Start the MQTT loop in a separate thread
            self.client.loop_start()
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            # Schedule reconnection
            threading.Timer(self.reconnect_delay, self._connect).start()
            self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Called when MQTT client connects"""
        if rc == 0:
            self.connected = True
            self.reconnect_delay = 5  # Reset reconnect delay
            logger.info("Connected to MQTT broker successfully")
            
            # Subscribe to relevant topics
            self._subscribe_to_topics()
            
            # Publish online status
            self._publish_status("online")
            
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Called when MQTT client disconnects"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker with code {rc}")
        
        if rc != 0:
            logger.info("Attempting to reconnect...")
            # Schedule reconnection
            threading.Timer(self.reconnect_delay, self._connect).start()
            self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
    
    def _on_message(self, client, userdata, msg):
        """Called when a message is received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"Received MQTT message: {topic} = {payload}")
            
            # Parse the message and determine device and event type
            device_info = self._parse_device_message(topic, payload)
            
            if device_info:
                # Call the event callback
                self.event_callback(
                    device_info['device_id'],
                    device_info['event_type'],
                    device_info['data']
                )
            
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Called when subscription is successful"""
        logger.debug(f"Subscribed to MQTT topic with QoS {granted_qos}")
    
    def _subscribe_to_topics(self):
        """Subscribe to relevant MQTT topics"""
        try:
            # Subscribe to Zigbee2MQTT device events
            self.client.subscribe("zigbee2mqtt/+/action")
            self.client.subscribe("zigbee2mqtt/+")
            
            # Subscribe to Home Assistant state changes
            self.client.subscribe("homeassistant/+/+/state")
            
            # Subscribe to Z-Wave events
            self.client.subscribe("zwave/+/action")
            
            # Subscribe to custom device topics
            self.client.subscribe("baby_care_tracker/+/+")
            
            # Subscribe to Home Assistant events
            self.client.subscribe("homeassistant/event/+")
            
            logger.info("Subscribed to MQTT topics for device monitoring")
            
        except Exception as e:
            logger.error(f"Error subscribing to MQTT topics: {e}")
    
    def _parse_device_message(self, topic: str, payload: str) -> Optional[Dict[str, Any]]:
        """Parse device message and extract relevant information"""
        try:
            # Try to parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                # Handle plain text payloads
                data = {'value': payload}
            
            device_info = None
            
            # Parse Zigbee2MQTT messages
            if topic.startswith('zigbee2mqtt/'):
                device_info = self._parse_zigbee2mqtt_message(topic, data)
            
            # Parse Home Assistant state changes
            elif topic.startswith('homeassistant/'):
                device_info = self._parse_homeassistant_message(topic, data)
            
            # Parse Z-Wave messages
            elif topic.startswith('zwave/'):
                device_info = self._parse_zwave_message(topic, data)
            
            # Parse custom baby care tracker messages
            elif topic.startswith('baby_care_tracker/'):
                device_info = self._parse_custom_message(topic, data)
            
            return device_info
            
        except Exception as e:
            logger.error(f"Error parsing device message: {e}")
            return None
    
    def _parse_zigbee2mqtt_message(self, topic: str, data: Dict) -> Optional[Dict[str, Any]]:
        """Parse Zigbee2MQTT device messages"""
        try:
            # Extract device name from topic
            parts = topic.split('/')
            if len(parts) < 2:
                return None
            
            device_id = parts[1]
            
            # Handle action messages (button presses, etc.)
            if topic.endswith('/action'):
                action = data.get('action')
                if action:
                    return {
                        'device_id': f"zigbee2mqtt_{device_id}",
                        'event_type': f"action_{action}",
                        'data': data
                    }
            
            # Handle state changes
            elif not topic.endswith('/availability') and not topic.endswith('/linkquality'):
                # Look for button presses, switch states, etc.
                if 'action' in data:
                    return {
                        'device_id': f"zigbee2mqtt_{device_id}",
                        'event_type': f"action_{data['action']}",
                        'data': data
                    }
                elif 'state' in data:
                    return {
                        'device_id': f"zigbee2mqtt_{device_id}",
                        'event_type': f"state_{data['state']}",
                        'data': data
                    }
                elif 'contact' in data:  # Door/window sensors
                    return {
                        'device_id': f"zigbee2mqtt_{device_id}",
                        'event_type': f"contact_{data['contact']}",
                        'data': data
                    }
                elif 'occupancy' in data:  # Motion sensors
                    return {
                        'device_id': f"zigbee2mqtt_{device_id}",
                        'event_type': f"motion_{data['occupancy']}",
                        'data': data
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Zigbee2MQTT message: {e}")
            return None
    
    def _parse_homeassistant_message(self, topic: str, data: Dict) -> Optional[Dict[str, Any]]:
        """Parse Home Assistant state change messages"""
        try:
            # Parse Home Assistant state topics
            # Format: homeassistant/domain/entity_id/state
            parts = topic.split('/')
            if len(parts) >= 4:
                domain = parts[1]
                entity_id = parts[2]
                
                # Handle different domains
                if domain in ['switch', 'binary_sensor', 'sensor', 'button']:
                    state = data.get('state', data.get('value', payload))
                    
                    return {
                        'device_id': f"ha_{entity_id}",
                        'event_type': f"state_{state}",
                        'data': data
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Home Assistant message: {e}")
            return None
    
    def _parse_zwave_message(self, topic: str, data: Dict) -> Optional[Dict[str, Any]]:
        """Parse Z-Wave device messages"""
        try:
            parts = topic.split('/')
            if len(parts) >= 2:
                device_id = parts[1]
                
                if topic.endswith('/action'):
                    action = data.get('action', data.get('value'))
                    return {
                        'device_id': f"zwave_{device_id}",
                        'event_type': f"action_{action}",
                        'data': data
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Z-Wave message: {e}")
            return None
    
    def _parse_custom_message(self, topic: str, data: Dict) -> Optional[Dict[str, Any]]:
        """Parse custom baby care tracker messages"""
        try:
            # Format: baby_care_tracker/device_id/event_type
            parts = topic.split('/')
            if len(parts) >= 3:
                device_id = parts[1]
                event_type = parts[2]
                
                return {
                    'device_id': f"custom_{device_id}",
                    'event_type': event_type,
                    'data': data
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing custom message: {e}")
            return None
    
    def publish(self, topic: str, payload: str, retain: bool = False):
        """Publish a message to MQTT"""
        try:
            if self.connected and self.client:
                self.client.publish(topic, payload, retain=retain)
                logger.debug(f"Published MQTT message: {topic} = {payload}")
            else:
                logger.warning("Cannot publish MQTT message: not connected")
                
        except Exception as e:
            logger.error(f"Error publishing MQTT message: {e}")
    
    def _publish_status(self, status: str):
        """Publish add-on status"""
        try:
            status_payload = {
                'status': status,
                'timestamp': time.time(),
                'version': '2.0.0'
            }
            
            self.publish(
                'baby_care_tracker/addon/status',
                json.dumps(status_payload),
                retain=True
            )
            
        except Exception as e:
            logger.error(f"Error publishing status: {e}")
    
    def publish_event(self, event_type: str, event_data: Dict):
        """Publish a baby care event to MQTT"""
        try:
            payload = {
                'event_type': event_type,
                'timestamp': time.time(),
                'data': event_data
            }
            
            self.publish(
                f'baby_care_tracker/events/{event_type}',
                json.dumps(payload)
            )
            
            # Also publish to Home Assistant discovery topic if configured
            if self.config.get('ha_discovery', True):
                self._publish_ha_discovery(event_type, event_data)
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
    
    def _publish_ha_discovery(self, event_type: str, event_data: Dict):
        """Publish Home Assistant discovery messages"""
        try:
            # Create sensor for this event type
            device_config = {
                'name': f"Baby Care {event_type.replace('_', ' ').title()}",
                'state_topic': f'baby_care_tracker/events/{event_type}',
                'value_template': '{{ value_json.timestamp }}',
                'device': {
                    'identifiers': ['baby_care_tracker'],
                    'name': 'Baby Care Tracker',
                    'model': 'Add-on v2.0.0',
                    'manufacturer': 'Baby Care Tracker'
                },
                'unique_id': f'baby_care_tracker_{event_type}'
            }
            
            discovery_topic = f'homeassistant/sensor/baby_care_tracker_{event_type}/config'
            self.publish(discovery_topic, json.dumps(device_config), retain=True)
            
        except Exception as e:
            logger.error(f"Error publishing HA discovery: {e}")
    
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self.connected
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            if self.client and self.connected:
                self._publish_status("offline")
                self.client.loop_stop()
                self.client.disconnect()
                logger.info("Disconnected from MQTT broker")
                
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.disconnect()
