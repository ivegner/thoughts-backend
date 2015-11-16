from google.appengine.api import users
from google.appengine.ext import ndb
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

package = 'Thoughts'

class ThoughtRequest(messages.Message):
	text = messages.StringField(1)

@endpoints.api(name='thoughts', version='v1')
class ThoughtsApi(remote.Service):

	THOUGHT_RESOURCE = endpoints.ResourceContainer(ThoughtRequest)
	@endpoints.method(THOUGHT_RESOURCE,ThoughtRequest,path="thoughtput",http_method='POST',name='put')
	def thought_put(self, request):
		putThought(request.text)
		return ThoughtRequest(text=request.text)
	
class Thought(ndb.Model):
	text = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)

def putThought(textIn):
	thought = Thought(text=textIn)
	thought.put()
	return thought
	
APPLICATION = endpoints.api_server([ThoughtsApi])
