**Redevelop a Data-driven Platform:**

Code: Groupify6.py

_⚠️ Because of the new restrictions of the Spotify API that were added in November 2024, the code sadly doesnt work anymore. Spotify restricted the acces of alot of features like characteristics of a song, song recommendations, and algorithmic playlist generation._

I redeveloped the "Blend" playlist function in Spotify, which combines music tastes into one playlist for two people. Characteristics like genre, new or known-by-users music were customisable.


**Getting Started**
This guide will help you get the project running locally. You’ll need a Spotify Developer account and Python installed.

**Prerequisites**
- Python 3.10+
- Spotify Developer Account
- pip (comes with Python)

**Install Python dependencies:**
pip install flask spotipy

**Spotify API Setup**
1. Go to https://developer.spotify.com/dashboard
2. Create a new app:
   - Name: Playlist Generator
   - Description: Creates shared playlists for two users based on genre and preferences
3. Click Edit Settings and add:
   http://localhost:5000/callback
   under Redirect URIs, then click Save
4. Copy your Client ID and Client Secret

**Installation**

_1. Clone the repository_
git clone https://github.com/your_username/spotify-playlist-generator.git
cd spotify-playlist-generator

_2. Set environment variables:_
export SPOTIPY_CLIENT_ID="your-client-id"
export SPOTIPY_CLIENT_SECRET="your-client-secret"
export SPOTIPY_REDIRECT_URI="http://localhost:5000/callback"

_3. Run the app:_
python app.py

_4. Open your browser and go to:_
http://localhost:5000/

**Usage**
- Each user logs in via Spotify (User 1 and User 2)
- Once both users are authenticated:
  - Select music genres
  - Choose between new music or familiar music
  - Enter a custom playlist name
- A playlist is created on User 1’s account
- Tokens are removed locally for privacy

You can easily modify genre lists or default playlist names in the code.


**Contact**
Merlijn Marquering
Email: merlijn.marquering@gmail.com
GitHub: https://github.com/MerrieQ

**Acknowledgments**
- Spotify Web API Docs
- Spotipy Library
- GitHub Emoji Cheat Sheet
