from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import sqlite3, os, json, hashlib, secrets
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tripmate-demo-secret-change-me")
DB = os.path.join(os.path.dirname(__file__), "database.db")

DESTINATIONS = {
    "Goa": {"activities":["Baga Beach","Fort Aguada","Anjuna Market"],"food":"Goan seafood / local thali","budget":6500},
    "Mumbai": {"activities":["Gateway of India","Marine Drive","Colaba Causeway"],"food":"Vada pav / street food","budget":5500},
    "Pune": {"activities":["Shaniwar Wada","Sinhagad Fort","FC Road"],"food":"Maharashtrian thali","budget":4000},
    "Delhi": {"activities":["India Gate","Red Fort","Qutub Minar"],"food":"Delhi street food","budget":6000},
    "Jaipur": {"activities":["Amber Fort","Hawa Mahal","City Palace"],"food":"Rajasthani thali","budget":6500},
    "Manali": {"activities":["Solang Valley","Mall Road","Hadimba Temple"],"food":"Himachali cuisine","budget":7500},
    "Kerala": {"activities":["Alleppey Backwaters","Fort Kochi","Munnar"],"food":"Kerala sadya","budget":8000},
    "Hyderabad": {"activities":["Charminar","Golconda Fort","Hussain Sagar"],"food":"Hyderabadi biryani","budget":5500},
    "Bengaluru": {"activities":["Cubbon Park","Lalbagh","Vidhana Soudha"],"food":"South Indian breakfast","budget":5000},
    "Kashmir": {"activities":["Dal Lake","Gulmarg","Pahalgam"],"food":"Kashmiri wazwan","budget":10000},
}

def db():
    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row
    return con

