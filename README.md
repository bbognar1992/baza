# README.md

# Baza – Építési vállalkozás AI segéd

**Baza** egy MVP webalkalmazás, ami az építési vállalkozók munkáját segíti az **anyagrendelések automatizálásával és ajánlatkérések egyszerűsítésével**.
Az alkalmazás AI segítségével készít hivatalos ajánlatkérő e-maileket, és könnyíti a beszállítói kapcsolattartást.

---

## ⚡ Fő funkciók (MVP)

* Anyaglista feltöltése és kezelése.
* Beszállítók listázása és kapcsolattartás.
* AI által generált **ajánlatkérő e-mailek** küldése a beszállítóknak.
* Egyszerű, gyors **Streamlit frontend** a kezelhetőséghez.
* **FastAPI backend** a logika és adatkezelés számára.

---

## 🛠️ Technológia

* Python 3.11
* FastAPI (backend)
* Streamlit (frontend)
* SQLite (adatbázis)
* OpenAI API (AI email generálás)
* Yagmail (email küldés)
* Docker + Docker Compose

---

## 🚀 Telepítés és futtatás Dockerrel

1. Klónozd a projektet vagy töltsd le a ZIP-et:

```bash
git clone <repo_url>
cd mvp_project
```

2. Futtasd a Docker Compose-t:

```bash
docker-compose up --build
```

3. Böngészőben elérheted:

* **FastAPI dokumentáció:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Streamlit frontend:** [http://localhost:8501](http://localhost:8501)

---

## ⚙️ Konfiguráció

* **OpenAI API kulcs**: a `backend` környezetben kell megadni (`docker-compose.yml`)
* **Email hitelesítés**: `yagmail`-hez Gmail fiók vagy app jelszó szükséges

---

## 📂 Projekt struktúra

```
mvp_project/
│
├─ backend/
│   ├─ main.py
│   ├─ requirements.txt
│   └─ Dockerfile
│
├─ frontend/
│   ├─ app.py
│   ├─ requirements.txt
│   └─ Dockerfile
│
├─ docker-compose.yml
└─ README.md
```

---

## 📝 Használati útmutató

1. Először rögzítsd a beszállítókat az adatbázisban (SQL-ből vagy bővített frontend).
2. Töltsd fel az anyaglistát a frontend felületen.
3. Kattints az **Ajánlatkérések kiküldése** gombra → az AI generálja az e-mailt, majd a rendszer elküldi a beszállítóknak.

---

## 📈 Fejlesztési lehetőségek

* Beérkező ajánlatok automatikus feldolgozása.
* Többnyelvű email generálás.
* AI alapú **erőforrás- és időjárás-alapú ütemezés** a projekt optimalizálásához.
* Műszaki átadás checklistek AI támogatással.
