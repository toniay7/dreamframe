from flask import Flask, request, jsonify, render_template
import requests
import time

app = Flask(__name__)

BASE_URL = 'https://api.thenextleg.io/v2'
AUTH_TOKEN = 'c3e9b67c-28d1-4635-821f-cb302340f7b3'
HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}',
    'Content-Type': 'application/json'
}

@app.route('/')
def index():
    return render_template('dreamframe.html')

@app.route('/backend-endpoint', methods=['POST'])
def process_image():
    data = request.json
    print("Data received from frontend:", data)  # Debugging line

    imageUrl = data['imageUrl']
    specialRequest = data['request']

    # Combine the selected image URL and user input into a single prompt
    combinedPrompt = f"{imageUrl} {specialRequest}"
    print("Combined prompt:", combinedPrompt)  # Debugging line

    # Send the combined prompt to Midjourney via The Next Leg to generate the image
    response = requests.post(f'{BASE_URL}/img-2-img', headers=HEADERS, json={
        "msg": combinedPrompt
    })

    # Debugging: Print the status code and raw response content
    print(response.status_code)
    print(response.text)

    # Check if the response has a JSON content type
    if 'application/json' in response.headers.get('Content-Type'):
        responseData = response.json()
    else:
        print("Received non-JSON response:", response.text)
        return jsonify({"error": "Received non-JSON response from the API"}), 500

    # Check if the API returned a non-200 status code
    if response.status_code != 200:
        print("API returned an error:", response.text)
        return jsonify({"error": f"API returned an error with status {response.status_code}: {response.text}"}), 500

    # Poll for image completion
    messageId = responseData['messageId']
    for _ in range(20):  # Max 20 retries
        time.sleep(5)  # Wait for 5 seconds before polling again
        imageRes = requests.get(f'{BASE_URL}/message/{messageId}', headers=HEADERS)
        imageResponseData = imageRes.json()
        if imageResponseData.get('progress') == 100:
            finalImageUrl = imageResponseData['response']['imageUrl']
            break
    else:
        return jsonify({"error": "Image generation took too long or failed"}), 500

    return jsonify({"finalImageUrl": finalImageUrl})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
