import streamlit as st

Lab_1 = st.Page("Lab_1.py", title = "Lab 1")
Lab_2 = st.Page("Lab_2.py", title = "Lab 2")
Lab_3 = st.Page("Lab_3.py", title = "Lab 3")

pg = st.navigation([Lab_3, Lab_2, Lab_1])
st.set_page_config(page_title="Labs")

pg.run()