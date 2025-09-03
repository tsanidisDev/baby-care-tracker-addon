#!/usr/bin/env python3
"""
Database migrations for Baby Care Tracker
Handles database schema updates between versions
"""

import os
import logging
import sqlite3
from typing import Dict, List, Callable

logger = logging.getLogger('baby_care_tracker.migrations')

class MigrationManager:
    """Manages database migrations between versions"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations = self._get_migrations()
    
    def _get_migrations(self) -> Dict[str, Callable]:
        """Get all available migrations"""
        return {
            '1.0.0': self._migrate_to_100,
            '1.0.1': self._migrate_to_101,
            '1.0.2': self._migrate_to_102,
            '1.0.3': self._migrate_to_103,
            '1.0.4': self._migrate_to_104,
        }
    
    def get_current_version(self) -> str:
        """Get current database version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='schema_version'
                """)
                
                if not cursor.fetchone():
                    # No version table, assume 1.0.0
                    return '1.0.0'
                
                cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
                result = cursor.fetchone()
                return result[0] if result else '1.0.0'
                
        except Exception as e:
            logger.warning(f"Could not determine database version: {e}")
            return '1.0.0'
    
    def set_version(self, version: str):
        """Set database version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create version table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert new version
                cursor.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (version,)
                )
                
                conn.commit()
                logger.info(f"Database version set to {version}")
                
        except Exception as e:
            logger.error(f"Failed to set database version: {e}")
            raise
    
    def needs_migration(self, target_version: str) -> bool:
        """Check if migration is needed"""
        current = self.get_current_version()
        return self._version_compare(current, target_version) < 0
    
    def migrate(self, target_version: str):
        """Run migrations to reach target version"""
        current_version = self.get_current_version()
        
        if not self.needs_migration(target_version):
            logger.info(f"Database is already at version {current_version}, no migration needed")
            return
        
        logger.info(f"Migrating database from {current_version} to {target_version}")
        
        # Get migration path
        migration_path = self._get_migration_path(current_version, target_version)
        
        for version in migration_path:
            if version in self.migrations:
                logger.info(f"Running migration to {version}")
                try:
                    self.migrations[version]()
                    self.set_version(version)
                    logger.info(f"Migration to {version} completed")
                except Exception as e:
                    logger.error(f"Migration to {version} failed: {e}")
                    raise
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """Compare two version strings"""
        def version_key(v):
            return tuple(map(int, v.split('.')))
        
        v1_key = version_key(v1)
        v2_key = version_key(v2)
        
        if v1_key < v2_key:
            return -1
        elif v1_key > v2_key:
            return 1
        else:
            return 0
    
    def _get_migration_path(self, current: str, target: str) -> List[str]:
        """Get list of versions to migrate through"""
        all_versions = sorted(self.migrations.keys(), key=lambda v: tuple(map(int, v.split('.'))))
        
        current_idx = all_versions.index(current) if current in all_versions else -1
        target_idx = all_versions.index(target)
        
        return all_versions[current_idx + 1:target_idx + 1]
    
    # Migration methods
    
    def _migrate_to_100(self):
        """Migration to version 1.0.0 (initial schema)"""
        # This is the base version, no migration needed
        pass
    
    def _migrate_to_101(self):
        """Migration to version 1.0.1"""
        # Add any schema changes for 1.0.1
        logger.info("No schema changes for 1.0.1")
        pass
    
    def _migrate_to_102(self):
        """Migration to version 1.0.2"""
        # Add any schema changes for 1.0.2
        logger.info("No schema changes for 1.0.2")
        pass
    
    def _migrate_to_103(self):
        """Migration to version 1.0.3"""
        # Add index for better performance
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add indexes for better query performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                    ON baby_events(timestamp)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_type 
                    ON baby_events(event_type)
                """)
                
                conn.commit()
                logger.info("Added performance indexes")
                
        except Exception as e:
            logger.warning(f"Could not add indexes: {e}")
            # Non-critical, continue anyway
    
    def _migrate_to_104(self):
        """Migration to version 1.0.4"""
        # Add any schema changes for 1.0.4
        logger.info("No schema changes for 1.0.4 - compatibility improvements only")
        pass


def run_migrations(db_path: str, target_version: str):
    """Run database migrations"""
    if not os.path.exists(db_path):
        logger.info("Database does not exist yet, will be created on first use")
        return
    
    manager = MigrationManager(db_path)
    manager.migrate(target_version)
