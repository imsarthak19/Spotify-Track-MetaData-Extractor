import os
import io
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Spotify API Setup
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def get_spotify_client():
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    return spotipy.Spotify(auth_manager=auth_manager)

def extract_playlist_id(playlist_input):
    """Extracts playlist ID from a URL or returns the ID if already provided."""
    if 'spotify.com/playlist/' in playlist_input:
        return playlist_input.split('playlist/')[1].split('?')[0]
    return playlist_input

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    playlist_input = request.form.get('playlist_id')
    if not playlist_input:
        flash("Please provide a Spotify Playlist ID or URL.")
        return redirect(url_for('index'))

    try:
        sp = get_spotify_client()
        playlist_id = extract_playlist_id(playlist_input)
        
        # Get playlist info (name)
        playlist_info = sp.playlist(playlist_id)
        playlist_name = playlist_info['name']
        
        tracks_data = []
        
        # Fetch all tracks with pagination
        results = sp.playlist_items(playlist_id)
        while results:
            for item in results['items']:
                track = item.get('track')
                if not track:
                    continue
                
                # Extract metadata
                title = track.get('name')
                artists = ", ".join([artist['name'] for artist in track.get('artists', [])])
                album = track.get('album', {}).get('name')
                release_date = track.get('album', {}).get('release_date', '')
                release_year = release_date.split('-')[0] if release_date else 'N/A'
                
                # Album Art URL (usually the first image in the list is the highest resolution)
                images = track.get('album', {}).get('images', [])
                album_art_url = images[0]['url'] if images else 'No Image'
                
                tracks_data.append({
                    'Song Title': title,
                    'Artist': artists,
                    'Album Name': album,
                    'Release Year': release_year,
                    'Album Art URL': album_art_url
                })
            
            # Check for next page
            if results['next']:
                results = sp.next(results)
            else:
                results = None
        
        if not tracks_data:
            flash("The playlist is empty or could not be processed.")
            return redirect(url_for('index'))

        # Create DataFrame and CSV
        df = pd.DataFrame(tracks_data)
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        filename = f"{playlist_name.replace(' ', '_')}_metadata.csv"
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except spotipy.exceptions.SpotifyException as e:
        flash(f"Spotify API Error: {str(e)}")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Using 5001 to avoid conflicts on MacOS
    app.run(debug=True, port=5001)
