# import logging
# import spotify
# logging.basicConfig(level=logging.DEBUG)

# config = spotify.Config()
# config.user_agent = 'Playlist Manager'
# session = spotify.Session(config=config)
# session.login('anuteja','symphoniks', True)

# session.process_events()
# while session.connection.state != spotify.ConnectionState.LOGGED_IN:
#     session.process_events()

# print 'Session State' 
# print session.connection.state

# toplist = session.get_toplist(
#      type=spotify.ToplistType.TRACKS, region='US')
# toplist.load()
# len(toplist.tracks)
# len(toplist.artists)
# print toplist.tracks[0]


# !/usr/bin/env python

# """
# This is an example of playing music from Spotify using pyspotify.
# The example use the :class:`spotify.AlsaSink`, and will thus only work on
# systems with an ALSA sound subsystem, which means most Linux systems.
# You can either run this file directly without arguments to play a default
# track::
#     python play_track.py
# Or, give the script a Spotify track URI to play::
#     python play_track.py spotify:track:3iFjScPoAC21CT5cbAFZ7b
# """

from __future__ import unicode_literals

import sys
import threading
import logging
import random
import spotify
import time
import json

def playtrack(tracks,username,password):


	logging.basicConfig(level=logging.DEBUG)
	config = spotify.Config()
	session = spotify.Session(config=config)

	#print session

	# Assuming a spotify_appkey.key in the current dir
	

	session.login(username, password, False)

	session.process_events()
	
	while session.connection.state != spotify.ConnectionState.LOGGED_IN:
    		session.process_events()
		#print session.connection.state

	# Connect an audio sink
	audio = spotify.AlsaSink(session)

	# Events for coordination
	logged_in = threading.Event()
	end_of_track = threading.Event()

	def on_connection_state_updated(session):
   	 	if session.connection.state is spotify.ConnectionState.LOGGED_IN:
       		 logged_in.set()

	def on_end_of_track(self):
    		end_of_track.set()


	# Register event listeners
	session.on( spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
	session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)
	# Play a track
	#loop of tracks
	for i,track_uri in enumerate(tracks):
		if i <4:
			#track_uri=random.choice(tracks)
			#print 'in for'
			track = session.get_track(track_uri).load()
			session.player.load(track)
			session.player.play()
			if i!=3:
				time.sleep(track.duration/12000)
				#print 'hi'
			else:
				session.player.play(0)
				break
	audio.off()
	#session.logout()	

	#session.forget_me()	
	#time.sleep(2)
	# Wait for playback to complettrackse or Ctrl+C
	#try:
 	 #  while not end_of_track.wait(0.1):
    	  #  pass
	#except KeyboardInterrupt:
  	 # pass
def spotify_stub(username):
	random.seed()
	#read decoded json files
	new_dict={}
	f1=open('data.txt','r')
	out=f1.readlines()
	f1.close()
	for line in out:
		decoded_data=json.loads(line)
		new_dict[decoded_data['name']]=decoded_data
	#print new_dict
	if username not in new_dict.keys():
		return 0
	tracks=new_dict[username]['tracks']
	username=new_dict[username]['name']
	password=new_dict[username]['password']
	playtrack(tracks,username,password)
	return 1
if __name__=="__main__":
	spotify_stub('anuteja')
	#spotify_stub('anuteja')
	#playtrack(['spotify:track:6xZtSE6xaBxmRozKA0F6TA','spotify:track:2Foc5Q5nqNiosCNqttzHof'],'anuteja','symphoniks')
