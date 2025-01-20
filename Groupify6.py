from flask import Flask, redirect, request, session, url_for, render_template_string, make_response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import secrets
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

SPOTIPY_CLIENT_ID = 'f04079769c2d438e83238d50f473c99a'
SPOTIPY_CLIENT_SECRET = 'e11af9729ad841c697f6f7583300e01d'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = "user-library-read user-top-read playlist-modify-public playlist-modify-private user-read-recently-played playlist-read-private"

genres = ['pop', 'rock', 'hip-hop', 'classical', 'jazz', 'electronic', 'country', 'reggae', 'latin']

# HTML-template voor de webinterface
index_html = """
<!doctype html>
<html lang="en">
  <head>
    <title>Spotify Playlist Generator</title>
  </head>
  <body>
    <h1>Welkom bij de Spotify Afspeellijst Generator 🎶</h1>
    {% if user1 or user2 %}
        <p>Hallo {{ user1 }}{% if user1 and user2 %} en {{ user2 }}{% elif user2 %}{{ user2 }}{% endif %}!</p>
        {% if not user1 %}
            <a href="/login?user=user1">Log in met Spotify (Gebruiker 1)</a><br>
        {% endif %}
        {% if not user2 %}
            <a href="/login?user=user2">Log in met Spotify (Gebruiker 2)</a><br>
        {% endif %}
        {% if user1 and user2 %}
            <h2>Maak een gezamenlijke afspeellijst:</h2>
            <form action="/playlist_two_users" method="post">
                <fieldset>
                    <legend>Genres</legend>
                    <input type="checkbox" id="select_all" onclick="toggleGenres()"> Selecteer alle<br>
                    {% for genre in genres %}
                        <input type="checkbox" class="genre" name="genres" value="{{ genre }}"> {{ genre }}<br>
                    {% endfor %}
                </fieldset>
                <br>
                <fieldset>
                    <legend>Bekendheidstype</legend>
                    <label>
                        <input type="radio" name="bekendheidstype" value="Nieuw" checked>
                        Zoveel mogelijk nieuwe muziek
                    </label><br>
                    <label>
                        <input type="radio" name="bekendheidstype" value="Bekend">
                        Zoveel mogelijk muziek die je al hebt geluisterd
                    </label>
                </fieldset>
                <br>
                <fieldset>
                    <legend>Afspeellijst naam</legend>
                    <input type="text" name="playlist_name" value="Gezamenlijke Afspeellijst">
                </fieldset>
                <br>
                <button type="submit">Creëer Afspeellijst</button>
            </form>
        {% endif %}
    {% else %}
        <a href="/login?user=user1">Log in met Spotify (Gebruiker 1)</a><br>
        <a href="/login?user=user2">Log in met Spotify (Gebruiker 2)</a>
    {% endif %}
    <script>
        function toggleGenres() {
            var checkboxes = document.getElementsByClassName('genre');
            var selectAll = document.getElementById('select_all').checked;
            for (var checkbox of checkboxes) {
                checkbox.checked = selectAll;
            }
        }
    </script>
  </body>
</html>
"""

def get_auth_manager(state=None, user=None):
    cache_path = os.path.join(Path.home(), f'.cache_{user}') if user else None
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        state=state,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=cache_path,
        show_dialog=True
    )

def clear_cache_for_users(users):
    """Verwijder de cachebestanden voor de opgegeven gebruikers."""
    for user in users:
        cache_path = os.path.join(Path.home(), f'.cache_{user}')
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print(f"Cache voor {user} verwijderd: {cache_path}")

@app.route('/')
def index():
    user1 = session.get('user1_display_name')
    user2 = session.get('user2_display_name')

    response = make_response(render_template_string(index_html, user1=user1, user2=user2, genres=genres))
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/login')
def login():
    user = request.args.get('user')
    if user not in ['user1', 'user2']:
        return "Ongeldige gebruikersparameter."

    state = f"{secrets.token_urlsafe(16)}_{user}"
    session[f'state_{user}'] = state
    auth_manager = get_auth_manager(state=state, user=user)
    session['current_user'] = user
    return redirect(auth_manager.get_authorize_url())

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    user = session.get('current_user')

    if not user or state != session.get(f'state_{user}'):
        return "Ongeldige state-parameter. Probeer opnieuw in te loggen."

    auth_manager = get_auth_manager(state=state, user=user)
    token_info = auth_manager.get_access_token(code)

    sp = spotipy.Spotify(auth=token_info['access_token'])
    display_name = sp.current_user()['display_name']
    session[f'{user}_token_info'] = token_info
    session[f'{user}_display_name'] = display_name
    session.pop(f'state_{user}', None)
    session.pop('current_user', None)

    return redirect(url_for('index'))

@app.route('/playlist_two_users', methods=['POST'])
def playlist_two_users():
    user1_token_info = session.get('user1_token_info')
    user2_token_info = session.get('user2_token_info')

    if not user1_token_info or not user2_token_info:
        return redirect(url_for('index'))

    sp_user1 = spotipy.Spotify(auth=user1_token_info['access_token'])
    sp_user2 = spotipy.Spotify(auth=user2_token_info['access_token'])

    selected_genres = request.form.getlist('genres')
    bekendheidstype = request.form.get('bekendheidstype')
    playlist_name = request.form.get('playlist_name')

    track_uris = set()

    if bekendheidstype == "Nieuw":
        for sp in [sp_user1, sp_user2]:
            for genre in selected_genres:
                results = sp.search(q=f"genre:{genre}", type='track', limit=10)
                track_uris.update([track['uri'] for track in results['tracks']['items']])

    elif bekendheidstype == "Bekend":
        top_tracks_user1 = sp_user1.current_user_top_tracks(limit=25)['items']
        top_tracks_user2 = sp_user2.current_user_top_tracks(limit=25)['items']
        track_uris.update([track['uri'] for track in top_tracks_user1 + top_tracks_user2])

    if not track_uris:
        return "Geen nummers gevonden."

    playlist = sp_user1.user_playlist_create(
        user=sp_user1.current_user()["id"],
        name=playlist_name,
        public=True
    )
    sp_user1.playlist_add_items(playlist_id=playlist["id"], items=list(track_uris))

    # Reset de cache na het aanmaken van de afspeellijst
    clear_cache_for_users(['user1', 'user2'])

    return f"Afspeellijst '{playlist_name}' succesvol aangemaakt!"

if __name__ == "__main__":
    app.run(debug=True)
