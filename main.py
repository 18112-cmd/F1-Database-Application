from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
from fastapi import HTTPException
app = FastAPI()

# Firebase authentication setup
firebase_request_adapter = requests.Request()

# Firestore client setup
db = firestore.Client()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Home route with Firebase auth check
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    error_message = "No error here"
    user_token = None

    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as err:
            print(str(err))

    # Fetch driver and team list for clickable links
    drivers = [doc.to_dict() for doc in db.collection("drivers").stream()]
    teams = [doc.to_dict() for doc in db.collection("teams").stream()]

    return templates.TemplateResponse("main.html", {
        "request": request,
        "user_token": user_token,
        "error_message": error_message,
        "drivers": drivers,
        "teams": teams
    })

# Add driver form
@app.get("/add_driver", response_class=HTMLResponse)
async def add_driver_form(request: Request):
    id_token = request.cookies.get("token")
    user_token = None
    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError:
            pass
    if not user_token:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("add_driver.html", {"request": request})

# Submit driver to Firestore
@app.post("/submit_driver")
async def submit_driver(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    pole_positions: int = Form(...),
    race_wins: int = Form(...),
    points: int = Form(...),
    world_titles: int = Form(...),
    fastest_laps: int = Form(...),
    team: str = Form(...)
):
    id_token = request.cookies.get("token")
    if not id_token:
        return RedirectResponse(url="/", status_code=302)
    doc_ref = db.collection("drivers").document(name)
    existing_driver = db.collection("drivers").document(name).get()
    if existing_driver.exists:
        return HTMLResponse(content="Driver already exists!", status_code=400)

    doc_ref.set({
        "name": name,
        "age": age,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "points": points,
        "world_titles": world_titles,
        "fastest_laps": fastest_laps,
        "team": team
    })
    return RedirectResponse(url="/", status_code=303)

# Add team form
@app.get("/add_team", response_class=HTMLResponse)
async def add_team_form(request: Request):
    id_token = request.cookies.get("token")
    user_token = None
    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError:
            pass
    if not user_token:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("add_team.html", {"request": request})


# Submit team to Firestore
@app.post("/submit_team")
async def submit_team(
    request: Request,
    name: str = Form(...),
    founded: int = Form(...),
    pole_positions: int = Form(...),
    race_wins: int = Form(...),
    constructor_titles: int = Form(...),
    prev_position: int = Form(...)
):
    id_token = request.cookies.get("token")
    if not id_token:
        return RedirectResponse(url="/", status_code=302)
    doc_ref = db.collection("teams").document(name)
    existing_team = db.collection("teams").document(name).get()
    if existing_team.exists:
        return HTMLResponse(content="Team already exists!", status_code=400)

    doc_ref.set({
        "name": name,
        "founded": founded,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "constructor_titles": constructor_titles,
        "prev_position": prev_position
    })
    return RedirectResponse(url="/", status_code=303)

@app.get("/edit_driver/{driver_id}", response_class=HTMLResponse)
async def edit_driver_form(driver_id: str, request: Request):
    id_token = request.cookies.get("token")
    user_token = None
    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError:
            pass

    if not user_token:
        return RedirectResponse(url="/", status_code=302)

    driver_doc = db.collection("drivers").document(driver_id).get()
    if not driver_doc.exists:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver = driver_doc.to_dict()
    return templates.TemplateResponse("edit_driver.html", {"request": request, "driver": driver})


@app.post("/edit_driver/{driver_id}")
async def edit_driver(driver_id: str, name: str = Form(...), age: int = Form(...),
                      pole_positions: int = Form(...), race_wins: int = Form(...),
                      points: int = Form(...), world_titles: int = Form(...),
                      fastest_laps: int = Form(...), team: str = Form(...),
                      request: Request = None):

    id_token = request.cookies.get("token")
    if not id_token:
        return RedirectResponse(url="/", status_code=302)

    db.collection("drivers").document(driver_id).update({
        "name": name,
        "age": age,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "points": points,
        "world_titles": world_titles,
        "fastest_laps": fastest_laps,
        "team": team
    })
    return RedirectResponse(url=f"/driver/{driver_id}", status_code=303)

@app.post("/delete_driver/{driver_id}")
async def delete_driver(driver_id: str, request: Request):
    id_token = request.cookies.get("token")
    if not id_token:
        return RedirectResponse(url="/", status_code=302)
    db.collection("drivers").document(driver_id).delete()
    return RedirectResponse(url="/", status_code=303)

# Driver details
@app.get("/driver/{driver_id}", response_class=HTMLResponse)
async def show_driver(driver_id: str, request: Request):
    id_token = request.cookies.get("token")
    user_token = None

    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as err:
            print(str(err))

    driver_doc = db.collection("drivers").document(driver_id).get()
    if driver_doc.exists:
        return templates.TemplateResponse("driver_details.html", {
            "request": request,
            "driver": driver_doc.to_dict(),
            "user_token": user_token  # 🔴 This must be included
        })
    return RedirectResponse(url="/", status_code=302)

