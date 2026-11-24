from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import requests
import urllib3
import json
import os
from datetime import datetime

from feature_extractor import extract_features, FEATURE_NAMES


urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = "phishing_detection_secret_key"


# ============================================================
# LOAD MODEL
# ============================================================

MODEL_PATH = "model/phishing_model_live.pkl"

model = joblib.load(MODEL_PATH)

print("========================================")
print("MODEL LOADED")
print("MODEL:", type(model))

if hasattr(model, "feature_names_in_"):
    print(
        "MODEL FEATURES:",
        len(model.feature_names_in_)
    )

print("MODEL CLASSES:", model.classes_)
print("========================================")


# ============================================================
# LABEL MAPPING
# ============================================================

LABEL_MAP = {
    0: "PHISHING",
    1: "LEGITIMATE"
}


# ============================================================
# CHECK MODEL CLASSES
# ============================================================

for cls in model.classes_:

    if cls not in LABEL_MAP:

        raise ValueError(
            f"Model class '{cls}' has no entry in LABEL_MAP. "
            f"Model classes are: {list(model.classes_)}"
        )


# ============================================================
# WEBSITE STATUS
# ============================================================

def check_website(url):

    try:

        response = requests.get(

            url,

            timeout=15,

            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0 Safari/537.36"
                )
            },

            allow_redirects=True,

            verify=False
        )

        print(
            "WEBSITE STATUS CODE:",
            response.status_code
        )

        print(
            "FINAL URL:",
            response.url
        )

        return True, response.status_code


    except Exception as e:

        print(
            "WEBSITE ERROR:",
            repr(e)
        )

        return False, None


# ============================================================
# SUSPICIOUS KEYWORD CHECK
# ============================================================

def check_suspicious_keywords(url):

    # Strong phishing-related words

    strong_keywords = [

        "fraud",
        "phishing",
        "scam",
        "malware",
        "fake",
        "credential"

    ]


    # Suspicious words

    suspicious_keywords = [

        "login",
        "signin",
        "verify",
        "verification",
        "bank",
        "banking",
        "account",
        "password",
        "secure",
        "security",
        "confirm",
        "update"

    ]


    url_lower = url.lower()


    # --------------------------------------------------------
    # Find strong keywords
    # --------------------------------------------------------

    found_strong = [

        keyword

        for keyword in strong_keywords

        if keyword in url_lower

    ]


    # --------------------------------------------------------
    # Find suspicious keywords
    # --------------------------------------------------------

    found_suspicious = [

        keyword

        for keyword in suspicious_keywords

        if keyword in url_lower

    ]


    # --------------------------------------------------------
    # Strong keyword alone = PHISHING
    # --------------------------------------------------------

    if found_strong:

        return True, found_strong + found_suspicious


    # --------------------------------------------------------
    # Two or more suspicious keywords = PHISHING
    # --------------------------------------------------------

    if len(found_suspicious) >= 2:

        return True, found_suspicious


    return False, found_suspicious


# ============================================================
# USER-SPECIFIC SCAN HISTORY
# ============================================================

HISTORY_FOLDER = "scan_history"


# Create folder automatically

if not os.path.exists(HISTORY_FOLDER):

    os.makedirs(HISTORY_FOLDER)


# ============================================================
# GET CURRENT USER HISTORY FILE
# ============================================================

def get_history_file():

    username = session.get("username")


    if not username:

        return None


    return os.path.join(

        HISTORY_FOLDER,

        f"{username}_history.json"

    )


# ============================================================
# LOAD HISTORY
# ============================================================

