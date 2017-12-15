import xbmcaddon
import xbmcgui
import socket, datetime, time, math, json, errno, os, time

def convertTime(seconds) :
	total_sec_int = int(seconds)
	converted = datetime.timedelta(seconds=total_sec_int)
	return str(converted)

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')

addon_dir = xbmc.translatePath( __addon__.getAddonInfo('path') )
sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )
# This is a throwaway variable to deal with a python bug
throwaway = datetime.datetime.strptime('20110101','%Y%m%d')
from libDisplay import Display

player = xbmc.Player()
#player.__init__(xbmc.PLAYER_CORE_MPLAYER)

display_maxHour = __addon__.getSetting('maxHourOn')+":00"
display_minHour = __addon__.getSetting('minHourOn')+":00"
h_max = datetime.datetime.strptime(display_maxHour, "%H:%M:%S")
h_min = datetime.datetime.strptime(display_minHour, "%H:%M:%S")

display_obj = Display.Display()
while True:
	display_obj.updateFont(__addon__.getSetting('displayFont'))
	if player.isPlayingVideo() :
		display_obj.displayBacklight(True)
		infoTag = player.getVideoInfoTag()
		current = convertTime(player.getTime())
		total = convertTime(player.getTotalTime())
		data = {'title':infoTag.getTitle(), 'serial':infoTag.getPlotOutline(),'current':str(current), 'total':str(total), 'timecode':str(current)+"/"+str(total)}
		display_obj.write(json.dumps(data), )
	else :
		day = time.strftime('%A %d %B')
		hour = time.strftime('%H:%M:%S')
		h_to_compare = datetime.datetime.strptime(hour, "%H:%M:%S")
		sec = time.strftime('%S')
		data = {'day':day, 'hour':hour}
		display_obj.idle(json.dumps(data), )
		max = h_max - h_to_compare
		min = h_to_compare - h_min
		if max.total_seconds() > 0 and min.total_seconds() > 0:
			display_obj.displayBacklight(True)
		else:
			display_obj.displayBacklight(False)
	time.sleep(1)
# if __addon__.getSetting('myscrypt_enabled') == "true" :
	# addon_ipaddress = __addon__.getSetting('ip_address')
	# addon_ipport = __addon__.getSetting('ip_port')
	# while True:
		# if player.isPlayingVideo() :
			# if addon_ipaddress and addon_ipport :
				# try :
					# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					# client.connect((addon_ipaddress, int(addon_ipport)))
				# except socket.error, v :
					# errorcode=v[0]
					# if errorcode == errno.ECONNREFUSED:
						# print "Connection Refused"
				# else :
					# infoTag = player.getVideoInfoTag()
					# current = convertTime(player.getTime())
					# total = convertTime(player.getTotalTime())
					# data = {'title':infoTag.getTitle(), 'serial':infoTag.getPlotOutline(),'current':str(current), 'total':str(total), 'timecode':str(current)+"/"+str(total)}
					# #client.sendall(infoTag.getTitle()+"\\"+str(current)+"/"+str(total))
				# # else:
					# # # on peut afficher 30 caracteres majuscucules sur lecran
					# # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					# # client.connect((addon_ipaddress, int(addon_ipport)))
					# # currentdate = datetime.datetime.now()
					# # heure = currentdate.__format__("%H:%M:%S")
					# # day = currentdate.__format__("%A %d %B")
					# # data = {'title':'', 'current':'', 'total':'', 'day':str(day), 'hour':str(heure)}
					# # #client.sendall(str(day)+"\\               "+str(heure))
					# try :
						# client.send(json.dumps(data))
					# except socket.error, v : 
						# errorcode=v[0]
						# if errorcode == errno.ECONNREFUSED:
							# client.close()
							# print "Connection Aborted"
					# else :
						# client.close()
						# time.sleep(1)