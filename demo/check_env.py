import os
print('provider=', os.getenv('DSL_PROVIDER'))
print('api_base=', os.getenv('DSL_API_BASE'))
key = os.getenv('DSL_API_KEY')
if key:
    print('api_key_prefix=', key[:6] + '...')
else:
    print('api_key=missing')
print('model=', os.getenv('DSL_MODEL'))
