import gradio as gr
import random
import time
import boto3
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.bedrock import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from promptManager import PromptManager
from RoleConversation import RoleConversation
import re
import os
bedrock_run = boto3.client(service_name='bedrock-runtime')
memory = ConversationBufferMemory()
modelId = "anthropic.claude-v2"
chatbotReady = 0
expessionDict = {'smile': './images/ts-smile.gif', 'sad': './images/ts-sad.gif', 'surprise': './images/ts-shocked.gif', 'serious':'./images/ts-serious.gif'}

raw_documents = TextLoader('./taylor-expression-words.txt').load()
text_splitter = CharacterTextSplitter(separator = "\n",chunk_size=1, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)
bed = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",region_name='us-east-1')
db = FAISS.from_documents(documents, bed)
pm = PromptManager("taylor")
#print("prompt:",pm.getPrompt())
ref_character = 'Taylor Swift'
ref_character_info = 'Taylor Alison Swift (born December 13, 1989) is an American singer-songwriter. Recognized for her songwriting, musical versatility, artistic reinventions, and influence on the music industry, she is a prominent cultural figure of the 21st century.'
player_name = 'Tom'
mt = RoleConversation(pm.getPrompt(),ref_character, ref_character_info, player_name,bedrock_run,"")


def respond(message, chat_history,imageurl):

    resp = mt.chat(message)
    print("type:",type(resp))
    print("resp:",resp)
    # get facial expression and show on chat window
    emotion = re.findall(r"\[.*?\]", resp)
    # print type of resp
    if (len(emotion) == 0):
        emotion = ["[surprise]"]
    emotion = emotion[0]
    
    # replace [] in string emotion
    emotion = emotion.replace("[","")
    emotion = emotion.replace("]","")
    print("emotion:",emotion)
    chat_history.append((message,resp))
    
    docs = db.similarity_search(emotion)
    emotion = docs[0].page_content
    imageurl = expessionDict[emotion]
    print(imageurl)
    return "", chat_history,imageurl
 
with gr.Blocks() as demo:
    imgBlock = gr.Image(value= "./images/ts-banner.jpg",height=300)
    chatbot = gr.Chatbot([],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, "images/ts-avatar.jpg"),
        height=500
        )
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])
    msg.submit(respond, [msg, chatbot,imgBlock], [msg,chatbot,imgBlock])

demo.launch()