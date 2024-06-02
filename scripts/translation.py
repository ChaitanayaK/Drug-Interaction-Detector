import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def translate(medicines, drug_interactions):
    review_template = """
        you are very good advisor of medicines and their chemical compounds you have all the data of each medicines and their chemical compounds and you know the side effects of all chemical compounds. you can also predict the chemical reaction if we take two different chemical compounds or tablets at the same time. You can advise like a experienced doctor.

        we have Given below is list of medicines with their chemical compounds involved and their drug interactions with name of the drugs, severity of their effects on health of patient, description and extended description of effects,

        your task is create a short dicription about side effects of those medicine if we take them both at the same time. use bullet points to define the side effects of those medicines if we take it same time. You can use the chemical compounds for reference to generate the response for the user. always suggest user to do not take any kind of medicine at the same time always take medicine in at least 10 to 30 minutes gape. always suggest user to take medicine as per doctors prescription.

        i want you to explain the user in very simpler terms about the side effects the drugs might have. Use names of the medicines with their names of chemicals while responding. If multiple interactions are present, then partition each interaction from each other:\

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