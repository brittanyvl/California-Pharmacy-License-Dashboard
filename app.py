import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk


#Load Data
all_pharmacies = pd.read_csv('all_pharmacies.csv', dtype=str)
available_pharmacies = pd.read_csv('available_pharmacies.csv', dtype=str)

#Set page config to wide
st.set_page_config(layout="wide")

st.title('Exploring Sterile Compounding Licenses in California')
st.header('Introduction')
st.markdown("""
**Sterile compounding** is the preparation of custom medications in a sterile environment, essential for treatments like IV infusions, chemotherapy, and nutritional therapy.

While California has granted over **800 active sterile compounding licenses**, many assume this means a large number of pharmacies are providing sterile compounded medications. In reality, most of these licenses are held by hospitals, medical centers, government research facilities, and infusion services, with **less than 20% held by pharmacies that prepare these medications for dispensation to patients or providers.**

This limited number of pharmacies highlights the challenges in accessing these essential medications. Understanding this distinction is crucial to recognizing the vital role these specialized pharmacies play in addressing drug shortages and providing life-saving, customized treatments.

When licensed pharmacies are not available, patients face difficult choices: **forgo their medications**, source them from **unlicensed research facilities** and **online markets**, or travel to other states with better access.
""", unsafe_allow_html=True)

st.subheader("About This Data")
st.write("All pharmacy license data was retrieved from the California Board of Pharmacy Sterile Compounding License Lookup Database on December 8th, 2024. Each record was then analyzed to identify the type of entity that was granted the license. If the facility was found to not be government, an infusion center, or a hospital/medical center, then their website and online presence was reviewed to identify their specialties and services.")

st.header("Who is issued sterile compounding licenses in California?")
st.subheader("License Types")
st.markdown("""
All active, clear licenses were one of (5) types issued by the California Board of Pharmacy: 
- **Government Owned**:  Government owned facilities, such as some hospitals or research centers, are identified by their own sterile compounding license type. 
- **Satellite** & **Satellite (Fee Exempt)**: A satellite pharmacy is typically within a care-giving institution, such as an operating room or critical care unit, and is outside of a primary pharmacy facility.
- **Nonresident Pharmacy**: These are pharmacies that are physically located outside of the state of California, but are licensed to ship products to Californian patients and/or providers.  
- **Compounding Pharmacy**: The generic sterile compounding license denotes a primary pharmacy facility that is physically located within the borders of California, is not a government facility, and is not a satellite location.  
""", unsafe_allow_html=True)

# Aggregate the counts of each 'License Type'
license_type_counts = all_pharmacies['License Type'].value_counts().reset_index()
license_type_counts.columns = ['License Type', 'Count']

# Create the donut chart for License Type
fig_licenses = px.pie(
    license_type_counts,
    names='License Type',
    values='Count',
    title="Distribution of License Types",
    hole=0.4,  # This makes it a donut chart
    color='License Type',  # Automatically color based on 'License Type'
    color_discrete_sequence=px.colors.sequential.Blues[::-1]  # Reverse the blue color scale (dark to light)
)

# Update the legend labels for each trace to be more descriptive
fig_licenses.for_each_trace(lambda trace: trace.update(
    name="License Type A" if trace.name == "Type A" else
    "License Type B" if trace.name == "Type B" else
    "License Type C" if trace.name == "Type C" else
    trace.name  # Keep original name if it doesn't match any condition
))

# Customize the layout for title and legend
fig_licenses.update_layout(
    title={
        'text': "Distribution of License Types",
        'y': 0.95,  # Position the title just below the top of the chart
        'x': 0.5,  # Horizontally center the title
        'xanchor': 'center',
        'yanchor': 'top'  # Align title's top edge with y position
    },
    legend=dict(
        title="License Type",  # Add a legend title
        orientation="v",  # Horizontal legend layout
        yanchor="bottom",
        y=0.5,  # Place legend below the chart
        xanchor="right",
        x=.25
    )
)

# Show the plot in Streamlit
st.plotly_chart(fig_licenses)

