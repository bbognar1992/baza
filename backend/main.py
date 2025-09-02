from fastapi import FastAPI
from sqlmodel import SQLModel, Session, create_engine, Field, select
from typing import List
import yagmail
import openai

openai.api_key = "IDE_IRD_AZ_API_KEYED"

engine = create_engine("sqlite:///database.db")

class Supplier(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    material_type: str

class Material(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    description: str
    quantity: str

SQLModel.metadata.create_all(engine)
app = FastAPI()

def generate_email(materials: List[Material], supplier: Supplier) -> str:
    material_text = "\n".join([f"- {m.description} ({m.quantity})" for m in materials])
    prompt = f"""
    Kérlek, írj rövid, hivatalos ajánlatkérő emailt a következő anyagokra:
    {material_text}
    Címzett: {supplier.name}
    Nyelv: magyar
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200
    )
    return response.choices[0].text.strip()

@app.get("/suppliers", response_model=List[Supplier])
def list_suppliers():
    with Session(engine) as session:
        return session.exec(select(Supplier)).all()

@app.get("/materials", response_model=List[Material])
def list_materials():
    with Session(engine) as session:
        return session.exec(select(Material)).all()

@app.post("/materials")
def add_material(material: Material):
    with Session(engine) as session:
        session.add(material)
        session.commit()
        session.refresh(material)
        return material

@app.post("/request_quotes")
def request_quotes():
    with Session(engine) as session:
        suppliers = session.exec(select(Supplier)).all()
        materials = session.exec(select(Material)).all()

    yag = yagmail.SMTP("sajat_email@gmail.com", "app_password")

    sent_to = []
    for supplier in suppliers:
        email_text = generate_email(materials, supplier)
        yag.send(
            to=supplier.email,
            subject="Ajánlatkérés",
            contents=email_text
        )
        sent_to.append(supplier.email)
    return {"message": "Ajánlatkérések kiküldve", "recipients": sent_to}
