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


