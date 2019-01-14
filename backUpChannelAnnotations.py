import requests,json,sys,re,os,time
import threading
from datetime import datetime


from VideoIDHelper import *
from collections import deque
from bs4 import BeautifulSoup


def reportPlaylistProgress():
	global t
	print("{} videos have been read from the playlist...".format(len(p)))
	t=threading.Timer(10.0, reportPlaylistProgress)
	t.start()

def reportProgress():
	global t
	if toGather != 1:
		print("Processed {}/{} videos.".format(i,toGather))
	else:
		print("Processed 0/1 video.")
	t=threading.Timer(10.0, reportProgress)
	t.start()

def reportGathering():
	global t
	print("{} links gathered so far...".format(len(m)))
	t=threading.Timer(10.0, reportGathering)
	t.start()

def reportMode1():
	global t
	print("Backed Up {}/{}".format(successes,len(m)))
	t=threading.Timer(10.0, reportMode1)
	t.start()

#Globals
m={}
q=deque()
p=[]
i=0
toGather=0
t = threading.Timer(10.0, reportProgress, [i,toGather])

hardLimitSet=False
hardLimit = 0

channelLock=False
channel=""
invld={}

mode1 = False
successes=0
def makeRequest(partialURL,parameter,ID):
	pars = {"parameter" : ID}
	return requests.get(partialURL, params=pars)
def makeRequestWithoutParameter(URL):
	return requests.get(URL)

def backUpAnnotations(ID):
	return makeRequestWithoutParameter("http://web.archive.org/save/https://www.youtube.com/annotations_invideo?video_id={}".format(ID))
def snapShotPage(ID):
	return makeRequest("http://web.archive.org/save/https://www.youtube.com/watch","v",ID)
def snapShotOfPlaylist(ID):
	return makeRequestWithoutParameter("http://web.archive.org/save/https://www.youtube.com/playlist?list={}".format(ID))

def annotationsBackedUp(ID):
	return makeRequestWithoutParameter("http://archive.org/wayback/available?url=https://www.youtube.com/annotations_invideo?video_id={}".format(ID))
def snapShotTaken(ID):
	return makeRequestWithoutParameter("http://archive.org/wayback/available?url=https://www.youtube.com/watch?v={}".format(ID))

def snapShotOfPlaylistTaken(ID):
	return makeRequestWithoutParameter("http://archive.org/wayback/available?url=https://www.youtube.com/playlist?list={}".format(ID))


