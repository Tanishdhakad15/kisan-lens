import streamlit as st
import pandas as pd
import requests
from datetime import date, datetime
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Kisan Lens", page_icon="🌱", layout="wide")

LANGUAGES = {
    "English": "en", "हिन्दी (Hindi)": "hi", "অসমীয়া (Assamese)": "as",
    "বাংলা (Bengali)": "bn", "बड़ो (Bodo)": "brx", "डोगरी (Dogri)": "doi",
    "ગુજરાતી (Gujarati)": "gu", "ಕನ್ನಡ (Kannada)": "kn", "कॉशुर (Kashmiri)": "ks",
    "कोंकणी (Konkani)": "gom", "मैथिली (Maithili)": "mai", "മലയാളം (Malayalam)": "ml",
    "মৈতৈলোন্ (Manipuri/Meitei)": "mni", "मराठी (Marathi)": "mr", "नेपाली (Nepali)": "ne",
    "ଓଡ଼ିଆ (Odia)": "or", "ਪੰਜਾਬੀ (Punjabi)": "pa", "संस्कृतम् (Sanskrit)": "sa",
    "سنڌي (Sindhi)": "sd", "संथाली (Santali)": "sat", "தமிழ் (Tamil)": "ta",
    "తెలుగు (Telugu)": "te", "اردو (Urdu)": "ur"
}

# Optional online translation. If the translation service is unavailable, the app remains usable in English.
try:
    from deep_translator import GoogleTranslator
except Exception:
    GoogleTranslator = None

@st.cache_data(show_spinner=False, ttl=86400)
def translate_text(text, target):
    if target == "en" or not GoogleTranslator:
        return text
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception:
        return text

def T(text):
    code = LANGUAGES.get(st.session_state.get("language", "English"), "en")
    return translate_text(text, code)

st.markdown("""
<style>
.main {background-color:#f7faf6;}
[data-testid="stSidebar"] {background:#edf5e9;}
.hero {padding:22px 24px;border-radius:18px;background:linear-gradient(110deg,#174d2b,#39834a);color:white;margin-bottom:18px;}
.hero h1 {color:white;margin:0;font-size:2.35rem;}
.hero p {color:#eef8ee;margin:6px 0 0 0;font-size:1.05rem;}
.small-note {color:#65736a;font-size:.86rem;}
.metric-card {padding:12px;border:1px solid #dce8dc;border-radius:12px;background:white;}
</style>
""", unsafe_allow_html=True)

if "language" not in st.session_state:
    st.session_state.language = "English"
if "crop_history" not in st.session_state:
    st.session_state.crop_history = []
if "photo_notes" not in st.session_state:
    st.session_state.photo_notes = []

with st.sidebar:
    st.markdown("## 🌱 Kisan Lens")
    st.caption("Smart farming companion")
    selected_language = st.selectbox("Choose language / भाषा चुनें", list(LANGUAGES.keys()),
                                     index=list(LANGUAGES.keys()).index(st.session_state.language))
    st.session_state.language = selected_language
    st.divider()
    page = st.radio("Navigation", [
        "🏠 Dashboard", "🧪 Soil & Water Analysis", "🌾 Crop Recommendations",
        "🗓️ Crop Planner", "📷 Crop Health Records", "🌦️ Weather Assistant",
        "🛒 Mandi & Selling", "ℹ️ About Project"
    ])

st.markdown(f"""
<div class="hero">
  <h1>🌱 KISAN LENS</h1>
  <p>{T("The right crop. The right guidance. Better farming.")}</p>
  <p style="font-size:.88rem">{T("A farmer-friendly agriculture decision-support prototype")}</p>
</div>
""", unsafe_allow_html=True)

