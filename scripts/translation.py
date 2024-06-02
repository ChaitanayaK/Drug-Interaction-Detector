import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def translate(medicines, drug_interactions):
    review_template = """
        Given below is list of medicines with their chemical compounds involved and their drug interactions with name of the drugs, severity of their effects on health of patient, description and extended description of effects, i want you to explain the user in very simpler terms about the side effects the drugs might have. Use names of the medicines instead of the names of chemicals while responding. If multiple interactions are present, then partition each interaction from each other:\
        
        medicines : {medicines}\
        drug_interactions : {drug_interactions}\
    """

    prompt_template = ChatPromptTemplate.from_template(review_template)
    messages = prompt_template.format_messages(medicines=medicines, drug_interactions=drug_interactions)

    chat = ChatOpenAI(temperature=0.7, model='gpt-3.5-turbo')
    # llm = GoogleGenerativeAI(model='gemini-pro')
    # chat = llm.invoke(input=messages)
    response = chat(messages)

    return response.content

if __name__ == "__main__":
    translation = translate(['hi', 'hello'], ['no hi', 'no hello'])
    print(translation)