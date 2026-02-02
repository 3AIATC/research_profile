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

st.image("assets/profile.jpg", width = 250)
st.markdown(f"### {name} {surname}")
st.write(f"ORCID: [{orcid_id}](https://orcid.org/{orcid_id})")
st.title("Academic Portfolio")

activities = record_data.get('activities-summary', {})
st.subheader("Employment")
emp_groups = activities.get('employments', {}).get('affiliation-group', [])
for group in emp_groups:
    summ = group.get('summaries', [{}])[0].get('employment-summary', {})
    org = summ.get('organization', {}).get('name', 'Unknown Organization')
    role = summ.get('role-title', 'Staff')
    st.write(f"**{org}** — {role}")

st.subheader("Education")
edu_groups = activities.get('educations', {}).get('affiliation-group', [])
for group in edu_groups:
    summ = group.get('summaries', [{}])[0].get('education-summary', {})
    org = summ.get('organization', {}).get('name', 'Unknown Institution')
    degree = summ.get('role-title', 'Researcher')
    st.write(f"**{org}** — {degree}")

st.subheader("External Identifiers")
external_ids = person_data.get('external-identifiers', {}).get('external-identifier', [])
scopus_id = None
for eid in external_ids:
    if 'scopus' in eid.get('external-id-type', '').lower():
        scopus_id = eid.get('external-id-value')
        scopus_url = eid.get('external-id-url', {}).get('value')
        st.write(f"Scopus Author ID: [{scopus_id}]({scopus_url})")
if not scopus_id:
    st.write("No Scopus profile linked in ORCID.")

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