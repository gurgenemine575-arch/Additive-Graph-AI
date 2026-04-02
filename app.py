from openai import OpenAI
import streamlit as st
from rdflib import Graph
import re

# 🔐 API
client = OpenAI()

# 📊 RDF
g = Graph()
g.parse("food_ontology.rdf")


# 🔍 SPARQL
def get_data_based_on_question(question, risk):

    question = question.lower()

    if "renk" in question:
        query = """
        PREFIX : <https://foodadditivegraph.org/ontology#>
        SELECT ?additive
        WHERE {
            ?additive :hasFoodCategory :Colorant .
        }
        """

    elif risk != "All":
        query = f"""
        PREFIX : <https://foodadditivegraph.org/ontology#>
        SELECT ?additive
        WHERE {{
            ?additive :hasRiskLevel :{risk} .
        }}
        """

    elif "e" in question:
        match = re.search(r"e\d+", question)
        if match:
            code = match.group().upper()
            query = f"""
            PREFIX : <https://foodadditivegraph.org/ontology#>
            SELECT ?additive ?risk ?category
            WHERE {{
                :{code} :hasRiskLevel ?risk .
                :{code} :hasFoodCategory ?category .
                BIND(:{code} AS ?additive)
            }}
            """
        else:
            return "Veri bulunamadı."

    else:
        query = """
        PREFIX : <https://foodadditivegraph.org/ontology#>
        SELECT ?additive ?risk
        WHERE {
            ?additive :hasRiskLevel ?risk .
        }
        LIMIT 5
        """

    results = g.query(query)

    data = ""
    for row in results:
        data += " - " + " | ".join([str(x).split("#")[-1] for x in row]) + "\n"

    return data if data else "Veri bulunamadı."


# 🤖 CHATBOT
def chatbot(question, risk):
    data = get_data_based_on_question(question, risk)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a food safety expert. Answer clearly in Turkish using bullet points. Only use the provided data."
            },
            {
                "role": "user",
                "content": f"{question}\n\nData:\n{data}"
            }
        ]
    )

    return response.choices[0].message.content


# ================= UI =================

st.title("🥗 Food Additive AI Assistant")

st.info("💡 Örnek: E102 zararlı mı? | Renklendirici katkılar hangileri?")

st.write("🚀 Hızlı sorular:")

# 🔘 BUTONLAR (KEY EKLİ → HATA YOK)
if st.button("E102 zararlı mı?", key="btn1"):
    st.session_state["question"] = "E102 zararlı mı?"

if st.button("Renklendirici katkılar hangileri?", key="btn2"):
    st.session_state["question"] = "Renklendirici katkılar hangileri?"

if st.button("Yüksek riskli katkılar nelerdir?", key="btn3"):
    st.session_state["question"] = "Yüksek riskli katkılar nelerdir?"

# 🎯 FILTER
risk = st.selectbox("Risk seviyesi seç:", ["All", "Low", "Medium", "High"])

# 🔍 INPUT
question = st.text_input(
    "Sorunu yaz:",
    value=st.session_state.get("question", "")
)

# 🚀 TEK BUTTON (KEY EKLİ)
if st.button("Sor", key="ask_button"):
    if question:
        with st.spinner("🤖 Cevap hazırlanıyor..."):
            answer = chatbot(question, risk)

        st.write("### 🤖 Cevap:")
        st.write(answer)