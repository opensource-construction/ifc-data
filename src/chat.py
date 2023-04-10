from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import tempfile
import openai

app = Flask(__name__)
CORS(app)

def chat_with_gpt(prompt, api_key, json_data):
    openai.api_key = api_key

    # Add JSON data as context to GPT the bot
    context = f"JSON data: {json_data}\n"
    prompt_with_context = context + prompt

    # Create a prompt for GPT-3
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt_with_context,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # Extract the generated text from the response
    message = response.choices[0].text.strip()
    return message

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()

        if data is None:
            raise ValueError("Invalid JSON data")

        api_key = os.getenv("OPENAI_API_KEY")

        prompt = data['prompt']
        ifc_content = data['ifc_content']

        # Convert the base64 IFC content to binary
        ifc_binary_content = base64.b64decode(ifc_content.split(",")[-1])

        # Save the IFC content to a temporary file
        temp_ifc_file = tempfile.NamedTemporaryFile(delete=False)
        temp_ifc_file.write(ifc_binary_content)
        temp_ifc_file.close()

        # Read the JSON content from the temporary file
        with open(temp_ifc_file.name, 'r') as file:
            json_content = file.read()

        response = chat_with_gpt(prompt, api_key, json_content)

        # Clean up the temporary file
        os.remove(temp_ifc_file.name)

        return jsonify({"response": response})
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001)
