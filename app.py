from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    format_type = request.form.get('format') # mp4 or mp3

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if format_type == 'mp4' else 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if format_type == 'mp3' else [],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if format_type == 'mp3':
                path = path.rsplit('.', 1)[0] + '.mp3'

        @after_this_request
        def remove_file(response):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error deleting file: {e}")
            return response

        return send_file(path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)