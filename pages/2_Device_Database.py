import streamlit as st
import pandas as pd
import plotly.express as px


main_df = pd.read_csv("categorized.csv")

st.title("Medical Device FDA Recall Analysis")

with st.sidebar:
    device_type = st.selectbox("Select Device Type:", ["All"] + list(main_df['Device Type'].unique()))
    recall_category = st.selectbox("Select Recall Category:", ["All"] + list(main_df['Recall Category'].unique()))
    event_class = st.selectbox("Select Event Class:", ["All", "Class I", "Class II", "Class III"])



filtered_df = main_df.copy()
filtered_df = filtered_df.drop(columns=["Unnamed: 0"])

# Apply filters based on selection
if device_type != "All":
    filtered_df = filtered_df[filtered_df["Device Type"] == device_type]

if recall_category != "All":
    filtered_df = filtered_df[filtered_df["Recall Category"] == recall_category]

if event_class != "All":
    filtered_df = filtered_df[main_df["Event Classification"] == event_class]

unique_reasons = filtered_df['Reason for Recall'].unique()


rows = len(filtered_df)  # Number of unique devices found (rows)
list_dev_types = filtered_df['Device Type'].unique()  # list of unique device types
list_rec_categories = filtered_df['Recall Category'].unique()  

st.markdown("---")
st.markdown("### Summary:")
st.markdown(
    f"""
    - **Number of device recalls found**: {rows}
    - **Unique device types**: {', '.join(list_dev_types)}
    - **Unique recall categories**: {', '.join(list_rec_categories)}
    """
)

with st.expander("See Unique Reasons for Recall"):
    st.write("The table below lists every unique reason for a device recall. There are " + str(filtered_df['Reason for Recall'].nunique()) + " unique recalls based on current filters.")
    st.table(unique_reasons)

# display a cleaned version of the filtered DataFrame without uneeded columns
st.subheader("Cleaned Data With Most Relevant Columns:")
clean_df = filtered_df.drop(columns=['FEI Number', 'Status', 'Product Type', 
                                     'Distribution Pattern', 'Recalling Firm City', 
                                     'Recalling Firm State', 'Recalling Firm Country',
                                     'Center Classification Date', 'Event ID', 'Product ID',
                                     'Center', 'Recall Details'])
clean_df = clean_df.reindex(columns=['Recalling Firm Name', 'Product Classification', 'Event Classification', 'Product Description', 'Reason for Recall', 'Device Type', 'Recall Category'])
st.dataframe(clean_df)

full = filtered_df

# display graph of associated recall categories for specified device type
filtered_df = main_df[main_df["Device Type"] == device_type]
recall_counts = filtered_df["Recall Category"].value_counts().reset_index() # Group by 'Recall Category' and count occurrences
recall_counts.columns = ['Recall Category', 'Count']
fig = px.bar(recall_counts, x='Recall Category', y='Count', title=f'Distribution of Recall Categories by Device Type: {device_type}')
fig.update_layout(xaxis_title='Recall Category', yaxis_title='Count', xaxis_tickangle=-45) # rotate x label
st.plotly_chart(fig)

# display graph of associated device types for specified recall category
filtered_df = main_df[(main_df["Recall Category"] == recall_category)]
recall_counts = filtered_df["Device Type"].value_counts().reset_index() # Group by 'Device Type' and count occurrences
recall_counts.columns = ['Device Type', 'Count']
fig2 = px.bar(recall_counts, x='Device Type', y='Count', title=f"Distribution of Device Types by Recall Category: {recall_category}")
fig2.update_layout(xaxis_title='Device Types', yaxis_title='Count', xaxis_tickangle=-45) # rotate x label
st.plotly_chart(fig2)

st.markdown("---")
st.subheader("Full Filtered Data:")
st.markdown("- Includes all columns")
st.dataframe(full)
