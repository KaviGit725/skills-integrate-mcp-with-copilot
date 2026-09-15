"""
High School Management System API

A simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

The app now supports a light club-directory model so each club can act as a
separate extracurricular profile while preserving the previous activity API.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


def make_club_record(name: str, description: str, schedule: str, max_participants: int,
                    participants: list[str], category: str = "General") -> dict:
    return {
        "club": name,
        "name": name,
        "description": description,
        "schedule": schedule,
        "category": category,
        "max_participants": max_participants,
        "participants": participants,
        "image": "🏫",
    }


# In-memory activity database
activities = {
    "Chess Club": make_club_record(
        "Chess Club",
        "Learn strategies and compete in chess tournaments",
        "Fridays, 3:30 PM - 5:00 PM",
        12,
        ["michael@mergington.edu", "daniel@mergington.edu"],
        category="Academic"
    ),
    "Programming Class": make_club_record(
        "Programming Class",
        "Learn programming fundamentals and build software projects",
        "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        20,
        ["emma@mergington.edu", "sophia@mergington.edu"],
        category="STEM"
    ),
    "Gym Class": make_club_record(
        "Gym Class",
        "Physical education and sports activities",
        "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        30,
        ["john@mergington.edu", "olivia@mergington.edu"],
        category="Wellness"
    ),
    "Soccer Team": make_club_record(
        "Soccer Team",
        "Join the school soccer team and compete in matches",
        "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        22,
        ["liam@mergington.edu", "noah@mergington.edu"],
        category="Sports"
    ),
    "Basketball Team": make_club_record(
        "Basketball Team",
        "Practice and play basketball with the school team",
        "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        15,
        ["ava@mergington.edu", "mia@mergington.edu"],
        category="Sports"
    ),
    "Art Club": make_club_record(
        "Art Club",
        "Explore your creativity through painting and drawing",
        "Thursdays, 3:30 PM - 5:00 PM",
        15,
        ["amelia@mergington.edu", "harper@mergington.edu"],
        category="Arts"
    ),
    "Drama Club": make_club_record(
        "Drama Club",
        "Act, direct, and produce plays and performances",
        "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        20,
        ["ella@mergington.edu", "scarlett@mergington.edu"],
        category="Arts"
    ),
    "Math Club": make_club_record(
        "Math Club",
        "Solve challenging problems and participate in math competitions",
        "Tuesdays, 3:30 PM - 4:30 PM",
        10,
        ["james@mergington.edu", "benjamin@mergington.edu"],
        category="Academic"
    ),
    "Debate Team": make_club_record(
        "Debate Team",
        "Develop public speaking and argumentation skills",
        "Fridays, 4:00 PM - 5:30 PM",
        12,
        ["charlotte@mergington.edu", "henry@mergington.edu"],
        category="Academic"
    )
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/clubs")
def get_clubs():
    """Return a lightweight club directory so each extracurricular group has its own profile."""
    clubs = []
    for name, details in activities.items():
        clubs.append({
            "name": name,
            "description": details["description"],
            "category": details.get("category", "General"),
            "schedule": details["schedule"],
            "image": details.get("image", "🏫"),
            "available_spots": max(details["max_participants"] - len(details["participants"]), 0),
            "activity_count": 1,
        })
    return clubs


@app.get("/clubs/{club_name}")
def get_club(club_name: str):
    """Get a single club profile with its activity details."""
    club = activities.get(club_name)
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")
    return {
        "name": club["name"],
        "description": club["description"],
        "schedule": club["schedule"],
        "category": club.get("category", "General"),
        "image": club.get("image", "🏫"),
        "max_participants": club["max_participants"],
        "participants": club["participants"],
    }


@app.get("/activities")
def get_activities(club: str | None = Query(default=None, alias="club")):
    if club is None:
        return activities

    filtered = {
        name: details for name, details in activities.items()
        if name.lower() == club.lower() or details.get("club", "").lower() == club.lower()
    }
    if not filtered:
        raise HTTPException(status_code=404, detail="Club not found")
    return filtered


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity."""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity."""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