# Keep a default farm profile in session state; no login or registration is required.
defaults = {
    "farmer_name": "", "location": "Bhopal", "state": "Madhya Pradesh",
    "soil_type": "Black soil", "ph": 7.0, "nitrogen": 60, "phosphorus": 35,
    "potassium": 40, "water_source": "Borewell", "water_availability": "Moderate",
    "water_quality": "Good", "salinity": "Low", "rainfall": 750,
    "temperature": 27.0, "season": "Kharif"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

crops = [
    {"crop":"Soybean","soil":["Black soil","Loamy soil"],"ph":(6.0,7.5),"rain":(600,1000),"temp":(20,32),"water":"Moderate","season":["Kharif"],"npk":(55,35,35),"duration":"90–110 days","notes":"Suitable for well-drained soil; avoid waterlogging."},
    {"crop":"Wheat","soil":["Black soil","Alluvial soil","Loamy soil"],"ph":(6.0,7.5),"rain":(300,750),"temp":(10,25),"water":"Moderate","season":["Rabi"],"npk":(100,50,40),"duration":"110–140 days","notes":"Needs cool weather during growth and dry weather near harvest."},
    {"crop":"Rice","soil":["Clay soil","Alluvial soil","Loamy soil"],"ph":(5.5,7.0),"rain":(1000,2000),"temp":(22,35),"water":"High","season":["Kharif"],"npk":(100,50,50),"duration":"120–150 days","notes":"Requires dependable water; choose a suitable variety for local conditions."},
    {"crop":"Gram (Chickpea)","soil":["Black soil","Loamy soil","Alluvial soil"],"ph":(6.0,8.0),"rain":(300,600),"temp":(15,25),"water":"Low","season":["Rabi"],"npk":(20,40,20),"duration":"100–120 days","notes":"Generally suited to lower water availability; avoid excess irrigation."},
    {"crop":"Mustard","soil":["Loamy soil","Alluvial soil","Black soil"],"ph":(6.0,7.5),"rain":(250,600),"temp":(10,25),"water":"Low","season":["Rabi"],"npk":(60,40,30),"duration":"110–140 days","notes":"Needs cool conditions; avoid waterlogging."},
    {"crop":"Maize","soil":["Loamy soil","Alluvial soil","Black soil"],"ph":(5.5,7.5),"rain":(500,800),"temp":(18,32),"water":"Moderate","season":["Kharif","Rabi"],"npk":(120,60,40),"duration":"90–120 days","notes":"Needs good drainage and timely nutrition, especially during flowering."},
    {"crop":"Cotton","soil":["Black soil","Loamy soil"],"ph":(5.8,8.0),"rain":(500,1000),"temp":(21,35),"water":"Moderate","season":["Kharif"],"npk":(100,50,50),"duration":"150–180 days","notes":"Long-duration crop; monitor pests and avoid prolonged waterlogging."},
    {"crop":"Pigeon Pea (Tur)","soil":["Black soil","Loamy soil"],"ph":(6.0,7.5),"rain":(600,1000),"temp":(20,35),"water":"Low","season":["Kharif"],"npk":(20,50,20),"duration":"150–180 days","notes":"Deep-rooted pulse; avoid standing water."},
    {"crop":"Groundnut","soil":["Sandy loam","Loamy soil"],"ph":(5.5,7.0),"rain":(500,1000),"temp":(22,30),"water":"Moderate","season":["Kharif"],"npk":(25,50,40),"duration":"100–130 days","notes":"Loose, well-drained soil supports pod development."},
    {"crop":"Millets (Pearl millet)","soil":["Sandy soil","Loamy soil","Black soil"],"ph":(5.5,8.0),"rain":(250,600),"temp":(25,35),"water":"Low","season":["Kharif"],"npk":(40,20,20),"duration":"75–100 days","notes":"Drought-tolerant option; suitable varieties depend on district."}
]

def range_score(value, bounds):
    lo, hi = bounds
    if lo <= value <= hi: return 1.0
    distance = lo-value if value < lo else value-hi
    return max(0.0, 1.0 - distance / max((hi-lo)*0.8, 1))

def recommendation_scores(profile):
    results = []
    for c in crops:
        soil_score = 1.0 if profile["soil_type"] in c["soil"] else 0.45
        ph_score = range_score(profile["ph"], c["ph"])
        rain_score = range_score(profile["rainfall"], c["rain"])
        temp_score = range_score(profile["temperature"], c["temp"])
        water_rank = {"Low":1, "Moderate":2, "High":3}
        water_score = 1.0 if water_rank[profile["water_availability"]] >= water_rank[c["water"]] else 0.55
        season_score = 1.0 if profile["season"] in c["season"] else 0.55
        n,p,k = c["npk"]
        nutrient_score = (range_score(profile["nitrogen"], (n*.65,n*1.35)) +
                          range_score(profile["phosphorus"], (p*.65,p*1.35)) +
                          range_score(profile["potassium"], (k*.65,k*1.35))) / 3
        score = 100*(.20*soil_score + .17*ph_score + .17*rain_score + .14*temp_score +
                     .12*water_score + .10*season_score + .10*nutrient_score)
        results.append({**c, "score":round(score), "soil_score":soil_score})
    return sorted(results, key=lambda x:x["score"], reverse=True)

def current_profile():
    return {k:st.session_state[k] for k in defaults}

if page.startswith("🏠"):
    st.subheader(T("Welcome to your farm assistant"))
    st.write(T("Kisan Lens helps farmers compare crop options and organize farm activities. Enter your farm details to get a first recommendation."))
    cols = st.columns(3)
    cols[0].metric(T("Supported languages"), "22")
    cols[1].metric(T("Crop options in demo"), str(len(crops)))
    cols[2].metric(T("Login required"), T("No"))
    st.info(T("Start with Soil & Water Analysis. Your details stay in this browser session and are not sent to a farmer account."))
    st.markdown("### " + T("Quick farm profile"))
    a,b,c = st.columns(3)
    st.session_state.farmer_name = a.text_input(T("Farmer name (optional)"), st.session_state.farmer_name)
    st.session_state.location = b.text_input(T("Village / district"), st.session_state.location)
    st.session_state.state = c.text_input(T("State"), st.session_state.state)
    st.markdown("### " + T("How it works"))
    st.write("1. " + T("Enter soil, water and farm details."))
    st.write("2. " + T("Review ranked crop suggestions and suitability scores."))
    st.write("3. " + T("Use the crop planner, weather assistant and selling tools."))
    st.caption(T("Prototype note: crop scores are rule-based demonstrations, not certified agronomic advice."))

elif page.startswith("🧪"):
    st.subheader(T("Soil & Water Analysis"))
    st.write(T("Enter values from a soil test report where possible. If you do not know a value, use an approximate value only for demonstration."))
    with st.form("farm_form"):
        a,b,c = st.columns(3)
        st.session_state.location = a.text_input(T("Village / district"), st.session_state.location)
        st.session_state.state = b.text_input(T("State"), st.session_state.state)
        st.session_state.season = c.selectbox(T("Growing season"), ["Kharif","Rabi","Zaid"], index=["Kharif","Rabi","Zaid"].index(st.session_state.season))
        a,b,c = st.columns(3)
        st.session_state.soil_type = a.selectbox(T("Soil type"), ["Black soil","Alluvial soil","Red soil","Clay soil","Sandy soil","Sandy loam","Loamy soil"], index=["Black soil","Alluvial soil","Red soil","Clay soil","Sandy soil","Sandy loam","Loamy soil"].index(st.session_state.soil_type) if st.session_state.soil_type in ["Black soil","Alluvial soil","Red soil","Clay soil","Sandy soil","Sandy loam","Loamy soil"] else 0)
        st.session_state.ph = b.number_input(T("Soil pH"), 3.0, 10.0, float(st.session_state.ph), .1)
        st.session_state.rainfall = c.number_input(T("Expected seasonal rainfall (mm)"), 0, 3000, int(st.session_state.rainfall), 25)
        a,b,c = st.columns(3)
        st.session_state.nitrogen = a.number_input(T("Nitrogen (N) kg/ha"), 0, 300, int(st.session_state.nitrogen))
        st.session_state.phosphorus = b.number_input(T("Phosphorus (P) kg/ha"), 0, 200, int(st.session_state.phosphorus))
        st.session_state.potassium = c.number_input(T("Potassium (K) kg/ha"), 0, 300, int(st.session_state.potassium))
        st.markdown("#### " + T("Water details"))
        a,b,c = st.columns(3)
        st.session_state.water_source = a.selectbox(T("Water source"), ["Borewell","Open well","Canal","River","Rain-fed","Other"])
        st.session_state.water_availability = b.selectbox(T("Water availability"), ["Low","Moderate","High"], index=["Low","Moderate","High"].index(st.session_state.water_availability))
        st.session_state.water_quality = c.selectbox(T("Water quality (your assessment)"), ["Good","Average","Poor","Not tested"])
        a,b = st.columns(2)
        st.session_state.salinity = a.selectbox(T("Water salinity"), ["Low","Medium","High","Not tested"])
        st.session_state.temperature = b.number_input(T("Typical growing-season temperature (°C)"), -5.0, 50.0, float(st.session_state.temperature), .5)
        submitted = st.form_submit_button(T("Save farm details"), type="primary")
    if submitted:
        st.success(T("Farm details saved for this session. Open Crop Recommendations to view suggestions."))
    st.warning(T("For real farming decisions, use a laboratory soil and irrigation-water test. NPK units and interpretation can vary by test method."))

elif page.startswith("🌾"):
    st.subheader(T("Crop Recommendations"))
    profile = current_profile()
    results = recommendation_scores(profile)
    st.write(f"**{T('Farm location')}:** {profile['location']}, {profile['state']}  |  **{T('Season')}:** {profile['season']}")
    st.caption(T("Ranking uses soil type, pH, rainfall, temperature, water availability, season and nutrient inputs."))
    for i, r in enumerate(results[:5]):
        with st.container(border=True):
            left,right = st.columns([4,1])
            left.markdown(f"### {i+1}. {T(r['crop'])}")
            left.write(T(r["notes"]))
            left.caption(f"{T('Typical duration')}: {r['duration']} · {T('Water need')}: {T(r['water'])}")
            right.metric(T("Demo suitability"), f"{r['score']}%")
            if r["score"] >= 75:
                st.success(T("Good match in this prototype"))
            elif r["score"] >= 60:
                st.info(T("Possible option; verify locally"))
            else:
                st.warning(T("Needs careful local verification"))
    st.session_state.crop_history.append({"date":str(date.today()),"location":profile["location"],"top_crop":results[0]["crop"],"score":results[0]["score"]})
    st.info(T("Important: these scores are illustrative rule-based rankings, not a trained AI model. Consult your Krishi Vigyan Kendra or agriculture officer before selecting seeds or applying inputs."))

elif page.startswith("🗓️"):
    st.subheader(T("Crop Planner"))
    crop_names = [c["crop"] for c in crops]
    selected = st.selectbox(T("Select crop"), crop_names)
    crop = next(c for c in crops if c["crop"] == selected)
    st.write(f"**{T('Typical crop duration')}:** {crop['duration']}")
    plan = [
        ("Land preparation", "Test soil, prepare a level seedbed, arrange quality seed and check drainage."),
        ("Sowing", "Use locally recommended seed variety, spacing and sowing window. Follow local agriculture department guidance."),
        ("Early growth", "Check germination, weeds and soil moisture. Irrigate only when needed."),
        ("Vegetative growth", "Monitor crop regularly; apply nutrients only according to soil test and crop recommendations."),
        ("Flowering / grain or pod formation", "Avoid moisture stress; inspect for pests and diseases at least twice a week."),
        ("Harvest", "Harvest at crop-appropriate maturity; dry and clean produce safely."),
        ("Storage & sale", "Use clean, dry storage; compare nearby mandi prices and transport costs before selling.")
    ]
    for stage, detail in plan:
        with st.expander(T(stage), expanded=False):
            st.write(T(detail))
    st.caption(T("This is a generic demonstration calendar. Actual dates and practices depend on crop variety, district and sowing date."))

elif page.startswith("📷"):
    st.subheader(T("Crop Health Records"))
    st.write(T("Upload a crop photo to keep a dated observation record. This prototype does not diagnose disease from the image."))
    uploaded = st.file_uploader(T("Upload crop photograph"), type=["jpg","jpeg","png"])
    note = st.text_area(T("What do you observe? (yellow leaves, spots, insects, wilting...)"))
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption=T("Uploaded crop image"), width=420)
        if st.button(T("Save observation")):
            st.session_state.photo_notes.append({"date":str(date.today()),"file":uploaded.name,"note":note or "No note entered"})
            st.success(T("Observation saved in this session."))
    if st.session_state.photo_notes:
        st.markdown("### " + T("Saved observations"))
        st.dataframe(pd.DataFrame(st.session_state.photo_notes), use_container_width=True)
    st.warning(T("Do not spray pesticides based only on a photo or this demo. Confirm the issue with a qualified local agriculture expert and follow label directions."))