st.subheader("Facility Types")
st.markdown("""
There are (5) primary types of facilities that are granted sterile compounding licenses: 
- **Hospital or Medical Center**:  Pharmacies preparing sterile drugs in hospitals, medical centers, and other provider settings. These are not available for use by the general public and concentrate on treating patients admitted to their facility. **Nearly 80% of licenses are for this type of facility.**
- **Infusion Service**: These are businesses that provide intravenous therapies for chronically ill patients and those with complex treatment needs. They are not manufacturing drugs, but may be compounding drugs to administer to their patients at infusion centers or in-home. 
- **Research Facility**: These facilities produce sterile drugs for research purposes; there is presently (1) government owned research facility with a sterile compounding license in California.  
- **Veterinary Only**:  These are pharmacies that specialize only in animal health and produce veterinary products; they do not presently produce sterile drugs for human administration.  
- **Compounding Pharmacy**: These are pharmacies that provide sterile compounding as a service to patients or providers; they are not located within a hospital or medical center, are not a research facility, and do not provide infusion/administrative services.  They are dedicated in whole or part to compounding sterile drugs. **Less than 13% of licenses are for this type of facility.**
""", unsafe_allow_html=True)

# Aggregate the counts of each 'Entity Type'
entity_type_counts = all_pharmacies['Entity Type'].value_counts().reset_index()
entity_type_counts.columns = ['Entity Type', 'Count']

# Create the horizontal bar chart for Entity Type
fig_entity = px.bar(
    entity_type_counts,
    x='Count',  # Count of each Entity Type will be on the x-axis
    y='Entity Type',  # The different Entity Types will be on the y-axis
    title="Distribution of Entity Types",
    color='Entity Type',  # Automatically color based on 'Entity Type'
    color_discrete_sequence=px.colors.sequential.Blues[::-1],  # Reverse the blue color scale (dark to light)
    text='Count'  # Show the count labels on the bars
)

# Customize the layout for title and labels
fig_entity.update_layout(
    title={
        'text': "Distribution of Entity Types",
        'y': 0.95,  # Position the title just below the top of the chart
        'x': 0.5,  # Horizontally center the title
        'xanchor': 'center',
        'yanchor': 'top'  # Align title's top edge with y position
    },
    xaxis_title="Count",  # Label for the x-axis
    yaxis_title="Entity Type",  # Label for the y-axis
    showlegend=False  # Hide the legend since the color is already shown on the bars
)

# Display the plot in Streamlit
st.plotly_chart(fig_entity)






# Prepare data for the map
map_filter = all_pharmacies.dropna(subset=['LAT', 'LNG'])
map_filter = map_filter.rename(columns={'LNG': 'LON'})
map_filter['LAT'] = map_filter['LAT'].astype(float)
map_filter['LON'] = map_filter['LON'].astype(float)
# Create the scatter mapbox plot with the correct color scale for categorical data
fig_map = px.scatter_mapbox(
    map_filter,
    lat='LAT',
    lon='LON',
    color='Entity Type',  # Use Entity Type for coloring
    title="Pharmacies with Sterile Compounding Licenses",
    labels={'Entity Type': 'Facility Type'},  # Customize the legend label
    hover_data=['Entity Type', 'License Type', 'Pharmacy Name'],  # Show Entity Type, License Type, and Pharmacy Name on hover
    color_discrete_sequence=px.colors.sequential.Blues[::-1],  # Dark to Light Blue color scale for categories
)

# Update the layout
fig_map.update_traces(marker=dict(
    size=10,
    opacity=0.7,
))

# Map style and layout settings
fig_map.update_layout(
    mapbox_style="carto-positron",  # Use a clean, simple map style
    mapbox_zoom=3,  # Set zoom level to show the entire contiguous U.S.
    mapbox_center={"lat": 39.8283, "lon": -98.5795},  # Center the map on the contiguous U.S.
    showlegend=True  # Display the legend for Entity Type
)

# Display the map in Streamlit
st.plotly_chart(fig_map)