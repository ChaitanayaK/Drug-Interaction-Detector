import streamlit as st
from PIL import Image
import google.generativeai as genai
from drug_interaction import Interaction
from translation import translate
from drugstore import DrugStore
import sqlite3
from langchain_google_genai import GoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

conn = sqlite3.connect('data/medicine.db')
cursor = conn.cursor()

genai.configure()

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold" : "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold" : "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold" : "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold" : "BLOCK_NONE"
    }
]

def getData(rows):
    drugs = []
    for row in rows:
        chemicals = []
        if row[2]:
            chemicals.append(row[2])
        if row[3]:
            chemicals.append(row[3])
        drugs.append({'name':row[1], 'chemicals': chemicals})

    chemicals = []
    for drug in drugs:
        chemicals.extend(drug['chemicals'])
    return (drugs, chemicals)

def remove_string(index):
    del st.session_state['medicines'][index]

def chat(question, data):
    review_template = """
        Following is the information about effects of interaction of 2 or more drugs, respond to the question based on the data as well your own knowledge about the subject. Use extra_data for seeking knowledge about the medicines, but main information about interaction is in data. Try giving response in a list format with bullet points:\
        
        data : {data}\
        extra_data : {extra_data}
        question: {question}\
    """

    prompt_template = ChatPromptTemplate.from_template(review_template)
    messages = prompt_template.format_messages(question=question, data=data, extra_data=st.session_state.extradata)

    chat = ChatOpenAI(temperature=0.7, model='gpt-3.5-turbo')
    # llm = GoogleGenerativeAI(model='gemini-pro')
    # chat = llm.invoke(input=messages)
    response = chat(messages)
    return response.content

def main():
    if 'medicines' not in st.session_state:
        st.session_state['medicines'] = []

    if 'extradata' not in st.session_state:
        st.session_state.extradata = []
    
    if 'output' not in st.session_state:
        st.session_state.output = ''

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.title('Drug Interaction Checker')
    with col2:
        if st.button('⟳'):
            st.session_state.clear()
            st.cache_data.clear()
            st.rerun()

    st.sidebar.title('Get Medicine From Photo')
    picture = st.sidebar.camera_input('Camera', )

    if picture is not None and 'medicines' in st.session_state and len(st.session_state['medicines']) < 2:
        image = Image.open(picture)
        model = genai.GenerativeModel(model_name='gemini-pro-vision', safety_settings=safety_settings)
        response = model.generate_content(['Just return only the name of medicine and nothing else',image])
        query_response = response.text.strip().split()[0]

        cursor.execute("SELECT * FROM medicine WHERE name LIKE ?", ('%' + query_response + '%',))
        names = [row[1] for row in cursor.fetchall()]
        names.insert(0, 'Select')

        name_cam = st.sidebar.selectbox('Select Medicine:', names, placeholder='Select', key='name_cam')
        if name_cam != 'Select':
            cursor.execute("SELECT * FROM medicine WHERE name = ?", (name_cam,))
            medicine = cursor.fetchone()
            if medicine not in st.session_state['medicines']:
                st.session_state['medicines'].append(medicine)

    if 'medicines' in st.session_state and len(st.session_state['medicines']) < 2:
        med_len = len(st.session_state['medicines'])
        heading_text = f'Add medicine {med_len+1} below: '
        st.subheader(heading_text)
        medicine_name = st.text_input('Enter Medicine Name', key='input_name')

        cursor.execute("SELECT * FROM medicine WHERE name LIKE ?", ('%' + medicine_name + '%',))
        names = [row[1] for row in cursor.fetchall()]
        names.insert(0, 'Select')

        if medicine_name:
            name = st.selectbox('Select Medicine:', names, key='medicine_name', placeholder='Select')
            if name != 'Select':
                cursor.execute("SELECT * FROM medicine WHERE name = ?", (name,))
                row = cursor.fetchone()
                if row not in st.session_state['medicines']:
                    st.session_state['medicines'].append(row)


    if 'medicines' in st.session_state:
        for i, row in enumerate (st.session_state['medicines']):
            st.write(f'• **Medicine {i+1} :** {row[1]}')

    if 'medicines' in st.session_state and len(st.session_state['medicines']) >= 2:
        if st.button('Check Interactions'):
            with st.spinner(text="This may take a moment..."):
                medicines, drugs = getData(st.session_state['medicines'])

                interaction = Interaction()
                output = interaction.check(drugs)
                if output:
                    translation = translate(medicines, output)
                    st.session_state.output = translation
                else:
                    st.write('Sorry, we could not find the information.\nThis does not mean that their is no interaction in the medicines.\nIt could be possible that the relevant data might not be in our database.\n You may try searching information about other medicines.')

        if st.session_state.output != '':
            if 'extradata' in st.session_state and len(st.session_state.extradata) == 0:
                drugstore = DrugStore()
                st.session_state.extradata = drugstore.fetch(st.session_state['medicines'])
            chat_input = st.chat_input(placeholder='Enter your query')
            if chat_input:
                st.session_state.chat_history.append(chat_input)
                st.session_state.chat_history.append(chat(chat_input, st.session_state.output))

            output_container = st.container(border=True)
            output_container.write(st.session_state.output)
    
        if len(st.session_state.chat_history) > 0:
            chat_container = st.container(border=True)
            for i, text in enumerate (st.session_state.chat_history):
                if i%2 == 0:
                    human = chat_container.chat_message('user')
                    human.write(text)
                else:
                    ai = chat_container.chat_message('assistant')
                    ai.write(text)


if __name__ == '__main__':
    main()