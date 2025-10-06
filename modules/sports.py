import requests
 
def get_live_cricket_score():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    headers = {
        "X-RapidAPI-Key": "e9993472ddmshb0031460eb9a41bp1d1ea5jsn082d4caff4ea",
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }
 
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        output = []
 
        for match_type in data.get("typeMatches", []):
            for series in match_type.get("seriesMatches", []):
                matches = series.get("seriesAdWrapper", {}).get("matches", [])
                for match in matches:
                    info = match.get("matchInfo", {})
                    score = match.get("matchScore", {})
                   
                    team1 = info.get("team1", {}).get("teamName", "Team 1")
                    team2 = info.get("team2", {}).get("teamName", "Team 2")
                    status = info.get("status", "Status not available")
 
                    line = f"🏏 {team1} vs {team2} — {status}"
                    output.append(line)
 
        return "\n".join(output) if output else "No live cricket matches available."
 
    except Exception as e:
        return f"❌ Error fetching live scores: {e}"
 
 
# For testing:
if __name__ == "__main__":
    print(get_live_cricket_score())