import streamlit as st
from datetime import date
from default_data import ensure_base_session_state
from navbar import render_navbar, set_current_page

st.set_page_config(page_title="Szerződéskészítés AI-val – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Set current page for navbar highlighting
set_current_page("Szerződéskészítés")

st.title("📄 Szerződéskészítés AI-val")
st.caption("Hasznos, de sok jogi finomhangolást igényel – nem minősül jogi tanácsnak.")

with st.expander("Fontos jogi megjegyzés", expanded=False):
    st.write(
        """
        Az itt generált szövegek csupán kiindulási alapok. Minden szerződést
        ügyvédnek kell felülvizsgálnia, és az adott ügyfél/projekt igényeihez
        kell igazítani. A használatból eredő következményekért felelősséget nem vállalunk.
        """
    )

st.write("Töltsd ki az alábbi mezőket a szerződés tervezetéhez.")

col1, col2 = st.columns(2)
with col1:
    contract_type = st.selectbox(
        "Szerződés típusa",
        [
            "Vállalkozási szerződés",
            "Alvállalkozói szerződés",
            "Adatfeldolgozási megállapodás (DPA)",
            "Titoktartási megállapodás (NDA)",
        ],
    )
    party_a = st.text_input("Megrendelő / Fél A neve", value="Megrendelő Kft.")
    party_b = st.text_input("Vállalkozó / Fél B neve", value="Vállalkozó Bt.")
    project_name = st.text_input("Projekt megnevezése", value="Családi ház építés")
    start_on = st.date_input("Kezdés", value=date.today())
    end_on = st.date_input("Befejezés (tervezett)")

with col2:
    scope = st.text_area(
        "Teljesítés tárgya (rövid leírás)",
        height=120,
        value=(
            "Kivitelezési munkák: alapozás, falazat, tetőszerkezet, "
            "nyílászárók beépítése, gépészeti és villamossági alapszerelés."
        ),
    )
    price = st.text_input("Ellenszolgáltatás / Vállalkozói díj (nettó)", value="35 000 000 Ft")
    payment = st.text_input("Fizetési feltételek", value="30% előleg, 60% részszámlák, 10% átadáskor")
    governing_law = st.text_input("Irányadó jog", value="Magyar jog")
    warranty = st.text_input("Jótállás / Szavatosság", value="12 hónap jótállás a műszaki átadástól")

include_nd_conf = st.checkbox("Titoktartás / adatvédelem fejezet beszúrása", value=True)
ack = st.checkbox("Megértettem, hogy a generált szöveg nem minősül jogi tanácsnak.")

generate = st.button("Szerződéstervezet generálása", disabled=not ack)

if generate:
    clauses = []
    clauses.append(f"Szerződés típusa: {contract_type}")
    clauses.append(f"Felek: {party_a} (Megrendelő) és {party_b} (Vállalkozó)")
    clauses.append(f"Projekt: {project_name}")
    clauses.append(f"Időtartam: {start_on.isoformat()} – {end_on.isoformat() if end_on else '(n/a)'}")
    clauses.append(f"Teljesítés tárgya: {scope}")
    clauses.append(f"Vállalkozói díj: {price}")
    clauses.append(f"Fizetési feltételek: {payment}")
    clauses.append(f"Irányadó jog: {governing_law}")
    clauses.append(f"Jótállás / szavatosság: {warranty}")

    body = [
        f"1. Felek\nA szerződő felek: {party_a} és {party_b}.",
        f"2. A szerződés tárgya\n{scope}",
        (
            "3. Határidők\nA teljesítés tervezett időtartama: "
            f"{start_on.isoformat()} – {end_on.isoformat() if end_on else '(n/a)'}"
        ),
        f"4. Díjazás és fizetés\nVállalkozói díj: {price}. Fizetés módja: {payment}.",
        "5. Teljesítés igazolása\nRész-számlázás mérföldkövek szerint, végszámla átadás-átvétel után.",
        f"6. Irányadó jog és jogvita rendezése\n{governing_law}. A jogvitákat felek elsősorban egyeztetéssel rendezik.",
        f"7. Jótállás és szavatosság\n{warranty}.",
    ]

    if include_nd_conf:
        body.append(
            "8. Titoktartás és adatvédelem\nA felek a szerződéssel összefüggő üzleti és személyes adatokat "
            "bizalmasan kezelik, és azokat kizárólag a teljesítéshez szükséges mértékben használják fel."
        )

    body.append("9. Vegyes rendelkezések\nA szerződés módosítása csak írásban érvényes.")

    draft = (
        f"{contract_type}\n\n"
        f"ALAPADATOK\n" + "\n".join(clauses) + "\n\n"
        f"RENDELKEZÉSEK\n" + "\n\n".join(body) + "\n\n"
        "FIGYELMEZTETÉS: A tervezet nem minősül jogi tanácsnak. Ügyvédi felülvizsgálat szükséges."
    )

    st.text_area("Generált szerződéstervezet", value=draft, height=420)


