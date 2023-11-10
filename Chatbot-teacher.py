
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
from RoleConversationMathTour import RoleConversationMathTour
import re
import os
bedrock_run = boto3.client(service_name='bedrock-runtime')
memory = ConversationBufferMemory()
modelId = "anthropic.claude-v2"
chatbotReady = 0
expessionDict = {'微笑': './images/t-smile2.gif', '假笑': './images/t-fakesmile.jpg', '开心': './images/t-smile.jpeg', '严肃':'./images/t-serious.webp'}
cl_llm = Bedrock(
    model_id=modelId,
    client=bedrock_run,
    model_kwargs={"max_tokens_to_sample": 1000},
)
conversation = ConversationChain(
    llm=cl_llm, verbose=True, memory=memory
)
raw_documents = TextLoader('./teacher-expression-words.txt').load()
text_splitter = CharacterTextSplitter(separator = "\n",chunk_size=1, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)
bed = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",region_name='us-east-1')
db = FAISS.from_documents(documents, bed)
pm = PromptManager("mathTeacher")
#print("prompt:",pm.getPrompt())
mt = RoleConversationMathTour(pm.getPrompt(), 'Assistant','','Human',bedrock_run)


def respond(message, chat_history,imageurl):

    resp = mt.chat(message)
    print("type:",type(resp))
    print("resp:",resp)
    # get facial expression and show on chat window
    emotion = re.findall(r"\[.*?\]", resp)
    # print type of resp


    if (len(emotion) == 0):
        emotion = ["[惊喜]"]
    emotion = emotion[0]
    chat_history.append((message,resp))
    
    docs = db.similarity_search(emotion)
    emotion = docs[0].page_content
    imageurl = expessionDict[emotion]
    print(imageurl)
    return "", chat_history,imageurl
 
with gr.Blocks() as demo:
    imgBlock = gr.Image(value= "./images/t-snp.gif")
    chatbot = gr.Chatbot([],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, (os.path.join(os.path.abspath(''), "snp.jpg"))),
        height = 500
        )
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])
    msg.submit(respond, [msg, chatbot,imgBlock], [msg,chatbot,imgBlock])

demo.launch()
