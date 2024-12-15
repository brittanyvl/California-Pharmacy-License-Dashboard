import streamlit as st
import pandas as pd
import plotly.express as px

#Load Data
all_pharmacies = pd.read_csv('all_pharmacies.csv', dtype=str)
available_pharmacies = pd.read_csv('available_pharmacies.csv', dtype=str)

st.title('Exploring California Sterile Compounding Licenses')
st.write("summary here")

st.subheader('Search Our Database')
# Example: Filter by State
type = st.selectbox('What Type of Pharmacy?', all_pharmacies['Entity Type'].unique())
filtered_data = all_pharmacies[all_pharmacies['Entity Type'] == type]

st.subheader(f'Pharmacies in {type}')
st.dataframe(filtered_data)

st.subheader("Explore License Types")
# Example: License Type Distribution
license_type_counts = all_pharmacies['License Type'].value_counts().reset_index()
license_type_counts.columns = ['License Type', 'Count']

fig = px.bar(
    license_type_counts,
    x='License Type',
    y='Count',
    title="Pharmacy Distribution by License Type"
)

st.plotly_chart(fig)
