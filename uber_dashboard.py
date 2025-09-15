import streamlit as st
import pandas as pd

# Read cleaned parquet from MinIO
df = pd.read_parquet(
    's3://uber-datalake/cleaned_ncr_ride_bookings.parquet',
    storage_options={
        'key': 'oliverminio',
        'secret': 'oliver#0L',
        'client_kwargs': {
            'endpoint_url': 'http://localhost:9000'
        }
    }
)

st.title("Uber Rides Analytics Dashboard")
st.dataframe(df.head(20))

# Core visualizations
import matplotlib.pyplot as plt

# 1. Booking Status Distribution
st.subheader("Booking Status Distribution")
status_counts = df["Booking Status"].value_counts()
st.bar_chart(status_counts)

# 2. Revenue Trends (Daily)
st.subheader("Daily Revenue Trend")
df["datetime"] = pd.to_datetime(df["datetime"])
daily_revenue = df.groupby(df["datetime"].dt.date)["Booking Value"].sum()
st.line_chart(daily_revenue)

# 3. Payment Method Breakdown
st.subheader("Payment Method Breakdown")
st.bar_chart(df["Payment Method"].value_counts())

# 4. Driver vs Customer Ratings
st.subheader("Rating Distribution")
fig, ax = plt.subplots()
ax.hist(df["Driver Ratings"].dropna(), bins=20, alpha=0.5, label='Driver Ratings')
ax.hist(df["Customer Rating"].dropna(), bins=20, alpha=0.5, label='Customer Rating')
ax.set_xlabel('Rating')
ax.set_ylabel('Frequency')
ax.legend()
st.pyplot(fig)

# Interactive Filters
# Sidebar Filters
st.sidebar.header("Filters")
vehicle = st.sidebar.selectbox("Vehicle Type", options=["All"] + df["Vehicle Type"].unique().tolist())
status = st.sidebar.selectbox("Booking Status", options=["All"] + df["Booking Status"].unique().tolist())
payment = st.sidebar.selectbox("Payment Method", options=["All"] + df["Payment Method"].unique().tolist())

filtered_df = df.copy()
if vehicle != "All":
    filtered_df = filtered_df[filtered_df["Vehicle Type"] == vehicle]
if status != "All":
    filtered_df = filtered_df[filtered_df["Booking Status"] == status]
if payment != "All":
    filtered_df = filtered_df[filtered_df["Payment Method"] == payment] 

st.subheader("Filtered Data")
st.dataframe(filtered_df.head(20))

# KPIs at the Top
st.markdown("### Key Performance Indicators (KPIs)")

total_rides = len(df)
completed_rides = len(df[df["Booking Status"] == "Completed"])
total_revenue = df["Booking Value"].sum()
average_driver_rating = df["Driver Ratings"].mean()
average_customer_rating = df["Customer Rating"].mean()

col1, col2, col3, col4, col5 = st.columns([2, 2, 4, 2, 2])
col1.metric("Total Rides", total_rides)
col2.metric("Completed Rides", completed_rides)
col3.metric("Total Revenue", f"${total_revenue:,.2f}")
col4.metric("Avg Driver Rating", f"{average_driver_rating:.2f}")
col5.metric("Avg Customer Rating", f"{average_customer_rating:.2f}")

# Heatmap of Cancelled Rides by Hour of Day
import seaborn as sns
import matplotlib.pyplot as plt

st.subheader("Heatmap of Cancelled Rides by Hour of Day")

df["datetime"] = pd.to_datetime(df["datetime"])
df["hour"] = df["datetime"].dt.hour
df["date"] = df["datetime"].dt.day_name()

cancelled = df[df["Booking Status"].isin(["Cancelled by Driver", "Cancelled by Customer"])]

if not cancelled.empty:     
    heatmap_data = cancelled.groupby(["date", "hour"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax)
    ax.set_title("Cancelled Rides by Hour of Day")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week")
    st.pyplot(fig)
else:
    st.write("No cancelled rides data available to display the heatmap.")

# Footer
st.markdown("""
### About
This dashboard provides insights into Uber ride bookings, including booking status, revenue trends, and user ratings.

### Data Source
The data is sourced from the Kaggle Uber Data and is updated regularly.

### Contact
For any inquiries, please contact the data team.
""")