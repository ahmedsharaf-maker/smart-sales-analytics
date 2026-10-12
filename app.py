
import streamlit as st
import pandas as pd

# Page settings
st.set_page_config(
    page_title="Smart Sales Analytics",
    page_icon="📊",
    layout="wide"
)

# Styling
st.title("📊 Smart Sales Analytics Dashboard")
st.caption("Turn sales data into useful business insights.")

# Demo data
def load_demo_data():
    return pd.DataFrame({
        "Order_ID": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
        "Product": [
            "Laptop", "Mouse", "Keyboard", "Monitor",
            "Laptop", "Mouse", "Monitor", "Keyboard"
        ],
        "Category": [
            "Electronics", "Accessories", "Accessories", "Electronics",
            "Electronics", "Accessories", "Electronics", "Accessories"
        ],
        "Quantity": [2, 5, 3, 1, 1, 8, 2, 4],
        "Unit_Price": [25000, 300, 800, 7000, 25000, 300, 7000, 800],
        "Region": [
            "Cairo", "Giza", "Alexandria", "Cairo",
            "Giza", "Cairo", "Alexandria", "Giza"
        ]
    })


# Sidebar: upload data
st.sidebar.header("📁 Upload Your Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("File uploaded successfully!")
    except Exception as e:
        st.error(f"Could not read the file: {e}")
        st.stop()
else:
    df = load_demo_data()
    st.sidebar.info("Showing sample data.")

# Clean column names
df.columns = df.columns.astype(str).str.strip()

# Check required columns
required_columns = ["Product", "Quantity", "Unit_Price", "Region"]
missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(
        "Your file is missing these columns: "
        + ", ".join(missing_columns)
    )
    st.write("Required columns:", ", ".join(required_columns))
    st.stop()

# Convert numeric columns
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")

# Remove rows with invalid essential values
df = df.dropna(
    subset=["Product", "Quantity", "Unit_Price", "Region"]
).copy()

# Calculate sales
df["Sales"] = df["Quantity"] * df["Unit_Price"]

if df.empty:
    st.warning("No valid rows found in the uploaded file.")
    st.stop()

# Filters
st.sidebar.header("🔎 Filters")

regions = sorted(df["Region"].astype(str).unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Select Region",
    regions,
    default=regions
)

products = sorted(df["Product"].astype(str).unique().tolist())
selected_products = st.sidebar.multiselect(
    "Select Product",
    products,
    default=products
)

filtered_df = df[
    df["Region"].astype(str).isin(selected_regions)
    & df["Product"].astype(str).isin(selected_products)
].copy()

if filtered_df.empty:
    st.warning("No data matches your selected filters.")
    st.stop()

# KPI cards
st.subheader("📌 Key Performance Indicators")

total_sales = filtered_df["Sales"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_orders = (
    filtered_df["Order_ID"].nunique()
    if "Order_ID" in filtered_df.columns
    else len(filtered_df)
)
average_sales = total_sales / total_orders if total_orders else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"{total_sales:,.2f}")
c2.metric("Total Orders", f"{total_orders:,}")
c3.metric("Units Sold", f"{total_quantity:,.0f}")
c4.metric("Average Sales / Order", f"{average_sales:,.2f}")

# Data preview
st.subheader("📋 Sales Data Preview")
st.dataframe(filtered_df, use_container_width=True)

# Charts
st.subheader("📈 Sales Analysis")

left, right = st.columns(2)

with left:
    st.markdown("**Sales by Product**")
    sales_by_product = (
        filtered_df.groupby("Product")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(sales_by_product)

with right:
    st.markdown("**Sales by Region**")
    sales_by_region = (
        filtered_df.groupby("Region")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(sales_by_region)

# Category chart, if available
if "Category" in filtered_df.columns:
    st.subheader("🗂️ Sales by Category")
    sales_by_category = (
        filtered_df.groupby("Category")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(sales_by_category)

# Automatic insights
st.subheader("💡 Business Insights")

best_product = sales_by_product.idxmax()
best_region = sales_by_region.idxmax()

st.write(
    f"🏆 **Top product by sales:** {best_product} "
    f"({sales_by_product.max():,.2f})"
)
st.write(
    f"🌍 **Top region by sales:** {best_region} "
    f"({sales_by_region.max():,.2f})"
)
st.write(
    f"📦 **Total units sold:** {total_quantity:,.0f}"
)

# Data quality
with st.expander("🧹 Data Quality Check"):
    st.write(f"Rows in uploaded data: {len(df)}")
    st.write(f"Rows after filtering: {len(filtered_df)}")
    st.write(f"Duplicate rows: {int(df.duplicated().sum())}")
    st.write(f"Missing values remaining: {int(df.isna().sum().sum())}")

# Download filtered results
st.subheader("⬇️ Download Results")

csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Download Analyzed Data (CSV)",
    data=csv_data,
    file_name="sales_analysis.csv",
    mime="text/csv"
)

st.caption("Smart Sales Analytics | Portfolio Project")
