import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk


#Load Data
all_pharmacies = pd.read_csv('all_pharmacies.csv', dtype=str)
available_pharmacies = pd.read_csv('available_pharmacies.csv', dtype=str)

# Set page config to wide
st.set_page_config(layout="wide")

# Create a Sidebar Menu
menu = st.sidebar.radio("", ["Introduction", "License Analysis", "Pharmacy Search", "About"])

if menu == "Introduction":
    # Introduction Page
    st.title("Safely Sourcing Sterile Medications in California")
    st.write("An interactive analysis by Brittany Campos [https://www.linkedin.com/in/brittanycampos/]")
    st.header("The Challenge in California")
    st.markdown("""
    **Sterile compounding** is the preparation of custom medications in a sterile environment, essential for treatments like IV infusions, chemotherapy, and nutritional therapy.

    While California has granted over **800 active sterile compounding licenses**, many assume this means a large number of pharmacies are providing sterile compounded medications. In reality, most of these licenses are held by hospitals, medical centers, government research facilities, and infusion services, with **less than 13% held by pharmacies that prepare these personalized medications for dispensation to patients or providers.**

    This limited number of pharmacies highlights the challenges in accessing these essential medications in California. Understanding this distinction is crucial to recognizing the vital role these specialized pharmacies play in addressing drug shortages and providing life-saving, customized treatments.
    """, unsafe_allow_html=True)

    st.error(
        "**When licensed pharmacies are not available, patients face difficult choices: forgo their medications, source them from unlicensed research facilities and unregulated online markets, or travel to other states.**")

    st.markdown("""
    This app is meant to:
    - **Educate** the public on the the small number of licensed sterile compounding pharmacies available to service Californian patients.
    - **Empower** patients and providers with information to source from appropriately licensed specialty pharmacies.
    - **Validate** interest in a sourcing tool that connects patients and providers with licensed sterile compounding pharmacies.
    """)
elif menu == "Pharmacy Search":
    # Pharmacy Search Page (placeholder for now)
    st.title("Pharmacy Search")
    st.write("This page will allow users to search for pharmacies based on different criteria in the future.")

