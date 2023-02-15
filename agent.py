import spotipy
from spotipy.oauth2 import SpotifyOAuth
from difflib import SequenceMatcher
import subprocess
import time
import os

class spotipyAgent:
	def __init__(self):
		scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-playback-position user-top-read user-read-recently-played user-library-modify user-library-read"

		self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
																												client_id='d80adeecdecf408e90a2dd984dd02af2',
																												client_secret='e09729dd87b648a5a0547125603d68b8',
																												redirect_uri='http://localhost:8888/callback'))

		try:
			if(not self.sp.currently_playing()['is_playing']):
				self.sp.start_playback()
		except:
			pass
	
	def similar(self, a, b):
		return SequenceMatcher(None, a, b).ratio()
		
	def trim_track(self, test_str):
		  ret = ''
		  skip1c = 0
		  skip2c = 0
		  for i in test_str:
		      if i == '[':
		          skip1c += 1
		      elif i == '(':
		          skip2c += 1
		      elif i == ']' and skip1c > 0:
		          skip1c -= 1
		      elif i == ')'and skip2c > 0:
		          skip2c -= 1
		      elif skip1c == 0 and skip2c == 0:
		          ret += i
		  return ret
		
		
	def searchTrack(self, name, artist):
		results = self.sp.search(q='track:' + name, type='track', limit=10, offset=0)
		items = results['tracks']['items']
		found = False
		os = 0
		while not found:
			for i in range(len(items)):
					track = items[i]
					art = track['artists'][0]['name']
					tra = self.trim_track(track['name'])
					if(self.similar(artist, art) > 0.5 and self.similar(name, tra) > 0.5):
						print(tra, 'by', art)
						found = True
						self.sp.add_to_queue(uri=track['uri'])
						self.skip()
						return 1
			os += 10
			results = self.sp.search(q='track:' + name, type='track', limit=10, offset=os)
			items = results['tracks']['items']

	def searchPlaylist(self, name, owner):
		results = self.sp.search(q=name, type='playlist')
		items = results['playlists']['items']
		for i in range(len(items)):
			playlist = items[i]
			if(self.similar(name, playlist['name']) > 0.5 and self.similar(owner, playlist['owner']['display_name']) > 0.5):
				print(playlist['name'], 'by', playlist['owner']['display_name'], '(URI:', playlist['uri'] + ")")
				self.sp.start_playback(context_uri=playlist['uri'])
				return 1
				
	def searchAlbum(self, name, artist):
		results = self.sp.search(q='album:' + name, type='album')
		items = results['albums']['items']
		for i in range(len(items)):
			album = items[i]
			if(self.similar(name, album['name']) > 0.5 and self.similar(artist, album['artists'][0]['name']) > 0.5):
				print(album['name'], 'by', album['artists'][0]['name'])
				self.sp.start_playback(context_uri=album['uri'])
				return 1
				
				
	def playLikedSongs(self):
		new_songs = self.sp.current_user_saved_tracks(limit=50)['items']
		liked_songs = new_songs
		uris = []
		os = 0
		while len(new_songs) > 0:
			os += 50
			new_songs = self.sp.current_user_saved_tracks(limit=50, offset=os)['items']
			liked_songs.extend(new_songs)
		for i in range(len(liked_songs)):
			uris.append(liked_songs[i]['track']['uri'])
			#print(liked_songs[i]['track']['name'], 'by', liked_songs[i]['track']['artists'][0]['name'])
		self.sp.start_playback(uris=uris)
		
	def toggleShuffle(self):
		if self.sp.current_playback()['shuffle_state']:
			self.sp.shuffle(False)
		else:
			self.sp.shuffle(True)
			
	def toggleRepeat(self):
		if self.sp.current_playback()['repeat_state'] == 'off':
			self.sp.repeat('track')
		elif self.sp.current_playback()['repeat_state'] == 'track':
			self.sp.repeat('off')
	
	def skip(self):
		self.sp.next_track()
		
	def previous(self):
		try:
			self.sp.previous_track()
		except:
			pass
	def togglePlayback(self):
		try:
			if self.sp.current_playback()['is_playing']:
				self.sp.pause_playback()
			else:
				self.sp.start_playback()
		except:
			pass
	def setVolumePercent(self, percent):
		try:
			self.sp.volume(percent)
		except:
			pass
			
	def restartTrack(self):
		try:
			self.sp.seek_track(0)
		except:
			pass
	
			
