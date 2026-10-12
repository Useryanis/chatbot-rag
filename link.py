import yt_dlp

def telecharger_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': False,
        
        # METHODE ULTRA SIMPLE : Connexion par code
        'username': 'oauth2',
        'password': '',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\nDébut du téléchargement pour : {url}")
            ydl.download([url])
            print("Téléchargement et conversion terminés avec succès !")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    lien_video = input("Entrez l'URL de la vidéo YouTube : ")
    telecharger_audio(lien_video)