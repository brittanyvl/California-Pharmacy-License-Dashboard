import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import itertools
from collections import Counter
import re
import seaborn as sns
import matplotlib.pyplot as plt


# Set the page configuration with the sidebar expanded
st.set_page_config(
    page_title="Sterile Sourcing: California Compounding Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Datasets
pharmacies = pd.read_csv('enriched_pharmacy_data_01032024.csv', dtype=str, encoding='utf-8')
pharmacies['Expiration Date'] = pd.to_datetime(pharmacies['Expiration Date'])

# Count Data
facility_counts = pharmacies['Facility Type'].value_counts().reset_index()
facility_counts.columns = ['Facility Type', 'Count']
license_counts = pharmacies['License Type'].value_counts().reset_index()
license_counts.columns = ['License Type', 'Count']
city_counts = pharmacies['City'].value_counts().reset_index()
city_counts.columns = ['City', 'Count']
state_counts = pharmacies['State'].value_counts().reset_index()
state_counts.columns = ['State', 'Count']
county_counts = pharmacies['County'].value_counts().reset_index()
county_counts.columns = ['County', 'Count']
zip_counts = pharmacies['Zip'].value_counts().reset_index()
zip_counts.columns = ['Zip', 'Count']
government_count = pharmacies['isGovernment'].value_counts().reset_index()
government_count.columns = ['isGovernment', 'Count']
outsourcer_count = pharmacies['Registered Outsourcer'].value_counts().reset_index()
outsourcer_count.columns = ['is503B', 'Count']
unique_facility_types = pharmacies['Facility Type'].dropna().unique()
facility_options = list(unique_facility_types)
unique_cities = pharmacies['City'].dropna().unique()
city_options = sorted(list(unique_cities))

# Specialty Search
pharmacies['Specialties'] = pharmacies['Specialties'].str.replace(
    "Ear, Nose, and Throat",
    "Ear Nose and Throat",
    regex=False
)
specialities = pharmacies.dropna(subset=['Specialties'])
# Define a function to clean the terms by removing unwanted punctuation
def clean_term(term):
    # Remove extra spaces, just in case
    term = term.strip()
    return term
# 1. Flatten all lists from the 'Specialties' column by splitting on commas
all_terms = list(itertools.chain(*specialities['Specialties'].apply(lambda x: x.split(','))))
# Apply the cleaning function to each term
cleaned_terms = [clean_term(term) for term in all_terms]
# 2. Generate unique terms
unique_specialty_terms = sorted(set(cleaned_terms))



# Condition Search
conditions = pharmacies.dropna(subset=['Conditions'])
all_conditions = list(itertools.chain(*conditions['Conditions'].apply(lambda x: x.split(','))))
cleaned_conditions = [clean_term(condition) for condition in all_conditions]
unique_condition_terms = sorted(set(cleaned_conditions))

#Accredidation Search
accreditations = pharmacies.dropna(subset=['Accreditations'])
all_accreditations = list(itertools.chain(*accreditations['Accreditations'].apply(lambda x: x.split(','))))
cleaned_accreditations = [clean_term(accreditation) for accreditation in all_accreditations]
unique_accreditations = sorted(set(cleaned_accreditations))
# Replace the specific value
unique_accreditations = [
    "AAHP" if acc == "American Association of Homeopathic Pharmacists" else acc
    for acc in unique_accreditations
]


# Sidebar for user input
st.sidebar.title("Sterile Search")
st.sidebar.write("Search my database of California licensed sterile compounders by location, specialty, condition, and more!")
st.sidebar.warning(
    "This is a student project meant to validate interest in a 50 state Sterile Compounding Directory. "
    "Sign up for my waitlist [here!](https://docs.google.com/forms/d/e/1FAIpQLSfvlpsCtIYb-CVyz9cSaV1IGzoJrksr20bid8TFOyySPNF9pg/viewform?usp=header)"
)
pharmacy_type = st.sidebar.segmented_control("**Pharmacy Type**", ['Patient Specific (503A)', 'Bulk In-Office (503B)'], selection_mode="multi", default=['Patient Specific (503A)', 'Bulk In-Office (503B)'])
facility_type = st.sidebar.multiselect("**Facility Type**", facility_options, default='Sterile Compounding Pharmacy')
city = st.sidebar.multiselect("**City**", city_options)
specialty = st.sidebar.multiselect("**Specialty**", unique_specialty_terms)
condition = st.sidebar.multiselect("**Condition**", unique_condition_terms)
accreditations = st.sidebar.pills("**Claimed Accreditations**", unique_accreditations, selection_mode='multi', default=None)

# Main content area with tabs
st.title("Safer Sourcing: A Study of California Sterile Compounding Licenses")
st.write("""
**California, home to 39 million residents, currently has only 70 licensed pharmacies authorized to provide sterile compounded drugs.**""")
st.write("""
This limited availability has raised concerns in the pharmaceutical supply chain, forcing some patients to seek medications illegally or go without. Unfortunately, healthcare providers are also affected. Some have been found purchasing unapproved chemicals, issuing false prescriptions, or rationing expired supplies. These practices increase the risk of harm to patients and undermine the integrity of the healthcare system.""")
tabs = st.tabs(["**Search Pharmacies**", "**License Analysis**", "**About**"])

# Home Tab
with tabs[0]:
    # Check if pharmacy type is selected
    if not pharmacy_type:
        st.error("Please select at least one pharmacy type.")  # Display error box if no pharmacy type is selected
    else:
        # Apply filters based on user selection
        filtered_df = pharmacies.copy()
        cols_to_drop = [
            'License Status',
            'LAT',
            'LONG',
            'isGovernment',
            'isSatellite'
        ]
        filtered_df.drop(columns=cols_to_drop, inplace=True)

        # Filter by Pharmacy Type (Handle all 4 possible scenarios)
        if 'Patient Specific (503A)' in pharmacy_type and 'Bulk In-Office (503B)' not in pharmacy_type:
            # Only 503A selected, filter by Registered Outsourcer = True
            filtered_df = filtered_df[filtered_df['Registered Outsourcer'] == "False"]
        elif 'Bulk In-Office (503B)' in pharmacy_type and 'Patient Specific (503A)' not in pharmacy_type:
            # Only 503B selected, filter by Registered Outsourcer = False
            filtered_df = filtered_df[filtered_df['Registered Outsourcer'] == "True"]
        elif 'Patient Specific (503A)' in pharmacy_type and 'Bulk In-Office (503B)' in pharmacy_type:
            # Both 503A and 503B selected, no filtering on Registered Outsourcer
            filtered_df = filtered_df

        # Filter by Facility Type
        if facility_type:
            filtered_df = filtered_df[filtered_df['Facility Type'].isin(facility_type)]

        # Filter by City
        if city:
            filtered_df = filtered_df[filtered_df['City'].isin(city)]

        # Filter by Specialty
        if specialty:
            filtered_df['Specialties'] = filtered_df['Specialties'].astype(str)
            specialty_set = set(specialty)
            filtered_df = filtered_df[
                (pd.notna(filtered_df['Specialties'])) &
                (filtered_df['Specialties'].apply(lambda x: all(term in x for term in specialty_set)))
            ]

        # Filter by Condition
        if condition:
            filtered_df['Conditions'] = filtered_df['Conditions'].astype(str)
            condition_set = set(condition)
            filtered_df = filtered_df[
                (pd.notna(filtered_df['Conditions'])) &
                (filtered_df['Conditions'].apply(lambda x: all(term in x for term in condition_set)))
            ]

        # Filter by Accreditations
        if accreditations:
            filtered_df['Accreditations'] = filtered_df['Accreditations'].astype(str)
            acc_set = set(accreditations)
            filtered_df = filtered_df[
                (pd.notna(filtered_df['Accreditations'])) &
                (filtered_df['Accreditations'].apply(lambda x: all(term in x for term in acc_set)))
            ]

        # Check if the filtered dataframe is empty and show an error if it is
        if filtered_df.empty:
            st.error("No pharmacies match your criteria; try your search again with fewer restrictions.")
        else:
            # Display the filtered dataframe (Read-Only view)
            st.subheader("Matching Pharmacies:")
            st.info("Use the sidebar to set your search criteria. Hover over the results table and a download icon will appear to save the table as a CSV locally.")
            st.dataframe(filtered_df, use_container_width=True)


# Profile Tab
with tabs[1]:
    # Table of Contents
    st.markdown("""
    ### Table of Contents
    - [What is sterile compounding?](#what-is-sterile-compounding)
    - [What Types of Sterile Licenses does California Grant?](#what-types-of-sterile-licenses-does-california-grant)
    - [What types of facilities are granted Sterile Compounding Licenses?](#what-types-of-facilities-are-granted-sterile-compounding-licenses)
    - [Exploring Purchasing Styles: Bulk vs Patient Specific](#exploring-purchasing-styles-bulk-vs-patient-specific)
    - [Which states do the pharmacies reside in?](#which-states-do-the-pharmacies-reside-in)
    - [Where are facilities located within California?](#where-are-facilities-located-within-california)
    - [When are the licenses anticipated to expire?](#when-are-the-licenses-anticipated-to-expire)
    """, unsafe_allow_html=True)
    st.subheader("What is sterile compounding?")
    st.write("Compounding pharmacies fill a critical role in our drug supply chain by producing medication when it is in shortage, the patient requires a customized dose or delivery, or the drug is not commercially available. When that drug is intended for sterile applications, such as injection, infusion, or eye drops, it is critical that the pharmacy is properly equipped AND licensed in sterile compounding.")
    st.write("All pharmacies that can legally distribute a sterile compounded drug into the state of California MUST obtain a Sterile Compounding License.  This paper will examine the current sterile licenses in a clear and active status as of 01/03/2025.")
    st.subheader("What Types of Sterile Licenses does California Grant?")
    st.write("""
    There are five types of sterile pharmacy licenses granted:
    - **Sterile Compounding Pharmacy**: Granted to 503A pharmacies physically located within California, not government-owned, and not a satellite location.
    - **Government-Owned Facility**: Specifically designated for facilities owned by the government.
    - **Satellite Locations**: Separate licenses are granted for satellite locations.
    - **Fee-Exempt Satellite Locations**: A special designation for fee-exempt satellite locations.
    - **Nonresident Sterile Compounding Pharmacy**: Issued to pharmacies physically located outside of California that are not government or satellite institutions.
    """)
    fig_donut_license_type = px.pie(
        license_counts,
        names='License Type',
        values='Count',
        title='Distribution of License Types',
        hole=0.25,
        labels={'License Type': 'Type of License', 'Count': 'Number of Licenses'},
        template='simple_white'
    )
    st.plotly_chart(fig_donut_license_type, use_container_width=True)
    st.subheader("What types of facilities are granted Sterile Compounding Licenses?")
    st.write("""
    The California Board of Pharmacy Database does not provide context for the types of facilities granted. This data was categorized through independent research utilizing the pharmacy name, address, and public information online. 
    - **Medical Facility**: Hospitals, Medical Centers, Surgical Floors, and many other healthcare facilities that you would not think of as a compounding pharmacy hold sterile compounding licenses. In fact, nearly 80% of active licenses are currently being held by medical facilities.
    - **Infusion Center**: Dialysis and infusion clinics, as well as some home health services, hold sterile compounding licenses so that they can properly and legally prepare infusions for their clients. They represent just over 11% of the active licenses.  
    - **Sterile Compounding Pharmacy**:  This is the more traditional pharmacy you would think of; it includes both retail and closed door pharmacies whose primary function is to produce compounded drugs. They represent roughly 8% of the active licenses. 
    - **Veterinary Only**: These are compound pharmacies that, upon review of their public information, only prepare veterinary compounds and would not be available to provide services for human patients. 
    - **Research Center**: There was (1) government owned research center located in San Diego, CA, that has an active Sterile Compounding License in California.  
    """)
    st.warning("**Note**: There were only (68) Licensed Sterile Compounding Pharmacies that service human patients for the entire population of 39 million Californians.")
    facility_counts = facility_counts.sort_values(by='Count', ascending=False)
    bar_fig = px.bar(
        facility_counts,
        x='Count',
        y='Facility Type',
        orientation='h',
        category_orders={'Facility Type': facility_counts['Facility Type'].tolist()},
        title='What Types of Facilities Hold Sterile Compounding Licenses in California?',
        labels={'Facility Type': 'Type of Facility', 'Count': 'Number of Facilities'},
        template='seaborn'
    )
    st.plotly_chart(bar_fig, use_container_width=True)
    st.subheader("Exploring Purchasing Styles: Bulk vs Patient Specific")
    st.write("""
    The Food, Drug, and Cosmetic Act defines two types of product distribution for compound pharmacies. Understanding them is critical if you are sourcing compound drugs.

    - **503B Bulk** pharmacies are FDA-registered outsourcers. They can distribute compounded drug products in bulk directly to medical providers for in-office use. This is more cost-efficient for providers who administer drugs on-site. These pharmacies require FDA inspection and licensing but are not FDA-approved for the drugs they produce.

    - **503A Patient-Specific** pharmacies are state-licensed and regulated. They create medications for individual patients, which can then be dispensed to the patient or their provider. While these pharmacies don’t require FDA registration, they ensure the medication is tailored to the specific patient's needs. However, 503A pharmacies generally meet a lower quality standard than 503B pharmacies.
    """)
    st.warning("""
    Only (5) 503B pharmacies in California have a sterile license and serve human patients. This severely limits options for in-office compounded drugs, increasing costs for both providers and patients and restricting access to a significant portion of the U.S. compound drug supply chain.
    """)
    pie_fig = px.pie(outsourcer_count,
                     names='is503B',
                     values='Count',
                     title="Is the licensed facility a registered 503B Outsourcer with the FDA?",
                     labels={'is503B': 'Pharmacy Type', 'Count': 'Count'})
    st.plotly_chart(pie_fig, use_container_width=True)
    st.subheader("Which states do the pharmacies reside in?")
    st.write("California's Board of Pharmacy has a known preference for resident pharmacies; however, facilities outside of California have successfully won a sterile license.")
    st.warning("**Note**: The California BOP may grant an outside pharmacy a license but that does not guarantee they will allow their entire sterile catalog into the state; California BOP is known for strict enforcement of sterile compounds at the individual drug product level.")
    # Apply a log transformation to the 'Count' column to compress large differences
    state_counts['Log_Count'] = np.log1p(state_counts['Count'])  # Use log1p to avoid issues with log(0)

    # Create the geographic heat map
    fig_geo_heatmap = px.choropleth(
        state_counts,
        locations='State',  # The column with state names or abbreviations
        locationmode='USA-states',  # Specify US states as the location mode
        color='Log_Count',  # Use the log-transformed values for color
        color_continuous_scale='Blues',  # Choose a color scale
        scope='usa',  # Limit the map to the USA
        title='Sterile Compounding Licenses: US Heatmap',
        labels={'Log_Count': 'Log of Count', 'State': 'State'},
        hover_name='State',  # Show state name when hovering
        hover_data={'Log_Count': False, 'Count': True}  # Only show 'Count' on hover, not the log count
    )
    # Update layout for better appearance
    fig_geo_heatmap.update_layout(
        title={
            'font': {'size': 16, 'family': 'Arial', 'color': 'darkblue'},
            'x': 0.5,  # Center the title
        },
        geo=dict(
            showframe=False,  # Hide the frame around the map
            showcoastlines=True,  # Show coastlines
            coastlinecolor="LightGray",  # Set the coastline color
        )
    )
    st.plotly_chart(fig_geo_heatmap, use_container_width=True)
    # Create the geographic scatter plot using LAT and LONG
    st.subheader("Where are facilities located within California?")
    st.write("""
    For some of the 39 million people in California having a sterile compound shipped to them is not enough - they need in person services.  Explore the map below to see where the different types of licensed facilities exist.
    """)
    fig_geo_pharmacies = px.scatter_geo(
        pharmacies,
        lat='LAT',  # Latitude column
        lon='LONG',  # Longitude column
        color='Facility Type',  # Color by Facility Type (you can replace this with any other column)
        hover_name='Pharmacy Name',  # Show pharmacy name on hover
        hover_data={'LAT': False, 'LONG': False},  # Do not show lat and long on hover
        title='Pharmacy Locations in California'
    )

    # Update layout for better appearance with focus on California
    fig_geo_pharmacies.update_layout(
        title={
            'font': {'size': 16, 'family': 'Arial', 'color': 'darkblue'},
            'x': 0.5,  # Center the title
        },
        geo=dict(
            showframe=False,  # Hide the frame around the map
            showcoastlines=True,  # Show coastlines
            coastlinecolor="LightGray",  # Set the coastline color
            projection_type="albers usa",  # Projection type for the USA
            center={"lat": 37.5, "lon": -119},  # Center on California (lat, lon for central California)
            projection_scale=2,  # Zoom level for California (adjust for better focus)
        ),
        coloraxis_colorbar=dict(
            title="Facility Type",  # Color bar title (if using categorical data)
        )
    )
    # Display the scatter plot
    st.plotly_chart(fig_geo_pharmacies, use_container_width=True)
    st.subheader("When are the licenses anticipated to expire?")
    st.write("""
    The California BOP issues Sterile Compounding Licenses for 12 months at a time; after that, they must be renewed.  Use the selection box below to determine what types of facilities you are interested in and review how many are expiring, and when. November of 2025 is expected to be a large month of turnover at the California BOP.
    """)
    # Multi-select for facility types directly above the area chart
    facility_types = sorted(pharmacies['Facility Type'].dropna().unique())
    selected_facility_types = st.multiselect(
        "Select Facility Types to Include in Expiration Analysis:",
        options=facility_types,
        default=facility_types
    )

    # Filter data based on selected facility types
    filtered_pharmacies = pharmacies[
        (pharmacies['Facility Type'].isin(selected_facility_types)) &
        (pharmacies['Expiration Date'].notna())
        ]

    # Process expiration data for the area chart
    filtered_pharmacies['Year'] = filtered_pharmacies['Expiration Date'].dt.year
    filtered_pharmacies['Month'] = filtered_pharmacies['Expiration Date'].dt.month
    filtered_pharmacies = filtered_pharmacies[filtered_pharmacies['Year'] != 2024]

    # Group by Facility Type, Year, and Month and count the number of expirations
    expirations_by_type_year_month = (
        filtered_pharmacies
        .groupby(['Facility Type', 'Year', 'Month'])
        .size()
        .reset_index(name='Count')
    )

    # Create a "Date" column for plotting
    expirations_by_type_year_month['Date'] = pd.to_datetime(
        expirations_by_type_year_month[['Year', 'Month']].assign(DAY=1)
    )

    # Create the stacked area chart
    area_fig = px.area(
        expirations_by_type_year_month,
        x='Date',
        y='Count',
        color='Facility Type',
        title="Pharmacy Expirations Over Time (Stacked by Facility Type)",
        labels={'Count': 'Number of Expirations', 'Date': 'Date', 'Facility Type': 'Type of Facility'},
        template='plotly_white'
    )

    # Display the area chart
    st.plotly_chart(area_fig, use_container_width=True)
    # Display the interactive, read-only dataframe
    st.write("""
    Below is the data of the pharmacies whose licenses are anticipated to expire, based on your selected facility types.
    """)
    display_filtered_df = filtered_pharmacies.copy()
    cols_to_drop = ['License Type', 'License Status', 'Zip', 'LAT', 'LONG', 'isGovernment', 'isSatellite', 'Specialties', 'Conditions', 'Registered Outsourcer', 'Accreditations', 'Year', 'Month']
    display_filtered_df.drop(columns=cols_to_drop, inplace=True)
    st.dataframe(display_filtered_df)


# Settings Tab
with tabs[2]:
    st.header("About The Data")
    st.write("""
    All pharmacy license data is public knowledge and available through the California State Board of Pharmacy License Verification website located at https://www.pharmacy.ca.gov/. The initial licensure data was collected from this portal on 01/03/2025.
    """)
    st.write("""
    In order to better categorize and search the available licenses the dataset was enriched by researching the individual pharmacies' online prescence.  Using their websites, social media, and other public information we are able to identify what type of services the pharmacy specialises in.
    """)
    st.divider()
    st.header("About the Problem & Project")
    st.write("""
    In the United States, the limited availability of licensed sterile compounding pharmacies poses a significant challenge to patients and healthcare providers. In California, for example, the state’s 39 million residents have access to only 70 licensed pharmacies authorized to provide sterile compounded drugs. This scarcity has led some patients to seek medications from unsafe or illegal sources, including black market drugs, research chemicals not intended for human use, or unlicensed drugs transported across state lines from regions with less stringent regulations.

    Such practices expose both patients and pharmacists to serious health risks and legal repercussions, further straining an already vulnerable healthcare system.
    """)
    st.write("""
    Currently, patients and providers must navigate a patchwork of over 50 state-specific databases to locate licensed pharmacies, with each state’s Board of Pharmacy maintaining its own set of regulations and search protocols. This creates significant friction, requiring users to sift through hundreds or thousands of listings, many of which may be irrelevant to their specific needs or location.
    """)
    st.subheader("Creating a National Directory of Sterile Compounding Pharmacies")
    st.write("""
    My vision is to develop a comprehensive, nationwide directory of licensed sterile compounding pharmacies. By consolidating data from all 50 states into a single platform, we could simplify the search process for patients and healthcare providers, making it easier to find pharmacies that meet their specific needs.

    This application serves as a prototype, focusing on California as a starting point. With additional validation, safeguards, and educational resources, this platform could evolve into a trusted tool, empowering patients and healthcare providers to source sterile compounded drugs safely and efficiently, while reducing the risk of harm.
    """)
    st.write("""
    The broader goal is to expand this concept to a nationwide scale, enabling easier access to licensed pharmacies and ultimately improving patient outcomes by ensuring safer, legal access to critical medications.
    """)
    st.divider()
    st.header("About the Author")
    st.markdown("""
    👋 Hi, I'm Brittany Campos — a seasoned analyst and operations leader with a passion for bridging the gap between business and technology. With over four years of experience in supply chain optimization, particularly in sourcing sterile and compounded drugs, I’ve developed a unique skill set that merges operational expertise with technical proficiency.

    Currently, I am a Software Engineering student, expected to graduate in March 2025, where I'm honing my skills in Python, SQL, and data engineering. My experience spans implementing enterprise systems like Salesforce B2B Commerce and Oracle NetSuite, as well as developing custom solutions that streamline processes, improve compliance, and deliver impactful data products. 

    This project is a example of my passion for pharmacy, compliance, and data—bringing those interests together to solve complex business challenges. I hope you find it useful, and if you have any questions or would like to connect, please don't hesitate to reach out to me on [LinkedIn](https://www.linkedin.com/in/brittanycampos/).

    Looking forward to hearing from you!
    """)
    st.info("""
    ***Interested In This Data for Another State? Sign up for my [waitlist!](https://docs.google.com/forms/d/e/1FAIpQLSfvlpsCtIYb-CVyz9cSaV1IGzoJrksr20bid8TFOyySPNF9pg/viewform?usp=header)""")