import requests
import radconfig

uri=radconfig.uri
client=radconfig.client
secret=radconfig.secret
myid=radconfig.myid
myname=radconfig.myname
savedir=radconfig.savedir



def gettwitchtoken(client=client,uri=uri,secret=secret):
	
	url ='https://id.twitch.tv/oauth2/token'
	params={'client_id':client,'client_secret':secret,'grant_type':'client_credentials','scope':''}
	ret=requests.post(url,data=params)
	print (ret.content)
	return ret.json()['access_token']
	
	
def names(tok,loop=True):
	data=[]
	n=requests.get('https://api.twitch.tv/helix/users/follows?to_id='+myid+'&first=100', headers={'Client-ID': client, "Authorization": "Bearer "+tok})
	pag= n.json()['pagination']['cursor']
	data.append(n.json())
	print (n.json())
	if not loop:
		pag='Null'
	while pag!='Null':
			n=requests.get('https://api.twitch.tv/helix/users/follows?to_id='+myid+'&first=100&after='+pag, headers={'Client-ID': client, "Authorization": "Bearer "+tok})
			data.append(n.json())
			try:
				pag= n.json()['pagination']['cursor']
			except KeyError:
				break
	res=[]
	import datetime
	for page in data:
		for user in page['data']:
			now = datetime.datetime.utcnow()
			t=int((now-datetime.datetime.strptime(user['followed_at'],'%Y-%m-%dT%H:%M:%SZ')).total_seconds()/86400)
			res.append([user['from_name'],t])
	return res		

def subs(tok,loop=True):
	data=[]
	n=requests.get('https://api.twitch.tv/helix/subscriptions?broadcaster_id='+myid+'&first=100', headers={'Client-ID': client, "Authorization": "Bearer "+tok})

	page=n.json()
	print (page)
	import datetime
	
	for user in page['data']:
		res.append([user['from_name'],t])
	return res	


def bits(tok):

	data=[]
	n=requests.get('https://api.twitch.tv/helix/bits/leaderboard?user_id='+myid+'&period=day', headers={'Client-ID': client, "Authorization": "Bearer "+tok})
	pag= n.json()
	data.append(n.json())
	print (n.json())

	res=[]
	import datetime
	for page in data:
		for user in page['data']:
			now = datetime.datetime.utcnow()
			t=int((now-datetime.datetime.strptime(user['followed_at'],'%Y-%m-%dT%H:%M:%SZ')).total_seconds()/86400)
			res.append([user['from_name'],t])
	return res	



def clips(tok):
	data=[]
	n=requests.get('https://api.twitch.tv/helix/clips?broadcaster_id='+myid+'&first=100', headers={'Client-ID': client, "Authorization": "Bearer "+tok})
	print (n.content)
	pag= n.json()['pagination']['cursor']
	data.append(n.json())
	while pag!='Null':
			n=requests.get('https://api.twitch.tv/helix/clips?broadcaster_id='+myid+'&first=100&after='+pag, headers={'Client-ID': client, "Authorization": "Bearer "+tok})
			data.append(n.json())
			try:
				pag= n.json()['pagination']['cursor']
			except KeyError:
				break
	print (data)
	res=[]
	import datetime
	for page in data:
		for user in page['data']:
			t=datetime.datetime.strptime(user['created_at'],'%Y-%m-%dT%H:%M:%SZ')
			res.append([user['title'],user['view_count'],t.year,t.month,user['thumbnail_url'][:-20]+'.mp4'])
		return res
		
	
def whoami(tok,me=myname):
	n=requests.get('https://api.twitch.tv/helix/users?login='+me, headers={'Client-ID': client, "Authorization": "Bearer "+tok})
	result=n.json()
	return result['data'][0]
		
def whatamistreaming(tok):
	data=[]
	n=requests.get('https://api.twitch.tv/helix/channels?broadcaster_id='+myid, headers={'Client-ID': client, "Authorization": "Bearer "+tok})
	data= n.json()
	return data["data"][0]["game_id"],data["data"][0]["game_name"]
	
