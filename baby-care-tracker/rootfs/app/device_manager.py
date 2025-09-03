#!/usr/bin/env python3
"""
Device Manager for Baby Care Tracker
Handles device discovery, mapping, and Home Assistant integration
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from database import Database

logger = logging.getLogger(__name__)

class DeviceManager:
    """Device manager for handling device mappings and discovery"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ha_api_url = self._get_ha_api_url()
        self.ha_token = self._get_ha_token()
        self.headers = {
            'Authorization': f'Bearer {self.ha_token}',
            'Content-Type': 'application/json'
        } if self.ha_token else {}
    
    def _get_ha_api_url(self) -> str:
        """Get Home Assistant API URL"""
        # Try to detect Home Assistant supervisor environment
        try:
            with open('/data/options.json', 'r') as f:
                options = json.load(f)
                return options.get('ha_api_url', 'http://supervisor/core/api')
        except:
            # Fallback to common URLs
            return self.config.get('ha_api_url', 'http://homeassistant.local:8123/api')
    
    def _get_ha_token(self) -> Optional[str]:
        """Get Home Assistant long-lived access token"""
        try:
            # Check if running in Home Assistant add-on environment
            with open('/data/options.json', 'r') as f:
                options = json.load(f)
                return options.get('ha_token')
        except:
            # Check environment variables
            import os
            return os.getenv('SUPERVISOR_TOKEN')
    
    def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover available devices from Home Assistant"""
        try:
            devices = []
            
            # Get devices from Home Assistant API
            if self.ha_token:
                ha_devices = self._get_ha_devices()
                devices.extend(ha_devices)
            
            # Add virtual/manual devices
            virtual_devices = self._get_virtual_devices()
            devices.extend(virtual_devices)
            
            logger.info(f"Discovered {len(devices)} devices")
            return devices
            
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            return []
    
    def _get_ha_devices(self) -> List[Dict[str, Any]]:
        """Get devices from Home Assistant"""
        try:
            # Get device registry
            response = requests.get(
                f'{self.ha_api_url}/config/device_registry/list',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to get HA devices: {response.status_code}")
                return []
            
            ha_devices = response.json()
            devices = []
            
            for device in ha_devices:
                # Filter for devices that can trigger events
                if self._is_compatible_device(device):
                    # Get entities for this device
                    entities = self._get_device_entities(device['id'])
                    
                    if entities:
                        devices.append({
                            'id': f"ha_{device['id']}",
                            'name': device.get('name_by_user') or device.get('name', 'Unknown Device'),
                            'manufacturer': device.get('manufacturer', ''),
                            'model': device.get('model', ''),
                            'type': 'home_assistant',
                            'entities': entities,
                            'triggers': self._get_device_triggers(device['id'])
                        })
            
            return devices
            
        except Exception as e:
            logger.error(f"Error getting HA devices: {e}")
            return []
    
    def _is_compatible_device(self, device: Dict) -> bool:
        """Check if device is compatible for baby care tracking"""
        # Check device model/manufacturer for known compatible devices
        manufacturer = device.get('manufacturer', '').lower()
        model = device.get('model', '').lower()
        
        compatible_manufacturers = [
            'philips', 'xiaomi', 'aqara', 'ikea', 'sonoff', 
            'tuya', 'zigbee', 'zwave', 'shelly'
        ]
        
        compatible_keywords = [
            'button', 'switch', 'sensor', 'remote', 'dimmer'
        ]
        
        # Check manufacturer
        if any(mfg in manufacturer for mfg in compatible_manufacturers):
            return True
        
        # Check model for keywords
        if any(keyword in model for keyword in compatible_keywords):
            return True
        
        # If we have entities, it's probably compatible
        return True
    
    def _get_device_entities(self, device_id: str) -> List[Dict[str, Any]]:
        """Get entities for a specific device"""
        try:
            response = requests.get(
                f'{self.ha_api_url}/config/entity_registry/list',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            all_entities = response.json()
            device_entities = []
            
            for entity in all_entities:
                if entity.get('device_id') == device_id:
                    domain = entity['entity_id'].split('.')[0]
                    
                    # Filter for relevant entity types
                    if domain in ['button', 'switch', 'binary_sensor', 'sensor', 'input_boolean', 'light']:
                        device_entities.append({
                            'entity_id': entity['entity_id'],
                            'name': entity.get('name') or entity['entity_id'],
                            'domain': domain,
                            'device_class': entity.get('device_class'),
                            'platform': entity.get('platform')
                        })
            
            return device_entities
            
        except Exception as e:
            logger.error(f"Error getting device entities: {e}")
            return []
    
    def _get_device_triggers(self, device_id: str) -> List[Dict[str, Any]]:
        """Get available triggers for a device"""
        try:
            response = requests.post(
                f'{self.ha_api_url}/config/device_automation/trigger/list',
                headers=self.headers,
                json={'device_id': device_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            logger.debug(f"No device triggers found for {device_id}: {e}")
            return []
    
    def _get_virtual_devices(self) -> List[Dict[str, Any]]:
        """Get virtual/manual devices for testing"""
        return [
            {
                'id': 'virtual_button_1',
                'name': 'Virtual Button 1',
                'manufacturer': 'Baby Care Tracker',
                'model': 'Virtual Device',
                'type': 'virtual',
                'entities': [
                    {
                        'entity_id': 'button.virtual_button_1',
                        'name': 'Virtual Button 1',
                        'domain': 'button',
                        'device_class': None,
                        'platform': 'virtual'
                    }
                ],
                'triggers': [
                    {
                        'type': 'button_press',
                        'subtype': 'single',
                        'device_id': 'virtual_button_1'
                    }
                ]
            },
            {
                'id': 'virtual_switch_1',
                'name': 'Virtual Switch 1',
                'manufacturer': 'Baby Care Tracker',
                'model': 'Virtual Device',
                'type': 'virtual',
                'entities': [
                    {
                        'entity_id': 'switch.virtual_switch_1',
                        'name': 'Virtual Switch 1',
                        'domain': 'switch',
                        'device_class': None,
                        'platform': 'virtual'
                    }
                ],
                'triggers': [
                    {
                        'type': 'state_change',
                        'from_state': 'off',
                        'to_state': 'on',
                        'device_id': 'virtual_switch_1'
                    },
                    {
                        'type': 'state_change',
                        'from_state': 'on',
                        'to_state': 'off',
                        'device_id': 'virtual_switch_1'
                    }
                ]
            }
        ]
    
    # ========================================================================
    # DEVICE MAPPING MANAGEMENT
    # ========================================================================
    
    def add_mapping(self, device_id: str, trigger_type: str, baby_care_action: str) -> int:
        """Add a new device mapping"""
        try:
            # Get device info
            devices = self.discover_devices()
            device = next((d for d in devices if d['id'] == device_id), None)
            
            if not device:
                raise ValueError(f"Device not found: {device_id}")
            
            device_name = device['name']
            
            # Add mapping to database (assuming we have db access)
            # This would need to be injected or passed in
            # For now, we'll store in memory or file
            mapping_data = {
                'device_id': device_id,
                'device_name': device_name,
                'trigger_type': trigger_type,
                'baby_care_action': baby_care_action
            }
            
            # Store mapping
            mapping_id = self._store_mapping(mapping_data)
            
            logger.info(f"Added device mapping: {device_id} -> {baby_care_action}")
            return mapping_id
            
        except Exception as e:
            logger.error(f"Error adding device mapping: {e}")
            raise
    
    def get_mapping(self, device_id: str, trigger_type: str) -> Optional[Dict[str, Any]]:
        """Get mapping for specific device and trigger"""
        try:
            mappings = self.get_all_mappings()
            
            for mapping in mappings:
                if (mapping['device_id'] == device_id and 
                    mapping['trigger_type'] == trigger_type):
                    return mapping
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting device mapping: {e}")
            return None
    
    def get_all_mappings(self) -> List[Dict[str, Any]]:
        """Get all device mappings"""
        try:
            # Load mappings from storage
            return self._load_mappings()
            
        except Exception as e:
            logger.error(f"Error getting all mappings: {e}")
            return []
    
    def delete_mapping(self, mapping_id: int) -> bool:
        """Delete a device mapping"""
        try:
            # Remove mapping from storage
            return self._delete_mapping(mapping_id)
            
        except Exception as e:
            logger.error(f"Error deleting mapping: {e}")
            return False
    
    # ========================================================================
    # MAPPING STORAGE (FILE-BASED FOR SIMPLICITY)
    # ========================================================================
    
    def _get_mappings_file(self) -> str:
        """Get path to mappings file"""
        return '/data/device_mappings.json'
    
    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from file"""
        try:
            mappings_file = self._get_mappings_file()
            
            try:
                with open(mappings_file, 'r') as f:
                    data = json.load(f)
                    return data.get('mappings', [])
            except FileNotFoundError:
                return []
                
        except Exception as e:
            logger.error(f"Error loading mappings: {e}")
            return []
    
    def _store_mapping(self, mapping_data: Dict[str, Any]) -> int:
        """Store a new mapping"""
        try:
            mappings = self._load_mappings()
            
            # Generate new ID
            mapping_id = max([m.get('id', 0) for m in mappings], default=0) + 1
            mapping_data['id'] = mapping_id
            mapping_data['created_at'] = datetime.now().isoformat()
            
            mappings.append(mapping_data)
            
            # Save back to file
            mappings_file = self._get_mappings_file()
            with open(mappings_file, 'w') as f:
                json.dump({'mappings': mappings}, f, indent=2)
            
            return mapping_id
            
        except Exception as e:
            logger.error(f"Error storing mapping: {e}")
            raise
    
    def _delete_mapping(self, mapping_id: int) -> bool:
        """Delete a mapping by ID"""
        try:
            mappings = self._load_mappings()
            original_count = len(mappings)
            
            mappings = [m for m in mappings if m.get('id') != mapping_id]
            
            if len(mappings) < original_count:
                # Save updated mappings
                mappings_file = self._get_mappings_file()
                with open(mappings_file, 'w') as f:
                    json.dump({'mappings': mappings}, f, indent=2)
                
                logger.info(f"Deleted mapping {mapping_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting mapping: {e}")
            return False
    
    # ========================================================================
    # BABY CARE ACTIONS
    # ========================================================================
    
    def get_baby_care_actions(self) -> List[Dict[str, str]]:
        """Get list of available baby care actions"""
        return [
            {'key': 'feeding_start_left', 'label': 'Start Left Breast Feeding', 'icon': 'mdi:baby-bottle'},
            {'key': 'feeding_start_right', 'label': 'Start Right Breast Feeding', 'icon': 'mdi:baby-bottle-outline'},
            {'key': 'feeding_stop', 'label': 'Stop Feeding', 'icon': 'mdi:stop-circle'},
            {'key': 'sleep_start', 'label': 'Start Sleep', 'icon': 'mdi:sleep'},
            {'key': 'wake_up', 'label': 'Wake Up', 'icon': 'mdi:weather-sunny'},
            {'key': 'diaper_pee', 'label': 'Pee Diaper Change', 'icon': 'mdi:water'},
            {'key': 'diaper_poo', 'label': 'Poo Diaper Change', 'icon': 'mdi:emoticon-poop'},
            {'key': 'diaper_both', 'label': 'Both (Pee & Poo) Diaper Change', 'icon': 'mdi:baby-carriage'}
        ]
    
    # ========================================================================
    # DEVICE EVENT PROCESSING
    # ========================================================================
    
    def process_device_event(self, device_id: str, event_type: str, event_data: Dict) -> Optional[str]:
        """Process a device event and return baby care action if mapped"""
        try:
            mapping = self.get_mapping(device_id, event_type)
            
            if mapping:
                logger.info(f"Device event mapped: {device_id}/{event_type} -> {mapping['baby_care_action']}")
                return mapping['baby_care_action']
            else:
                logger.debug(f"No mapping found for device event: {device_id}/{event_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing device event: {e}")
            return None
    
    def test_device_connection(self, device_id: str) -> bool:
        """Test if we can communicate with a device"""
        try:
            if device_id.startswith('virtual_'):
                # Virtual devices are always "connected"
                return True
            
            if device_id.startswith('ha_'):
                # Test Home Assistant API connection
                response = requests.get(
                    f'{self.ha_api_url}/states',
                    headers=self.headers,
                    timeout=5
                )
                return response.status_code == 200
            
            return False
            
        except Exception as e:
            logger.error(f"Error testing device connection: {e}")
            return False