def init_db():
    con=db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS trips(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,starting_location TEXT,destination TEXT,date TEXT,duration INTEGER,travelers INTEGER,budget REAL,preferences TEXT,itinerary TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,booking_type TEXT,booking_id TEXT,destination TEXT,date TEXT,amount REAL,status TEXT);
    CREATE TABLE IF NOT EXISTS hotels(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,location TEXT,contact TEXT,price REAL,rating REAL);
    CREATE TABLE IF NOT EXISTS travel_history(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,destination TEXT,date TEXT,budget REAL,expenses REAL,itinerary TEXT);
    """)
    if con.execute("SELECT COUNT(*) FROM users").fetchone()[0]==0:
        con.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                    ("Demo User","demo@tripmate.ai",hashlib.sha256(b"demo123").hexdigest()))
    if con.execute("SELECT COUNT(*) FROM hotels").fetchone()[0]==0:
        hotels=[
            ("Sea Breeze Resort","Goa","+91 90000 10001",2200,4.5),
            ("Royal Heritage Hotel","Jaipur","+91 90000 10002",2800,4.6),
            ("Mountain View Stay","Manali"," +91 90000 10003",2500,4.4),
            ("City Comfort Inn","Mumbai"," +91 90000 10004",3200,4.2),
            ("Backwater Retreat","Kerala"," +91 90000 10005",3500,4.7),
        ]
        con.executemany("INSERT INTO hotels(name,location,contact,price,rating) VALUES(?,?,?,?,?)",hotels)
    con.commit(); con.close()

def current_user():
    return session.get("user_id")

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

def make_itinerary(data):
    dest=data.get("destination","Goa")
    days=max(1,int(data.get("days") or 3))
    travelers=max(1,int(data.get("travelers") or 1))
    budget=float(data.get("budget") or 10000)
    style=data.get("style","Moderate")
    interests=data.get("interests",[])
    if isinstance(interests,str): interests=[interests]
    info=DESTINATIONS.get(dest,{"activities":["Main attraction","Local market","Scenic viewpoint"],"food":"Local specialties","budget":6000})
    base=max(1200, info["budget"]*days/3)
    if style=="Budget": base*=0.78
    elif style=="Luxury": base*=1.65
    base*=max(1,travelers/2)
    itinerary=[]
    for d in range(1,days+1):
        acts=info["activities"]
        morning=acts[(d-1)%len(acts)]
        afternoon=acts[d%len(acts)]
        evening=acts[(d+1)%len(acts)]
        itinerary.append({
            "day":d,"morning":f"Explore {morning}","afternoon":f"Visit {afternoon}",
            "evening":f"Enjoy {evening}","food":info["food"],
            "cost":round(base/days),"distance":f"{4+d} km","time":f"{25+d*5} min",
            "transport":"Public transport" if style=="Budget" else "Cab / local transport"
        })
    return {"destination":dest,"duration":days,"travelers":travelers,"budget":budget,"style":style,
            "estimated_cost":round(base),"interests":interests,"days":itinerary}

@app.context_processor
def inject():
    return {"logged_in":bool(current_user()),"user_name":session.get("user_name","")}

@app.route("/")
def index():
    if current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"].strip().lower()
        pw=hashlib.sha256(request.form["password"].encode()).hexdigest()
        con=db(); u=con.execute("SELECT * FROM users WHERE email=? AND password=?",(email,pw)).fetchone(); con.close()
        if u:
            session.update(user_id=u["id"],user_name=u["name"],email=u["email"])
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.","danger")
    return render_template("login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        if request.form["password"]!=request.form["confirm"]:
            flash("Passwords do not match.","danger")
            return render_template("signup.html")
        try:
            con=db(); con.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (request.form["name"],request.form["email"].lower(),hashlib.sha256(request.form["password"].encode()).hexdigest()))
            con.commit(); con.close(); flash("Account created. Please log in.","success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.","danger")
    return render_template("signup.html")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    con=db()
    trips=con.execute("SELECT * FROM trips WHERE user_id=? ORDER BY id DESC",(current_user(),)).fetchall()
    bookings=con.execute("SELECT * FROM bookings WHERE user_id=? ORDER BY id DESC",(current_user(),)).fetchall()
    history=con.execute("SELECT * FROM travel_history WHERE user_id=? ORDER BY id DESC",(current_user(),)).fetchall()
    con.close()
    return render_template("dashboard.html",trips=trips,bookings=bookings,history=history)

@app.route("/plan-trip",methods=["GET","POST"])
@login_required
def plan_trip():
    if request.method=="POST":
        data=request.form.to_dict(flat=True)
        data["interests"]=request.form.getlist("interests")
        plan=make_itinerary(data)
        session["current_plan"]=plan
        if current_user():
            con=db()
            con.execute("""INSERT INTO trips(user_id,starting_location,destination,date,duration,travelers,budget,preferences,itinerary,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?)""",(current_user(),data.get("starting_location"),plan["destination"],data.get("date"),
                plan["duration"],plan["travelers"],plan["budget"],json.dumps(data),json.dumps(plan),datetime.now().isoformat()))
            con.commit(); con.close()
        return render_template("itinerary.html",plan=plan)
    return render_template("plan_trip.html")

@app.route("/itinerary")
@login_required
def itinerary():
    return render_template("itinerary.html",plan=session.get("current_plan") or make_itinerary({"destination":"Goa","days":3,"travelers":2,"budget":15000,"style":"Moderate"}))

@app.route("/modify",methods=["POST"])
@login_required
def modify():
    data=request.form.to_dict(flat=True); data["interests"]=request.form.getlist("interests")
    plan=make_itinerary(data); session["current_plan"]=plan
    return render_template("itinerary.html",plan=plan)

@app.route("/explore")
@login_required
def explore(): return render_template("explore.html",destinations=DESTINATIONS)

@app.route("/hotels")
@login_required
def hotels():
    con=db(); hotels=con.execute("SELECT * FROM hotels ORDER BY rating DESC").fetchall(); con.close()
    return render_template("hotels.html",hotels=hotels)

@app.route("/transportation")
@login_required
def transportation(): return render_template("transportation.html")

@app.route("/bookings")
@login_required
def bookings():
    con=db(); rows=con.execute("SELECT * FROM bookings WHERE user_id=? ORDER BY id DESC",(current_user(),)).fetchall(); con.close()
    return render_template("bookings.html",bookings=rows)

@app.route("/book",methods=["POST"])
@login_required
def book():
    con=db()
    bid="TM-"+secrets.token_hex(4).upper()
    con.execute("INSERT INTO bookings(user_id,booking_type,booking_id,destination,date,amount,status) VALUES(?,?,?,?,?,?,?)",
                (current_user(),request.form.get("type","Hotel"),bid,request.form.get("destination","Goa"),
                 request.form.get("date",""),float(request.form.get("amount",0)), "Confirmed"))
    con.commit(); con.close()
    return jsonify(ok=True,booking_id=bid)

@app.route("/history")
@login_required
def history():
    con=db(); rows=con.execute("SELECT * FROM travel_history WHERE user_id=? ORDER BY id DESC",(current_user(),)).fetchall(); con.close()
    return render_template("history.html",history=rows)

@app.route("/assistant")
@login_required
def assistant(): return render_template("assistant.html")

@app.route("/api/chat",methods=["POST"])
@login_required
def chat():
    msg=request.json.get("message","").lower()
    if "rain" in msg: reply="If rain is expected, choose indoor museums, cafés and covered markets. TripMate can regenerate your plan around the weather."
    elif "cheap hotel" in msg: reply="Try the hotel list and sort by rating/price. For a budget plan, choose a moderate-rated stay and public transport."
    elif "cost" in msg or "budget" in msg: reply="Reduce cost by using public transport, choosing budget hotels, travelling on flexible dates and prioritising free attractions."
    elif "food" in msg: reply="Tell me your destination and food preference; I can suggest local specialties and budget-friendly options."
    elif "photo" in msg: reply="For photography, prioritise scenic viewpoints, heritage areas, sunrise/sunset spots and local markets."
    else: reply="I can help with itineraries, budgets, hotels, transport, weather changes and destination ideas. Try asking about one of these."
    return jsonify(reply=reply)

@app.route("/admin")
@login_required
def admin():
    con=db()
    stats={
      "users":con.execute("SELECT COUNT(*) FROM users").fetchone()[0],
      "trips":con.execute("SELECT COUNT(*) FROM trips").fetchone()[0],
      "bookings":con.execute("SELECT COUNT(*) FROM bookings").fetchone()[0],
      "spending":con.execute("SELECT COALESCE(SUM(amount),0) FROM bookings").fetchone()[0]
    }
    con.close()
    return render_template("admin.html",stats=stats)

if __name__=="__main__":
    init_db()
    app.run(debug=True)
