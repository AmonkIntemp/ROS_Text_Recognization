import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/amonk/MyWorkSpace/test/py_cpp/install/publish_python_topic'
