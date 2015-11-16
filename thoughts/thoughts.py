from google.appengine.api import users
from google.appengine.ext import ndb
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

package = 'Thoughts'	#package name for organization

class ThoughtRequest(messages.Message):
	text = messages.StringField(1)	#only has one parameter which is a string with ID 1

@endpoints.api(name='thoughts', version='v1')	#API declaration decorator
class ThoughtsApi(remote.Service):

	THOUGHT_RESOURCE = endpoints.ResourceContainer(ThoughtRequest)	#basically a thing that handles passed in URL parameters I think
	@endpoints.method(THOUGHT_RESOURCE,ThoughtRequest,path="thoughtput",http_method='POST',name='put') #We've got no clue what this does
	def thought_put(self, request):
		putThought(request.text) #calls function that actually puts the text passed into the request in DB
		return ThoughtRequest(text=request.text)	#shitty debug

############### Database Interaction Part Starts ###############

class Thought(ndb.Model):	#database entity class with a bunch of properties
	text = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)

def putThought(textIn):
	thought = Thought(text=textIn)
	thought.put()
	return thought
	
APPLICATION = endpoints.api_server([ThoughtsApi]) #passed into app.yaml to actually start the API 