elif menu == "License Analysis":

    st.title('An Analysis of Sterile Compounding Licenses in California')
    st.write("An interactive analysis by Brittany Campos [https://www.linkedin.com/in/brittanycampos/]")

    st.header("Who is issued sterile compounding licenses in California?")
    st.subheader("Facility Types")
    st.markdown("""
    After reviewing the 845 active, clear sterile compounding licenses I found that they were issued to (5) types of facilities: 
    - **Hospital or Medical Center**:  Pharmacies preparing sterile drugs in hospitals, medical centers, and other provider settings. These are not available for use by the general public and concentrate on treating patients admitted to their facility. **Nearly 80% of licenses are for this type of facility.**
    - **Infusion Service**: These are businesses that provide intravenous therapies for chronically ill patients and those with complex treatment needs. They are not manufacturing drugs, but may be compounding drugs when preparing infusions to administer to their patients at private medical centers or in patients' homes. 
    - **Research Facility**: These facilities produce sterile drugs for research purposes; during our review we found a singular government facility listed as a research lab that had obtained a sterile compounding license.
    - **Veterinary Only**:  These are pharmacies that specialize only in animal health and produce veterinary products; they do not presently produce sterile drugs for human administration per their online presence.
    - **Compounding Pharmacy**: These are pharmacies that provide sterile compounding as a service to patients or providers; they are not located within a hospital or medical center, are not a research facility, and do not provide infusion/administrative services.  They are dedicated in whole or part to compounding sterile drugs. **Less than 13% of licenses are for this type of facility.** 
    """, unsafe_allow_html=True)

    st.info(
        "**Only 28% of licensed sterile compounding pharmacies solely focus on sterile compounding** per the Alliance for Pharmacy Compounding's 2023 - 2024 Snapshot in Pharmacy Compounding in America. The majority are primarily a traditional pharmacy with only a small portion of their business providing sterile compounding services.")

    # Aggregate the counts of each 'Entity Type'
    entity_type_counts = all_pharmacies['Entity Type'].value_counts().reset_index()
    entity_type_counts.columns = ['Entity Type', 'Count']

    # Create the horizontal bar chart for Entity Type
    fig_entity = px.bar(
        entity_type_counts,
        x='Count',  # Count of each Entity Type will be on the x-axis
        y='Entity Type',  # The different Entity Types will be on the y-axis
        title="Count of Sterile Licenses by Facility Type",
        color='Entity Type',  # Automatically color based on 'Entity Type'
        color_discrete_sequence=px.colors.sequential.Blues[::-1],  # Reverse the blue color scale (dark to light)
        text='Count'  # Show the count labels on the bars
    )

    # Customize the layout for title and labels
    fig_entity.update_layout(
        title={
            'text': "Count of Sterile Licenses by Facility Type",
            'y': 0.95,  # Position the title just below the top of the chart
            'x': 0.5,  # Horizontally center the title
            'xanchor': 'center',
            'yanchor': 'top'  # Align title's top edge with y position
        },
        xaxis_title="Count",  # Label for the x-axis
        yaxis_title="Facility Type",  # Label for the y-axis
        showlegend=False  # Hide the legend since the color is already shown on the bars
    )

    st.plotly_chart(fig_entity)

    st.header("What specialties do the compounding pharmacies serve?")
    st.write(
        "To identify what specialties are being served by sterile compounding pharmacies I visited each of the 105 pharmacy websites. They may provide services to other types of providers, but below are what they are publically advertising.")
    st.write(
        "While most pharmacies did not have a web presence, or provided no insight to what types of specialties they might serve, there were several that appeared frequently - such as Hormone Replacement Therapy, Oncology, Dermatology, Hospice, Nutrition, and Opthalmic medications.")
    # Exclude unwanted columns
    cols_to_drop = ['isGovernment', 'isHospital', 'isInfusionCenter', 'isSatellite', 'isVeterinaryOnly']
    specialties = available_pharmacies.drop(columns=cols_to_drop)

    # Select columns that start with 'is'
    is_columns = [col for col in specialties.columns if col.startswith('is')]

    # Rename the columns to remove 'is' and format them
    renamed_columns = {col: col[2:].replace(",", ", ") for col in is_columns}
    specialties = specialties.rename(columns=renamed_columns)

    # Count the number of `True` values for each renamed column
    # Count `True` values for each of the renamed columns
    specialty_counts = specialties[list(renamed_columns.values())].sum()

    # Create a DataFrame for plotting
    specialty_counts_df = pd.DataFrame({
        'Specialty': specialty_counts.index,  # Specialty names
        'Count': specialty_counts.values  # Count of `True` values (1 for True)
    }).sort_values(by='Count', ascending=False)  # Sort by count for better visualization


    # Define a function to count the number of 'True' values in a string
    def count_true_values(count_string):
        # Count how many times 'True' appears in the string
        return count_string.count('True')


    # Apply the function to the "Count" column to update it with the actual count of 'True' values
    specialty_counts_df['Count'] = specialty_counts_df['Count'].apply(count_true_values)

    # Sort the DataFrame by the 'Count' column in descending order
    specialty_counts_df_sorted = specialty_counts_df[['Specialty', 'Count']].sort_values(by='Count', ascending=True)

    # Create the horizontal bar chart
    fig_specialty = px.bar(
        specialty_counts_df_sorted,
        x='Count',  # Values are on the x-axis
        y='Specialty',  # Categories are on the y-axis
        orientation='h',  # Horizontal bar chart
        title='Count of Pharmacies by Specialty',
        labels={'Specialty': 'Pharmacy Specialty', 'Count': 'Number of Pharmacies'},
        color='Count',  # Color the bars based on the 'Count'
        color_continuous_scale='Blues'  # Choose a color scale for bars
    )

    # Customize the chart layout for better readability
    fig_specialty.update_layout(
        xaxis_title="Number of Pharmacies",  # Label for the x-axis
        yaxis_title="Specialty",  # Label for the y-axis
        xaxis_tickformat='d',  # Format the x-axis as integers
        height=600,  # Set a specific height for the chart
        margin={"r": 0, "t": 50, "l": 50, "b": 50},  # Add some margin for readability
        autosize=True  # Allow the chart to automatically adjust size
    )

    st.plotly_chart(fig_specialty)

    st.header("What conditions do Sterile Compounding Pharmacies treat?")
    st.write(
        "To identify what types of conditions the licensed and available sterile compounding pharmacies are able to treat we visited each of their 105 websites.  This list is not exhaustive, and includes only what the pharmacies have made publicly available on their respective websites.")
    st.info(
        "Note that out of 845 licenses, only (5) or fewer pharmacies were identified as specializing in treatments for these conditions, or any other condition.")
    # Create a copy of the original available_pharmacies DataFrame
    conditions = available_pharmacies.copy()

    # Select columns that start with 'services'
    services_columns = [col for col in conditions.columns if col.startswith('services')]

    # Rename the columns to remove 'services' prefix and clean up the names
    renamed_columns = {col: col[8:].replace(",", ", ") for col in services_columns}
    conditions.rename(columns=renamed_columns, inplace=True)

    # Count the number of True values in each renamed 'services' column
    services_counts = conditions[list(renamed_columns.values())].sum()

    # Create a DataFrame for easier plotting
    services_counts_df = pd.DataFrame({
        'Condition': services_counts.index,  # Condition names
        'Count': services_counts.values  # Count of True values (1 for True)
    }).sort_values(by='Count', ascending=False)  # Sort by count for better visualization


    # Define a function to count the number of 'True' values in the string
    def count_true_values(count_string):
        # Count how many times 'True' appears in the string
        return count_string.count('True')


    # Apply the function to the "Count" column to update it with the actual count of 'True' values
    services_counts_df['Count'] = services_counts_df['Count'].apply(count_true_values)

    # Sort the DataFrame by the 'Count' column in descending order
    services_counts_df_sorted = services_counts_df[['Condition', 'Count']].sort_values(by='Count', ascending=True)

    # Create the horizontal bar chart using Plotly
    fig_conditions = px.bar(
        services_counts_df_sorted,
        x='Count',  # Values are on the x-axis
        y='Condition',  # Categories are on the y-axis
        orientation='h',  # Horizontal bar chart
        title='Count of Pharmacies by Conditions Treated',
        labels={'Condition': 'Condition', 'Count': 'Number of Pharmacies'},
        color='Count',  # Color the bars based on the 'Count'
        color_continuous_scale='Blues'  # Choose a color scale for bars
    )

    # Customize the chart layout for better readability
    fig_conditions.update_layout(
        xaxis_title="Number of Pharmacies",  # Label for the x-axis
        yaxis_title="Condition",  # Label for the y-axis
        xaxis_tickformat='d',  # Format the x-axis as integers
        height=600,  # Set a specific height for the chart
        margin={"r": 0, "t": 50, "l": 50, "b": 50},  # Add some margin for readability
        autosize=True  # Allow the chart to automatically adjust size
    )

    st.plotly_chart(fig_conditions)

    st.subheader("How many specialties did each pharmacy mention on their website?")

    # Create the `pharmacy_specialty` DataFrame based on `available_pharmacies`
    pharmacy_specialty = available_pharmacies.copy()

    # Drop unnecessary columns
    cols_to_drop_spec = ['isGovernment', 'isSatellite', 'isInfusionCenter', 'isHospital', 'isVeterinaryOnly']
    pharmacy_specialty = pharmacy_specialty.drop(columns=cols_to_drop_spec)

    # Drop columns that start with 'services'
    service_columns = [col for col in pharmacy_specialty.columns if col.startswith('services')]
    pharmacy_specialty = pharmacy_specialty.drop(columns=service_columns)

    # Remove duplicate pharmacy names
    pharmacy_specialty = pharmacy_specialty.drop_duplicates(subset=['Pharmacy Name'])

    # Identify the boolean columns (those starting with 'is')
    bool_columns = [col for col in pharmacy_specialty.columns if col.startswith('is')]

    # Convert string 'True'/'False' to actual booleans (True/False)
    for col in bool_columns:
        pharmacy_specialty[col] = pharmacy_specialty[col].apply(lambda x: x == 'True')

    # Create a new column 'Specialty Count' by counting the number of True values in each row
    pharmacy_specialty['Specialty Count'] = pharmacy_specialty[bool_columns].apply(lambda row: row.sum(), axis=1)
    pharmacy_specialty = pharmacy_specialty[pharmacy_specialty['Specialty Count'] > 0]

    pharmacy_specialty.sort_values(by='Specialty Count', ascending=True, inplace=True)

    # Create the bar chart using Plotly
    fig_spec_count = px.bar(
        pharmacy_specialty,
        x='Specialty Count',  # Number of specialties on the x-axis
        y='Pharmacy Name',  # Pharmacy Name on the y-axis
        orientation='h',  # Horizontal bar chart
        title='Number of Specialties per Pharmacy',  # Chart title
        labels={'Specialty Count': 'Number of Specialties', 'Pharmacy Name': 'Pharmacy Name'},  # Axis labels
        color='Specialty Count',  # Color bars based on the number of specialties
        color_continuous_scale='Blues',  # Blue color scale
        text='Specialty Count'  # Show the count on the bars
    )

    # Customize the layout for better readability
    fig_spec_count.update_layout(
        xaxis_title="Number of Specialties",  # X-axis title
        yaxis_title="Pharmacy Name",  # Y-axis title
        xaxis_tickformat='d',  # Format x-axis as integers
        height=600,  # Set the height for the plot
        margin={"r": 0, "t": 50, "l": 50, "b": 150},  # Add margins for better spacing
        autosize=True  # Allow automatic resizing of the chart
    )

    st.plotly_chart(fig_spec_count)

    st.header("Where are the licensed facilities physically located?")
    st.write(
        "The California Board of Pharmacy has a known preference for pharmacies located within the physical borders of the state, however, there are pharmacies and facilities outside of California that have obtained Sterile Compounding Licenses. Please note that having a sterile license does not mean the pharmacy can ship any sterile product into the state, and that the board of pharmacy often limits what products can be shipped to patients or providers within California.")

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
        title="Mapping California Licensed Sterile Compounding Facilities",
        labels={'Entity Type': 'Facility Type'},  # Customize the legend label
        hover_data=['Entity Type', 'License Type', 'Pharmacy Name'],
        # Show Entity Type, License Type, and Pharmacy Name on hover
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

    st.header("Sources & Acknowledgements")

    st.markdown("""
    - **Pharmacy License Data** was sourced from the California State Board of Pharmacy License Database on December 8th, 2024. [https://www.pharmacy.ca.gov/about/verify_lic.shtml]
    - **Latitude & Longitude** were retrieved by Zip code using the US zip code dataset, much thanks to [https://www.github.com/erichurst/]
    - **Snapshot of Pharmacy Compounding in America** 2023 - 2024, Alliance for Pharmacy Compounding [https://a4pc.org/files/APC-Snapshot-23-24-updated-version.pdf]
    """, unsafe_allow_html=True)

elif menu == "About":
    # About Page (placeholder)
    st.title("About")
    st.write("This page will contain information about the data sources and methodology used in the analysis.")