def main():
	global i,toGather,p,playListSweep,successes,mode1
	first = True
	argument = ""
	print( "Hello today is: " + str(datetime.now().month) + "/" + str(datetime.now().day))
	#print( "Remember that we have time until: " + "1/15" + "for Annotations and Credits; and until " + "1/31" +" for Episodes (presumably PST 0:00) " )
	print( "Remember that we have time until: " + "1/15" + " for the Annotations (presumably PST 0:00) " )
	while first or argument == "":
		#argument ="horse"
		argument = input("Type in the URL of a channel whose videos you'd like to back up or a video from said channel:\n")

		if argument == "":
			print("Program Terminated")
			break

		else:
			uPLink = ""
			#Assume channel ID:
			if not channelIDInvalid(channelExtractor(argument)):
				tid = channelExtractor(argument)
				#print ("{} is a channel".format(tid))
				#For a channel use as is
				uPLink = "https://www.youtube.com/playlist?list={}".format("UU"+tid[2:])
			#Assume user ID:
			elif not channelUnavailable(userExtractor(argument)):
				tid = userExtractor(argument)
				#print ("{} is a user".format(tid))
				#Get the channel id of the user
				userPage=""
				Break=False
				while True:
					r = requests.get("https://www.youtube.com/user/{}/videos".format(tid))
					if r.status_code != 200:
						print("An error occured while trying to load the channel...")
						print(r.status_code)
						action=""
						while action!='r' and action!='a'  :
							action = input("Type r to retry or a to abort:\n")
							action = action.rstrip().strip()
						if action == 'r':
							continue
						elif action == 'a':
							Break=True
							break

					userPage = r.text
					break
				if Break: 
					continue
				lazySearch = userPage.find('/channel/UC')
				uP=userPage[lazySearch+9:userPage.find('"',lazySearch+10)]
				#print("uP")
				#print(uP)
				uPLink = "https://www.youtube.com/playlist?list={}".format("UU"+uP[2:])
			#Assume video ID:
			elif not videoUnavailable(idExtractor(argument)):
				tid = idExtractor(argument)
				#print ("{} is a video".format(tid))
				#Get the channel id from the video
				pageHtml=""
				Break=False
				while True:
					r = requests.get("https://www.youtube.com/watch?v={}".format(tid))
					if r.status_code != 200:
						print("An error occured while trying to load the channel...")
						print(r.status_code)
						action=""
						while action!='r' and action!='a'  :
							action = input("Type r to retry or a to abort:\n")
							action = action.rstrip().strip()
						if action == 'r':
							continue
						elif action == 'a':
							Break=True
							break

					pageHtml = r.text
					break
				if Break: 
					continue
				lazySearch = pageHtml.find('/channel/UC')
				uP=pageHtml[lazySearch+9:pageHtml.find('"',lazySearch+10)]
				#print("uP")
				#print(uP)
				uPLink = "https://www.youtube.com/playlist?list={}".format("UU"+uP[2:])
			#Error
			else :
				print ("Unable to load channel.")
				continue
			
			#print(uPLink)
			#return

			"""
			if isChannelId(argument):
				#Channel ID
				uPLink = "https://www.youtube.com/playlist?list={}".format("UU"+getChannelId(argument)[2:])
			else:
				#Maybe User ID or maybe Video URL/ID
				print("User ID or Video URL/ID")
				pass
				channel = channelExtractor(argument)
				#print(channel)
				userPage=""
				Break=False
				while True:
					print(channel)
					r = requests.get("https://www.youtube.com/user/{}/videos".format(channel))
					if r.status_code != 200:
						print("An error occured while trying to load the channel...")
						print(r.status_code)
						action=""
						while action!='r' and action!='a'  :
							action = input("Type r to retry or a to abort:\n")
							action = action.rstrip().strip()
						if action == 'r':
							continue
						elif action == 'a':
							Break=True
							break

					userPage = r.text
					break
				if Break: 
					continue
				#print("https://www.youtube.com/user/{}/videos".format(channel))
				#with open("serious-bug2.html","w") as f:
				#	f.write(userPage)
				#userSoup = BeautifulSoup(userPage,"html.parser")
				#print(userPage.find("play-all-icon-btn"))
				#uP = userSoup.find("a", class_="play-all-icon-btn")
				lazySearch = userPage.find('/channel/UC')
				uP=userPage[lazySearch+9:userPage.find('"',lazySearch+10)]
				#print("uP")
				#print(uP)
				uPLink = "https://www.youtube.com/playlist?list={}".format("UU"+uP[2:])
			"""
			#uPLink = "https://www.youtube.com{}".format(uP.get('href'))
			
			print("getting upload playlist...")

			lID = playlistIdExtractor(uPLink)

			#print(lID)
			#return

			r=snapShotOfPlaylistTaken(lID)
			if 'closest' in r.json()["archived_snapshots"]:
				print('I have a hunch that this playlist has been scanned.')
				isY = input('But if you want to make sure that all sublinks have also been saved type y\n')
				if isY.rstrip().strip() != "y":
					continue

			#Go to the playlist page using teh id
			reportPlaylistProgress()
			err = analyzePlaylist(lID)
			t.cancel()
			if err==1:
				continue
			else:
				print("Video Count in Playlist: {}".format(len(p)))


			print("First Upload Date: {}".format(getVideoDate(p[len(p)-1])))
			print("Latest Upload Date: {}".format(getVideoDate(p[0])))

			print("****************************************************")
			
			print("Optionally you may specify the interval of the videos to be scanned")
			print("as two dates in YYYY-MM-DD format on a single line.")
			print("Otherwise hit enter")
			print("By default the start date will be set to 2005-04-23")
			print("And the end date to 2017-05-03 (the day after annotation editing was removed)")
			#Query date
			#print(getVideoDate(p[0]))
			#Format is year-month-day
			#4-2-2

			#index=dateSearch(dateConvert("2017-05-10"),p,0,len(p)-1,False)
			sdate=datetime(2005,4,23)
			edate=datetime(2017,5,3)
			#sdate=datetime(getVideoDate(p[len(p)-1])

			while True:
				inp = input()
				inp = inp.strip().rstrip()
				
				if inp=="":
					break

				elif not isTwoDates(inp):
					print("Unrecognized input")
					continue
				try:
					sC,eC = getTwoDates(inp)
					#print (sC,eC)
					d1 = dateConvert(sC)
					d2 = dateConvert(eC)
					#print (d1,d2)
					if not validTwoDates(d1,d2):
						print("Invalid interval, make sure you wrote the start date first!")
						continue
					print("Adjusting Interval...")
					sdate = max(d1,sdate)
					edate = min(d2,edate)
					break
				except:
					print("Unable to convert input to date format")
					continue

			#y,m,d = map( int, sC.split('-') )
			
			#y,m,d = map( int, sC.split('-') )
			
			#indexS = 0
			#if sdate != getVideoDate(p[0]):
			indexS=dateSearch(edate,p,0,len(p)-1,False)

			#Special Case:
			#If date is 4 23 2005 it's len(p)-1
			indexE=len(p)-1
			if edate != datetime(2005,4,23):
				indexE=dateSearch(sdate,p,0,len(p)-1,True)

			#print(indexS,indexE)
			#print("error handle index later:")

			#print(index)
			#return
			#sdate = 0
			#edate = len(p)+1

			"""
			while True:
				print("Type the index of the video you want to start from and the index of the last one you'd like to include.")
				print("Or simply press enter without typing anything to scan the full playlist...")
				intervalInput = input()
				if contains2Numbers(intervalInput):
					start,end = get2Numbers(intervalInput)
					if validInterval(start,end,len(p)):
						end+=1
						break
					else:
						print("Please specify a valid interval!")
				elif intervalInput=="":
					start = 0
					end = len(p)+1
					break
				else:
					print("Please type only two numbers representing indices in the playlist if you wish to specify an interval OR press enter to skip.")

			#In the case of a playlist sweep ALSO take a snapshot of the playlist
			
			if start == 0 and end == len(p)+1:
				playListSweep = True
			"""
			playListSweep = False
			if indexS == 0 and indexE == len(p)-1:
				playListSweep = True
			p = p[indexS:indexE+1]

			#print(indexS,indexE)
			#print(p)

			#Adjust hard limit so it goes beyond the playlist
			hardLimitSet = False 
			#err = setHardLimit()
			#if err ==1:
			#continue
			setHardLimit()

			channelLock = False 
			err = setChannelLock()
			if err ==1:
				continue

			mode1 = False 
			setMode()


			#vID = idExtractor(argument)
			#print("vID: {}".format(vID))
			#r = annotationsBackedUp(vID)
			#if 'closest' in r.json()["archived_snapshots"]:
			#	print('That link seems to have been saved.')
			#	isY = input('But if you want to make sure that all sublinks have also been saved type y\n')
			#	if isY.rstrip().strip() != "y":
			#		continue

			#gather videos linked to from this playlist
			#print (p)
			#continue

			Break = False
			while True:
				err = activateChannelLock(idExtractor(p[0]))
				if err == 1:
					print("an error occured while trying to access the channel")
					action=""
					while action!='r' and action!='a':
						action = input("Type r to retry or a to abort:\n")
						action = action.rstrip().strip()
					if action == 'r':
						continue
					if action == 'a':
						Break = True
						break
				break
			if Break:
				continue

			err = gatherStartingFromPlaylistVids()
			t.cancel()
			if err == 1:
				Break=True
				continue

			#mode 2
				toGather = len(m)
				print("Discovered {} videos...".format(toGather))

				i=0
				successes=0
				Break=False
				reportProgress()
				#t.start()
				for ID in m:
					while True:
						code = backUp(ID)
						if code == 1:
							t.cancel()
							# #19 is problematic
							print("https://www.youtube.com/watch?v={} wasn't saved properly".format(ID))
							action=""
							while action!='r' and action!='a' and action!='i':
								action = input("Type r to retry,i to ignore or a to abort:\n")
								action = action.rstrip().strip()
							if action == 'r':
								reportProgress()
								continue
							if action == 'i':
								reportProgress()
								i+=1
								break
							if action == 'a':
								Break=True
								playListSweep = False
								i+=1
								break
						elif code == 2:
							print("https://www.youtube.com/watch?v={} is unavailable, skipping...".format(ID))
							i+=1
							break
						else:
							m[ID]=True
							i+=1
							successes+=1
							break
					if Break:
						break
				t.cancel()
				if toGather == 1:
					print("{}/{} is now backed up!".format(successes,toGather))
				print("{}/{} are now backed up!".format(successes,toGather))
			
			#mode 1
			else:
				print("DONE!")
				print("{}/{} backed up!".format(successes,len(m)))


			if playListSweep:
				snapShotOfPlaylist(lID)
				print("Took a snapshot of the playlist to let people know its been fully scanned.")
	
