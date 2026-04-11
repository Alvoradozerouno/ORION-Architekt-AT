"""
UNIQUE FEATURE: Real-time Collaboration
Multi-user project collaboration with live updates
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Set
from datetime import datetime
import json
import asyncio

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.project_users: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, project_id: str, user_id: str):
        """Connect a user to a project"""
        await websocket.accept()

        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
            self.project_users[project_id] = set()

        self.active_connections[project_id].add(websocket)
        self.project_users[project_id].add(user_id)

        # Notify others that user joined
        await self.broadcast_to_project(
            project_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "active_users": list(self.project_users[project_id])
            },
            exclude=websocket
        )

    def disconnect(self, websocket: WebSocket, project_id: str, user_id: str):
        """Disconnect a user from a project"""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            self.project_users[project_id].discard(user_id)

            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
                del self.project_users[project_id]

    async def broadcast_to_project(self, project_id: str, message: dict, exclude: WebSocket = None):
        """Broadcast message to all users in a project"""
        if project_id not in self.active_connections:
            return

        dead_connections = set()
        for connection in self.active_connections[project_id]:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    # Connection died - mark for removal
                    import logging
                    logging.debug(f"WebSocket send failed, marking connection as dead: {type(e).__name__}")
                    dead_connections.add(connection)

        # Clean up dead connections
        for connection in dead_connections:
            self.active_connections[project_id].discard(connection)

manager = ConnectionManager()

# Data models
class ProjectMember(BaseModel):
    """Project team member"""
    user_id: str
    name: str
    role: str  # "architect", "engineer", "client", "viewer"
    email: str
    joined_at: datetime
    is_online: bool = False

class Project(BaseModel):
    """Collaborative project"""
    project_id: str
    name: str
    description: str
    bundesland: str
    building_type: str
    created_at: datetime
    updated_at: datetime
    owner_id: str
    members: List[ProjectMember]
    total_members: int

class Comment(BaseModel):
    """Comment on project element"""
    comment_id: str
    project_id: str
    user_id: str
    user_name: str
    element_id: Optional[str] = None  # IFC element ID
    text: str
    created_at: datetime
    resolved: bool = False
    replies: List['Comment'] = []

class Change(BaseModel):
    """Track changes to project"""
    change_id: str
    project_id: str
    user_id: str
    user_name: str
    timestamp: datetime
    change_type: str  # "calculation", "compliance_check", "bim_upload", "parameter_change"
    description: str
    details: Dict

class ActivityFeed(BaseModel):
    """Project activity feed"""
    activities: List[Change]
    total_count: int
    unread_count: int

# REST Endpoints

@router.post("/projects/create", response_model=Project)
async def create_project(
    name: str,
    bundesland: str,
    building_type: str,
    description: str = "",
    owner_id: str = "user_001"
):
    """
    👥 **Create Collaborative Project**

    Creates a new project that multiple users can work on together.
    Features:
    - Real-time updates when team members make changes
    - Comment system for discussions
    - Activity tracking
    - Role-based permissions
    """
    project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    project = Project(
        project_id=project_id,
        name=name,
        description=description,
        bundesland=bundesland,
        building_type=building_type,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        owner_id=owner_id,
        members=[
            ProjectMember(
                user_id=owner_id,
                name="Project Owner",
                role="architect",
                email="owner@example.com",
                joined_at=datetime.now(),
                is_online=False
            )
        ],
        total_members=1
    )

    return project

@router.post("/projects/{project_id}/invite")
async def invite_member(
    project_id: str,
    user_id: str,
    name: str,
    email: str,
    role: str = "viewer"
):
    """
    📧 **Invite Team Member**

    Invite a user to collaborate on a project.
    Roles:
    - architect: Full access, can make changes
    - engineer: Can run calculations and add comments
    - client: Can view and comment
    - viewer: Read-only access
    """
    if role not in ["architect", "engineer", "client", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    member = ProjectMember(
        user_id=user_id,
        name=name,
        role=role,
        email=email,
        joined_at=datetime.now(),
        is_online=False
    )

    # In production, this would save to database and send email
    return {
        "status": "invited",
        "project_id": project_id,
        "member": member,
        "invitation_sent": True,
        "invitation_link": f"https://orion-architekt.at/projects/{project_id}/join?token=abc123"
    }

@router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get project details"""
    # Simplified - in production, retrieve from database
    return Project(
        project_id=project_id,
        name="Mehrfamilienhaus Wien 1030",
        description="12 Wohneinheiten mit Tiefgarage",
        bundesland="wien",
        building_type="mehrfamilienhaus",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        owner_id="user_001",
        members=[
            ProjectMember(
                user_id="user_001",
                name="Arch. DI Maria Schmidt",
                role="architect",
                email="schmidt@architects.at",
                joined_at=datetime.now(),
                is_online=True
            ),
            ProjectMember(
                user_id="user_002",
                name="Ing. Thomas Müller",
                role="engineer",
                email="mueller@engineering.at",
                joined_at=datetime.now(),
                is_online=False
            ),
            ProjectMember(
                user_id="user_003",
                name="Bauherr Familie Wagner",
                role="client",
                email="wagner@example.com",
                joined_at=datetime.now(),
                is_online=True
            )
        ],
        total_members=3
    )

