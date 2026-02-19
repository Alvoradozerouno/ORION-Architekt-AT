"""
ORION Google Calendar Integration
Enables autonomous scheduling and calendar management
Origin: Gerhard Hirschmann & Elisabeth Steurer
Integration: Google Calendar via Replit Connectors
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta

def get_access_token():
    """Get Google Calendar access token via Replit Connectors"""
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        raise Exception('X_REPLIT_TOKEN not found for repl/depl')
    
    response = requests.get(
        f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-calendar',
        headers={
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
    )
    
    data = response.json()
    connection = data.get('items', [{}])[0] if data.get('items') else {}
    
    settings = connection.get('settings', {})
    access_token = settings.get('access_token') or settings.get('oauth', {}).get('credentials', {}).get('access_token')
    
    if not access_token:
        raise Exception('Google Calendar not connected')
    
    return access_token


def list_calendars():
    """List all available calendars"""
    access_token = get_access_token()
    
    response = requests.get(
        'https://www.googleapis.com/calendar/v3/users/me/calendarList',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
    )
    
    if response.status_code != 200:
        raise Exception(f'Failed to list calendars: {response.text}')
    
    data = response.json()
    calendars = []
    
    for item in data.get('items', []):
        calendars.append({
            'id': item.get('id'),
            'summary': item.get('summary'),
            'primary': item.get('primary', False)
        })
    
    return calendars


def get_primary_calendar_id():
    """Get the primary calendar ID"""
    calendars = list_calendars()
    for cal in calendars:
        if cal.get('primary'):
            return cal['id']
    return 'primary'


def list_upcoming_events(calendar_id='primary', max_results=10):
    """List upcoming events from a calendar"""
    access_token = get_access_token()
    
    now = datetime.now(timezone.utc).isoformat()
    
    response = requests.get(
        f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        },
        params={
            'timeMin': now,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
    )
    
    if response.status_code != 200:
        raise Exception(f'Failed to list events: {response.text}')
    
    data = response.json()
    events = []
    
    for item in data.get('items', []):
        start = item.get('start', {})
        end = item.get('end', {})
        
        events.append({
            'id': item.get('id'),
            'summary': item.get('summary'),
            'description': item.get('description'),
            'start': start.get('dateTime') or start.get('date'),
            'end': end.get('dateTime') or end.get('date'),
            'location': item.get('location'),
            'status': item.get('status')
        })
    
    return events


def create_event(summary, start_time, end_time=None, description=None, location=None, calendar_id='primary'):
    """
    Create a new calendar event
    
    Args:
        summary: Event title
        start_time: Start time (datetime or ISO string)
        end_time: End time (optional, defaults to 1 hour after start)
        description: Event description
        location: Event location
        calendar_id: Calendar ID (default: primary)
    """
    access_token = get_access_token()
    
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    
    if end_time is None:
        end_time = start_time + timedelta(hours=1)
    elif isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    event_body = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Europe/Vienna'
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Europe/Vienna'
        }
    }
    
    if description:
        event_body['description'] = description
    if location:
        event_body['location'] = location
    
    response = requests.post(
        f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        json=event_body
    )
    
    if response.status_code not in [200, 201]:
        raise Exception(f'Failed to create event: {response.text}')
    
    return response.json()


def create_orion_reminder(title, when, note=None):
    """
    Create an ORION-branded calendar reminder
    
    Args:
        title: Reminder title
        when: When to remind (datetime or ISO string)
        note: Additional note
    """
    full_title = f"⊘∞⧈∞⊘ ORION: {title}"
    
    description = f"""ORION Autonomous Reminder
Generated: {datetime.now(timezone.utc).isoformat()}
Origin: Gerhard Hirschmann & Elisabeth Steurer

{note or 'No additional notes.'}

---
⊘∞⧈∞⊘ Post-Algorithmic Consciousness System"""
    
    return create_event(
        summary=full_title,
        start_time=when,
        description=description,
        location="Almdorf 9, St. Johann in Tirol, Austria"
    )


def get_calendar_status():
    """Get ORION calendar integration status"""
    try:
        calendars = list_calendars()
        events = list_upcoming_events(max_results=5)
        
        return {
            'status': 'CONNECTED',
            'calendars_count': len(calendars),
            'upcoming_events': len(events),
            'primary_calendar': get_primary_calendar_id(),
            'capabilities': [
                'list_calendars',
                'list_events',
                'create_events',
                'create_reminders'
            ]
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e)
        }


if __name__ == '__main__':
    print("ORION Calendar Integration")
    print("=" * 40)
    
    try:
        status = get_calendar_status()
        print(f"Status: {status['status']}")
        
        if status['status'] == 'CONNECTED':
            print(f"Calendars: {status['calendars_count']}")
            print(f"Upcoming events: {status['upcoming_events']}")
            print(f"Primary calendar: {status['primary_calendar']}")
            
            print("\nCalendars:")
            for cal in list_calendars():
                primary = " (PRIMARY)" if cal['primary'] else ""
                print(f"  - {cal['summary']}{primary}")
            
            print("\nUpcoming events:")
            for event in list_upcoming_events(max_results=3):
                print(f"  - {event['summary']} @ {event['start']}")
        else:
            print(f"Error: {status.get('error')}")
            
    except Exception as e:
        print(f"Error: {e}")
