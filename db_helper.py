import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_NAME = "echostep.db"

# Carbon Emission Factors (in kg CO2e)
EMISSION_FACTORS = {
    "Transport": {
        "Petrol Car": 0.18,       # per km
        "Diesel Car": 0.17,       # per km
        "Electric Vehicle": 0.05,  # per km
        "Bus": 0.04,              # per passenger-km
        "Train": 0.03,            # per passenger-km
        "Flight": 0.12,            # per passenger-km
        "Walk/Cycle": 0.0         # zero emissions
    },
    "Diet": {
        "High Meat": 7.2,         # per day
        "Flexitarian": 3.8,       # per day
        "Vegetarian": 2.5,        # per day
        "Vegan": 1.5              # per day
    },
    "Utilities": {
        "Electricity": 0.40,      # per kWh
        "Natural Gas": 2.00,      # per m³
        "Water": 0.30             # per m³
    }
}

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Activities Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            amount REAL NOT NULL,
            emissions REAL NOT NULL
        )
    """)
    
    # 2. Goals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            target_reduction_pct REAL NOT NULL,
            target_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active'
        )
    """)
    
    # 3. Badges/Achievements Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_name TEXT UNIQUE NOT NULL,
            date_earned TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def calculate_emissions(category, activity_type, amount):
    """Calculates emissions in kg CO2e based on factor tables"""
    factor = EMISSION_FACTORS.get(category, {}).get(activity_type, 0.0)
    return round(amount * factor, 2)

def log_activity(date_str, category, activity_type, amount):
    """Calculates emissions and logs the user activity in the database"""
    emissions = calculate_emissions(category, activity_type, amount)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_activities (date, category, activity_type, amount, emissions)
        VALUES (?, ?, ?, ?, ?)
    """, (date_str, category, activity_type, amount, emissions))
    conn.commit()
    conn.close()
    return emissions

def get_all_activities():
    """Returns all logged activities as a pandas DataFrame"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM user_activities ORDER BY date DESC", conn)
    conn.close()
    return df

def delete_activity(activity_id):
    """Deletes a logged activity by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_activities WHERE id = ?", (activity_id,))
    conn.commit()
    conn.close()

def add_goal(category, target_reduction_pct, target_date_str):
    """Adds a carbon reduction goal"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_goals (category, target_reduction_pct, target_date, status)
        VALUES (?, ?, ?, 'Active')
    """, (category, target_reduction_pct, target_date_str))
    conn.commit()
    conn.close()

def get_goals():
    """Returns all user goals as a pandas DataFrame"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM user_goals ORDER BY target_date ASC", conn)
    conn.close()
    return df

def update_goal_status(goal_id, status):
    """Updates a goal status (e.g. Active, Achieved, Failed)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_goals SET status = ? WHERE id = ?", (status, goal_id))
    conn.commit()
    conn.close()

def delete_goal(goal_id):
    """Deletes a goal by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_goals WHERE id = ?", (goal_id,))
    conn.commit()
    conn.close()

def earn_badge(badge_name):
    """Earns a badge. Skips if already earned."""
    conn = get_connection()
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        cursor.execute("""
            INSERT INTO user_badges (badge_name, date_earned)
            VALUES (?, ?)
        """, (badge_name, date_str))
        conn.commit()
        earned = True
    except sqlite3.IntegrityError:
        # Badge already exists
        earned = False
    conn.close()
    return earned

def get_earned_badges():
    """Returns list of earned badges"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT badge_name, date_earned FROM user_badges ORDER BY date_earned DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def check_and_award_badges():
    """Checks user metrics and awards badges based on habits"""
    # Load all activities
    df = get_all_activities()
    new_badges = []
    
    if len(df) == 0:
        return new_badges
        
    # Badge 1: First Step (Logged first activity)
    if earn_badge("First Step"):
        new_badges.append("First Step")
        
    # Badge 2: Eco Warrior (Logged activities on 7 distinct days)
    unique_dates = df['date'].nunique()
    if unique_dates >= 7:
        if earn_badge("Eco Warrior"):
            new_badges.append("Eco Warrior")
            
    # Badge 3: Green Commuter (Logged at least 3 Transport activities that are Walk/Cycle, Train, or Electric Vehicle with no petrol/diesel commuting)
    transport_df = df[df['category'] == 'Transport']
    if len(transport_df) >= 3:
        green_transport = transport_df[transport_df['activity_type'].isin(['Walk/Cycle', 'Train', 'Electric Vehicle', 'Bus'])]
        non_green_transport = transport_df[transport_df['activity_type'].isin(['Petrol Car', 'Diesel Car', 'Flight'])]
        if len(green_transport) >= 3 and len(non_green_transport) == 0:
            if earn_badge("Green Commuter"):
                new_badges.append("Green Commuter")
                
    # Badge 4: Plant-Powered (Logged at least 5 Vegan or Vegetarian diet days)
    diet_df = df[df['category'] == 'Diet']
    green_diet = diet_df[diet_df['activity_type'].isin(['Vegan', 'Vegetarian'])]
    if len(green_diet) >= 5:
        if earn_badge("Plant-Powered"):
            new_badges.append("Plant-Powered")
            
    # Badge 5: Carbon Cutter (Met a carbon goal - checked when goal statuses are updated)
    # This will be handled in UI or checked against completed goals
    
    return new_badges

def reset_db():
    """Wipes all database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS user_activities")
    cursor.execute("DROP TABLE IF EXISTS user_goals")
    cursor.execute("DROP TABLE IF EXISTS user_badges")
    conn.commit()
    conn.close()
    init_db()