elif page.startswith("🌦️"):
    st.subheader(T("Weather Assistant"))
    st.write(T("Get a current weather snapshot when the online weather service is reachable."))
    city = st.text_input(T("Town / district for weather"), st.session_state.location or "Bhopal")
    if st.button(T("Fetch weather")):
        try:
            geo = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name":city,"count":1,"language":"en","format":"json"}, timeout=10).json()
            if not geo.get("results"):
                st.error(T("Location not found. Check spelling or enter a nearby larger town."))
            else:
                place = geo["results"][0]
                weather = requests.get("https://api.open-meteo.com/v1/forecast", params={
                    "latitude":place["latitude"],"longitude":place["longitude"],
                    "current":"temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
                    "daily":"precipitation_probability_max,precipitation_sum,temperature_2m_max,temperature_2m_min",
                    "forecast_days":3,"timezone":"auto"
                }, timeout=10).json()
                cur = weather.get("current",{})
                a,b,c,d = st.columns(4)
                a.metric(T("Temperature"), f"{cur.get('temperature_2m','—')} °C")
                b.metric(T("Humidity"), f"{cur.get('relative_humidity_2m','—')}%")
                c.metric(T("Precipitation now"), f"{cur.get('precipitation','—')} mm")
                d.metric(T("Wind speed"), f"{cur.get('wind_speed_10m','—')} km/h")
                daily = weather.get("daily",{})
                st.markdown("### " + T("Next 3 days"))
                st.dataframe(pd.DataFrame({
                    "Date":daily.get("time",[]),"Rain probability (%)":daily.get("precipitation_probability_max",[]),
                    "Rain (mm)":daily.get("precipitation_sum",[]),"Max temp (°C)":daily.get("temperature_2m_max",[]),
                    "Min temp (°C)":daily.get("temperature_2m_min",[])
                }), use_container_width=True)
                st.caption(f"{T('Weather location')}: {place.get('name')}, {place.get('admin1','')}. {T('Source')}: Open-Meteo.")
        except Exception as e:
            st.error(T("Could not fetch live weather. Check internet connection and try again."))
    st.info(T("Weather is a planning aid, not a guarantee. Check local forecasts before spraying, irrigation or harvesting."))

