import streamlit as st
import requests

API_URL = "http://backend:8000"  # docker-compose hálózat miatt "backend"

st.set_page_config(page_title="Építési Vállalkozás AI", layout="centered")
st.title("🏗️ Építési Vállalkozás AI - MVP")

st.header("📦 Anyagok")
desc = st.text_input("Anyag megnevezése")
qty = st.text_input("Mennyiség (pl. 100m2, 5db, 2t)")

if st.button("➕ Anyag hozzáadása"):
    if desc and qty:
        r = requests.post(f"{API_URL}/materials", json={"description": desc, "quantity": qty})
        if r.status_code == 200:
            st.success("Anyag hozzáadva!")
        else:
            st.error("Hiba történt!")

materials = requests.get(f"{API_URL}/materials").json()
st.subheader("📋 Jelenlegi anyaglista")
if materials:
    st.table(materials)
else:
    st.info("Nincs rögzített anyag.")

st.header("🏭 Beszállítók")
suppliers = requests.get(f"{API_URL}/suppliers").json()
if suppliers:
    st.table(suppliers)
else:
    st.info("Nincs rögzített beszállító (SQL-ben előre feltöltve).")

st.header("📨 Ajánlatkérés küldése")
if st.button("✉️ Ajánlatkérések kiküldése"):
    r = requests.post(f"{API_URL}/request_quotes")
    if r.status_code == 200:
        st.success(f"Elküldve: {r.json()['recipients']}")
    else:
        st.error("Hiba történt az e-mailek küldése közben.")