def gatherStartingFromPlaylistVids():
	global m,q,invld,mode1,successes,playListSweep
	Break=False
	successes=0

	m={}
	invld={}
	q=deque()
	
	for video in p:
		q.append(video)
		m[video] = False

	if not mode1:
		print("Gathering links... This might take quite a while...")
		print("If you're having second thoughts close and re-open the program to switch to mode 1!")
		reportGathering()
	else:
		print("Starting up...")
		reportMode1()

	while len(q) != 0 and not (hardLimitSet and len(m) >= hardLimit):
		head = q.pop()
		code = gather(head)
		#check for errors
		if code == 1:
			print("An error occured while trying to gather the videos...")
			action=""
			t.cancel()
			while action!='r' and action!='a'  :
				action = input("Type r to retry or a to abort:\n")
				action = action.rstrip().strip()
			if action == 'r':
				#reset this
				if mode1: reportMode1()
				else: reportGathering()
				q.append(head)
				continue
			if action == 'a':
				return 1
		#Mode 1
		elif mode1:
			while True:
				code = backUp(head)
				if code == 1:
					t.cancel()
					print("https://www.youtube.com/watch?v={} wasn't saved properly".format(head))
					action=""
					while action!='r' and action!='a' and action!='i':
						action = input("Type r to retry, i to ignore or a to abort:\n")
						action = action.rstrip().strip()
					if action == 'r':
						reportMode1()
						continue
					if action == 'i':
						reportMode1()
						#i+=1
						break
					if action == 'a':
						Break=True
						playListSweep = False
						#i+=1
						break
				elif code == 2:
					print("https://www.youtube.com/watch?v={} is unavailable, skipping...".format(head))
					#i+=1
					break
				else:
					m[head]=True
					#i+=1
					successes+=1
					break
			if Break:
				break
		#q.pop()
	if (hardLimitSet and len(m) >= hardLimit):
		print("HARDLIMIT of {} reached! Scan halted!".format(len(m)))
		print("Backing up already scanned videos...")
		if mode1:
			while len(q) != 0:
				code = gather(head)
				#check for errors
				if code == 1:
					print("An error occured while backing up the videos...")
					action=""
					t.cancel()
					while action!='r' and action!='a':
						action = input("Type r to retry or a to abort:\n")
						action = action.rstrip().strip()
					if action == 'r':
						#reset this
						if mode1: reportMode1()
						else: reportGathering()
						q.append(head)
						continue
					if action == 'a':
						return 1
						break
	return 0
