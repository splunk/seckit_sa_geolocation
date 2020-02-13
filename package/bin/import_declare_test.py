try:
    import http.client
    import queue
    import copyreg
except:
    pass

import os.path as op
import sys
sys.path.insert(0, op.join(op.dirname(op.abspath(__file__)), 'splunktalib'))