def load_history():

    history_file = get_history_file()


    if not history_file:

        return []


    if not os.path.exists(history_file):

        return []


    try:

        with open(

            history_file,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(file)


    except Exception:

        return []


# ============================================================
# SAVE HISTORY
# ============================================================

def save_history(history):

    history_file = get_history_file()


    if not history_file:

        return


    with open(

        history_file,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            history,

            file,

            indent=4

        )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return render_template(
        "home.html"
    )


# ============================================================
# MULTIPLE LOGIN USERS
# ============================================================

USERS = {

    "admin": "admin123",

    "tharun": "tharun123",

    "user1": "user123",

    "student": "student123"

}


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(

            "username",

            ""

        ).strip()


        password = request.form.get(

            "password",

            ""

        ).strip()


        # ----------------------------------------------------
        # CHECK LOGIN
        # ----------------------------------------------------

        if (

            username in USERS

            and

            USERS[username] == password

        ):

            session["username"] = username


            return redirect(

                url_for("dashboard")

            )


        else:

            return render_template(

                "login.html",

                error="Invalid username or password"

            )


    return render_template(
        "login.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:

        return redirect(

            url_for("login")

        )


    return render_template(

        "dashboard.html",

        username=session["username"]

    )


# ============================================================
# HISTORY PAGE
# ============================================================

@app.route("/history")
def history():

    if "username" not in session:

        return redirect(

            url_for("login")

        )


    # Load only current user's history

    scan_history = load_history()


    # Newest scan first

    scan_history.reverse()


    return render_template(

        "history.html",

        history=scan_history,

        username=session.get("username")

    )


# ============================================================
# CLEAR CURRENT USER HISTORY
# ============================================================

@app.route(
    "/clear-history",
    methods=["POST"]
)
def clear_history():

    if "username" not in session:

        return redirect(

            url_for("login")

        )


    # Clear only logged-in user's history

    save_history([])


    return redirect(

        url_for("history")

    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()


    return redirect(

        url_for("home")

    )


# ============================================================
# PHISHING DETECTION PAGE
# ============================================================

@app.route("/detect")
def detect():

    if "username" not in session:

        return redirect(

            url_for("login")

        )


    return render_template(

        "index.html",

        username=session.get("username")

    )


# ============================================================
# PREDICT URL
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    if "username" not in session:

        return redirect(

            url_for("login")

        )


    # ========================================================
    # GET URL
    # ========================================================

    url = request.form.get(

        "url",

        ""

    ).strip()


    # ========================================================
    # EMPTY URL
    # ========================================================

    if not url:

        return render_template(

            "index.html",

            error="Please enter a URL.",

            username=session.get("username")

        )


    # ========================================================
    # ADD HTTPS IF NEEDED
    # ========================================================

    if not url.startswith(

        ("http://", "https://")

    ):

        url = "https://" + url


    try:

        # ====================================================
        # WEBSITE STATUS
        # ====================================================

        online, status_code = check_website(url)


        if online:

            website_status = (

                f"ONLINE ({status_code})"

            )

        else:

            website_status = (

                "OFFLINE / UNREACHABLE"

            )


        # ====================================================
        # FEATURE EXTRACTION
        # ====================================================

        features = extract_features(url)


        # ====================================================
        # EXACT FEATURE ORDER
        # ====================================================

        features = features[

            FEATURE_NAMES

        ]


        # ====================================================
        # CONVERT TO NUMERIC
        # ====================================================

        features = features.apply(

            lambda column:

            column.astype(float)

        )


        # ====================================================
        # FEATURE CHECK
        # ====================================================

        if hasattr(

            model,

            "feature_names_in_"

        ):

            expected = list(

                model.feature_names_in_

            )


            actual = list(

                features.columns

            )


            if actual != expected:

                raise ValueError(

                    "Feature mismatch!\n"

                    f"Expected: {expected}\n"

                    f"Got: {actual}"

                )


        # ====================================================
        # TERMINAL INFORMATION
        # ====================================================

        print()

        print(
            "========================================"
        )

        print(

            "USER:",

            session.get("username")

        )

        print(

            "URL:",

            url

        )

        print(

            "FEATURE COUNT:",

            len(features.columns)

        )


        if hasattr(

            model,

            "feature_names_in_"

        ):

            print(

                "FEATURE ORDER CORRECT:",

                list(features.columns)

                ==

                list(model.feature_names_in_)

            )


        print(
            "========================================"
        )


        # ====================================================
        # MODEL PREDICTION
        # ====================================================

        prediction = model.predict(

            features

        )[0]


        print(

            "RAW PREDICTION:",

            prediction

        )


        print(

            "MODEL CLASSES:",

            model.classes_

        )


        # ====================================================
        # PROBABILITY
        # ====================================================

        if hasattr(

            model,

            "predict_proba"

        ):

            probabilities = model.predict_proba(

                features

            )[0]


            predicted_index = list(

                model.classes_

            ).index(

                prediction

            )


            confidence = (

                probabilities[

                    predicted_index

                ]

                * 100

            )


            print(

                "PROBABILITIES:",

                probabilities

            )


        else:

            confidence = 0.0


        # ====================================================
        # ML RESULT
        # ====================================================

        ml_result = LABEL_MAP.get(

            prediction,

            "UNKNOWN"

        )


        # ====================================================
        # SUSPICIOUS KEYWORD CHECK
        # ====================================================

        suspicious, found_keywords = (

            check_suspicious_keywords(url)

        )


        print(

            "SUSPICIOUS KEYWORDS:",

            found_keywords

        )


        # ====================================================
        # FINAL RESULT
        # ====================================================

        result = ml_result


        if suspicious:

            result = "PHISHING"


            print(

                "KEYWORD SECURITY CHECK: PHISHING"

            )

        else:

            print(

                "KEYWORD SECURITY CHECK: CLEAR"

            )


        # ====================================================
        # SAVE USER-SPECIFIC HISTORY
        # ====================================================

        history = load_history()


        history.append({

            "url": url,

            "result": result,

            "confidence": round(

                float(confidence),

                2

            ),

            "time": datetime.now().strftime(

                "%d-%m-%Y %H:%M:%S"

            )

        })


        save_history(history)


        # ====================================================
        # TERMINAL RESULT
        # ====================================================

        print(
            "========================================"
        )

        print(

            "USER:",

            session.get("username")

        )

        print(

            "ML RESULT:",

            ml_result

        )

        print(

            "FINAL RESULT:",

            result

        )

        print(

            "Confidence:",

            f"{confidence:.2f}%"

        )

        print(

            "Website:",

            website_status

        )

        print(

            "History Saved: YES"

        )

        print(
            "========================================"
        )


        # ====================================================
        # SEND RESULT TO HTML
        # ====================================================

        return render_template(

            "index.html",

            url=url,

            website_status=website_status,

            result=result,

            confidence=f"{confidence:.2f}",

            username=session.get(

                "username"

            )

        )


    # ========================================================
    # ERROR
    # ========================================================

    except Exception as e:

        print()

        print(

            "PREDICTION ERROR:",

            str(e)

        )


        return render_template(

            "index.html",

            url=url,

            error=f"Error: {str(e)}",

            username=session.get(

                "username"

            )

        )


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )