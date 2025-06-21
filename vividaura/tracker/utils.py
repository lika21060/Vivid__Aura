import requests
def search_youtube_videos(query, api_key):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'type': 'video',  
        'q': query,
        'key': api_key,
        'maxResults': 5,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
       
        items = data.get('items', [])
        videos = []
        for item in items:
          
            if 'id' in item and 'videoId' in item['id']:
                videos.append(item)
        return videos
    else:
        return []
