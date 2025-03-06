import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("Complaints Dashboard")

search_query = st.text_input("Search Organization", "")

api_url = "http://127.0.0.1:8000/organization"

try:
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()


# Extract organizations safely
org_data_list = []
for item in data:
    if "organization" in item:
        org = item["organization"]
        # Ensure required keys exist, provide defaults
        org.setdefault("name", "N/A")
        org.setdefault("complaints_created", 0)
        org.setdefault("source", {})
        org.setdefault("related_to", {})
        org.setdefault("TAT", "N/A")
        org_data_list.append(org)
    else:
        st.warning("Item missing 'organization' key")

# Debug: Show processed data
st.write("Organizations")

# NEW: Filter organizations by search query (case-insensitive)  
if search_query:
    org_data_list = [
        org for org in org_data_list
        if search_query.lower() in org.get("name", "").lower()
    ]

columns_per_row = 2
for i in range(0, len(org_data_list), columns_per_row):
    cols = st.columns(columns_per_row)
    for j, org in enumerate(org_data_list[i:i+columns_per_row]):
        with cols[j]:
            # Build HTML with explicit text styling
            html_content = f"""
            <div style="
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
                background-color: #f9f9f9;
                color: black;
                font-family: Arial, sans-serif;
                box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);">
                <h3 style="margin-top: 0; color: #333;">{org['name']}</h3>
                <p><strong>Complaints Created:</strong> {org['complaints_created']}</p>
                <p><strong>Source:</strong><br>
            """
            # Add source data or placeholder
            if org["source"]:
                for src, count in org["source"].items():
                    html_content += f"{src}: {count}<br>"
            else:
                html_content += "No sources found.<br>"
            
            html_content += "</p><p><strong>Related To:</strong><br>"
            
            # Add related_to data or placeholder
            if org["related_to"]:
                for rel, count in org["related_to"].items():
                    html_content += f"{rel}: {count}<br>"
            else:
                html_content += "No related items.<br>"
            
            html_content += f"</p><p><strong>TAT:</strong> {org['TAT']} days</p></div>"
            
            st.markdown(html_content, unsafe_allow_html=True)