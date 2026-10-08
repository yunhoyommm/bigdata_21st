import os
from gpt_functions import get_current_time, tools
from openai import OpenAI
from dotenv import load_dotenv
import json


load_dotenv()
api_key=os.getenv('OPENAI_API_KEY')
client=OpenAI(api_key=api_key)


def get_ai_response(messages, tools=None):
    response=client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        tools=tools,
    )
    return response


messages=[
    {'role':'system','content':'너는 사용자를 도와주는 상담사야'},
]


while True:
    user_input=input('사용자\t: ')
    if user_input =='exit':
        break
    messages.append({'role':'user','content':user_input})


    ai_response=get_ai_response(messages=messages, tools=tools)
    ai_message=ai_response.choices[0].message
    print(ai_message)


    # if → while : GPT가 함수를 또 요청하면 끝날 때까지 반복 처리
    while ai_message.tool_calls:    # 호출할 함수 존재하면 반복
        # 함수 호출 요청 메시지를 먼저 기록에 추가
        messages.append(ai_message)


        # tool_calls[0] 하나가 아니라 모든 요청 처리
        for tool_call in ai_message.tool_calls:
            tool_name=tool_call.function.name
            tool_call_id=tool_call.id
            arguments=json.loads(tool_call.function.arguments)


            if tool_name=='get_current_time':
                func_result=get_current_time(timezone=arguments['timezone'])
            else:  # 모르는 함수여도 결과는 반드시 돌려줘야 함
                func_result=f'알 수 없는 함수: {tool_name}'


            # role 'function'(구식) → 'tool'(표준), name 대신 tool_call_id로 연결
            messages.append({
                'role':'tool',
                'tool_call_id':tool_call_id,
                'content':func_result,
            })


        ai_response=get_ai_response(messages=messages, tools=tools)
        ai_message=ai_response.choices[0].message


    messages.append(ai_message)
    print(f'AI \t: {ai_message.content}')


print('프로그램 종료')
