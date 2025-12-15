import sys
try:
    import requests
    print('requests OK', requests.__version__)
except Exception as e:
    print('requests missing', type(e).__name__, e)
