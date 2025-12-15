import os
k = os.environ.get('DSL_API_KEY')
print('val=', k[:6] + '...' if k else 'None')
if k is None:
    print('missing')
else:
    try:
        k.encode('ascii')
        print('ascii-ok')
    except Exception as e:
        print('ascii-fail', type(e).__name__, str(e))