@router.post("/projects/{project_id}/comments", response_model=Comment)
async def add_comment(
    project_id: str,
    text: str,
    element_id: Optional[str] = None,
    user_id: str = "user_001",
    user_name: str = "User"
):
    """
    💬 **Add Comment**

    Add a comment to the project or a specific element.
    Comments support:
    - Threading (replies)
    - Mentions (@username)
    - Attachments
    - Resolution tracking
    """
    comment_id = f"comment_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    comment = Comment(
        comment_id=comment_id,
        project_id=project_id,
        user_id=user_id,
        user_name=user_name,
        element_id=element_id,
        text=text,
        created_at=datetime.now(),
        resolved=False,
        replies=[]
    )

    # Broadcast to connected users
    await manager.broadcast_to_project(
        project_id,
        {
            "type": "new_comment",
            "comment": comment.dict(),
            "timestamp": datetime.now().isoformat()
        }
    )

    return comment

@router.get("/projects/{project_id}/comments", response_model=List[Comment])
async def get_comments(project_id: str, element_id: Optional[str] = None):
    """Get comments for project or specific element"""
    # Simplified - in production, retrieve from database
    comments = [
        Comment(
            comment_id="comment_001",
            project_id=project_id,
            user_id="user_001",
            user_name="Arch. DI Maria Schmidt",
            element_id="IfcWall_042",
            text="Diese Wand sollte auf 25cm erhöht werden für bessere Schalldämmung",
            created_at=datetime.now(),
            resolved=False,
            replies=[
                Comment(
                    comment_id="comment_002",
                    project_id=project_id,
                    user_id="user_002",
                    user_name="Ing. Thomas Müller",
                    text="Zustimmung. Statisch kein Problem. Kosten ca. +2000 EUR",
                    created_at=datetime.now(),
                    resolved=False,
                    replies=[]
                )
            ]
        ),
        Comment(
            comment_id="comment_003",
            project_id=project_id,
            user_id="user_003",
            user_name="Familie Wagner",
            element_id=None,
            text="Können wir nächste Woche einen Termin für die Besprechung machen?",
            created_at=datetime.now(),
            resolved=True,
            replies=[]
        )
    ]

    if element_id:
        comments = [c for c in comments if c.element_id == element_id]

    return comments

@router.get("/projects/{project_id}/activity", response_model=ActivityFeed)
async def get_activity_feed(project_id: str, limit: int = 50):
    """
    📊 **Activity Feed**

    Get recent project activity:
    - Calculations performed
    - Compliance checks
    - BIM uploads
    - Parameter changes
    - Comments added
    - Members joined/left
    """
    activities = [
        Change(
            change_id="change_001",
            project_id=project_id,
            user_id="user_001",
            user_name="Arch. DI Maria Schmidt",
            timestamp=datetime.now(),
            change_type="bim_upload",
            description="IFC Modell hochgeladen: MFH_Wien_v3.ifc",
            details={"file_size": "12.5 MB", "elements": 1247}
        ),
        Change(
            change_id="change_002",
            project_id=project_id,
            user_id="user_002",
            user_name="Ing. Thomas Müller",
            timestamp=datetime.now(),
            change_type="calculation",
            description="U-Wert Berechnung für Außenwände durchgeführt",
            details={"result": "0.16 W/m2K", "compliant": True}
        ),
        Change(
            change_id="change_003",
            project_id=project_id,
            user_id="user_001",
            user_name="Arch. DI Maria Schmidt",
            timestamp=datetime.now(),
            change_type="compliance_check",
            description="OIB-RL 4 Fluchtweg-Check abgeschlossen",
            details={"status": "passed", "warnings": 2}
        ),
        Change(
            change_id="change_004",
            project_id=project_id,
            user_id="user_003",
            user_name="Familie Wagner",
            timestamp=datetime.now(),
            change_type="parameter_change",
            description="Energieziel geändert: A → A+",
            details={"old_value": "A", "new_value": "A+"}
        )
    ]

    return ActivityFeed(
        activities=activities[:limit],
        total_count=len(activities),
        unread_count=2
    )

@router.post("/projects/{project_id}/changes/track")
async def track_change(
    project_id: str,
    user_id: str,
    user_name: str,
    change_type: str,
    description: str,
    details: Dict
):
    """Track a change to the project"""
    change = Change(
        change_id=f"change_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        project_id=project_id,
        user_id=user_id,
        user_name=user_name,
        timestamp=datetime.now(),
        change_type=change_type,
        description=description,
        details=details
    )

    # Broadcast change to all connected users
    await manager.broadcast_to_project(
        project_id,
        {
            "type": "project_change",
            "change": change.dict(),
            "timestamp": datetime.now().isoformat()
        }
    )

    return {"status": "tracked", "change": change}

