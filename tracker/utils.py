def predict_category(text):
    text = (text or "").lower()
    keywords = {
        "Food": ["restaurant", "food", "lunch", "dinner", "breakfast", "coffee", "grocery", "swiggy", "zomato"],
        "Transport": ["bus", "train", "metro", "fuel", "petrol", "taxi", "uber", "ola", "auto"],
        "Shopping": ["shopping", "clothes", "shoes", "amazon", "flipkart", "mall"],
        "Bills": ["electricity", "water bill", "internet", "mobile recharge", "rent", "bill"],
        "Health": ["doctor", "medicine", "hospital", "pharmacy", "clinic"],
        "Education": ["book", "course", "college", "tuition", "exam", "stationery"],
        "Entertainment": ["movie", "cinema", "netflix", "game", "concert"],
        "Travel": ["hotel", "flight", "trip", "booking", "vacation"],
    }
    for category, words in keywords.items():
        if any(word in text for word in words):
            return category
    return "Other"
