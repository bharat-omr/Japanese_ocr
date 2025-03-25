import asyncio
from googletrans import Translator

async def translate_japanese_to_english(text):
    translator = Translator()
    result = await translator.translate(text, src='ja', dest='en')  # Await the coroutine
    return result.text  # Returns the translated text

# Example usage
async def main():
    japanese_texts = ["こんにちは", "ありがとう", "日本は美しい"]
    for text in japanese_texts:
        translated_text = await translate_japanese_to_english(text)
        print(f"Japanese: {text} → English: {translated_text}")

asyncio.run(main())  # Run the async function
