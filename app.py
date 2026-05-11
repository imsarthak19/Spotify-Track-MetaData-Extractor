import os
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    playlist_id = request.form.get('playlist_id')
    # Placeholder for Spotify extraction logic
    return f"Playlist ID received: {playlist_id}. Extraction logic coming soon!"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
