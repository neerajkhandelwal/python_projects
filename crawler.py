import urllib2
import re
from BeautifulSoup import BeautifulSoup
import robotparser
import time

def filterLinks(html):
	anchor_tags = html.findAll('a', href=re.compile('^[^#].*'))
	links = []
	for link in anchor_tags: 
		links.append(str(link['href']))
	return links
	
def canreadSite(robot_link, link):
	print 'Reading URL...', link
	try:
		rp = robotparser.RobotFileParser()
		rp.set_url(link)
		rp.read()
		can_fetch = rp.can_fetch("*", link)
	except:
		can_fetch = True
	return can_fetch
	
def filterURLParts(url):
	sub_domain = ''
	domain = ''
	requested = ''
	www = ''
	
	print 'Validating URL....', url
	parts = url.split('/')
	protocol = parts[0].rstrip(':')
	havesubDomain = parts[2].split('.')
	if len(havesubDomain) == 2:
		domain = havesubDomain[0]+'.'+havesubDomain[1]
	elif len(havesubDomain) == 3 and havesubDomain[0] == 'www':
		domain = havesubDomain[1]
		www = 'www.'
	elif len(havesubDomain) == 3 and havesubDomain[0] != 'www':
		domain = havesubDomain[1]+'.'+havesubDomain[2]
		sub_domain = havesubDomain[0]+'.'
	elif len(havesubDomain) == 4:
		domain = havesubDomain[2]+'.'+havesubDomain[3]
		sub_domain = havesubDomain[1]+'.'
		www = 'www.'
	requested = '/'+''.join(parts[3:])
	return {'protocol': protocol, 'subdomain': sub_domain, 'domain': domain, 'request': requested, 'www': www}

def crawl(seed):
	global crawled
	global tobeCrawled
	global total_crawled
	global invalid_links
	parts = filterURLParts(seed)
	if (canreadSite(parts['protocol']+'://'+parts['www']+parts['subdomain']+parts['domain']+'/robots.txt', seed)) and (seed not in crawled):
		try:
			content = urllib2.urlopen(seed)
			html = BeautifulSoup(content)
			tobeCrawled.append(filterLinks(html))
			crawled.append(seed)
			total_crawled += 1
			print 'Crawled so far...', total_crawled, '\n'
		except:
			invalid_links.append(seed)
	else:
		print 'Either robots.txt is denying crawling or webpage already been crawled.'
		return
	if total_crawled >= 20:
		return
	del tobeCrawled[0][0]
	time.sleep(1)
	if tobeCrawled[0][0][0] == '/':
		crawl(parts['protocol']+'://'+parts['www']+parts['subdomain']+parts['domain']+tobeCrawled[0][0])
	elif tobeCrawled[0][0][0] == '?':
		crawl(parts['protocol']+'://'+parts['www']+parts['subdomain']+parts['domain']+'/'+tobeCrawled[0][0])
	else:
		crawl(tobeCrawled[0][0])
		
	#print crawled
	
if __name__ == '__main__':
	seed = 'http://python.org/'
	crawled = []
	tobeCrawled = []
	invalid_links = []
	total_crawled = 0
	crawl(seed)
	print 'List of crawled: ',crawled,'\n'
	print 'List of to be crawled', tobeCrawled, '\n'