import streamlit as st
import pandas as pd

# ---------------- PAGE SETUP ---------------- #
st.set_page_config(page_title="Cricket Analytics", layout="wide")

st.title("🏏 Cricket Analytics App")

st.markdown("""
### 📊 Smart Cricket Analytics Dashboard  
Compare players based on match situations and get data-driven recommendations.
""")

# ---------------- LOAD DATA ---------------- #
deliveries = pd.read_csv("deliveries.csv")
matches = pd.read_csv("matches.csv")

# Merge datasets
matches = matches.rename(columns={"id": "match_id"})
df = deliveries.merge(matches[["match_id", "date"]], on="match_id", how="left")

# ---------------- CREATE PHASE ---------------- #
def get_phase(over):
    if over <= 6:
        return "Powerplay"
    elif over <= 15:
        return "Middle"
    else:
        return "Death"

df["phase"] = df["over"].apply(get_phase)

st.success("Data Loaded Successfully ✅")

# ---------------- SIDEBAR INPUT ---------------- #
st.sidebar.header("🎯 Select Inputs")

batsmen = sorted(df["batsman"].dropna().unique())
bowlers = sorted(df["bowler"].dropna().unique())

player1 = st.sidebar.selectbox("Select Batsman 1", batsmen)
player2 = st.sidebar.selectbox("Select Batsman 2", batsmen)

bowler = st.sidebar.selectbox("Select Bowler", ["All"] + bowlers)
phase = st.sidebar.selectbox("Select Phase", ["All", "Powerplay", "Middle", "Death"])

# ---------------- SHOW SELECTION ---------------- #
st.subheader("📌 Selected Inputs")

colA, colB, colC, colD = st.columns(4)

colA.metric("Player 1", player1)
colB.metric("Player 2", player2)
colC.metric("Bowler", bowler)
colD.metric("Phase", phase)

# ---------------- FILTER DATA ---------------- #
filtered = df[df["batsman"].isin([player1, player2])]

if bowler != "All":
    filtered = filtered[filtered["bowler"] == bowler]

if phase != "All":
    filtered = filtered[filtered["phase"] == phase]

# ---------------- CALCULATE STATS ---------------- #
stats = filtered.groupby("batsman").agg(
    balls=("ball", "count"),
    runs=("total_runs", "sum"),
    dismissals=("player_dismissed", lambda x: x.notna().sum())
).reset_index()

# Avoid division errors
stats["strike_rate"] = (stats["runs"] / stats["balls"]) * 100
stats["average"] = stats["runs"] / stats["dismissals"].replace(0, 1)

# ---------------- DISPLAY RESULTS ---------------- #
st.subheader("📊 Player Comparison")

if len(stats) == 2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {stats.iloc[0]['batsman']}")
        st.metric("Runs", int(stats.iloc[0]["runs"]))
        st.metric("Balls", int(stats.iloc[0]["balls"]))
        st.metric("Strike Rate", f"{stats.iloc[0]['strike_rate']:.2f}")
        st.metric("Average", f"{stats.iloc[0]['average']:.2f}")

    with col2:
        st.markdown(f"### {stats.iloc[1]['batsman']}")
        st.metric("Runs", int(stats.iloc[1]["runs"]))
        st.metric("Balls", int(stats.iloc[1]["balls"]))
        st.metric("Strike Rate", f"{stats.iloc[1]['strike_rate']:.2f}")
        st.metric("Average", f"{stats.iloc[1]['average']:.2f}")

elif len(stats) > 0:
    st.dataframe(stats)
else:
    st.warning("No data available for selected filters ⚠️")

# ---------------- GRAPH ---------------- #
st.subheader("📈 Performance Comparison")

if len(stats) > 0:
    st.bar_chart(stats.set_index("batsman")[["runs", "strike_rate"]])

# ---------------- RECOMMENDATION ---------------- #
st.subheader("🏆 Final Recommendation")

if len(stats) == 2:
    better = stats.sort_values(by=["strike_rate", "average"], ascending=False).iloc[0]

    st.success(f"""
✅ **{better['batsman']} is the better choice**

📌 Based on:
- Higher Strike Rate: {better['strike_rate']:.2f}
- Better Average: {better['average']:.2f}
- Total Runs: {better['runs']}
""")
else:
    st.info("Select two players to get recommendation")

# ---------------- 🔥 NEW FEATURE: TOP PLAYERS ---------------- #
st.subheader("🥇 Top 5 Players for Selected Filters")

# Apply same filters but for ALL players
filtered_all = df.copy()

if bowler != "All":
    filtered_all = filtered_all[filtered_all["bowler"] == bowler]

if phase != "All":
    filtered_all = filtered_all[filtered_all["phase"] == phase]

top_stats = filtered_all.groupby("batsman").agg(
    balls=("ball", "count"),
    runs=("total_runs", "sum"),
    dismissals=("player_dismissed", lambda x: x.notna().sum())
).reset_index()

top_stats["strike_rate"] = (top_stats["runs"] / top_stats["balls"]) * 100
top_stats["average"] = top_stats["runs"] / top_stats["dismissals"].replace(0, 1)

# Sort by performance
top_players = top_stats.sort_values(by=["strike_rate", "runs"], ascending=False).head(5)

if len(top_players) > 0:
    st.dataframe(top_players)
else:
    st.warning("No players found for selected filters")