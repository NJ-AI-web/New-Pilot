from googlesearch import search

print("🌍 Testing Free Google Search...")

try:
    # advanced=True கொடுத்தால் தலைப்பு மற்றும் விளக்கம் கிடைக்கும்
    results = search("latest iphone 16 price india", num_results=1, advanced=True)
    
    # இது ஒரு 'Generator', அதனால் list-ஆக மாற்றுகிறோம்
    results_list = list(results)

    if results_list:
        print("✅ SUCCESS! Google is Working (FREE)!")
        print(f"Title: {results_list[0].title}")
        print(f"Info: {results_list[0].description}")
    else:
        print("❌ Connected, but no results.")

except Exception as e:
    print(f"❌ ERROR: {e}")