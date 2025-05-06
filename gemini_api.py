import requests

GOOGLE_API_KEY = 'AIzaSyC9iG2ZU6mHOo1a_qKNPiZ0tioUcbWrb1M'
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

def generate_gemini_response(prompt):
    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        'key': GOOGLE_API_KEY,
    }

    json_data = {
        'contents': [
            {
                'parts': [{'text': prompt}],
            },
        ],
    }

    response = requests.post(
        GEMINI_URL,
        params=params,
        headers=headers,
        json=json_data,
    )

    if response.status_code != 200:
        return {'error': 'API error', 'details': response.text}

    try:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        return {'response': text}
    except (KeyError, IndexError):
        return {'error': 'Invalid response structure', 'details': result}
