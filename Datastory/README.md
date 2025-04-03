**Wolf Attacks in the Netherlands – Animated Geospatial Visualization**

Code: FINAL_CODE.py

This Streamlit application visualizes wolf attacks in the Netherlands over the past 10 years. It displays data on wolf sightings and total livestock casualties per city using an animated interactive map built with Plotly.

**Getting Started**
This project is designed to be run locally. Follow the steps below to prepare your environment.

**Prerequisites**
- Python 3.10+
- Required libraries:
  - pandas
  - plotly
  - streamlit
  - geopy (for older dataset wrangling)
  - time
  - json

Install required packages using pip:
pip install pandas plotly streamlit geopy

**Installation**
1. Clone the repository:
git clone https://github.com/MerrieQ/Portfolio/tree/main/Datastory
cd Datastory

2. Ensure the following CSV files are placed in your working directory:
- Wolfschade_geocoded.csv
- Wolfschade_grouped.csv
- Wolfschade_cumulative.csv

3. Run the app:
streamlit run FINAL_CODE.py

**Usage**
The app consists of:
- An animated map showing the cumulative number of livestock killed per month per location.
- A slider that animates monthly data updates.
- Optional checkbox to display raw data.
- Province borders overlay via GeoJSON.
- Consistent color axis to avoid flickering between frames.

**OLD CODE**
The file "OLD CODE" documents the original dataset wrangling and geocoding process, before converting data into static CSV files for performance. These preprocessing steps were split into a separate workflow to reduce runtime on every launch.

**Original datasets included:**
- Original dataset:"Verified Wolf Sightings" ("Wolfwaarnemingen.csv")
- Original dataset:"Verified Wolf Damages" ("Wolfschade.csv")

These were geocoded, grouped by month and location, and cleaned into:
- Wolfschade_geocoded.csv
- Wolfschade_grouped.csv
- Wolfschade_cumulative.csv

This preprocessing allowed the new visualization app to focus only on mapping and animation.

**License**
This project has no license. You are free to use, copy, and modify it as you wish.

**Contact**
Created by Merlijn Marquering  
GitHub: https://github.com/MerrieQ
Email: merlijn.marquering@gmail.com
Original data transformation and mapping by Merlijn for personal academic portfolio and visualization skill development.
