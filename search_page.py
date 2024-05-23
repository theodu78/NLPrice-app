import streamlit as st
from chat_agent import ChatAgent
from db_connector import query_sql, query_pinecone

# Initialisation de l'agent de discussion
chat_agent = ChatAgent()

def main():
    st.title("Recherche de Prix")
    
    # Interface du chatbot
    st.write("Posez votre question ci-dessous:")
    user_input = st.text_input("Votre question:", "")
    
    if st.button("Envoyer"):
        if user_input:
            # Obtenir la réponse de l'agent
            response = chat_agent.get_response(user_input)
            st.write("Réponse:")
            st.write(response)
        else:
            st.write("Veuillez entrer une question.")

if __name__ == "__main__":
    main()
