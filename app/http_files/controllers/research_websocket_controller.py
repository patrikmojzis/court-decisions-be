import json
import threading
from typing import Dict, Set

from flask import request
from flask_socketio import SocketIO, emit

from app.utils.redis_utils import redis_events_pubsub_client

# Track active connections per research_id
active_connections: Dict[str, Set[str]] = {}
connection_lock = threading.Lock()

def init_socketio(app):
    """Initialize SocketIO with the Flask app"""
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to research stream'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
        # Clean up from all research channels
        with connection_lock:
            for research_id, connections in active_connections.items():
                connections.discard(request.sid)
                if not connections:
                    # Stop listening if no more connections for this research_id
                    del active_connections[research_id]

    @socketio.on('subscribe')
    def handle_subscribe(data):
        """Subscribe to research updates for a specific research_id"""
        research_id = data.get('research_id')
        if not research_id:
            emit('error', {'message': 'research_id is required'})
            return
        
        print(f"Client {request.sid} subscribing to research: {research_id}")
        
        with connection_lock:
            if research_id not in active_connections:
                active_connections[research_id] = set()
                # Start Redis listener for this research_id in a separate thread
                thread = threading.Thread(
                    target=redis_listener,
                    args=(research_id, socketio),
                    daemon=True
                )
                thread.start()
            
            active_connections[research_id].add(request.sid)
        
        emit('subscribed', {'research_id': research_id, 'message': 'Subscribed to research updates'})

    @socketio.on('unsubscribe')
    def handle_unsubscribe(data):
        """Unsubscribe from research updates"""
        research_id = data.get('research_id')
        if not research_id:
            emit('error', {'message': 'research_id is required'})
            return
        
        print(f"Client {request.sid} unsubscribing from research: {research_id}")
        
        with connection_lock:
            if research_id in active_connections:
                active_connections[research_id].discard(request.sid)
                if not active_connections[research_id]:
                    del active_connections[research_id]
        
        emit('unsubscribed', {'research_id': research_id, 'message': 'Unsubscribed from research updates'})

    return socketio


def redis_listener(research_id: str, socketio):
    """Listen for Redis pub/sub messages for a specific research_id"""
    pubsub = redis_events_pubsub_client.pubsub()
    channel_name = f"research:{research_id}"
    pubsub.subscribe(channel_name)
    
    print(f"Started Redis listener for channel: {channel_name}")
    
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    event_data = json.loads(message['data'])
                    
                    # Check if we still have active connections for this research_id
                    with connection_lock:
                        if research_id not in active_connections:
                            print(f"No active connections for {research_id}, stopping listener")
                            break
                        
                        connections = active_connections[research_id].copy()
                    
                    # Emit to all connected clients for this research_id
                    for sid in connections:
                        socketio.emit('update_research', event_data, room=sid)
                        
                except json.JSONDecodeError as e:
                    print(f"Failed to decode Redis message: {e}")
                except Exception as e:
                    print(f"Error processing Redis message: {e}")
    
    except Exception as e:
        print(f"Redis listener error for {research_id}: {e}")
    finally:
        pubsub.close()
        # Clean up connections
        with connection_lock:
            if research_id in active_connections:
                del active_connections[research_id] 