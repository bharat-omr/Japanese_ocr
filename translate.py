from flask import Blueprint, request, jsonify
from googletrans import Translator

translate_bp = Blueprint("translate", __name__)
translator = Translator()

@translate_bp.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        english_text = data.get("text", "")

        if not english_text:
            return jsonify({"error": "No text provided"}), 400

        # Just call translate normally (without async)
        translated = translator.translate(english_text, src="en", dest="ja")

        return jsonify({"translated_text": translated.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