def analyzePlaylist(pID):
	try:
		#First link is extracted as an html
		target="https://www.youtube.com/playlist?list={}".format(pID)
		while True:
			r=requests.get(target)
			if r.status_code != 200:
				t.cancel()
				print("An error occured while trying to read the playlist...")
				action=""
				while action!='r' and action!='a'  :
					action = input("Type r to retry or a to abort:\n")
					action = action.rstrip().strip()
				if action == 'r':
					reportProgress()
					continue
				if action == 'a':
					return 1
			break
		plt=r.text
		imAtSoup = BeautifulSoup(plt,"html.parser")
		#print("TRYING TO ADD NEW STUFF FROM imAtSoup HERE")
		#print(str(imAtSoup.find_all("a")))
		#print("did it work tho?")
		for link in imAtSoup.find_all("a", class_="pl-video-title-link"):
			p.append(idExtractor('https://www.youtube.com{}'.format(link.get('href'))))
		nB = imAtSoup.find_all("button", class_="load-more-button")
		if len(nB) == 0:
			return 0
		ajaxTarget=nB[0].get("data-uix-load-more-href")
		target = "https://www.youtube.com{}".format(ajaxTarget)
		while True:
			#later playlist links are the internal html of a json
			#and to be loaded links are stored in a seperate entry of said json 
			#print(target)
			#print(plt.find('browse_ajax?ctoken='))
			Break=False
			while True:
				#print(target)
				r=requests.get(target)
				#print(r.status_code)
				if r.status_code != 200:
					t.cancel()
					print("An error occured while trying to read the upload playlist...")
					action=""
					while action!='r' and action!='a':
						action = input("Type r to retry or a to abort:\n")
						action = action.rstrip().strip()
					if action == 'r':
						reportPlaylistProgress()
						continue
					if action == 'a':
						return 1
				break
			plt=r.json()['content_html']
			imAtSoup = BeautifulSoup(plt,"html.parser")
			for link in imAtSoup.find_all("a", class_="pl-video-title-link"):
				p.append(idExtractor('https://www.youtube.com{}'.format(link.get('href'))))
			nextLink=r.json()['load_more_widget_html']
			whereIsSoup = BeautifulSoup(nextLink,"html.parser")
			#print(whereIsSoup.prettify())
			nB = whereIsSoup.find_all("button", class_="load-more-button")
			if len(nB) == 0:
				return 0
			ajaxTarget=nB[0].get("data-uix-load-more-href")
			target = "https://www.youtube.com{}".format(ajaxTarget)
			#return 0
			#print(plt)
			#return 1
	except Exception as e:
		print(e)
		return 1
	else:
		return 0

