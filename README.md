# 🚀 Nave OnLine

**Nave OnLine** is an arcade-style game developed in **Python** using **Tkinter**.  
The player controls a spaceship using the **WASD** keys, navigating through space to capture planets and advance through levels.

## 🕹️ How to Play
- Use the **W**, **A**, **S**, **D** keys to move the spaceship.  
- Capture planets to progress to the next level.  
- In the final stage, survive the **meteor shower** for as long as possible.

## ✨ Features
- Fully built with **Python** and **Tkinter**.  
- Smooth WASD controls.  
- Progressive difficulty: planets grow larger and move faster with each level.  
- Final survival stage with meteor showers.  
- **Planet names dynamically generated using an exoplanet API**, adding diversity and authenticity to the game.

## ⚙️ About the Planet API
The game uses a public API to generate unique planet names, fetching them dynamically from NASA's Exoplanet Archive. A fallback list is used if the API is unavailable.

```python
EXOPLANET_API = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    "?query=select+pl_name+from+ps&format=json"
)
# Get exoplanet names from the API
try:
    req = urllib.request.Request(EXOPLANET_API, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    self.exo_names = list({item["pl_name"] for item in data})
except:
    # Fallback list in case the API fails
    self.exo_names = ["Kepler-22b", "Proxima Centauri b", "TRAPPIST-1e", "HD 209458 b"]
