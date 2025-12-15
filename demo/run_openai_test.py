from openai import OpenAI
import os
client = OpenAI(api_key=os.environ.get('DSL_API_KEY'), base_url=os.environ.get('DSL_API_BASE'))
try:
    res = client.chat.completions.create(model=os.environ.get('DSL_MODEL'), messages=[{"role":"user","content":"今天天气如何"}], max_tokens=10)
    print('OK', res.choices[0].message.content)
except Exception as e:
    import traceback
    print('ERR', type(e).__name__)
    traceback.print_exc()
