import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import db_helper
import ai_engine
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Initialize database
db_helper.init_db()

# Page Setup
st.set_page_config(
    page_title="EchoStep AI - Carbon Footprint Tracker",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
CSS_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Base style overrides */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #F8F7F3 !important; /* Premium off-white/cream background */
    font-family: 'Outfit', sans-serif !important;
    color: #1A3E2D !important;
}

/* Sidebar styling overrides */
[data-testid="stSidebar"] {
    background-color: #1A3E2D !important; /* Forest green */
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

[data-testid="stSidebar"] .stMarkdown, 
[data-testid="stSidebar"] .stRadio, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p, 
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span,
[data-testid="stSidebar"] p {
    color: #FFFFFF !important;
    font-family: 'Outfit', sans-serif !important;
}

/* Prevent Streamlit collapse button and other UI icons from breaking */
[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] *,
[data-testid="stSidebar"] [data-testid="stIcon"] {
    font-family: inherit !important;
    color: inherit !important;
}

/* Input boxes in sidebar */
[data-testid="stSidebar"] input {
    color: #1A3E2D !important;
    background-color: #FFFFFF !important;
}

/* Styled containers for metrics */
.metric-card {
    background: #FFFFFF;
    border: 1px solid rgba(26, 62, 45, 0.1);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 4px 15px rgba(26, 62, 45, 0.03);
    margin-bottom: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(26, 62, 45, 0.07);
}

.metric-title {
    font-size: 13px;
    font-weight: 600;
    color: #5C7667;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #1A3E2D;
    line-height: 1.1;
}

.metric-unit {
    font-size: 14px;
    font-weight: 500;
    color: #5C7667;
}

.metric-subtitle {
    font-size: 11px;
    color: #79D14C;
    margin-top: 6px;
    font-weight: 600;
}

/* Badge Cards */
.badge-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 15px;
}

.badge-card {
    background: #FFFFFF;
    border: 1px solid rgba(26, 62, 45, 0.12);
    border-radius: 14px;
    padding: 16px;
    width: 140px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.01);
    transition: all 0.2s ease;
}

.badge-card.unlocked {
    border-color: #79D14C;
    background-color: #F0FAF3;
}

.badge-card.locked {
    opacity: 0.45;
    background-color: #ECEBE8;
    filter: grayscale(100%);
}

.badge-icon {
    font-size: 32px;
    margin-bottom: 8px;
}

.badge-name {
    font-size: 12px;
    font-weight: 700;
    color: #1A3E2D;
}

.badge-desc {
    font-size: 9px;
    color: #5C7667;
    margin-top: 4px;
    line-height: 1.2;
}

/* Equivalency items */
.equiv-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background-color: #F0F5F2;
    border-radius: 10px;
    margin-bottom: 8px;
}

.equiv-icon {
    font-size: 24px;
}

.equiv-text {
    font-size: 13px;
    color: #1A3E2D;
    font-weight: 500;
}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# Badge catalog configuration
ALL_BADGES = {
    "First Step": {"icon": "🌱", "desc": "Logged your first activity. Commenced the green journey!"},
    "Eco Warrior": {"icon": "🛡️", "desc": "Logged carbon activities on 7 distinct days."},
    "Green Commuter": {"icon": "🚲", "desc": "Logged 3+ transits using only eco options (Walk/Cycle, train, bus, EV)."},
    "Plant-Powered": {"icon": "🥗", "desc": "Logged 5+ plant-based (vegan/vegetarian) days."},
    "Carbon Cutter": {"icon": "✂️", "desc": "Successfully met one of your carbon reduction goals."}
}

# Session API Key Management
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# Sidebar Configurations
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/leaf.png", width=60) # Visual logo representation
    st.markdown("## **EchoStep AI**")
    st.markdown("*Climate Action Advisor*")
    st.markdown("---")
    
    # Navigation Radio
    nav_selection = st.radio(
        "Navigation Menu",
        ["📊 Dashboard", "📝 Log Activity", "💬 AI Eco-Coach", "🏆 Goals & Badges", "📄 AI Action Plan"]
    )
    
    st.markdown("---")
    st.markdown("### Settings")
    user_key = st.text_input("Gemini API Key", value=st.session_state["api_key"], type="password", placeholder="Using default key...")
    if user_key:
        st.session_state["api_key"] = user_key
        
    st.markdown("---")
    st.markdown("© 2026 EchoStep AI. Empowering bottom-up carbon tracking for global sustainability.")

# Load active data
activities_df = db_helper.get_all_activities()
goals_df = db_helper.get_goals()

