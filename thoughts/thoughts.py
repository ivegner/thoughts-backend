import random
from google.appengine.api import users
from google.appengine.ext import ndb
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

package = 'Thoughts'	#package name for organization

class ThoughtText(messages.Message):
	text = messages.StringField(1)		#only has one parameter which is a string with ID 1
	testNum = messages.FloatField(2)	#debug returns the number used as random point
	
@endpoints.api(name='thoughts', version='v3')	#API declaration decorator
class ThoughtsApi(remote.Service):

	THOUGHT_TEXT_RESOURCE = endpoints.ResourceContainer(ThoughtText)	#basically a thing that handles passed in URL parameters I think
	
	@endpoints.method(THOUGHT_TEXT_RESOURCE,ThoughtText,path="thoughtput",http_method='POST',name='put')
	#THOUGHT_TEXT_RESOURCE is what the method expects in the request, ThoughtText is the actual request, path is the url path to the method, 
	#http_method is the method (GET or POST) and the name is the name of the method in the API, which seems kinda redundant but is necessary
	def thought_put(self, request):
		putThought(request.text) #calls function that actually puts the text passed into the request in DB
		return ThoughtText(text=request.text) #debug?
		
	@endpoints.method(message_types.VoidMessage, ThoughtText, path='getThought', http_method='GET',name='getThought')
	#as above, only ThoughtText here is the response
	def thought_get(self, request):
		thought=getThought()
		return thought

############### Database Interaction Part Starts ###############

class Thought(ndb.Model):	#database entity class with a bunch of properties
	text = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)
	index = ndb.FloatProperty()	#random index for random outputting

def putThought(textIn):
	thought = Thought(text=textIn, index=random.random())
	thought.put()
	return thought

def getThought():
	randNum=random.random()
	thought = Thought.query().filter(Thought.index >= randNum).order(Thought.index) #documentation here is real shitty, just use this as a model. This builds a query
	test = thought.get()	#this runs the query and gets the first result. use fetch($num) to get $num results
	if test is None:		#if randNum is higher than any indices
		thought = Thought.query().filter(Thought.index <= randNum).order(Thought.index) #reverse 
		test = thought.get()
		return ThoughtText(text=test.text, testNum=randNum)
	else:
		print "\n\nThe query was: " + str(thought) #displays after server is shut down
		return ThoughtText(text=test.text, testNum=randNum)	#response
	
APPLICATION = endpoints.api_server([ThoughtsApi]) #passed into app.yaml to actually start the API 
