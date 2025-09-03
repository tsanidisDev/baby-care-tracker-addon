#!/usr/bin/env python3
"""
Database module for Baby Care Tracker
Handles all data persistence with SQLite/PostgreSQL support
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

Base = declarative_base()

class BabyCareEvent(Base):
    """Baby care event model"""
    __tablename__ = 'baby_care_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)  # feeding_start_left, sleep_start, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, nullable=True)  # Duration in minutes
    notes = Column(Text, nullable=True)
    device_source = Column(String(100), nullable=True)  # Which device triggered this
    trigger_data = Column(Text, nullable=True)  # Raw trigger data as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DeviceMapping(Base):
    """Device to baby care action mappings"""
    __tablename__ = 'device_mappings'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100), nullable=False)
    device_name = Column(String(200), nullable=True)
    trigger_type = Column(String(50), nullable=False)  # button_press, state_change, etc.
    baby_care_action = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Analytics(Base):
    """Cached analytics data"""
    __tablename__ = 'analytics_cache'
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_data = Column(Text, nullable=True)  # JSON data
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    """Database manager class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self.initialized = False
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and tables"""
        try:
            db_type = self.config.get('database_type', 'sqlite')
            
            if db_type == 'sqlite':
                db_path = '/data/database/baby_care_tracker.db'
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                database_url = f'sqlite:///{db_path}'
            elif db_type == 'postgresql':
                # PostgreSQL configuration (for advanced users)
                host = self.config.get('postgres_host', 'localhost')
                port = self.config.get('postgres_port', 5432)
                user = self.config.get('postgres_user', 'baby_care')
                password = self.config.get('postgres_password', '')
                db_name = self.config.get('postgres_db', 'baby_care_tracker')
                database_url = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            self.engine = create_engine(database_url, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            self.initialized = True
            logger.info(f"Database initialized successfully with {db_type}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def is_healthy(self) -> bool:
        """Check if database is healthy"""
        try:
            with self.get_session() as session:
                session.execute('SELECT 1')
                return True
        except Exception:
            return False
    
    # ========================================================================
    # BABY CARE EVENTS
    # ========================================================================
    
    def add_event(self, event_type: str, duration: Optional[int] = None, 
                  notes: str = '', device_source: Optional[str] = None,
                  trigger_data: Optional[str] = None) -> int:
        """Add a new baby care event"""
        try:
            with self.get_session() as session:
                event = BabyCareEvent(
                    event_type=event_type,
                    duration=duration,
                    notes=notes,
                    device_source=device_source,
                    trigger_data=trigger_data
                )
                session.add(event)
                session.commit()
                session.refresh(event)
                
                logger.info(f"Added baby care event: {event_type} (ID: {event.id})")
                return event.id
                
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            raise
    
    def get_events(self, event_type: Optional[str] = None, 
                   limit: int = 50, offset: int = 0,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> List[Dict]:
        """Get baby care events with optional filtering"""
        try:
            with self.get_session() as session:
                query = session.query(BabyCareEvent)
                
                if event_type:
                    query = query.filter(BabyCareEvent.event_type == event_type)
                
                if start_date:
                    query = query.filter(BabyCareEvent.timestamp >= start_date)
                
                if end_date:
                    query = query.filter(BabyCareEvent.timestamp <= end_date)
                
                events = query.order_by(BabyCareEvent.timestamp.desc())\
                             .offset(offset).limit(limit).all()
                
                return [self._event_to_dict(event) for event in events]
                
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """Get most recent baby care events"""
        return self.get_events(limit=limit)
    
    def get_events_by_date_range(self, start_date: datetime, 
                                end_date: datetime) -> List[Dict]:
        """Get events within a date range"""
        return self.get_events(start_date=start_date, end_date=end_date, limit=1000)
    
    def get_total_events_count(self) -> int:
        """Get total number of events"""
        try:
            with self.get_session() as session:
                return session.query(BabyCareEvent).count()
        except Exception as e:
            logger.error(f"Error getting event count: {e}")
            return 0
    
    def update_event(self, event_id: int, **kwargs) -> bool:
        """Update an existing event"""
        try:
            with self.get_session() as session:
                event = session.query(BabyCareEvent).filter(BabyCareEvent.id == event_id).first()
                if not event:
                    return False
                
                for key, value in kwargs.items():
                    if hasattr(event, key):
                        setattr(event, key, value)
                
                event.updated_at = datetime.utcnow()
                session.commit()
                
                logger.info(f"Updated event {event_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating event {event_id}: {e}")
            return False
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event"""
        try:
            with self.get_session() as session:
                event = session.query(BabyCareEvent).filter(BabyCareEvent.id == event_id).first()
                if event:
                    session.delete(event)
                    session.commit()
                    logger.info(f"Deleted event {event_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting event {event_id}: {e}")
            return False
    
    # ========================================================================
    # DEVICE MAPPINGS
    # ========================================================================
    
    def add_device_mapping(self, device_id: str, device_name: str,
                          trigger_type: str, baby_care_action: str) -> int:
        """Add a new device mapping"""
        try:
            with self.get_session() as session:
                mapping = DeviceMapping(
                    device_id=device_id,
                    device_name=device_name,
                    trigger_type=trigger_type,
                    baby_care_action=baby_care_action
                )
                session.add(mapping)
                session.commit()
                session.refresh(mapping)
                
                logger.info(f"Added device mapping: {device_id} -> {baby_care_action}")
                return mapping.id
                
        except Exception as e:
            logger.error(f"Error adding device mapping: {e}")
            raise
    
    def get_device_mappings(self, enabled_only: bool = True) -> List[Dict]:
        """Get all device mappings"""
        try:
            with self.get_session() as session:
                query = session.query(DeviceMapping)
                
                if enabled_only:
                    query = query.filter(DeviceMapping.enabled == True)
                
                mappings = query.order_by(DeviceMapping.created_at.desc()).all()
                return [self._mapping_to_dict(mapping) for mapping in mappings]
                
        except Exception as e:
            logger.error(f"Error getting device mappings: {e}")
            return []
    
    def get_device_mapping(self, device_id: str, trigger_type: str) -> Optional[Dict]:
        """Get mapping for specific device and trigger"""
        try:
            with self.get_session() as session:
                mapping = session.query(DeviceMapping).filter(
                    DeviceMapping.device_id == device_id,
                    DeviceMapping.trigger_type == trigger_type,
                    DeviceMapping.enabled == True
                ).first()
                
                return self._mapping_to_dict(mapping) if mapping else None
                
        except Exception as e:
            logger.error(f"Error getting device mapping: {e}")
            return None
    
    def delete_device_mapping(self, mapping_id: int) -> bool:
        """Delete a device mapping"""
        try:
            with self.get_session() as session:
                mapping = session.query(DeviceMapping).filter(DeviceMapping.id == mapping_id).first()
                if mapping:
                    session.delete(mapping)
                    session.commit()
                    logger.info(f"Deleted device mapping {mapping_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting device mapping {mapping_id}: {e}")
            return False
    
    # ========================================================================
    # ANALYTICS AND STATS
    # ========================================================================
    
    def get_feeding_stats(self, days: int = 7) -> Dict:
        """Get feeding statistics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            with self.get_session() as session:
                # Get feeding events
                feeding_events = session.query(BabyCareEvent).filter(
                    BabyCareEvent.event_type.in_(['feeding_start_left', 'feeding_start_right']),
                    BabyCareEvent.timestamp >= start_date
                ).all()
                
                # Calculate stats
                total_feedings = len(feeding_events)
                left_breast = len([e for e in feeding_events if e.event_type == 'feeding_start_left'])
                right_breast = len([e for e in feeding_events if e.event_type == 'feeding_start_right'])
                
                # Average duration (if recorded)
                durations = [e.duration for e in feeding_events if e.duration]
                avg_duration = sum(durations) / len(durations) if durations else 0
                
                return {
                    'total_feedings': total_feedings,
                    'left_breast': left_breast,
                    'right_breast': right_breast,
                    'average_duration': round(avg_duration, 1),
                    'daily_average': round(total_feedings / days, 1)
                }
                
        except Exception as e:
            logger.error(f"Error getting feeding stats: {e}")
            return {}
    
    def get_sleep_stats(self, days: int = 7) -> Dict:
        """Get sleep statistics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            with self.get_session() as session:
                sleep_events = session.query(BabyCareEvent).filter(
                    BabyCareEvent.event_type.in_(['sleep_start', 'wake_up']),
                    BabyCareEvent.timestamp >= start_date
                ).order_by(BabyCareEvent.timestamp).all()
                
                # Calculate sleep sessions
                sleep_sessions = []
                current_sleep_start = None
                
                for event in sleep_events:
                    if event.event_type == 'sleep_start':
                        current_sleep_start = event.timestamp
                    elif event.event_type == 'wake_up' and current_sleep_start:
                        duration = (event.timestamp - current_sleep_start).total_seconds() / 3600  # hours
                        sleep_sessions.append(duration)
                        current_sleep_start = None
                
                # Calculate stats
                total_sleep_time = sum(sleep_sessions)
                avg_sleep_duration = sum(sleep_sessions) / len(sleep_sessions) if sleep_sessions else 0
                
                return {
                    'total_sleep_sessions': len(sleep_sessions),
                    'total_sleep_hours': round(total_sleep_time, 1),
                    'average_sleep_duration': round(avg_sleep_duration, 1),
                    'daily_sleep_average': round(total_sleep_time / days, 1)
                }
                
        except Exception as e:
            logger.error(f"Error getting sleep stats: {e}")
            return {}
    
    def get_diaper_stats(self, days: int = 7) -> Dict:
        """Get diaper statistics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            with self.get_session() as session:
                diaper_events = session.query(BabyCareEvent).filter(
                    BabyCareEvent.event_type.in_(['diaper_pee', 'diaper_poo', 'diaper_both']),
                    BabyCareEvent.timestamp >= start_date
                ).all()
                
                pee_count = len([e for e in diaper_events if e.event_type in ['diaper_pee', 'diaper_both']])
                poo_count = len([e for e in diaper_events if e.event_type in ['diaper_poo', 'diaper_both']])
                total_changes = len(diaper_events)
                
                return {
                    'total_changes': total_changes,
                    'pee_count': pee_count,
                    'poo_count': poo_count,
                    'daily_average': round(total_changes / days, 1)
                }
                
        except Exception as e:
            logger.error(f"Error getting diaper stats: {e}")
            return {}
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def cleanup_old_data(self, days: int = 365):
        """Clean up old data beyond specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with self.get_session() as session:
                # Delete old events
                deleted_events = session.query(BabyCareEvent).filter(
                    BabyCareEvent.timestamp < cutoff_date
                ).delete()
                
                # Delete old analytics cache
                deleted_analytics = session.query(Analytics).filter(
                    Analytics.date < cutoff_date
                ).delete()
                
                session.commit()
                
                logger.info(f"Cleaned up {deleted_events} old events and {deleted_analytics} old analytics")
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def _event_to_dict(self, event: BabyCareEvent) -> Dict:
        """Convert event object to dictionary"""
        return {
            'id': event.id,
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat(),
            'duration': event.duration,
            'notes': event.notes,
            'device_source': event.device_source,
            'trigger_data': event.trigger_data,
            'created_at': event.created_at.isoformat(),
            'updated_at': event.updated_at.isoformat()
        }
    
    def _mapping_to_dict(self, mapping: DeviceMapping) -> Dict:
        """Convert mapping object to dictionary"""
        return {
            'id': mapping.id,
            'device_id': mapping.device_id,
            'device_name': mapping.device_name,
            'trigger_type': mapping.trigger_type,
            'baby_care_action': mapping.baby_care_action,
            'enabled': mapping.enabled,
            'created_at': mapping.created_at.isoformat(),
            'updated_at': mapping.updated_at.isoformat()
        }
