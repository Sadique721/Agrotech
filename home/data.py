# Static Reference Data for AgroTech

# Per-state city list for dropdown in weather page
STATE_CITIES = {
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar", "Anand", "Patan", "Morbi", "Mehsana", "Navsari"],
    "Delhi": ["New Delhi", "Dwarka", "Rohini", "Shahdara", "Janakpuri", "Lajpat Nagar", "Connaught Place", "Karol Bagh", "Saket"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Kolhapur", "Amravati", "Nanded", "Sangli", "Latur", "Akola"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Hoshiarpur", "Gurdaspur", "Firozpur", "Fazilka", "Moga"],
    "Uttar Pradesh": ["Lucknow", "Varanasi", "Agra", "Kanpur", "Prayagraj", "Meerut", "Ghaziabad", "Noida", "Mathura", "Ayodhya", "Gorakhpur", "Moradabad"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Purnia", "Arrah", "Begusarai", "Katihar", "Munger", "Chapra", "Samastipur"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer", "Bhilwara", "Alwar", "Bharatpur", "Sikar", "Pali", "Nagaur"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Malda", "Bardhaman", "Kharagpur", "Haldia", "Bankura", "Cooch Behar"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Dewas", "Satna", "Ratlam", "Rewa", "Murwara", "Singrauli"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Vellore", "Erode", "Thoothukudi", "Dindigul", "Thanjavur"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi", "Davanagere", "Ballari", "Vijayapura", "Shimoga", "Tumkur", "Bidar"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Palakkad", "Malappuram", "Kannur", "Alappuzha", "Kottayam"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Yamunanagar", "Rohtak", "Hisar", "Karnal", "Sonipat", "Bhiwani", "Sirsa"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", "Tirupati", "Kadapa", "Eluru", "Ongole", "Anantapur"],
    "Telangana": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad", "Khammam", "Ramagundam", "Mahbubnagar", "Nalgonda", "Adilabad", "Suryapet"],
    "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tinsukia", "Tezpur", "Bongaigaon", "Dhubri", "Haflong", "Karimganj"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Brahmapur", "Sambalpur", "Puri", "Balasore", "Bhadrak", "Baripada", "Jharsuguda"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamsala", "Solan", "Mandi", "Baddi", "Nahan", "Palampur", "Bilaspur", "Hamirpur", "Una"],
    "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Sopore", "Baramulla", "Kathua", "Udhampur", "Poonch", "Rajouri", "Kulgam"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar", "Hazaribagh", "Giridih", "Ramgarh", "Phusro", "Medininagar"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani", "Rudrapur", "Kashipur", "Rishikesh", "Mussoorie", "Nainital", "Almora"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Korba", "Bilaspur", "Durg", "Rajnandgaon", "Jagdalpur", "Raigarh", "Ambikapur", "Mahasamund"],
}

