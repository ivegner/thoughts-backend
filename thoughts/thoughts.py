
from google.appengine.ext import ndb
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import logging

import cloudstorage as gcs
from authtopus.api import Auth
from authtopus.cron import CleanupTokensHandler, CleanupUsersHandler
import webapp2	#for cron
import random	#for the index

package = 'Thoughts'	#package name for organization

bucketName = "thoughtsubmissions"

############### API Part Starts ##############################

class IOThought(messages.Message):
	text = messages.StringField(1, default = None)		#string param with ID 1
	img = messages.BytesField(2, default = None)
	
@endpoints.api(name='thoughts', version='v5')	#API declaration decorator
class ThoughtsApi(remote.Service):

	RETURN_THOUGHT_RESOURCE = endpoints.ResourceContainer(IOThought)	#declares that the input will be an IOThought object
	
	@endpoints.method(RETURN_THOUGHT_RESOURCE,IOThought,path="putThought",http_method='POST',name='putThought')
	#RETURN_THOUGHT_RESOURCE is what the method expects in the request, IOThought is the return, path is the url path to the method, 
	#http_method is the method (GET or POST) and the name is the name of the method in the API, which seems kinda redundant but is necessary

	def thought_put(self, request):
		submitMessage = putThought(request) #calls function that actually puts the text passed into the request in DB
		return submitMessage
		
	@endpoints.method(message_types.VoidMessage, IOThought, path='getThought', http_method='GET',name='getThought')
	#as above, only IOThought here is the response
	def thought_get(self, request):
		thought=getThought()
		return thought

############### Database Interaction Part Starts ###############

class Thought(ndb.Model):	#database entity class with a bunch of properties
	gcsObjectName = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)
	index = ndb.FloatProperty()	#random index for random outputting
	type = ndb.StringProperty()
	
def _put(content_type, payload):
	randIndex = random.random()
	filename = "/" + bucketName + "/" + str(randIndex)
	with gcs.open(filename, mode="w", content_type=content_type) as f:	#makes file in bucketName with name randIndex
		f.write(payload)
		f.close()
		dbEntry = Thought(gcsObjectName=filename, index = randIndex, type = content_type)
		dbEntry.put()
		return dbEntry
		
def putThought(request):
	checkIfVerified()
	if request.text != None:
		gcsObject = _put("text/plain", str(request.text))
	elif request.img != None:
		gcsObject = _put("image/png", str(request.img))
	else:
		return IOThought(text="No Submission Made")
	
	return IOThought(text="Submission made to " + gcsObject.gcsObjectName)

def getThought():
	checkIfVerified()
	randNum=random.random()
	thought = Thought.query().filter(Thought.index >= randNum).order(Thought.index) #documentation here is real shitty, just use this as a model. This builds a query
	dbEntry = thought.get()	#this runs the query and gets the first result.
	if dbEntry is None:		#if randNum is higher than any indices
		thought = Thought.query().filter(Thought.index <= randNum).order(Thought.index) #reverse 
		dbEntry = thought.get()
	gcsFilename = dbEntry.gcsObjectName	#get filename
	dbEntryType = dbEntry.type	#get type
	
	try:
		submission = getFromDB(gcsFilename, dbEntryType)
		if dbEntryType == "text/plain":
			return IOThought(text=submission)
		elif dbEntryType == "image/png":
			return IOThought(img=submission)
	except Exception as e: 
		return IOThought(text=e)
	
def getFromDB(filename, type):
	with gcs.open(filename) as f:
		r = f.read()
		f.close()
		return r
################### Authentication Part Starts ################

def checkIfVerified():
	user = Auth.get_current_user( verified_email_required=True ) #check if user is logged in and has a verified email
	if user is None:
		raise endpoints.UnauthorizedException( 'Invalid credentials' )

	
API = endpoints.api_server([Auth, ThoughtsApi], restricted = False) #passed into app.yaml to actually start the APIs

CRON = webapp2.WSGIApplication(
  [ ( '/cron/auth/cleanup-token/?', CleanupTokensHandler ),
    ( '/cron/auth/cleanup-users/?', CleanupUsersHandler ), ]
) #this is to clean up tokens.
