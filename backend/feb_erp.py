from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import json
import os

app = FastAPI()

def process_data():
    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_dir, "data", "feb_erp.csv")
    
    df = pd.read_csv(file_path, sep=",", encoding="utf-8")

    # Select and convert the needed columns
    selected_df = df[['COMPLAINT ID', 'CREATED DATE', 'SUBJECT', 'CLOSED DATE',
                      'RELATED TO', 'COMPLAINT BY', 'RESPONSIBLE', 'RESPONSIBLE DEPARTMENT',
                      'ORGANISATION', 'CREATED_BY', 'SOURCE', 'TICKET_TYPE',
                      'CREATED_BY_DEPARTMENT', 'STATUS', 'ACTIVE']]
    selected_df = selected_df.convert_dtypes()
    selected_df['CREATED DATE'] = pd.to_datetime(selected_df['CREATED DATE'], errors='coerce')
    selected_df['CLOSED DATE'] = pd.to_datetime(selected_df['CLOSED DATE'], errors='coerce')
    
    # Calculate Turn-Around Time (TAT)
    selected_df["TAT"] = (selected_df["CLOSED DATE"] - selected_df["CREATED DATE"]).dt.days

    output = []
    for org_name, group in selected_df.groupby("ORGANISATION"):
        # (a) Total complaints for this organization
        total_complaints = len(group)
        
        # (b) SOURCE counts (e.g., how many "Email", "WhatsApp", etc.)
        source_counts = group["SOURCE"].value_counts().to_dict()
        
        # (c) RELATED TO counts (e.g., "Device Hardware", "Delivery/Installation", etc.)
        related_counts = group["RELATED TO"].value_counts().to_dict()
        
        # (d) Average TAT across all complaints for this org
        avg_tat = group["TAT"].mean()
        avg_tat = int(round(avg_tat)) if not pd.isna(avg_tat) else 0
        
        org_data = {
            "organization": {
                "name": org_name,
                "complaints_created": total_complaints,
                "source": source_counts,
                "related_to": related_counts,
                "TAT": avg_tat
            }
        }
        output.append(org_data)
    
    return output

@app.get("/organization")
def get_complaints():
    data = process_data()
    return JSONResponse(content=data)