def howmanyviewers(tok):
	data=[]
	n=requests.get('https://api.twitch.tv/helix/streams?user_login='+myname, headers={'Client-ID': client, "Authorization": "Bearer "+tok})
	data=n.json()
	print (data)
	if data['data']:
		 return (int(data['data'][0]['viewer_count']))
	else:
		 return 0
	

def whoisplaying(tok, game):
	data=[]
	n=requests.get('https://api.twitch.tv/helix/streams?game_id='+str(game)+'&language=en&first=100', headers={'Client-ID': client, "Authorization": "Bearer "+tok})
	#print (n.content)
	data.append(n.json())
	try:
		pag= n.json()['pagination']['cursor']
	except KeyError:
		pag='Null'
	c=1
	while pag!='Null':
			n=requests.get('https://api.twitch.tv/helix/streams?game_id='+str(game)+'&language=en&first=100&after='+pag, headers={'Client-ID': client, "Authorization": "Bearer "+tok})
			#n=requests.get('https://api.twitch.tv/helix/streams?after='+pag, headers={'Client-ID': client, "Authorization": "Bearer "+tok})
			#print (n.json())
			data.append(n.json())
			try:
				pag= n.json()['pagination']['cursor']
			except KeyError:
				break
			print (c)
			c+=1
	#print (data)
	res=[]
	import datetime
	for page in data:
		for user in page['data']:
			now = datetime.datetime.utcnow()
			t=int((now-datetime.datetime.strptime(user['started_at'],'%Y-%m-%dT%H:%M:%SZ')).total_seconds()/60)
			res.append([user['user_name'],int(user['viewer_count']),user['title'],t,user['thumbnail_url']])
	return res

def insert_newlines(string, every=96):
        lines = []
        for i in range(0, len(string), every):
                lines.append(string[i:i+every])
                return '\n'.join(lines)

def getraidsuggestions():
	mydir='raidinfo'
	import os
	filelist = [ f for f in os.listdir(mydir) ]
	for f in filelist:
	    os.remove(os.path.join(mydir, f))
	tok=gettwitchtoken()
	print (whoami(tok))
	views=(howmanyviewers(tok))
	game,gname=whatamistreaming(tok)
	play=whoisplaying(tok,game)
	diff=sorted([[abs(views-n[1]),n] for n in play if n[0].lower()!=myname])[:5]
	fin=sorted([[n[1][3],n[1]]for n in diff])
	c=1
	for n in fin:
		print ('player: '+str(c))
		print ('name: '+n[1][0])
		print ('currently playing: '+gname)
		print ('Stream Title: ' + n[1][2])
		print ('Time online: '+str(n[1][3])+' minutes')
		print (n[1][4].replace('{width}','160').replace('{height}','120'))
		t=whoami(tok,me=n[1][0])
		print ('Bio: '.encode('utf-8')+t['description'].encode('utf-8'))
		with open('raidinfo/name'+str(c)+'.txt','w') as f:
			f.write('Twitch name: '+n[1][0])
		with open('raidinfo/playing'+str(c)+'.txt','w') as f:
			f.write(gname)
		with open('raidinfo/title'+str(c)+'.txt','w',encoding='utf-8') as f:
			f.write(n[1][2])
		with open('raidinfo/time'+str(c)+'.txt','w') as f:
			f.write(str(n[1][3])+' minutes')
		with open('raidinfo/bio'+str(c)+'.txt','w',encoding='utf-8') as f:
			f.write(insert_newlines(t['description']+' '))
		with open('raidinfo/pic'+str(c)+'.jpeg','wb') as f:
			f.write(requests.get(t['profile_image_url'],stream=True).content)
		with open('raidinfo/thumb'+str(c)+'.jpeg','wb') as f:
			f.write(requests.get(n[1][4].replace('{width}','320').replace('{height}','180'),stream=True).content)
		c+=1
	with open ('raidinfo/follows.txt','w',encoding='utf-8') as f:
		t=[n[0] for n in names(tok,loop=False) if n[1]<10]
		for n in t:
			f.write(n+'\n')

if __name__=='__main__':
	import os
	os.chdir(savedir)
	getraidsuggestions()

