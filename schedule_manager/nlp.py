"""
Natural language date/time parsing utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import re
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pytz


class DateTimeParser:
    def __init__(self, timezone: str = "America/Los_Angeles"):
        self.timezone = pytz.timezone(timezone)
    
    def parse(self, text: str, base_time: Optional[datetime] = None) -> Optional[datetime]:
        """
        Parse natural language date/time into datetime object
        
        Examples:
        - "tomorrow at 3pm"
        - "next monday 10:00"
        - "in 2 hours"
        - "jan 15 at 2:30pm"
        - "friday 14:00"
        """
        if base_time is None:
            base_time = datetime.now(self.timezone)
        
        text = text.lower().strip()
        
        # Handle relative times
        relative_result = self._parse_relative(text, base_time)
        if relative_result:
            return relative_result
        
        # Handle day-based references
        day_result = self._parse_day_reference(text, base_time)
        if day_result:
            return day_result
        
        # Try dateutil parser as fallback
        try:
            result = parser.parse(text, default=base_time, fuzzy=True)
            # Localize to timezone if naive
            if result.tzinfo is None:
                result = self.timezone.localize(result)
            return result
        except:
            pass
        
        return None
    
    def _parse_relative(self, text: str, base_time: datetime) -> Optional[datetime]:
        """Parse relative time expressions like 'in 2 hours', 'in 30 minutes'"""
        
        # "in X minutes/hours/days"
        match = re.search(r'in\s+(\d+)\s+(minute|minutes|min|hour|hours|hr|day|days)', text)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit.startswith('min'):
                return base_time + timedelta(minutes=amount)
            elif unit.startswith('hour') or unit.startswith('hr'):
                return base_time + timedelta(hours=amount)
            elif unit.startswith('day'):
                return base_time + timedelta(days=amount)
        
        # "tomorrow"
        if 'tomorrow' in text:
            tomorrow = base_time + timedelta(days=1)
            time_result = self._extract_time(text)
            if time_result:
                tomorrow = tomorrow.replace(hour=time_result[0], minute=time_result[1], second=0, microsecond=0)
            else:
                tomorrow = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
            return tomorrow
        
        # "today"
        if 'today' in text:
            time_result = self._extract_time(text)
            if time_result:
                return base_time.replace(hour=time_result[0], minute=time_result[1], second=0, microsecond=0)
        
        return None
    
    def _parse_day_reference(self, text: str, base_time: datetime) -> Optional[datetime]:
        """Parse day references like 'monday', 'next friday', 'this wednesday'"""
        
        days = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1, 'tues': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3, 'thur': 3, 'thurs': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        
        for day_name, day_num in days.items():
            if day_name in text:
                current_day = base_time.weekday()
                days_ahead = day_num - current_day
                
                # If the day has passed this week or is today, move to next week
                if days_ahead <= 0:
                    days_ahead += 7
                
                # Handle "next" modifier (always next week)
                if 'next' in text:
                    if days_ahead < 7:
                        days_ahead += 7
                
                target_date = base_time + timedelta(days=days_ahead)
                
                # Extract time if present
                time_result = self._extract_time(text)
                if time_result:
                    target_date = target_date.replace(hour=time_result[0], minute=time_result[1], second=0, microsecond=0)
                else:
                    target_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
                
                return target_date
        
        return None
    
    def _extract_time(self, text: str) -> Optional[Tuple[int, int]]:
        """Extract time from text like '3pm', '14:30', '10:00am'"""
        
        # Match patterns like "3pm", "3:30pm", "15:00", "3:30 pm"
        match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?', text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            meridiem = match.group(3)
            
            if meridiem and meridiem.lower().startswith('p') and hour < 12:
                hour += 12
            elif meridiem and meridiem.lower().startswith('a') and hour == 12:
                hour = 0
            
            # Assume 24-hour format if no meridiem and hour > 12
            if not meridiem and hour > 23:
                return None
            
            return (hour, minute)
        
        return None
    
    def parse_duration(self, text: str) -> int:
        """
        Parse duration from text into minutes
        
        Examples:
        - "30 minutes" -> 30
        - "1 hour" -> 60
        - "1.5 hours" -> 90
        - "2h 30m" -> 150
        """
        total_minutes = 0
        
        # Match "X hours"
        hour_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hour|hours|hr|hrs|h)', text)
        if hour_match:
            hours = float(hour_match.group(1))
            total_minutes += int(hours * 60)
        
        # Match "X minutes"
        min_match = re.search(r'(\d+)\s*(?:minute|minutes|min|mins|m)', text)
        if min_match:
            minutes = int(min_match.group(1))
            total_minutes += minutes
        
        return total_minutes if total_minutes > 0 else 30  # Default to 30 minutes
    
    def parse_recurrence(self, text: str) -> Optional[dict]:
        """
        Parse recurrence patterns from text
        
        Examples:
        - "every monday" -> {"days": ["mon"], "time": None}
        - "mon, wed, fri at 12:00" -> {"days": ["mon", "wed", "fri"], "time": "12:00"}
        - "daily at 9am" -> {"days": ["all"], "time": "09:00"}
        - "weekdays" -> {"days": ["mon", "tue", "wed", "thu", "fri"], "time": None}
        """
        text = text.lower()
        
        # Daily pattern
        if 'daily' in text or 'every day' in text:
            time_result = self._extract_time(text)
            return {
                "days": ["all"],
                "time": f"{time_result[0]:02d}:{time_result[1]:02d}" if time_result else None
            }
        
        # Weekdays pattern
        if 'weekday' in text:
            time_result = self._extract_time(text)
            return {
                "days": ["mon", "tue", "wed", "thu", "fri"],
                "time": f"{time_result[0]:02d}:{time_result[1]:02d}" if time_result else None
            }
        
        # Specific days pattern
        day_abbrevs = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        found_days = []
        for i, (abbrev, name) in enumerate(zip(day_abbrevs, day_names)):
            if abbrev in text or name in text:
                found_days.append(abbrev)
        
        if found_days:
            time_result = self._extract_time(text)
            return {
                "days": found_days,
                "time": f"{time_result[0]:02d}:{time_result[1]:02d}" if time_result else None
            }
        
        return None