elif page.startswith("🛒"):
    st.subheader(T("Mandi & Selling Assistant"))
    st.write(T("Compare prices you have collected from nearby markets. Demo values below are sample inputs, not live mandi prices."))
    crop_name = st.selectbox(T("Harvested crop"), [c["crop"] for c in crops])
    qty = st.number_input(T("Quantity available (quintals)"), 1.0, 100000.0, 10.0, .5)
    a,b,c = st.columns(3)
    market1 = a.text_input(T("Market 1"), "Nearby Mandi")
    price1 = b.number_input(T("Market 1 price (₹/quintal)"), 0, 200000, 2500, 50)
    cost1 = c.number_input(T("Transport / other cost (₹)"), 0, 1000000, 300, 50)
    a,b,c = st.columns(3)
    market2 = a.text_input(T("Market 2"), "District Mandi")
    price2 = b.number_input(T("Market 2 price (₹/quintal)"), 0, 200000, 2600, 50)
    cost2 = c.number_input(T("Transport / other cost (₹)"), 0, 1000000, 600, 50)
    if st.button(T("Compare estimated returns"), type="primary"):
        rows = []
        for market,price,cost in [(market1,price1,cost1),(market2,price2,cost2)]:
            gross = qty*price
            rows.append({"Market":market,"Price (₹/quintal)":price,"Gross value (₹)":gross,"Costs (₹)":cost,"Estimated net (₹)":gross-cost})
        df = pd.DataFrame(rows).sort_values("Estimated net (₹)",ascending=False)
        st.dataframe(df, use_container_width=True)
        st.success(f"{T('Higher estimated net return')}: {df.iloc[0]['Market']} — ₹{df.iloc[0]['Estimated net (₹)']:,.0f}")
    st.caption(T("Check current official mandi prices, quality requirements, commission, loading, transport and payment terms before choosing a buyer. This tool does not connect to live e-NAM or AGMARKNET data."))

