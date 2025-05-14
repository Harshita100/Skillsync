from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS so the frontend can communicate with this backend
CORS(app)

@app.route('/api/receive', methods=['POST'])
def receive_data():
    data = request.json  # Try to parse incoming JSON
    if not data or 'text' not in data:
        # Log the issue if the data is invalid or missing the 'text' key
        print("Invalid data received:", data)
        return jsonify({"error": "Invalid data"}), 400

    # Extract the text data from the received JSON
    text_data = data.get('text')
    
    # Save the text data to a file for reference
    with open('input_text.txt', 'w') as file:
        file.write(text_data)
    
    # Log the valid data for debugging purposes
    print("Received text data:", text_data)
    
    # Return only the input text in the response
    return jsonify({"text": text_data}), 201

# Run the Flask app
if __name__ == '_main_':
    app.run(port=5000, debug=True)