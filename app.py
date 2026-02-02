import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Researcher Profile", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; font-family: 'serif'; }
    h1, h2, h3 { color: #b89b72; }
    .stDataFrame { border: 1px solid #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

def get_orcid_token():
    url = "https://orcid.org/oauth/token"
    data = {
        'client_id': st.secrets["ORCID_CLIENT_ID"],
        'client_secret': st.secrets["ORCID_CLIENT_SECRET"],
        'grant_type': 'client_credentials',
        'scope': '/read-public'
    }
    headers = {'Accept': 'application/json'}
    res = requests.post(url, data=data, headers=headers)
    return res.json().get("access_token")


def get_orcid_data(orcid_id, token, endpoint="person"):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/{endpoint}"
    headers = {'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
    return requests.get(url, headers=headers).json()


token = get_orcid_token()
orcid_id = "0000-0003-4263-6034"

person_data = get_orcid_data(orcid_id, token, "person")
works_data = get_orcid_data(orcid_id, token, "works")
record_data = get_orcid_data(orcid_id, token, "record")
name = person_data.get('name', {}).get('given-names', {}).get('value', 'Researcher')
surname = person_data.get('name', {}).get('family-name', {}).get('value', '')

col1, col2 = st.columns([1, 3])

with col1:
    st.image("assets/profile.jpg")
    st.markdown(f"### {name} {surname}")
    st.write(f"ORCID: [{orcid_id}](https://orcid.org/{orcid_id})")

with col2:
    st.title("Academic Portfolio")
    st.subheader("Publications")
    pub_list = []
    group = works_data.get('group', [])
    for work in group:
        summary = work.get('work-summary', [{}])[0]
        title = summary.get('title', {}).get('title', {}).get('value', 'Unknown Title')
        year = summary.get('publication-date', {}).get('year', {}).get('value', 'N/A')
        pub_list.append({"Year": year, "Title": title})

    if pub_list:
        df = pd.DataFrame(pub_list).sort_values(by="Year", ascending=False)
        st.table(df)
    else:
        st.write("No publications found.")