import logging
import json
import spotify
import codecs
import os

username='anuteja'#'tegjyotsingh'
password='symphoniks'#'werunited'

logging.basicConfig(level=logging.DEBUG)
config = spotify.Config()
config.user_agent = 'Playlist Manager'
session = spotify.Session(config=config)
session.login(username,password, True)

session.process_events()
while session.connection.state != spotify.ConnectionState.LOGGED_IN:
    print session.connection.state
    session.process_events()
print session.connection.state
#p=session.search('e')
#p.load()
#p = session.playlist_container[0]
p=session.get_starred()
#p=session.get_playlist('spotify:user:anuteja:playlist:6ksaskR08sDR57kCtLI3W1')
p.load()
print p
print p.tracks


#playlist = session.playlist_container

#print len(session.playlist_container)
#playlist= session.playlist_container[0]
#x= playlist.load()
#print x, playlist.name
#print search
#print search.tracks

list1=list(p.tracks)
print p.tracks
print list1
for i in list1:
	print i
#print search.tracks[0].name

#store the file dump in a json file
field={}
field['name']= username
field['password']=password
list2=[]
for i in list1:
	list2.append(str(i)[8:-2])
field['tracks']= list2
if os.path.isfile('data.txt'):
	f1=open('data.txt','r')
	out=f1.readlines()
	f1.close()
	encoded_text=''
	for line in out:
		decoded_data=json.loads(line)
		print decoded_data
		print decoded_data		
		if decoded_data[u'name']!=username:
			encoded_text=encoded_text+line
		
	encoded_text=encoded_text+json.dumps(field)
	f1=open('data.txt','w')
	f1.write(encoded_text)
	f1.close()
	print "in if"
with codecs.open('data.txt','w') as outfile:
	json.dump(field, outfile)
#print type(field)
session.logout()
print 'logout'