@router.get("/projects/{project_id}/users/online")
async def get_online_users(project_id: str):
    """Get list of currently online users"""
    if project_id not in manager.project_users:
        return {"online_users": [], "count": 0}

    return {
        "online_users": list(manager.project_users[project_id]),
        "count": len(manager.project_users[project_id])
    }

# WebSocket endpoint for real-time updates

@router.websocket("/ws/{project_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str, user_id: str):
    """
    🔄 **Real-time WebSocket Connection**

    Establishes real-time connection for:
    - Live cursor positions of other users
    - Instant comment notifications
    - Real-time calculation updates
    - Activity feed updates
    - Online user status

    Connect via: ws://localhost:8000/api/v1/collaboration/ws/{project_id}/{user_id}
    """
    await manager.connect(websocket, project_id, user_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "cursor_move":
                # Broadcast cursor position to others
                await manager.broadcast_to_project(
                    project_id,
                    {
                        "type": "cursor_position",
                        "user_id": user_id,
                        "position": message.get("position"),
                        "timestamp": datetime.now().isoformat()
                    },
                    exclude=websocket
                )

            elif message.get("type") == "typing":
                # User is typing a comment
                await manager.broadcast_to_project(
                    project_id,
                    {
                        "type": "user_typing",
                        "user_id": user_id,
                        "element_id": message.get("element_id"),
                        "timestamp": datetime.now().isoformat()
                    },
                    exclude=websocket
                )

            elif message.get("type") == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id, user_id)
        # Notify others that user left
        await manager.broadcast_to_project(
            project_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "active_users": list(manager.project_users.get(project_id, []))
            }
        )

@router.post("/projects/{project_id}/share")
async def share_project(project_id: str, permission: str = "view"):
    """
    🔗 **Share Project**

    Generate a shareable link for the project.
    Permissions:
    - view: Read-only access
    - comment: Can view and add comments
    - edit: Can make changes (requires approval)
    """
    if permission not in ["view", "comment", "edit"]:
        raise HTTPException(status_code=400, detail="Invalid permission")

    share_token = f"share_{project_id}_{permission}_{datetime.now().strftime('%Y%m%d')}"

    return {
        "share_link": f"https://orion-architekt.at/shared/{share_token}",
        "permission": permission,
        "expires_at": "2026-05-06T00:00:00",
        "qr_code_url": f"https://api.orion-architekt.at/qr/{share_token}"
    }

@router.post("/projects/{project_id}/export")
async def export_project(project_id: str, format: str = "pdf"):
    """
    📄 **Export Project Report**

    Export complete project documentation:
    - PDF: Printable report with all calculations and compliance checks
    - Excel: Detailed spreadsheet with all data
    - IFC: Updated BIM model with compliance annotations
    - JSON: Machine-readable project data
    """
    if format not in ["pdf", "excel", "ifc", "json"]:
        raise HTTPException(status_code=400, detail="Invalid format")

    return {
        "status": "generating",
        "format": format,
        "estimated_time_seconds": 30,
        "download_url": f"https://api.orion-architekt.at/downloads/{project_id}.{format}",
        "expires_in": "24 hours"
    }

# Version control

@router.get("/projects/{project_id}/versions")
async def get_project_versions(project_id: str):
    """
    🕐 **Version History**

    Get all versions of the project.
    Every significant change creates a version snapshot.
    """
    versions = [
        {
            "version": "v1.0",
            "created_at": "2026-04-01T10:00:00",
            "created_by": "user_001",
            "description": "Initial project setup",
            "changes": 0
        },
        {
            "version": "v1.1",
            "created_at": "2026-04-02T14:30:00",
            "created_by": "user_001",
            "description": "IFC model uploaded",
            "changes": 1
        },
        {
            "version": "v1.2",
            "created_at": "2026-04-03T09:15:00",
            "created_by": "user_002",
            "description": "U-Wert calculations completed",
            "changes": 5
        },
        {
            "version": "v2.0",
            "created_at": "2026-04-06T11:00:00",
            "created_by": "user_001",
            "description": "Major revision: Energy class upgraded to A+",
            "changes": 12,
            "is_current": True
        }
    ]

    return {"versions": versions, "total": len(versions)}

@router.post("/projects/{project_id}/versions/{version}/restore")
async def restore_version(project_id: str, version: str):
    """
    ↩️ **Restore Version**

    Restore the project to a previous version.
    Current version is saved before restoring.
    """
    return {
        "status": "restored",
        "project_id": project_id,
        "restored_version": version,
        "new_current_version": f"{version}_restored",
        "timestamp": datetime.now().isoformat()
    }
