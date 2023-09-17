from flask import Flask, request, jsonify, render_template
from midjourney_api import TNL
import os

app = Flask(__name__)

TNL_API_KEY = 'c3e9b67c-28d1-4635-821f-cb302340f7b3'
tnl = TNL(TNL_API_KEY)

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
    response = tnl.img_2_img(combinedPrompt)

    # Check if the response is successful
    if response.get('status') != 'success':
        print("API returned an error:", response.get('message'))
        return jsonify({"error": f"API returned an error: {response.get('message')}"}), 500

    # Poll for image completion
    messageId = response['messageId']
    for _ in range(20):  # Max 20 retries
        imageResponseData = tnl.get_message(messageId)
        if imageResponseData.get('progress') == 100:
            finalImageUrl = imageResponseData['response']['imageUrl']
            break
    else:
        return jsonify({"error": "Image generation took too long or failed"}), 500

    return jsonify({"finalImageUrl": finalImageUrl})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
