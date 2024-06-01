import streamlit as st
from PIL import Image
import google.generativeai as genai
from drug_interaction import Interaction
from translation import translate
import sqlite3

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

def main():
    if 'medicines' not in st.session_state:
        st.session_state['medicines'] = []

    st.title('Drug Interaction Checker')

    st.sidebar.title('Camera')
    picture = st.sidebar.camera_input('Camera')

    if picture is not None and 'medicines' in st.session_state and len(st.session_state['medicines']) < 2:
        image = Image.open(picture)
        model = genai.GenerativeModel(model_name='gemini-pro-vision', safety_settings=safety_settings)
        response = model.generate_content(['Just return only the name of medicine and nothing else',image])
        query_response = response.text.strip().split()[0]

        cursor.execute("SELECT * FROM medicine WHERE name LIKE ?", ('%' + query_response + '%',))
        names = [row[1] for row in cursor.fetchall()]
        names.insert(0, 'Select')
        name = st.sidebar.selectbox('Select Medicine:', names, placeholder='Select')
        if name != 'Select':
            cursor.execute("SELECT * FROM medicine WHERE name = ?", (name,))
            medicine = cursor.fetchone()
            st.session_state['medicines'].append(medicine)
            # st.rerun()

    if 'medicines' in st.session_state and len(st.session_state['medicines']) < 2:
        medicine_name = st.text_input('Enter Medicine Name', key='input_name')

        cursor.execute("SELECT * FROM medicine WHERE name LIKE ?", ('%' + medicine_name + '%',))
        names = [row[1] for row in cursor.fetchall()]
        names.insert(0, 'Select')

        if medicine_name:
            name = st.selectbox('Select Medicine:', names, key='medicine_name', placeholder='Select')
            if name != 'Select':
                cursor.execute("SELECT * FROM medicine WHERE name = ?", (name,))
                row = cursor.fetchone()
                st.session_state['medicines'].append(row)
                if len(st.session_state['medicines']) == 2:
                    st.rerun()            

    if 'medicines' in st.session_state:
        for row in st.session_state['medicines']:
            st.write(f'• {row[1]}')

    if 'medicines' in st.session_state and len(st.session_state['medicines']) == 2:
        if st.button('Check Interactions'):
            medicines, drugs = getData(st.session_state['medicines'])

            interaction = Interaction()
            output = interaction.check(drugs)
            if output:
                translation = translate(medicines, output)
                st.write(translation)
            else:
                st.write('Sorry, we could not find the information.')

if __name__ == '__main__':
    main()