import streamlit as st
import pandas as pd
import plotly.express as px

main_df = pd.read_csv("lemmatized1.csv")

st.title("Firm Comparison")

st.markdown("""
    - Medical device, food, and drug recall data from 2012-2024
    - Input up to 3 company names and any comma-separated issues you'd like to filter by.
    - The recall reasons will be filtered to include only those that contain all the words you provide.
""")

st.sidebar.subheader("Available Companies")
# Get companies with at least 3 rows
company_counts = main_df['Recalling Firm Name'].value_counts()
filtered_companies = company_counts[company_counts >= 3].index
sorted_companies = sorted(filtered_companies)
for company in sorted_companies:
    st.sidebar.markdown(company)


# User selects up to 3 product types
product_types = main_df['Product Type'].unique()

selected_product_types = st.multiselect(
    "Choose up to 3 Product Types",
    options=product_types,
    default=product_types[:3]
)

st.markdown("---")

col1, col2 = st.columns(2)

companies = []

with col1:
    for i in range(3):  # Loop for 3 companies
        company = st.text_input(f"Company {i + 1}", key=f"company_{i}")
        companies.append(company)

with col2:
    issues = st.text_area("Issues (comma-separated)", key="issues")
    issues_list = issues.split(",") if issues else []


# -- Start Filitering --

if st.button("Submit Changes"):
    filtered_df = main_df.copy()

    # Filter by product type
    if selected_product_types:
        filtered_df = main_df[main_df['Product Type'].isin(selected_product_types)]

    # Filter by company
    if any(companies):  # True if there is at least one non-empty string
        filtered_df = main_df[main_df['Recalling Firm Name'].isin([c for c in companies if c])]

    # Filter by issues
    if issues_list:
        filtered_df = filtered_df[
            filtered_df['Reason for Recall'].apply(lambda x: all(issue in x.lower() for issue in issues_list))
        ]

    # Creating a new dataframe with the following: 'Year-Month', 'Recalling Firm Name', 'Count'
    recalls_over_time = (
        filtered_df.groupby(['Year-Month', 'Recalling Firm Name'])
        .size() # this gets count
        .reset_index(name='Count')
    )

    st.markdown("---")


    # Display
    display_df = filtered_df.drop(columns=['FEI Number', 'Status', 'Product Type', 
                                        'Distribution Pattern', 'Recalling Firm City', 
                                        'Recalling Firm State', 'Recalling Firm Country',
                                        'Product ID',
                                        'Center', 'Recall Details', 'Lemmatized Reason'])

    if not display_df.empty:
        st.write(f"Filtered results: {display_df.shape[0]} records found.")
    else:
        st.write("No data available for the selected filters.")

    # Create bar graph
    if not recalls_over_time.empty:
        fig = px.bar(
            recalls_over_time,
            x='Year-Month',
            y='Count',
            color='Recalling Firm Name',
            title="Recall Count Over Time",
            labels={'Year-Month': 'Time (Year-Month)', 'Count': 'Recall Count'},
        )

        fig.update_xaxes(tickangle=45)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available for the selected companies.")

    # Create pie chart with top 10 companies based on selected product type
    if selected_product_types:
        product_type_filter = main_df[main_df['Product Type'].isin(selected_product_types)]
    else:
        product_type_filter = main_df

    top_companies = product_type_filter['Recalling Firm Name'].value_counts().head(10)

    # Create the Pie Chart
    fig = px.pie(
        top_companies,
        names=top_companies.index,
        values=top_companies.values,
        title="Top 10 Companies with Most Recalls In Selected Product Type",
        labels={'value': 'Recall Count', 'names': 'Company'},
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(display_df)
else:
    st.write("Make changes and press 'Submit Changes' to view the results.")