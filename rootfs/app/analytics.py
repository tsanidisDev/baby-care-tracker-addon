#!/usr/bin/env python3
"""
Analytics module for Baby Care Tracker
Provides comprehensive analytics, reports, and data visualization
"""

import os
import json
import logging
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from database import Database

logger = logging.getLogger(__name__)

class Analytics:
    """Analytics engine for baby care data"""
    
    def __init__(self, database: Database):
        self.db = database
        self.export_dir = '/data/exports'
        os.makedirs(self.export_dir, exist_ok=True)
    
    # ========================================================================
    # DAILY STATISTICS
    # ========================================================================
    
    def get_daily_stats(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive daily statistics"""
        try:
            if not date:
                date = datetime.now().date()
            
            start_date = datetime.combine(date, datetime.min.time())
            end_date = datetime.combine(date, datetime.max.time())
            
            events = self.db.get_events_by_date_range(start_date, end_date)
            
            # Calculate daily stats
            feeding_count = len([e for e in events if 'feeding' in e['event_type']])
            sleep_events = [e for e in events if e['event_type'] in ['sleep_start', 'wake_up']]
            diaper_count = len([e for e in events if 'diaper' in e['event_type']])
            
            # Calculate sleep duration
            total_sleep_minutes = self._calculate_sleep_duration(sleep_events)
            
            return {
                'date': date.isoformat(),
                'feeding_count': feeding_count,
                'diaper_changes': diaper_count,
                'sleep_duration_hours': round(total_sleep_minutes / 60, 1),
                'total_events': len(events),
                'last_feeding': self._get_last_event_time(events, 'feeding'),
                'last_diaper': self._get_last_event_time(events, 'diaper'),
                'current_sleep_status': self._get_current_sleep_status(sleep_events)
            }
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}
    
    def get_weekly_stats(self, weeks_back: int = 1) -> Dict[str, Any]:
        """Get weekly statistics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks_back)
            
            events = self.db.get_events_by_date_range(start_date, end_date)
            
            # Group events by day
            daily_data = {}
            for event in events:
                event_date = datetime.fromisoformat(event['timestamp']).date()
                if event_date not in daily_data:
                    daily_data[event_date] = []
                daily_data[event_date].append(event)
            
            # Calculate weekly trends
            weekly_stats = {
                'total_feedings': len([e for e in events if 'feeding' in e['event_type']]),
                'total_diapers': len([e for e in events if 'diaper' in e['event_type']]),
                'daily_breakdown': {},
                'feeding_trend': [],
                'sleep_trend': [],
                'diaper_trend': []
            }
            
            # Calculate daily breakdown
            for date, day_events in daily_data.items():
                feeding_count = len([e for e in day_events if 'feeding' in e['event_type']])
                diaper_count = len([e for e in day_events if 'diaper' in e['event_type']])
                sleep_events = [e for e in day_events if e['event_type'] in ['sleep_start', 'wake_up']]
                sleep_duration = self._calculate_sleep_duration(sleep_events)
                
                weekly_stats['daily_breakdown'][date.isoformat()] = {
                    'feedings': feeding_count,
                    'diapers': diaper_count,
                    'sleep_hours': round(sleep_duration / 60, 1)
                }
                
                weekly_stats['feeding_trend'].append({'date': date.isoformat(), 'count': feeding_count})
                weekly_stats['diaper_trend'].append({'date': date.isoformat(), 'count': diaper_count})
                weekly_stats['sleep_trend'].append({'date': date.isoformat(), 'hours': round(sleep_duration / 60, 1)})
            
            return weekly_stats
            
        except Exception as e:
            logger.error(f"Error getting weekly stats: {e}")
            return {}
    
    # ========================================================================
    # FEEDING ANALYTICS
    # ========================================================================
    
    def get_feeding_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive feeding analytics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            events = self.db.get_events_by_date_range(start_date, end_date)
            feeding_events = [e for e in events if 'feeding' in e['event_type']]
            
            # Basic stats
            total_feedings = len(feeding_events)
            left_breast = len([e for e in feeding_events if e['event_type'] == 'feeding_start_left'])
            right_breast = len([e for e in feeding_events if e['event_type'] == 'feeding_start_right'])
            
            # Calculate feeding intervals
            intervals = self._calculate_feeding_intervals(feeding_events)
            
            # Hourly pattern analysis
            hourly_pattern = self._analyze_hourly_pattern(feeding_events)
            
            # Weekly pattern analysis
            weekly_pattern = self._analyze_weekly_pattern(feeding_events)
            
            return {
                'total_feedings': total_feedings,
                'daily_average': round(total_feedings / days, 1),
                'left_breast_count': left_breast,
                'right_breast_count': right_breast,
                'breast_balance': round((left_breast / total_feedings * 100) if total_feedings > 0 else 0, 1),
                'average_interval_hours': round(sum(intervals) / len(intervals), 1) if intervals else 0,
                'shortest_interval': min(intervals) if intervals else 0,
                'longest_interval': max(intervals) if intervals else 0,
                'hourly_pattern': hourly_pattern,
                'weekly_pattern': weekly_pattern,
                'feeding_timeline': self._create_feeding_timeline(feeding_events)
            }
            
        except Exception as e:
            logger.error(f"Error getting feeding analytics: {e}")
            return {}
    
    def _calculate_feeding_intervals(self, feeding_events: List[Dict]) -> List[float]:
        """Calculate time intervals between feedings"""
        intervals = []
        
        if len(feeding_events) < 2:
            return intervals
        
        # Sort events by timestamp
        sorted_events = sorted(feeding_events, key=lambda x: x['timestamp'])
        
        for i in range(1, len(sorted_events)):
            prev_time = datetime.fromisoformat(sorted_events[i-1]['timestamp'])
            curr_time = datetime.fromisoformat(sorted_events[i]['timestamp'])
            interval_hours = (curr_time - prev_time).total_seconds() / 3600
            intervals.append(interval_hours)
        
        return intervals
    
    def _analyze_hourly_pattern(self, events: List[Dict]) -> List[Dict]:
        """Analyze feeding patterns by hour of day"""
        hourly_counts = {hour: 0 for hour in range(24)}
        
        for event in events:
            hour = datetime.fromisoformat(event['timestamp']).hour
            hourly_counts[hour] += 1
        
        return [{'hour': hour, 'count': count} for hour, count in hourly_counts.items()]
    
    def _analyze_weekly_pattern(self, events: List[Dict]) -> List[Dict]:
        """Analyze feeding patterns by day of week"""
        daily_counts = {day: 0 for day in range(7)}  # 0 = Monday
        
        for event in events:
            day = datetime.fromisoformat(event['timestamp']).weekday()
            daily_counts[day] += 1
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return [{'day': day_names[day], 'count': count} for day, count in daily_counts.items()]
    
    def _create_feeding_timeline(self, feeding_events: List[Dict]) -> List[Dict]:
        """Create a timeline of recent feedings"""
        timeline = []
        sorted_events = sorted(feeding_events, key=lambda x: x['timestamp'], reverse=True)
        
        for event in sorted_events[:20]:  # Last 20 feedings
            timeline.append({
                'timestamp': event['timestamp'],
                'type': event['event_type'],
                'side': 'Left' if 'left' in event['event_type'] else 'Right' if 'right' in event['event_type'] else 'Unknown',
                'duration': event.get('duration'),
                'device_source': event.get('device_source', 'Manual')
            })
        
        return timeline
    
    # ========================================================================
    # SLEEP ANALYTICS
    # ========================================================================
    
    def get_sleep_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive sleep analytics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            events = self.db.get_events_by_date_range(start_date, end_date)
            sleep_events = [e for e in events if e['event_type'] in ['sleep_start', 'wake_up']]
            
            # Calculate sleep sessions
            sleep_sessions = self._calculate_sleep_sessions(sleep_events)
            
            # Calculate statistics
            total_sleep_hours = sum(session['duration_hours'] for session in sleep_sessions)
            avg_sleep_duration = sum(session['duration_hours'] for session in sleep_sessions) / len(sleep_sessions) if sleep_sessions else 0
            
            # Night vs day sleep analysis
            night_sleep, day_sleep = self._analyze_night_vs_day_sleep(sleep_sessions)
            
            # Sleep pattern analysis
            sleep_pattern = self._analyze_sleep_pattern(sleep_sessions)
            
            return {
                'total_sleep_sessions': len(sleep_sessions),
                'total_sleep_hours': round(total_sleep_hours, 1),
                'daily_sleep_average': round(total_sleep_hours / days, 1),
                'average_session_duration': round(avg_sleep_duration, 1),
                'longest_sleep_session': max([s['duration_hours'] for s in sleep_sessions]) if sleep_sessions else 0,
                'shortest_sleep_session': min([s['duration_hours'] for s in sleep_sessions]) if sleep_sessions else 0,
                'night_sleep_hours': round(night_sleep, 1),
                'day_sleep_hours': round(day_sleep, 1),
                'sleep_efficiency': self._calculate_sleep_efficiency(sleep_sessions),
                'sleep_pattern': sleep_pattern,
                'recent_sessions': sleep_sessions[-10:]  # Last 10 sessions
            }
            
        except Exception as e:
            logger.error(f"Error getting sleep analytics: {e}")
            return {}
    
    def _calculate_sleep_sessions(self, sleep_events: List[Dict]) -> List[Dict]:
        """Calculate sleep sessions from sleep_start and wake_up events"""
        sessions = []
        
        # Sort events by timestamp
        sorted_events = sorted(sleep_events, key=lambda x: x['timestamp'])
        
        current_sleep_start = None
        
        for event in sorted_events:
            if event['event_type'] == 'sleep_start':
                current_sleep_start = datetime.fromisoformat(event['timestamp'])
            elif event['event_type'] == 'wake_up' and current_sleep_start:
                wake_time = datetime.fromisoformat(event['timestamp'])
                duration_hours = (wake_time - current_sleep_start).total_seconds() / 3600
                
                sessions.append({
                    'start_time': current_sleep_start.isoformat(),
                    'end_time': wake_time.isoformat(),
                    'duration_hours': duration_hours,
                    'start_hour': current_sleep_start.hour,
                    'is_night_sleep': self._is_night_sleep(current_sleep_start, wake_time)
                })
                
                current_sleep_start = None
        
        return sessions
    
    def _is_night_sleep(self, start_time: datetime, end_time: datetime) -> bool:
        """Determine if a sleep session is night sleep (7 PM - 7 AM)"""
        start_hour = start_time.hour
        end_hour = end_time.hour
        
        # Night sleep typically starts between 6 PM and midnight
        # and ends between 5 AM and 10 AM
        return (start_hour >= 18 or start_hour <= 2) and (end_hour >= 5 and end_hour <= 10)
    
    def _analyze_night_vs_day_sleep(self, sleep_sessions: List[Dict]) -> tuple:
        """Analyze night vs day sleep totals"""
        night_sleep = sum(session['duration_hours'] for session in sleep_sessions if session['is_night_sleep'])
        day_sleep = sum(session['duration_hours'] for session in sleep_sessions if not session['is_night_sleep'])
        
        return night_sleep, day_sleep
    
    def _analyze_sleep_pattern(self, sleep_sessions: List[Dict]) -> List[Dict]:
        """Analyze sleep patterns by time of day"""
        hourly_sleep = {hour: 0 for hour in range(24)}
        
        for session in sleep_sessions:
            start_hour = datetime.fromisoformat(session['start_time']).hour
            hourly_sleep[start_hour] += session['duration_hours']
        
        return [{'hour': hour, 'sleep_hours': round(hours, 1)} for hour, hours in hourly_sleep.items()]
    
    def _calculate_sleep_efficiency(self, sleep_sessions: List[Dict]) -> float:
        """Calculate sleep efficiency (percentage of time actually sleeping)"""
        if not sleep_sessions:
            return 0
        
        # Simple efficiency calculation based on ideal vs actual sleep
        total_sleep = sum(session['duration_hours'] for session in sleep_sessions)
        days = len(set(datetime.fromisoformat(session['start_time']).date() for session in sleep_sessions))
        
        # Ideal sleep for babies: 14-17 hours per day
        ideal_sleep = days * 15.5  # Middle of recommended range
        efficiency = (total_sleep / ideal_sleep) * 100 if ideal_sleep > 0 else 0
        
        return round(min(efficiency, 100), 1)  # Cap at 100%
    
    def _calculate_sleep_duration(self, sleep_events: List[Dict]) -> float:
        """Calculate total sleep duration in minutes from events"""
        sessions = self._calculate_sleep_sessions(sleep_events)
        return sum(session['duration_hours'] * 60 for session in sessions)
    
    # ========================================================================
    # DIAPER ANALYTICS
    # ========================================================================
    
    def get_diaper_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive diaper analytics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            events = self.db.get_events_by_date_range(start_date, end_date)
            diaper_events = [e for e in events if 'diaper' in e['event_type']]
            
            # Count different types
            pee_count = len([e for e in diaper_events if e['event_type'] in ['diaper_pee', 'diaper_both']])
            poo_count = len([e for e in diaper_events if e['event_type'] in ['diaper_poo', 'diaper_both']])
            total_changes = len(diaper_events)
            
            # Calculate intervals
            intervals = self._calculate_diaper_intervals(diaper_events)
            
            # Pattern analysis
            hourly_pattern = self._analyze_hourly_pattern(diaper_events)
            daily_pattern = self._analyze_daily_diaper_pattern(diaper_events)
            
            return {
                'total_changes': total_changes,
                'daily_average': round(total_changes / days, 1),
                'pee_count': pee_count,
                'poo_count': poo_count,
                'both_count': len([e for e in diaper_events if e['event_type'] == 'diaper_both']),
                'pee_percentage': round((pee_count / total_changes * 100) if total_changes > 0 else 0, 1),
                'poo_percentage': round((poo_count / total_changes * 100) if total_changes > 0 else 0, 1),
                'average_interval_hours': round(sum(intervals) / len(intervals), 1) if intervals else 0,
                'shortest_interval': round(min(intervals), 1) if intervals else 0,
                'longest_interval': round(max(intervals), 1) if intervals else 0,
                'hourly_pattern': hourly_pattern,
                'daily_pattern': daily_pattern,
                'recent_changes': diaper_events[-10:]  # Last 10 changes
            }
            
        except Exception as e:
            logger.error(f"Error getting diaper analytics: {e}")
            return {}
    
    def _calculate_diaper_intervals(self, diaper_events: List[Dict]) -> List[float]:
        """Calculate time intervals between diaper changes"""
        intervals = []
        
        if len(diaper_events) < 2:
            return intervals
        
        sorted_events = sorted(diaper_events, key=lambda x: x['timestamp'])
        
        for i in range(1, len(sorted_events)):
            prev_time = datetime.fromisoformat(sorted_events[i-1]['timestamp'])
            curr_time = datetime.fromisoformat(sorted_events[i]['timestamp'])
            interval_hours = (curr_time - prev_time).total_seconds() / 3600
            intervals.append(interval_hours)
        
        return intervals
    
    def _analyze_daily_diaper_pattern(self, diaper_events: List[Dict]) -> List[Dict]:
        """Analyze diaper changes by day"""
        daily_data = {}
        
        for event in diaper_events:
            date = datetime.fromisoformat(event['timestamp']).date()
            if date not in daily_data:
                daily_data[date] = {'pee': 0, 'poo': 0, 'both': 0, 'total': 0}
            
            event_type = event['event_type']
            if event_type == 'diaper_pee':
                daily_data[date]['pee'] += 1
            elif event_type == 'diaper_poo':
                daily_data[date]['poo'] += 1
            elif event_type == 'diaper_both':
                daily_data[date]['both'] += 1
            
            daily_data[date]['total'] += 1
        
        return [
            {
                'date': date.isoformat(),
                'pee': data['pee'],
                'poo': data['poo'],
                'both': data['both'],
                'total': data['total']
            }
            for date, data in sorted(daily_data.items())
        ]
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_live_stats(self) -> Dict[str, Any]:
        """Get live statistics for real-time dashboard"""
        try:
            today_stats = self.get_daily_stats()
            
            # Get current status
            recent_events = self.db.get_recent_events(limit=5)
            last_feeding = None
            last_diaper = None
            current_sleep_status = 'awake'
            
            for event in recent_events:
                if 'feeding' in event['event_type'] and not last_feeding:
                    last_feeding = event
                elif 'diaper' in event['event_type'] and not last_diaper:
                    last_diaper = event
                elif event['event_type'] == 'sleep_start':
                    current_sleep_status = 'sleeping'
                    break
                elif event['event_type'] == 'wake_up':
                    current_sleep_status = 'awake'
                    break
            
            return {
                'today': today_stats,
                'current_status': {
                    'sleep_status': current_sleep_status,
                    'last_feeding': last_feeding,
                    'last_diaper': last_diaper,
                    'time_since_last_feeding': self._calculate_time_since(last_feeding) if last_feeding else None,
                    'time_since_last_diaper': self._calculate_time_since(last_diaper) if last_diaper else None
                },
                'recent_events': recent_events
            }
            
        except Exception as e:
            logger.error(f"Error getting live stats: {e}")
            return {}
    
    def _get_last_event_time(self, events: List[Dict], event_category: str) -> Optional[str]:
        """Get timestamp of last event in category"""
        category_events = [e for e in events if event_category in e['event_type']]
        if category_events:
            latest = max(category_events, key=lambda x: x['timestamp'])
            return latest['timestamp']
        return None
    
    def _get_current_sleep_status(self, sleep_events: List[Dict]) -> str:
        """Determine current sleep status"""
        if not sleep_events:
            return 'unknown'
        
        # Sort by timestamp and get the latest event
        latest_event = max(sleep_events, key=lambda x: x['timestamp'])
        
        return 'sleeping' if latest_event['event_type'] == 'sleep_start' else 'awake'
    
    def _calculate_time_since(self, event: Dict) -> Dict[str, Any]:
        """Calculate time since an event"""
        if not event:
            return None
        
        event_time = datetime.fromisoformat(event['timestamp'])
        now = datetime.now()
        diff = now - event_time
        
        hours = diff.total_seconds() / 3600
        minutes = (diff.total_seconds() % 3600) / 60
        
        return {
            'hours': int(hours),
            'minutes': int(minutes),
            'total_minutes': int(diff.total_seconds() / 60),
            'human_readable': f"{int(hours)}h {int(minutes)}m ago" if hours >= 1 else f"{int(minutes)}m ago"
        }
    
    # ========================================================================
    # DATA EXPORT
    # ========================================================================
    
    def export_data(self, format: str, days: int = 30) -> str:
        """Export data in specified format"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            events = self.db.get_events_by_date_range(start_date, end_date)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format == 'csv':
                return self._export_csv(events, timestamp)
            elif format == 'json':
                return self._export_json(events, timestamp)
            elif format == 'pdf':
                return self._export_pdf(events, timestamp)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise
    
    def _export_csv(self, events: List[Dict], timestamp: str) -> str:
        """Export events to CSV"""
        df = pd.DataFrame(events)
        filename = f"baby_care_export_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath
    
    def _export_json(self, events: List[Dict], timestamp: str) -> str:
        """Export events to JSON"""
        filename = f"baby_care_export_{timestamp}.json"
        filepath = os.path.join(self.export_dir, filename)
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_events': len(events),
            'events': events,
            'summary': {
                'feeding_events': len([e for e in events if 'feeding' in e['event_type']]),
                'sleep_events': len([e for e in events if e['event_type'] in ['sleep_start', 'wake_up']]),
                'diaper_events': len([e for e in events if 'diaper' in e['event_type']])
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath
    
    def _export_pdf(self, events: List[Dict], timestamp: str) -> str:
        """Export events to PDF report"""
        # This would require additional PDF libraries like ReportLab
        # For now, we'll create a simple text-based report
        filename = f"baby_care_report_{timestamp}.txt"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("Baby Care Tracker Report\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Events: {len(events)}\n\n")
            
            # Summary statistics
            feeding_events = [e for e in events if 'feeding' in e['event_type']]
            sleep_events = [e for e in events if e['event_type'] in ['sleep_start', 'wake_up']]
            diaper_events = [e for e in events if 'diaper' in e['event_type']]
            
            f.write("Summary:\n")
            f.write(f"- Feeding Events: {len(feeding_events)}\n")
            f.write(f"- Sleep Events: {len(sleep_events)}\n")
            f.write(f"- Diaper Changes: {len(diaper_events)}\n\n")
            
            # Recent events
            f.write("Recent Events:\n")
            for event in sorted(events, key=lambda x: x['timestamp'], reverse=True)[:20]:
                f.write(f"- {event['timestamp']}: {event['event_type']}\n")
        
        return filepath
    
    def generate_daily_report(self, date: Optional[datetime] = None):
        """Generate automated daily report"""
        try:
            if not date:
                date = datetime.now().date()
            
            stats = self.get_daily_stats(date)
            
            # Save daily report
            report_data = {
                'date': date.isoformat(),
                'stats': stats,
                'generated_at': datetime.now().isoformat()
            }
            
            filename = f"daily_report_{date.strftime('%Y%m%d')}.json"
            filepath = os.path.join(self.export_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"Generated daily report for {date}")
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