else:
    st.subheader(T("About Kisan Lens"))
    st.write(T("Kisan Lens is a student mini-project prototype intended to demonstrate how digital tools can support farm decisions."))
    st.markdown("### " + T("Technology used"))
    st.write("- Python and Streamlit for the web application")
    st.write("- Rule-based crop suitability scoring for the prototype")
    st.write("- Open-Meteo for optional live weather data")
    st.write("- Optional Google Translate integration for the interface")
    st.markdown("### " + T("Prototype limitations"))
    st.write("- Crop recommendations are educational examples, not certified advice.")
    st.write("- Crop-photo upload stores an observation; it does not yet run a trained disease-detection model.")
    st.write("- Mandi prices are entered by the user; no live market feed is connected.")
    st.write("- Translation requires internet and may fall back to English if the translation service is unavailable.")
    st.write("- Data is session-based and is not permanently stored or synced between devices.")
    st.markdown("### " + T("Future improvements"))
    st.write("- Train and validate a crop recommendation model with reliable Indian agricultural datasets.")
    st.write("- Add district-specific crop calendars, soil-test interpretation and water-quality thresholds.")
    st.write("- Integrate verified crop-disease models and official mandi data.")
    st.write("- Add secure farmer profiles, offline mode, voice input and verified regional-language content.")
    st.caption("Built as an academic prototype. Verify all real-world farm decisions with local agricultural experts.")