# Team details
@app.get("/team/{team_id}", response_class=HTMLResponse)
async def show_team(team_id: str, request: Request):
    id_token = request.cookies.get("token")
    user_token = None

    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError:
            pass

    team_doc = db.collection("teams").document(team_id).get()
    if team_doc.exists:
        return templates.TemplateResponse("team_details.html", {
            "request": request,
            "team": team_doc.to_dict(),
            "user_token": user_token  # ✅ this enables button visibility
        })
    return RedirectResponse(url="/", status_code=302)


@app.get("/edit_team/{team_id}", response_class=HTMLResponse)
async def edit_team_form(team_id: str, request: Request):
    id_token = request.cookies.get("token")
    user_token = None
    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError:
            pass

    if not user_token:
        return RedirectResponse(url="/", status_code=302)

    team_doc = db.collection("teams").document(team_id).get()
    if not team_doc.exists:
        raise HTTPException(status_code=404, detail="Team not found")
    team = team_doc.to_dict()
    return templates.TemplateResponse("edit_team.html", {"request": request, "team": team})


@app.post("/edit_team/{team_id}")
async def edit_team(team_id: str, name: str = Form(...), founded: int = Form(...),
                    pole_positions: int = Form(...), race_wins: int = Form(...),
                    constructor_titles: int = Form(...), prev_position: int = Form(...),
                    request: Request = None):

    id_token = request.cookies.get("token")
    if not id_token:
        return RedirectResponse(url="/", status_code=302)

    db.collection("teams").document(team_id).update({
        "name": name,
        "founded": founded,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "constructor_titles": constructor_titles,
        "prev_position": prev_position
    })
    return RedirectResponse(url=f"/team/{team_id}", status_code=303)


@app.post("/delete_team/{team_id}")
async def delete_team(team_id: str, request: Request):
    id_token = request.cookies.get("token")
    if not id_token:
        return RedirectResponse(url="/", status_code=302)
    db.collection("teams").document(team_id).delete()
    return RedirectResponse(url="/", status_code=303)

# Query drivers
@app.get("/query_driver", response_class=HTMLResponse)
async def query_driver_form(request: Request):
    return templates.TemplateResponse("query_driver.html", {"request": request})

@app.post("/query_driver_results", response_class=HTMLResponse)
async def query_driver_results(request: Request, attribute: str = Form(...), operator: str = Form(...), value: int = Form(...)):
    query = db.collection("drivers")
    query = query.where(attribute, operator, value)
    results = [doc.to_dict() for doc in query.stream()]
    return templates.TemplateResponse("query_results.html", {"request": request, "results": results, "type": "driver"})

# Query teams
@app.get("/query_team", response_class=HTMLResponse)
async def query_team_form(request: Request):
    return templates.TemplateResponse("query_team.html", {"request": request})

@app.post("/query_team_results", response_class=HTMLResponse)
async def query_team_results(request: Request, attribute: str = Form(...), operator: str = Form(...), value: int = Form(...)):
    query = db.collection("teams")
    query = query.where(attribute, operator, value)
    results = [doc.to_dict() for doc in query.stream()]
    return templates.TemplateResponse("query_results.html", {"request": request, "results": results, "type": "team"})

# Compare drivers
@app.get("/compare_drivers/{id1}/{id2}", response_class=HTMLResponse)
async def compare_drivers(id1: str, id2: str, request: Request):
    d1 = db.collection("drivers").document(id1).get()
    d2 = db.collection("drivers").document(id2).get()
    if d1.exists and d2.exists:
        return templates.TemplateResponse("compare_drivers.html", {"request": request, "driver1": d1.to_dict(), "driver2": d2.to_dict()})
    return RedirectResponse(url="/", status_code=302)

# Compare teams
@app.get("/compare_teams/{id1}/{id2}", response_class=HTMLResponse)
async def compare_teams(id1: str, id2: str, request: Request):
    t1 = db.collection("teams").document(id1).get()
    t2 = db.collection("teams").document(id2).get()
    if t1.exists and t2.exists:
        return templates.TemplateResponse("compare_teams.html", {"request": request, "team1": t1.to_dict(), "team2": t2.to_dict()})
    return RedirectResponse(url="/", status_code=302)

# Redirect form for comparing drivers
@app.post("/compare_drivers_redirect")
async def compare_drivers_redirect(id1: str = Form(...), id2: str = Form(...)):
    return RedirectResponse(url=f"/compare_drivers/{id1}/{id2}", status_code=303)

# Redirect form for comparing teams
@app.post("/compare_teams_redirect")
async def compare_teams_redirect(id1: str = Form(...), id2: str = Form(...)):
    return RedirectResponse(url=f"/compare_teams/{id1}/{id2}", status_code=303)