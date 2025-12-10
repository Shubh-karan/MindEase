import random

THERAPISTS_DB = [
    {"name": "Dr. Sarah Cohen", "specialty": "Anxiety & Stress", "location": "Downtown", "rating": 4.9, "contact": "555-0101"},
    {"name": "Dr. Rajesh Gupta", "specialty": "Depression & Mood Disorders", "location": "Northside", "rating": 4.8, "contact": "555-0102"},
    {"name": "Emily Chen, LCSW", "specialty": "Trauma & PTSD", "location": "West End", "rating": 4.7, "contact": "555-0103"},
    {"name": "Dr. Michael O'Connor", "specialty": "Cognitive Behavioral Therapy", "location": "City Center", "rating": 4.9, "contact": "555-0104"},
    {"name": "Lisa Ray", "specialty": "Art Therapy & Mindfulness", "location": "South Hills", "rating": 4.6, "contact": "555-0105"}
]

def find_therapists(emotion):
    if emotion.lower() in ['sad', 'fear', 'angry', 'negative']:
        return random.sample(THERAPISTS_DB, 2)
    return random.sample(THERAPISTS_DB, 1)