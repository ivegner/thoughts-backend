import random	#for the index
from google.appengine.ext import ndb
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import cloudstorage as gcs	#in the lib folder

package = 'Thoughts'	#package name for organization

bucketName = "thoughtsubmissions"

############### API Part Starts ##############################

class IOThought(messages.Message):
	text = messages.StringField(1, default = None)		#string param with ID 1
	testNum = messages.FloatField(2) #debug returns the number used as random point
	img = messages.BytesField(3, default = None)
	
@endpoints.api(name='thoughts', version='v4')	#API declaration decorator
class ThoughtsApi(remote.Service):

	RETURN_THOUGHT_RESOURCE = endpoints.ResourceContainer(IOThought)	#basically a thing that handles passed in URL parameters I think
	
	@endpoints.method(RETURN_THOUGHT_RESOURCE,IOThought,path="putThought",http_method='POST',name='put')
	#RETURN_THOUGHT_RESOURCE is what the method expects in the request, IOThought is the actual request, path is the url path to the method, 
	#http_method is the method (GET or POST) and the name is the name of the method in the API, which seems kinda redundant but is necessary
	def thought_put(self, request):
		debug = putThought(request.text, request.img) #calls function that actually puts the text passed into the request in DB
		return debug #debug?
		
	@endpoints.method(message_types.VoidMessage, IOThought, path='getThought', http_method='GET',name='getThought')
	#as above, only IOThought here is the response
	def thought_get(self, request):
		thought=getThought()
		return thought

############### Database Interaction Part Starts ###############

class Thought(ndb.Model):	#database entity class with a bunch of properties
	gcsObjectName = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)
	index = ndb.FloatProperty()	#random index for random outputting

def putThought(textIn, imgIn):
	randIndex = random.random()
	filename = "/" + bucketName + "/" + str(randIndex)
	if textIn != None:
		with gcs.open(filename, mode="w", content_type="text/plain") as f:	#makes file in bucketName with name randIndex
			f.write(str(textIn))
			dbEntry = Thought(gcsObjectName=filename, index = randIndex)
			dbEntry.put()
	elif imgIn != None:
		with gcs.open(filename, "w", content_type="image/png") as f:	#makes file in bucketName with name randIndex
			f.write(imgIn)
			dbEntry = Thought(gcsObjectName=filename, index = randIndex)
			dbEntry.put()
	else:
		return IOThought(text="No Submission Made")
	return IOThought(text="Submission Made")

def getThought():
	randNum=random.random()
	thought = Thought.query().filter(Thought.index >= randNum).order(Thought.index) #documentation here is real shitty, just use this as a model. This builds a query
	test = thought.get()	#this runs the query and gets the first result. use fetch($num) to get $num results
	if test is None:		#if randNum is higher than any indices
		thought = Thought.query().filter(Thought.index <= randNum).order(Thought.index) #reverse 
		test = getFromDB(thought.get())
		return IOThought(text=test, testNum=randNum)
	else:
		print "\n\nThe query was: " + str(thought) #displays after server is shut down
		return IOThought(text=test.text, testNum=randNum)	#response
def getFromDB(thoughtQueryResult):
	return thoughtQueryResult.text
	
APPLICATION = endpoints.api_server([ThoughtsApi]) #passed into app.yaml to actually start the API 
