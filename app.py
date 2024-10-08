import streamlit as st
import pandas as pd
import plotly.express as px

# Load your dataset
data = pd.read_csv('cleaned_data.csv')

# Title of the Dashboard
st.title("App Analytics Dashboard")

# Sidebar for filters
st.sidebar.header("Filters")

# Dropdown for categories
selected_categories = st.sidebar.multiselect(
    'Select categories',
    options=data['Category'].unique(),
    default=data['Category'].unique()[:1]  # Default to the first category
)

# Dropdown for types
selected_types = st.sidebar.multiselect(
    'Select type',
    options=['Free', 'Paid'],
    default=['Free']  # Default to Free
)

# Rating slider
rating_range = st.sidebar.slider(
    'Select rating range',
    min_value=0.0,
    max_value=5.0,
    value=(0.0, 5.0),
    step=0.1
)

# Search input
search_value = st.sidebar.text_input("Search for an app...")

# Button for downloading data (placeholder functionality)
if st.sidebar.button("Download Data"):
    st.sidebar.success("Data Downloaded!")  # Placeholder action

# Filter data based on user selections
filtered_data = data[
    (data['Category'].isin(selected_categories) if selected_categories else True) &
    (data['Type'].isin(selected_types) if selected_types else True) &
    (data['Rating'] >= rating_range[0]) &
    (data['Rating'] <= rating_range[1]) &
    (data['App'].str.contains(search_value, case=False) if search_value else True)
]

# Create and display the various plots in columns
if not filtered_data.empty:
    col1, col2 = st.columns(2)

    with col1:
        # Rating histogram
        rating_hist = px.histogram(filtered_data, x='Rating', nbins=10, title="Distribution of Ratings")
        st.plotly_chart(rating_hist)

        # Installs vs Rating scatter plot
        installs_rating_fig = px.scatter(filtered_data, x='Installs', y='Rating', title='Installs vs Rating')
        st.plotly_chart(installs_rating_fig)

        # Box plot of rating by Type
        box_fig = px.box(filtered_data, x='Type', y='Rating', title='Box Plot of Ratings by Type')
        st.plotly_chart(box_fig)

    with col2:
        # Price vs Rating scatter plot
        price_rating_fig = px.scatter(filtered_data, x='Price', y='Rating', title='Price vs Rating')
        st.plotly_chart(price_rating_fig)

        # Bar chart of average installations by category
        installs_bar_fig = px.bar(
            filtered_data,
            x='Category',
            y='Installs',
            title='Total Number of Installs by Category',
            text='Installs'
        )
        st.plotly_chart(installs_bar_fig)

    # Summary statistics
    avg_rating = filtered_data['Rating'].mean() if not filtered_data.empty else 0
    total_apps = filtered_data.shape[0]
    st.write(f"Total Apps: {total_apps}, Average Rating: {avg_rating:.2f}")

    # Create pivot table
    pivot_table = filtered_data.groupby(['Category', 'Type']).agg({
        'Rating': 'mean',
        'Installs': 'sum'
    }).reset_index().rename(columns={'Rating': 'Average Rating', 'Installs': 'Total Installs'})

    st.subheader("Pivot Table")
    st.dataframe(pivot_table)

else:
    st.warning("No data available for the selected filters.")
