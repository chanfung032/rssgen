import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sae
sae.add_vendor_dir('vendor')
from main import app as application
