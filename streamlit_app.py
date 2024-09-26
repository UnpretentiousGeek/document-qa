import streamlit as st

Lab_1 = st.Page("Lab_1.py", title = "Lab 1")
Lab_2 = st.Page("Lab_2.py", title = "Lab 2")
Lab_3 = st.Page("Lab_3.py", title = "Lab 3")
Lab_4 = st.Page("Lab_4.py", title = "Lab 4")
Lab_5 = st.Page("Lab_5.py", title = "Lab 5")

pg = st.navigation([Lab_5, Lab_4, Lab_3, Lab_2, Lab_1])
st.set_page_config(page_title="Labs")

pg.run()