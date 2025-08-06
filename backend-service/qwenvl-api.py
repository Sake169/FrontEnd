
# def nomal_chat():
#     url = "http://10.20.200.121:7556/v1/chat/completions"
#     data = {
#         'model' : 'Qwen2.5-VL-72B-Instruct',
#         'messages' : [
#             {
#                 'role' : 'system',
#                 'content' : '你是一个OCR引擎，请根据图片',
#             }
#         ]
#     }
#     response = requests.post(url, headers=headers, json=data)
#     return response.json()