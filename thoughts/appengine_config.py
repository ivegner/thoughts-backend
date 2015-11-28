import os
import sys

ENDPOINTS_PROJECT_DIR = os.path.join( os.path.dirname( __file__ ),
                                      'libraries/endpoints_proto_datastore' )
AUTHTOPUS_PROJECT_DIR = os.path.join( os.path.dirname( __file__ ),
                                      'libraries/authtopus' )
GCS_PROJECT_DIR = os.path.join( os.path.dirname( __file__ ),
                                      'libraries/cloudstorage' )

sys.path.extend( [ ENDPOINTS_PROJECT_DIR, AUTHTOPUS_PROJECT_DIR,
				   GCS_PROJECT_DIR,
                  ] )