# Crop icon and image for each state (primary crop emoji + Cloudinary CDN image URL)
STATE_CROP_INFO = {
    "Gujarat":           {"icon": "🥜", "crop": "Groundnut", "img": "https://images.unsplash.com/photo-1568254183919-78a4f43a2877?w=400&h=250&fit=crop&q=80"},
    "Delhi":             {"icon": "🌾", "crop": "Wheat",     "img": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=250&fit=crop&q=80"},
    "Maharashtra":       {"icon": "🎋", "crop": "Sugarcane", "img": "https://images.unsplash.com/photo-1593113598332-cd288d649433?w=400&h=250&fit=crop&q=80"},
    "Punjab":            {"icon": "🌾", "crop": "Wheat",     "img": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=250&fit=crop&q=80"},
    "Uttar Pradesh":     {"icon": "🎋", "crop": "Sugarcane", "img": "https://images.unsplash.com/photo-1593113598332-cd288d649433?w=400&h=250&fit=crop&q=80"},
    "Bihar":             {"icon": "🌾", "crop": "Paddy (Rice)", "img": "https://images.unsplash.com/photo-1536657235019-0307116c19e0?w=400&h=250&fit=crop&q=80"},
    "Rajasthan":         {"icon": "🌿", "crop": "Mustard",   "img": "https://images.unsplash.com/photo-1599930113854-d6d7fd521f10?w=400&h=250&fit=crop&q=80"},
    "West Bengal":       {"icon": "🌾", "crop": "Paddy (Rice)", "img": "https://images.unsplash.com/photo-1536657235019-0307116c19e0?w=400&h=250&fit=crop&q=80"},
    "Madhya Pradesh":    {"icon": "🫘", "crop": "Soybean",   "img": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=400&h=250&fit=crop&q=80"},
    "Tamil Nadu":        {"icon": "🌾", "crop": "Paddy (Rice)", "img": "https://images.unsplash.com/photo-1536657235019-0307116c19e0?w=400&h=250&fit=crop&q=80"},
    "Karnataka":         {"icon": "☕", "crop": "Coffee",    "img": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&h=250&fit=crop&q=80"},
    "Kerala":            {"icon": "🌿", "crop": "Rubber",    "img": "https://images.unsplash.com/photo-1600718374662-0483d2b9da44?w=400&h=250&fit=crop&q=80"},
    "Haryana":           {"icon": "🌾", "crop": "Basmati Rice", "img": "https://images.unsplash.com/photo-1536657235019-0307116c19e0?w=400&h=250&fit=crop&q=80"},
    "Andhra Pradesh":    {"icon": "🌶️", "crop": "Chilli",    "img": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?w=400&h=250&fit=crop&q=80"},
    "Telangana":         {"icon": "🌿", "crop": "Cotton",    "img": "https://images.unsplash.com/photo-1594756202469-9ff9799b2e4e?w=400&h=250&fit=crop&q=80"},
    "Assam":             {"icon": "🍵", "crop": "Tea",       "img": "https://images.unsplash.com/photo-1557800636-894a64c1696f?w=400&h=250&fit=crop&q=80"},
    "Odisha":            {"icon": "🌾", "crop": "Paddy (Rice)", "img": "https://images.unsplash.com/photo-1536657235019-0307116c19e0?w=400&h=250&fit=crop&q=80"},
    "Himachal Pradesh":  {"icon": "🍎", "crop": "Apple",     "img": "https://images.unsplash.com/photo-1619546813926-a78fa6372cd2?w=400&h=250&fit=crop&q=80"},
    "Jammu & Kashmir":   {"icon": "🌸", "crop": "Saffron",   "img": "https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?w=400&h=250&fit=crop&q=80"},
    "Jharkhand":         {"icon": "🌾", "crop": "Paddy (Rice)", "img": "https://images.unsplash.com/photo-1536657235019-0307116c19e0?w=400&h=250&fit=crop&q=80"},
    "Uttarakhand":       {"icon": "🌾", "crop": "Basmati Rice", "img": "https://images.unsplash.com/photo-1536657235019-0307116c19e0?w=400&h=250&fit=crop&q=80"},
    "Chhattisgarh":      {"icon": "🌾", "crop": "Paddy (Rice)", "img": "https://images.unsplash.com/photo-1536657235019-0307116c19e0?w=400&h=250&fit=crop&q=80"},
}

# List of major Indian States & Union Territories with coordinates for instant fast lookup
INDIAN_STATES = [
    {
        "name": "Gujarat (Patan)", 
        "city": "Patan", 
        "state": "Gujarat", 
        "capital": "Gandhinagar / Patan", 
        "pincode": "360001 - 396590", 
        "crops": "Groundnut, Cotton, Wheat, Tobacco, Mustard",
        "lat": 23.85, 
        "lon": 72.12
    },
    {
        "name": "Delhi (New Delhi)", 
        "city": "New Delhi", 
        "state": "Delhi", 
        "capital": "New Delhi", 
        "pincode": "110001 - 110097", 
        "crops": "Wheat, Paddy, Vegetables, Floriculture",
        "lat": 28.61, 
        "lon": 77.21
    },
    {
        "name": "Maharashtra (Mumbai)", 
        "city": "Mumbai", 
        "state": "Maharashtra", 
        "capital": "Mumbai / Nashik", 
        "pincode": "400001 - 445402", 
        "crops": "Sugarcane, Cotton, Soybean, Grapes, Onion",
        "lat": 19.07, 
        "lon": 72.87
    },
    {
        "name": "Punjab (Ludhiana)", 
        "city": "Ludhiana", 
        "state": "Punjab", 
        "capital": "Ludhiana / Chandigarh", 
        "pincode": "140001 - 160001", 
        "crops": "Wheat, Paddy (Rice), Cotton, Sugarcane, Maize",
        "lat": 30.90, 
        "lon": 75.85
    },
    {
        "name": "Uttar Pradesh (Lucknow)", 
        "city": "Lucknow", 
        "state": "Uttar Pradesh", 
        "capital": "Lucknow", 
        "pincode": "201001 - 285223", 
        "crops": "Sugarcane, Wheat, Paddy, Potato, Mango",
        "lat": 26.85, 
        "lon": 80.95
    },
    {
        "name": "Bihar (Begusarai)", 
        "city": "Begusarai", 
        "state": "Bihar", 
        "capital": "Begusarai / Patna", 
        "pincode": "800001 - 855116", 
        "crops": "Paddy, Wheat, Maize, Makhana, Litchi, Mango",
        "lat": 25.42, 
        "lon": 86.13
    },
    {
        "name": "Rajasthan (Jaipur)", 
        "city": "Jaipur", 
        "state": "Rajasthan", 
        "capital": "Jaipur", 
        "pincode": "301001 - 345034", 
        "crops": "Mustard, Bajra, Spices, Guar, Pulses",
        "lat": 26.91, 
        "lon": 75.78
    },
    {
        "name": "West Bengal (Kolkata)", 
        "city": "Kolkata", 
        "state": "West Bengal", 
        "capital": "Kolkata", 
        "pincode": "700001 - 743711", 
        "crops": "Paddy (Rice), Jute, Tea, Potato, Maize",
        "lat": 22.57, 
        "lon": 88.36
    },
    {
        "name": "Madhya Pradesh (Bhopal)", 
        "city": "Bhopal", 
        "state": "Madhya Pradesh", 
        "capital": "Bhopal", 
        "pincode": "450001 - 488448", 
        "crops": "Soybean, Wheat, Gram (Chana), Garlic, Cotton",
        "lat": 23.26, 
        "lon": 77.41
    },
    {
        "name": "Tamil Nadu (Chennai)", 
        "city": "Chennai", 
        "state": "Tamil Nadu", 
        "capital": "Chennai", 
        "pincode": "600001 - 643253", 
        "crops": "Paddy, Sugarcane, Coconut, Groundnut, Spices",
        "lat": 13.08, 
        "lon": 80.27
    },
    {
        "name": "Karnataka (Bengaluru)", 
        "city": "Bengaluru", 
        "state": "Karnataka", 
        "capital": "Bengaluru", 
        "pincode": "560001 - 591344", 
        "crops": "Coffee, Ragi, Silk, Sugarcane, Maize, Spices",
        "lat": 12.97, 
        "lon": 77.59
    },
    {
        "name": "Kerala (Thiruvananthapuram)", 
        "city": "Thiruvananthapuram", 
        "state": "Kerala", 
        "capital": "Thiruvananthapuram", 
        "pincode": "680001 - 695615", 
        "crops": "Rubber, Pepper, Cardamom, Coconut, Tea, Coffee",
        "lat": 8.52, 
        "lon": 76.94
    },
    {
        "name": "Haryana (Karnal)", 
        "city": "Karnal", 
        "state": "Haryana", 
        "capital": "Karnal / Chandigarh", 
        "pincode": "121001 - 136135", 
        "crops": "Basmati Rice, Wheat, Cotton, Mustard, Sugarcane",
        "lat": 29.69, 
        "lon": 76.98
    },
    {
        "name": "Andhra Pradesh (Vijayawada)", 
        "city": "Vijayawada", 
        "state": "Andhra Pradesh", 
        "capital": "Vijayawada / Amaravati", 
        "pincode": "515001 - 535593", 
        "crops": "Chilli, Tobacco, Paddy, Cotton, Groundnut",
        "lat": 16.51, 
        "lon": 80.64
    },
    {
        "name": "Telangana (Hyderabad)", 
        "city": "Hyderabad", 
        "state": "Telangana", 
        "capital": "Hyderabad", 
        "pincode": "500001 - 509412", 
        "crops": "Cotton, Paddy, Red Gram, Turmeric, Maize",
        "lat": 17.38, 
        "lon": 78.48
    },
    {
        "name": "Assam (Guwahati)", 
        "city": "Guwahati", 
        "state": "Assam", 
        "capital": "Guwahati / Dispur", 
        "pincode": "781001 - 788931", 
        "crops": "Tea, Rice, Jute, Mustard, Arecanut",
        "lat": 26.14, 
        "lon": 91.73
    },
    {
        "name": "Odisha (Bhubaneswar)", 
        "city": "Bhubaneswar", 
        "state": "Odisha", 
        "capital": "Bhubaneswar", 
        "pincode": "751001 - 770077", 
        "crops": "Paddy (Rice), Pulses, Oilseeds, Jute, Coconut",
        "lat": 20.30, 
        "lon": 85.82
    },
    {
        "name": "Himachal Pradesh (Shimla)", 
        "city": "Shimla", 
        "state": "Himachal Pradesh", 
        "capital": "Shimla", 
        "pincode": "171001 - 177601", 
        "crops": "Apple, Maize, Wheat, Plum, Exotic Vegetables",
        "lat": 31.10, 
        "lon": 77.17
    },
    {
        "name": "Jammu & Kashmir (Srinagar)", 
        "city": "Srinagar", 
        "state": "Jammu & Kashmir", 
        "capital": "Srinagar / Jammu", 
        "pincode": "180001 - 194404", 
        "crops": "Saffron, Apple, Walnut, Almond, Rice",
        "lat": 34.08, 
        "lon": 74.79
    },
    {
        "name": "Jharkhand (Ranchi)", 
        "city": "Ranchi", 
        "state": "Jharkhand", 
        "capital": "Ranchi", 
        "pincode": "814101 - 835325", 
        "crops": "Paddy (Rice), Pulses, Maize, Vegetables",
        "lat": 23.34, 
        "lon": 85.31
    },
    {
        "name": "Uttarakhand (Dehradun)", 
        "city": "Dehradun", 
        "state": "Uttarakhand", 
        "capital": "Dehradun", 
        "pincode": "246001 - 263681", 
        "crops": "Rice, Wheat, Basmati, Organic Fruits",
        "lat": 30.31, 
        "lon": 78.03
    },
    {
        "name": "Chhattisgarh (Raipur)", 
        "city": "Raipur", 
        "state": "Chhattisgarh", 
        "capital": "Raipur", 
        "pincode": "490001 - 497449", 
        "crops": "Rice (Rice Bowl of India), Kodo-Kutki, Maize",
        "lat": 21.25, 
        "lon": 81.63
    },
]

WMO_WEATHER_CODES = {
    0: {"desc": "Clear Sky / Sunny", "icon": "☀️", "bg": "sunny"},
    1: {"desc": "Mainly Clear", "icon": "🌤️", "bg": "partly-cloudy"},
    2: {"desc": "Partly Cloudy", "icon": "⛅", "bg": "partly-cloudy"},
    3: {"desc": "Overcast / Cloudy", "icon": "☁️", "bg": "cloudy"},
    45: {"desc": "Foggy / Hazy", "icon": "🌫️", "bg": "foggy"},
    48: {"desc": "Depositing Rime Fog", "icon": "🌫️", "bg": "foggy"},
    51: {"desc": "Light Drizzle", "icon": "🌦️", "bg": "rainy"},
    53: {"desc": "Moderate Drizzle", "icon": "🌦️", "bg": "rainy"},
    55: {"desc": "Dense Drizzle", "icon": "🌧️", "bg": "rainy"},
    61: {"desc": "Slight Rain", "icon": "🌧️", "bg": "rainy"},
    63: {"desc": "Moderate Rain", "icon": "🌧️", "bg": "rainy"},
    65: {"desc": "Heavy Rain", "icon": "🌧️", "bg": "rainy"},
    80: {"desc": "Light Rain Showers", "icon": "🌦️", "bg": "rainy"},
    81: {"desc": "Moderate Rain Showers", "icon": "🌧️", "bg": "rainy"},
    82: {"desc": "Violent Rain Showers", "icon": "⛈️", "bg": "stormy"},
    95: {"desc": "Thunderstorm", "icon": "⛈️", "bg": "stormy"},
    96: {"desc": "Thunderstorm with Hail", "icon": "⛈️", "bg": "stormy"},
}
