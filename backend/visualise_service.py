import streamlit as st
import pandas as pd
import json
import altair as alt
import os

st.set_page_config(layout="wide")

# Get token from URL
token = st.query_params.get("token")

if not token:
    st.error("No token provided in URL.")
    st.stop()

file_path = f"streamlit_data/{token}.json"

if not os.path.exists(file_path):
    st.error("Data not found for the provided token.")
    st.stop()

with open(file_path) as f:
    data = json.load(f)

# rest of the code stays the same

st.title("Market Data Visualisation")
view_mode = st.radio("View mode", ["Table", "Grid"], horizontal=True)

# Function to convert scraped data into a dataframe
def to_df(scraped_data):
    df = pd.DataFrame(scraped_data)
    df = df[["Title", "Price", "Discount", "Link"]]
    df = df.rename(columns={
        "Price": "Price (SGD)",
        "Discount": "Discount (%)",
        "Link": "Store Link"
    })
    df["Price (SGD)"] = df["Price (SGD)"].map("{:.2f}".format)
    df["Discount (%)"] = df["Discount (%)"].map("{:.0f}".format)
    df.index = range(1, len(df) + 1)
    df.index.name = "Ranking"
    return df

def render_marketplace_tab(name, df, average_price):
    st.subheader(name)
    st.metric("Average Price", f"${average_price:.2f}")
    df_cleaned = to_df(df)
    col1, col2 = st.columns([1, 1])
    with col1:
        if view_mode == "Table":
            st.data_editor(
                df_cleaned,
                column_config={
                    "Store Link": st.column_config.LinkColumn("Store Link", display_text="View")
                },
                use_container_width=True,
                disabled=True
            )
        else:
            for i in range(0, len(df), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(df):
                        product = pd.DataFrame(df).iloc[i + j]
                        with cols[j]:
                            with st.container():
                                st.markdown(
                                    f'''
                                    <div style="height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 1rem;">
                                        <strong>{product['Title']}</strong><br>
                                        {('<img src="' + product['Image'] + '" width="150" style="display: block; margin: 0 auto;">' if product.get('Image') else '')}
                                        <span><strong>Price:</strong> ${float(product['Price']):.2f} &nbsp;&nbsp; <strong>Discount:</strong> {int(product['Discount'])}%</span><br>
                                        <a href="{product['Link']}" target="_blank">View Product</a>
                                    </div>
                                    ''',
                                    unsafe_allow_html=True
                                )
    with col2:
        chart = alt.Chart(pd.DataFrame(df)).mark_bar().encode(
            x=alt.X('Ranking:O', title='Ranking', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Price:Q', title='Price (SGD)')
        ).properties(title='Top Listings', width='container')
        st.altair_chart(chart, use_container_width=True)

# Tabs for marketplaces
tab1, tab2 = st.tabs(["Lazada", "Carousell"])

with tab1:
    lazada_data = data["market_scrape_results"]["lazada"]
    render_marketplace_tab("Lazada", lazada_data["scraped_data"], lazada_data["average_price"])

with tab2:
    carousell_data = data["market_scrape_results"]["carousell"]
    render_marketplace_tab("Carousell", carousell_data["scraped_data"], carousell_data["average_price"])