def gather(vID):
	#OPEN vID's ANNOTATIONS BY REQUEST
	#Done
	#SCAN FOR ANYTHING THAT HAS /WATCH or the shortened URL
	#Done

	#TRY TO ADD TO M
	#IF CAN ADD TO M ADD TO Q
	#done

	#IF CAN'T ADD TO M MOVE ON
	#done
	#RETURN 1 if ERROR IS RAISED
	#done
	try:
		r = requests.get("https://www.youtube.com/annotations_invideo?video_id={}".format(vID))
		#print("https://www.youtube.com/annotations_invideo?video_id={}".format(vID))
		#xml = ""
		xml = str(r.text)
		soup = BeautifulSoup(xml, 'xml')
		#print(soup.prettify()[:300])
		#filteredSoup = [ x.attrs for x in soup.find_all(type=['text','highlight'])]
		#filteredSoup = [ x['value'] for x in soup.find_all('url') if (x['value'].find('/watch') != -1 or x['value'].find('.be') != -1)]
		filteredSoup=[ idExtractor(x['value']) for x in soup.find_all('url') if (x['value'].find('/watch') != -1 or x['value'].find('.be') != -1) ]
		#shortUrls=[ idExtractor(x['value']) for x in soup.find_all('url') if x['value'].find('.be') != -1]
		#print(longUrls)
		#print(shortUrls)
		#itct = soup.annotations["itct"]
		#newSoup=BeautifulSoup("<document><annotations itct=\""+itct+"\">"+"".join([str(x) for x in filteredSoup])+"</annotations></document>",'xml')
		#print(newSoup.prettify())


		for lId in filteredSoup:
			#print (lId)
			if not lId in m:
				#Channel Lock
				if channelLock:
					#new dictionary for invalited links 
					if not lId in invld:
						thisChannel=channelExtractor(getVideoUser(lId))
						if channelUnavailable(thisChannel) or thisChannel!=channel: 
							invld[lId] = True
							continue
					else:
						continue
				m[lId] = False
				q.append(lId)
				if(hardLimitSet and len(m) >= hardLimit):
					return 0
				#print("added {} to queue".format(lId))
			#else:
				#print("duplicate entry detected")
	except:
		return 1
	else:
		return 0