def main():
	user_input = ''
	agent = spotipyAgent()
	print("Hello! Welcome to Spotipy Agent, please select from a command below.")
	error = None
	while True:
		os.system('clear')
		try:
			print("Hello! Welcome to Spotipy Agent, please select from a command below.")
			print("\n[#] (argument1) (argument2) ... Command Name")
			print("[T] (Track Title) by (Artist Name) Search for Track")
			print("[P] (Playlist Name) by (Playlist Owner) Search for Public PLaylist")
			print("[A] (Album Name) by (Artist Name) Search for Album")
			print("[L] Play your liked songs")
			print("[S] Toggle Shuffle")
			print("[R] Toggle Repeat")
			print("[>] Skip Song")
			print("[<] Previous Song")
			print("[<<] Restart current Song")
			print("[X] Pause or Play Current Song")
			print("[V] (%) Set volume to percent")
			print("[Q] Quit")
			
			if error is not None:
				print("\n" + error)
				error = None

			user_input = input("\nCommand: ")
			
			split = user_input.split()
			if split[0] == "T" or split[0] == "t":
				try:
					by_index = split.index("by")
					track_name = ' '.join(split[1:by_index])
					artist_name = ' '.join(split[by_index:])
					agent.searchTrack(track_name, artist_name)
				except:
					error = "Error: check that you've entered your command in the format 'T (Song Name) by (Artist Name)!"
					continue
			elif split[0] == "P" or split[0] == "p":
				try:
					by_index = split.index("by")
					playlist_name = ' '.join(split[1:by_index])
					owner_name = ' '.join(split[by_index:])
					agent.searchPlaylist(playlist_name, owner_name)
				except:
					error = "Error: check that you've entered your command in the format 'P (Playlist Name) by (Owner Name)!"
					continue
					
			elif split[0] == "A" or split[0] == "a":
				try:
					by_index = split.index("by")
					album_name = ' '.join(split[1:by_index])
					artist_name = ' '.join(split[by_index:])
					agent.searchAlbum(album_name, artist_name)
				except:
					error = "Error: check that you've entered your command in the format 'A (Album Name) by (Artist Name)!"
					continue
					
			elif split[0] == "L" or split[0] == "l":
				try:
					agent.playLikedSongs()
				except:
					error = "Error: check that you've entered the command correctly!"
					continue
					
			elif split[0] == "S" or split[0] == "s":
				try:
					agent.toggleShufle()
				except:
					error = "Error: check that you've entered the command correctly!"
					continue
					
			elif split[0] == "X" or split[0] == "x":
				try:
					agent.togglePlayback()
				except:
					error = "Error: check that you've entered the command correctly!"
					continue
			
			elif split[0] == "R" or split[0] == "r":
				try:
					agent.toggleRepeat()
				except:
					error = "Error: check that you've entered the command correctly!"
					continue
					
			elif split[0] == ">":
				try:
					agent.skip()
				except:
					error = "Error: check that you've entered the command correctly!"
					continue
					
			elif split[0] == "<":
				try:
					agent.previous()
				except:
					error = "Error: check that you've entered the command correctly!"
					continue
					
			elif split[0] == "<<":
					agent.restartTrack()
					
			elif split[0] == "V" or split[0] == "v":
				try:
					agent.setVolumePercent(int(split[1]))
				except:
					error = "Error: check that you've a whole number after the command!"
					continue
			elif split[0] == "Q" or split[0] == "q":
				os.system('clear')
				return 0
					
			else:
				error = "Error: check that you've entered the command correctly!"
		except KeyboardInterrupt:
			os.system('clear')
			return 0

if __name__ == '__main__':
		main()
