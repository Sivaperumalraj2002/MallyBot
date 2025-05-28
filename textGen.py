from ollama import chat
from ollama import ChatResponse

def llmOut(model,input):

    response: ChatResponse = chat(model=model, messages=[
    {
        'role': 'user',
        'content': input,
    },
    ])
    return response.message.content
    # print(response['message']['content'])
    # # or access fields directly from the response object
    # print(response.message.content)

def llmStream(model,input):
    stream = chat(
    model=model,
    messages=[{'role': 'user', 'content': input}],
    stream=True,
    )
    return stream
    # for chunk in stream:
    #     print(chunk['message']['content'], end='', flush=True)