def backUp(vID, retries=3):
	try:
		r = snapShotTaken(vID)
		if 'closest' not in r.json()["archived_snapshots"]:
			r2=snapShotPage(vID)
			if r2.status_code != 200:
				#Make a check to ensure the video isn't unavailable
				if videoUnavailable(vID):
					return 2
				else:
					return 1
		r = annotationsBackedUp(vID)
		if 'closest' not in r.json()["archived_snapshots"]:
			r2=backUpAnnotations(vID)
			if r2.status_code != 200:
				if videoUnavailable(vID):
					return 2
				else:
					return 1
	except Exception as e:
		if retries <= 0:
			print(e)
			return 1
		else:
			print("Unable to load retrying...")
			time.sleep(5)
			return backUp(vID, retries-1)

		
	else:
		return 0

def setHardLimit():
	global hardLimit,hardLimitSet
	print("Throughly scanning links can sometimes generate thousands of videos.")
	print("To spare your computer we offer the option of setting a hard limit to how many videos its allowed to scan.")
	print("(Besides the publicly listed videos of the channel)")
	print("Although this is largely dependent on which channel you're scanning and on your internet speed")
	print("We found that the average speed was about 10000 videos/hour on our devices.")
	#print("Keep in mind that this is only the discovery process and that nothing is backed up in this phase.")
	action=""
	while True:
		print("Please type a single number specifying the maximum number of videos to be scanned")
		print("Or hit enter to scan everything available. (Do this only if you know what you're doing)")
		action = input("")
		action = action.rstrip().strip()
		if action == '':
			return 0
		elif isASingleNumber(action):
			hardLimitSet = True
			hardLimit = getTheNumber(action)+len(p)
			if hardLimit==1:
				print("Limited scan to 1 video.")
			else:
				print("Limited scan to {} videos.".format(str(hardLimit)))
			return 0



def isASingleNumber(inp):
	return ( len(re.findall('(?!\-|\.)[0-9]+',inp)) == 1) and ( int(re.findall('(?!\-|\.)[0-9]+',inp)[0]) > 0)

def getTheNumber(inp):
	numberList = re.findall('(?!\-|\.)[0-9]+',inp)
	return int(numberList[0])

#Interval functions
def contains2Numbers(inp):
	return ( len(re.findall('(?!\-|\.)[0-9]+',inp)) == 2)
	
def get2Numbers(inp):
	numberList = re.findall('(?!\-|\.)[0-9]+',inp)
	return int(numberList[0]),int(numberList[1])

def validInterval(a,b,d):
	if a <= 0:
		return False
	elif b > d:
		return False
	elif a > b:
		return False
	return True 

def setChannelLock():
	#Channel Lock
	global channelLock
	print("Would you like to only search for videos linked to same channel?")
	print("This is a good idea if you only want to fetch unlisted videos from a video.")
	#print("Keep in mind that this is only the discovery process and that nothing is backed up in this phase.")
	action=""
	while True:
		print("Type y to confirm or enter to scan regardless:")
		action = input("")
		action = action.rstrip().strip()
		if action == '':
			channelLock=False
			return 0
		elif action == 'y':
			channelLock=True
			return 0

def activateChannelLock(vID):
	#Attempt to get channel of vID
	#print("attempting to get channel")
	cID=getVideoUser(vID)
	if cID=="":
		if videoUnavailable(vID):
			return 2
		return 1
	channel=channelExtractor(cID)
	return 0
	#cID

def isTwoDates(s):
	return ( len(re.findall(r'[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]',s))==2 )
def getTwoDates(s):
	return s.split(' ')
def validTwoDates(d1, d2):
	if d1 > d2:
		return False
	return True 
def setMode():
	#Channel Lock
	global mode1
	print("Please choose the mode you'd like to use.")
	print("Mode 1: Scan as you back up")
	print("Mode 2: Scan first, then back up")
	print("We recommend you use mode 1 since it doesn't waste any time making back-ups.")
	print("Plus it's slightly faster.")
	print("Mode 2's advantage is that it'll better help you track the progress.")
	print("Consider using mode 2 if you know there won't be a lot of videos linked to from this video.")
	action=""
	while True:
		action = input("Type 1 or 2:")
		action = action.rstrip().strip()
		if action == '1':
			mode1=True
			return 0
		elif action == '2':
			mode1=False
			return 0

if __name__== "__main__":
	main()