# Automatically check and award badges
new_badges = db_helper.check_and_award_badges()
for badge in new_badges:
    st.toast(f"🎉 Achievement Unlocked: {badge}!", icon="🏆")

# Load earned badges
earned_badges_data = db_helper.get_earned_badges()
earned_badges_names = [b['badge_name'] for b in earned_badges_data]

# Report Generator Helper
def generate_pdf_report(activities, goals, action_plan_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22,
        leading=26, textColor=colors.HexColor('#1A3E2D'), spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14,
        leading=18, textColor=colors.HexColor('#1A3E2D'), spaceBefore=15, spaceAfter=8
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'], fontName='Helvetica', fontSize=10,
        leading=14, textColor=colors.HexColor('#222222'), spaceAfter=8
    )
    
    story.append(Paragraph("EchoStep AI - Carbon Footprint & Action Plan", title_style))
    story.append(Paragraph(f"Report Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1. Carbon Footprint Summary", h2_style))
    if not activities.empty:
        total = activities['emissions'].sum()
        by_cat = activities.groupby('category')['emissions'].sum().to_dict()
        
        table_data = [["Category", "Total Emissions (kg CO2e)", "Percentage"]]
        for cat, val in by_cat.items():
            pct = (val / total) * 100 if total > 0 else 0
            table_data.append([cat, f"{val:.2f}", f"{pct:.1f}%"])
        table_data.append(["TOTAL", f"{total:.2f}", "100.0%"])
        
        t = Table(table_data, colWidths=[150, 150, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A3E2D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-2), colors.HexColor('#F8F7F3')),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E2ECE6')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D3D3D3')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No activity logs available yet.", body_style))
        
    story.append(Spacer(1, 15))
    story.append(Paragraph("2. AI-Driven Carbon Reduction Advice", h2_style))
    
    # Simple formatting of markdown to PDF
    import re
    lines = action_plan_text.split('\n')
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            story.append(Spacer(1, 4))
            continue
            
        html_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cleaned)
        if html_line.startswith('###'):
            story.append(Paragraph(html_line.replace('###', '').strip(), ParagraphStyle('h3', parent=h2_style, fontSize=11, leading=13)))
        elif html_line.startswith('##'):
            story.append(Paragraph(html_line.replace('##', '').strip(), ParagraphStyle('h2_sub', parent=h2_style, fontSize=12, leading=14)))
        elif html_line.startswith('#'):
            story.append(Paragraph(html_line.replace('#', '').strip(), h2_style))
        elif html_line.startswith('-') or html_line.startswith('*'):
            story.append(Paragraph(f"&bull; {html_line[1:].strip()}", ParagraphStyle('bullet', parent=body_style, leftIndent=12)))
        else:
            story.append(Paragraph(html_line, body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# RENDERING NAVIGATION SECTIONS

if nav_selection == "📊 Dashboard":
    st.markdown("# 📊 Carbon Accountant Dashboard")
    st.markdown("Monitor emission metrics and understand your environmental footprint.")
    
    if activities_df.empty:
        st.info("👋 Welcome to EchoStep AI! You haven't logged any carbon activities yet. Go to **Log Activity** in the sidebar to get started.")
        # Render a mock/placeholder analysis section to demonstrate capabilities
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Carbon Accounting Scope Breakdown")
            st.markdown(
                "Once logged, your daily footprint will automatically classify into **Scopes** (based on the Greenhouse Gas Protocol):\n"
                "- **Scope 1 (Direct)**: Petrol/Diesel commuter trips.\n"
                "- **Scope 2 (Indirect - Utilities)**: Home electricity consumption.\n"
                "- **Scope 3 (Other Indirect)**: Dietary habits and global short/long haul flights."
            )
        with col2:
            st.markdown("### Smart Carbon Offset Potential")
            st.markdown("Visualized equivalents will map your total footprint to physical units like tree seedlings planted or smartphone charges avoided.")
    else:
        # Total Carbon stats
        total_co2 = activities_df['emissions'].sum()
        
        # Calculate Top Sector
        category_totals = activities_df.groupby('category')['emissions'].sum()
        top_sector = category_totals.idxmax() if not category_totals.empty else "None"
        
        # Metrics Row
        st.markdown(f"""
        <div style="display: flex; gap: 20px; justify-content: space-between; flex-wrap: wrap;">
            <div class="metric-card" style="flex: 1; min-width: 250px;">
                <div class="metric-title">Total Emissions</div>
                <div class="metric-value">{total_co2:.2f} <span class="metric-unit">kg CO2e</span></div>
                <div class="metric-subtitle">Accumulated overall footprint</div>
            </div>
            <div class="metric-card" style="flex: 1; min-width: 250px;">
                <div class="metric-title">Highest Emission Category</div>
                <div class="metric-value">{top_sector}</div>
                <div class="metric-subtitle">Sector requiring priority action</div>
            </div>
            <div class="metric-card" style="flex: 1; min-width: 250px;">
                <div class="metric-title">Unlocked Badges</div>
                <div class="metric-value">{len(earned_badges_names)} <span class="metric-unit">/ 5</span></div>
                <div class="metric-subtitle">Gamified Climate Milestones</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Grid layout for charts and equivalencies
        chart_col, info_col = st.columns([2, 1])
        
        with chart_col:
            st.subheader("Footprint Category Distribution")
            pie_data = activities_df.groupby('category', as_index=False)['emissions'].sum()
            fig_pie = px.pie(
                pie_data, 
                values='emissions', 
                names='category', 
                hole=0.45,
                color_discrete_sequence=['#1A3E2D', '#79D14C', '#5C7667']
            )
            fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.subheader("Emissions Log History")
            hist_data = activities_df.groupby(['date', 'category'], as_index=False)['emissions'].sum()
            fig_bar = px.bar(
                hist_data,
                x='date',
                y='emissions',
                color='category',
                barmode='stack',
                color_discrete_map={'Transport': '#1A3E2D', 'Diet': '#79D14C', 'Utilities': '#5C7667'}
            )
            fig_bar.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with info_col:
            st.subheader("Scope Breakdowns")
            # Scope 1: Petrol/Diesel Car, Flight
            # Scope 2: Electricity
            # Scope 3: Gas, Water, Diet, Bus, Train, EV
            scope_emissions = {"Scope 1 (Direct)": 0.0, "Scope 2 (Indirect)": 0.0, "Scope 3 (Other Indirect)": 0.0}
            
            for _, row in activities_df.iterrows():
                cat = row['category']
                act = row['activity_type']
                em = row['emissions']
                
                if cat == 'Transport' and act in ['Petrol Car', 'Diesel Car', 'Flight']:
                    scope_emissions["Scope 1 (Direct)"] += em
                elif cat == 'Utilities' and act == 'Electricity':
                    scope_emissions["Scope 2 (Indirect)"] += em
                else:
                    scope_emissions["Scope 3 (Other Indirect)"] += em
                    
            st.markdown(f"""
            <div class="metric-card" style="padding: 15px; margin-bottom: 15px;">
                <div style="font-weight: 600; font-size:12px; color:#5C7667;">Scope 1 - Direct Emissions</div>
                <div style="font-size:22px; font-weight:700;">{scope_emissions["Scope 1 (Direct)"]:.2f} kg CO2e</div>
            </div>
            <div class="metric-card" style="padding: 15px; margin-bottom: 15px;">
                <div style="font-weight: 600; font-size:12px; color:#5C7667;">Scope 2 - Utility Indirect</div>
                <div style="font-size:22px; font-weight:700;">{scope_emissions["Scope 2 (Indirect)"]:.2f} kg CO2e</div>
            </div>
            <div class="metric-card" style="padding: 15px; margin-bottom: 15px;">
                <div style="font-weight: 600; font-size:12px; color:#5C7667;">Scope 3 - Other Indirect</div>
                <div style="font-size:22px; font-weight:700;">{scope_emissions["Scope 3 (Other Indirect)"]:.2f} kg CO2e</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Footprint Equivalents")
            # Math conversions
            car_miles = total_co2 / 0.4
            smartphone_charges = total_co2 / 0.008
            tree_years = total_co2 / 22.0
            
            st.markdown(f"""
            <div class="equiv-card">
                <span class="equiv-icon">🚗</span>
                <span class="equiv-text">Driving a petrol car <b>{car_miles:.1f}</b> miles</span>
            </div>
            <div class="equiv-card">
                <span class="equiv-icon">📱</span>
                <span class="equiv-text">Charging a smartphone <b>{smartphone_charges:,.0f}</b> times</span>
            </div>
            <div class="equiv-card">
                <span class="equiv-icon">🌲</span>
                <span class="equiv-text"><b>{tree_years:.2f}</b> trees needed to absorb this in 1 year</span>
            </div>
            """, unsafe_allow_html=True)


elif nav_selection == "📝 Log Activity":
    st.markdown("# 📝 Log Daily Activities")
    st.markdown("Record your travel, food, and home utility usage to track carbon metrics.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Log Activity Form")
        category = st.selectbox("Category", ["Transport", "Diet", "Utilities"])
        
        # Date selection
        log_date = st.date_input("Date", value=date.today())
        date_str = log_date.strftime("%Y-%m-%d")
        
        if category == "Transport":
            transit_type = st.selectbox(
                "Transportation Mode", 
                ["Petrol Car", "Diesel Car", "Electric Vehicle", "Bus", "Train", "Flight", "Walk/Cycle"]
            )
            distance = st.number_input("Distance (kilometers)", min_value=0.1, max_value=5000.0, value=10.0, step=1.0)
            
            if st.button("Add Transport Log", use_container_width=True):
                emissions = db_helper.log_activity(date_str, "Transport", transit_type, distance)
                st.success(f"Successfully logged transport! Calculated emissions: {emissions} kg CO2e")
                st.rerun()
                
        elif category == "Diet":
            diet_type = st.selectbox(
                "Dietary Habits",
                ["High Meat", "Flexitarian", "Vegetarian", "Vegan"]
            )
            days = st.number_input("Number of Days", min_value=1, max_value=31, value=1, step=1)
            
            if st.button("Add Diet Log", use_container_width=True):
                emissions = db_helper.log_activity(date_str, "Diet", diet_type, days)
                st.success(f"Successfully logged diet! Calculated emissions: {emissions} kg CO2e")
                st.rerun()
                
        elif category == "Utilities":
            utility_type = st.selectbox(
                "Utility Type",
                ["Electricity", "Natural Gas", "Water"]
            )
            if utility_type == "Electricity":
                amount = st.number_input("Electricity Used (kWh)", min_value=0.1, max_value=5000.0, value=10.0, step=1.0)
            elif utility_type == "Natural Gas":
                amount = st.number_input("Gas Used (cubic meters - m³)", min_value=0.1, max_value=2000.0, value=5.0, step=0.5)
            else:
                amount = st.number_input("Water Consumption (cubic meters - m³)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
                
            if st.button("Add Utility Log", use_container_width=True):
                emissions = db_helper.log_activity(date_str, "Utilities", utility_type, amount)
                st.success(f"Successfully logged utility usage! Calculated emissions: {emissions} kg CO2e")
                st.rerun()
                
    with col2:
        st.subheader("Logged Activity Records")
        if activities_df.empty:
            st.info("No activity records found. Use the form on the left to log some data.")
        else:
            # Display records inside a table with deletion buttons
            activities_show = activities_df.copy()
            activities_show.columns = ["Record ID", "Date", "Category", "Sub-Type", "Logged Amount", "Emissions (kg CO2e)"]
            
            # Simple paginated/scrollable table
            st.dataframe(activities_show, use_container_width=True, hide_index=True)
            
            # Delete record tool
            st.markdown("### Remove Incorrect Entries")
            record_to_delete = st.selectbox("Select Record ID to Delete", activities_df['id'].tolist())
            if st.button("Delete Selected Record", type="secondary"):
                db_helper.delete_activity(record_to_delete)
                st.toast("Record deleted successfully.")
                st.rerun()
                
            # Clear Database Tool
            st.markdown("---")
            if st.checkbox("Show Developer Reset Options"):
                if st.button("Wipe Database", type="primary"):
                    db_helper.reset_db()
                    st.toast("Database wiped successfully.")
                    st.rerun()


elif nav_selection == "💬 AI Eco-Coach":
    st.markdown("# 💬 AI Eco-Coach Chatbot")
    st.markdown("Ask our sustainability coach how to adopt greener daily habits and reduce emissions.")
    
    # Init chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        
    # Display chat messages
    for msg in st.session_state["chat_history"]:
        role_label = "Model" if msg["role"] == "model" else "User"
        avatar = "🌱" if msg["role"] == "model" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
    # Chat Input
    if prompt := st.chat_input("Ask about sustainable alternative transit, diets, electricity saving..."):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        
        # Get AI Response
        with st.chat_message("model", avatar="🌱"):
            with st.spinner("AI Coach is formulating advice..."):
                response_text = ai_engine.get_eco_coach_response(
                    st.session_state["chat_history"][:-1], 
                    prompt, 
                    st.session_state["api_key"]
                )
                st.markdown(response_text)
                
        st.session_state["chat_history"].append({"role": "model", "content": response_text})


elif nav_selection == "🏆 Goals & Badges":
    st.markdown("# 🏆 Gamified Milestones & Goals")
    st.markdown("Set carbon targets, reduce your footprint, and unlock special eco-badges!")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Set a Carbon Goal")
        goal_cat = st.selectbox("Goal Category", ["Transport", "Diet", "Utilities", "Total"])
        target_reduction = st.number_input("Target Reduction (%)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
        target_date = st.date_input("Target Achieve Date", value=date.today())
        
        if st.button("Set Goal", use_container_width=True):
            db_helper.add_goal(goal_cat, target_reduction, target_date.strftime("%Y-%m-%d"))
            st.success("Reduction goal successfully set! Track it on the right panel.")
            st.rerun()
            
    with col2:
        st.subheader("Your Active Carbon Goals")
        if goals_df.empty:
            st.info("No reduction goals established yet. Challenge yourself with a target!")
        else:
            # Table list of goals
            display_goals = goals_df.copy()
            display_goals.columns = ["Goal ID", "Category", "Target Red. %", "Target Date", "Status"]
            st.dataframe(display_goals, use_container_width=True, hide_index=True)
            
            # Interactive Complete & Delete Goal Tool
            st.markdown("### Manage Goal Status")
            all_goal_ids = goals_df['id'].tolist()
            if all_goal_ids:
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    active_goal_ids = goals_df[goals_df['status'] == 'Active']['id'].tolist()
                    if active_goal_ids:
                        goal_select = st.selectbox("Select Goal to Complete", active_goal_ids)
                        if st.button("Mark Goal as Achieved", type="primary", use_container_width=True):
                            db_helper.update_goal_status(goal_select, "Achieved")
                            db_helper.earn_badge("Carbon Cutter")
                            st.toast("Congratulations! Goal marked as Achieved. Carbon Cutter badge awarded!", icon="🏆")
                            st.rerun()
                    else:
                        st.success("All active goals completed!")
                with col_g2:
                    goal_delete_select = st.selectbox("Select Goal to Delete", all_goal_ids)
                    if st.button("Delete Selected Goal", type="secondary", use_container_width=True):
                        db_helper.delete_goal(goal_delete_select)
                        st.toast("Goal deleted successfully.")
                        st.rerun()
                
    st.markdown("---")
    st.subheader("Unlocked Achievements & Eco-Badges")
    
    # Draw badges
    badge_html = "<div class='badge-grid'>"
    for badge_name, badge_info in ALL_BADGES.items():
        is_unlocked = badge_name in earned_badges_names
        unlock_class = "unlocked" if is_unlocked else "locked"
        status_text = "Unlocked" if is_unlocked else "Locked"
        
        badge_html += f'<div class="badge-card {unlock_class}">' \
                      f'<div class="badge-icon">{badge_info["icon"]}</div>' \
                      f'<div class="badge-name">{badge_name}</div>' \
                      f'<div class="badge-desc">{badge_info["desc"]}</div>' \
                      f'<div style="font-size: 9px; font-weight: 700; margin-top: 6px; color: {"#79D14C" if is_unlocked else "#888888"};">{status_text}</div>' \
                      f'</div>'
    badge_html += "</div>"
    st.markdown(badge_html, unsafe_allow_html=True)


elif nav_selection == "📄 AI Action Plan":
    st.markdown("# 📄 AI Carbon Advisor & Action Plan")
    st.markdown("Run the recommendation engine to compile custom strategies, then download the PDF report.")
    
    # Store recommendation plan in session state
    if "recommendation_plan" not in st.session_state:
        st.session_state["recommendation_plan"] = ""
        
    plan_col, pdf_col = st.columns([2, 1])
    
    with plan_col:
        st.subheader("Personalized Carbon Mitigation Strategies")
        
        if st.button("Generate Recommendations Plan", type="primary", use_container_width=True):
            with st.spinner("AI Engine is compiling carbon profile and drafting steps..."):
                plan_text = ai_engine.generate_action_plan(
                    activities_df, 
                    goals_df[goals_df['status'] == 'Active'], 
                    st.session_state["api_key"]
                )
                st.session_state["recommendation_plan"] = plan_text
                
        if st.session_state["recommendation_plan"]:
            st.markdown(st.session_state["recommendation_plan"])
        else:
            st.info("Click the button above to analyze your historical logs and generate custom carbon-offset instructions.")
            
    with pdf_col:
        st.subheader("Export PDF Document")
        st.markdown("Compile your logged activities and the AI carbon mitigation plan into a downloadable PDF document to submit or share.")
        
        if st.session_state["recommendation_plan"]:
            pdf_data = generate_pdf_report(
                activities_df,
                goals_df,
                st.session_state["recommendation_plan"]
            )
            
            st.download_button(
                label="📥 Download Carbon Report PDF",
                data=pdf_data,
                file_name="EchoStep_CarbonReport.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("Please generate the Recommendations Plan first to export the complete PDF report.")
