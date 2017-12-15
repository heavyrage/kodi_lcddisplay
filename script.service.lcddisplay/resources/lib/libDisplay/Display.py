#!/usr/bin/python
from PIL import Image, ImageDraw, ImageColor, ImageFont
from ctypes import CDLL
import time, sys, locale, json, os
import xbmcaddon

__addon__ = xbmcaddon.Addon()
addon_dir = __addon__.getAddonInfo('path')
setting_font_name = __addon__.getSetting('displayFont')

class Display(object):
        IDLE_TIME = 2                      # seconds
        DISPNAME = "ALPHACOOL"
        SDCDEV = "USB:060c/04eb"
        SERDISPLIB = os.path.join(addon_dir,"resources","lib","libserdisp", "libserdisp.so")
        print "mylib:"+SERDISPLIB
        FONTSIZE = 22
        HOUR_FONTSIZE = 30
        FONTWIDTH = FONTSIZE/2
        HOUR_FONTWIDTH = HOUR_FONTSIZE/2
        DATA_DIR=os.path.join(addon_dir,"resources","data")
        print "myhome:"+DATA_DIR
        FONT_NAME=setting_font_name
        FONT_PATH=os.path.join(DATA_DIR,"data-latin.ttf")
        print "myfont:"+FONT_PATH
        FONT = ImageFont.truetype(FONT_PATH, FONTSIZE)
        HOUR_FONT = ImageFont.truetype(FONT_PATH, HOUR_FONTSIZE)
        RECT_HEIGHT = 10
        RECT_WIDTH = 100
        RECT_BEGIN_X = 0
        RECT_BEGIN_Y = 0
        RECT_END_X = 0
        RECT_END_Y = 0
        OFFSET = 0
        LINE = 0
        LINE_OFFSET = 0

        def __init__(self):
                #self._load_config()
                os.environ["TZ"]="Europe/Paris"
                self.updated = time.time()
                self._init_display()
                #self.write('Hello')
                self.img = self._createImage()

        def _load_config(self):
                config = ConfigParser.ConfigParser()
                config_file = (os.path.join(os.getcwd(),'/storage/lcdcontrol/lcdcontrol.conf'))
                #config.read(config_file)
                self.IDLE_TIME = config.getint('Display','IDLE_TIME')
                self.DISPNAME = config.get('Display','DISPNAME')
                self.SDCDEV = config.get('Display','SDCDEV')
                self.FONTSIZE = config.getint('Display','FONTSIZE')
                self.HOUR_FONTSIZE = config.getint('Display','HOUR_FONTSIZE')
                self.RECT_HEIGHT = config.getint('Display','RECT_HEIGHT')
                self.RECT_WIDTH = config.getint('Display','RECT_WIDTH')
                self.RECT_BEGIN_X = config.getint('Display','RECT_BEGIN_X')
                self.RECT_BEGIN_Y = config.getint('Display','RECT_BEGIN_Y')
                self.RECT_END_X = config.getint('Display','RECT_END_X')
                self.RECT_END_Y = config.getint('Display','RECT_END_Y')
                self.FONT = ImageFont.truetype(str(config.get('Display','FONT')), self.FONTSIZE)
                self.LINE_OFFSET = config.getint('Display','LINE_OFFSET')
                self.HOUR_FONT = ImageFont.truetype(str(config.get('Display','HOUR_FONT')), self.HOUR_FONTSIZE)
                self.FONTWIDTH = config.getint('Display','FONTWIDTH')
                self.HOUR_FONTWIDTH = config.getint('Display','HOUR_FONTWIDTH')

        def _init_display(self):
                self.serdisp = CDLL(self.SERDISPLIB)
                sdcd = self.serdisp.SDCONN_open(self.SDCDEV)
                if sdcd == 0:
                        print 'No connection to ', self.SDCDEV
                        sys.exit(0)
                self.dd = self.serdisp.serdisp_init(sdcd,self.DISPNAME,"")
                if self.dd == 0:
                        print 'Error opening display', self.DISPNAME
                self.serdisp.serdisp_clear(self.dd)
                self.serdisp.serdisp_setpixel(self.dd, 0, 0, 1)
                self.serdisp.serdisp_update(self.dd)
                self.RECT_BEGIN_X = ((self.serdisp.serdisp_getwidth(self.dd)-self.RECT_WIDTH)/2)-1
                self.RECT_BEGIN_Y = 2*self.FONTSIZE+(self.FONTSIZE-self.RECT_HEIGHT)/2
                self.RECT_END_X = self.RECT_BEGIN_X + self.RECT_WIDTH + 1
                self.RECT_END_Y = 2*self.FONTSIZE+(self.FONTSIZE+self.RECT_HEIGHT)/2

        def _createImage(self):
                img = Image.new('1',(self.serdisp.serdisp_getwidth(self.dd), self.serdisp.serdisp_getheight(self.dd)), 'white')
                draw = ImageDraw.Draw(img)
                return img

        def _convertToSeconds(self, timecode):
                timearray = timecode.split(':')
                time_sec = 3600*int(timearray[0])+60*int(timearray[1])+int(timearray[2])
                return time_sec

        def _drawVideoTag(self, json_data, img):
                draw = ImageDraw.Draw(img)
                title = json_data['title']
                timecode = json_data['timecode']
                if self.FONTWIDTH*len(title) > self.serdisp.serdisp_getwidth(self.dd):
                        title_pos = 0 - self.OFFSET
                else:
                        title_pos = (self.serdisp.serdisp_getwidth(self.dd)-self.FONTWIDTH*len(title))/2
                draw.text((title_pos,0),json_data['title'], font=self.FONT)
                timecode_pos = (self.serdisp.serdisp_getwidth(self.dd)-self.FONTWIDTH*len(timecode))/2
                draw.text((timecode_pos,self.FONTSIZE),json_data['timecode'], font=self.FONT)
                draw.rectangle(((self.RECT_BEGIN_X, self.RECT_BEGIN_Y),(self.RECT_END_X,self.RECT_END_Y)))
                current_sec = self._convertToSeconds(json_data['current'])
                total_sec = self._convertToSeconds(json_data['total'])
                if total_sec == 0:
                        total_sec = 1
                rect_pos = self.RECT_WIDTH*current_sec/total_sec
                for i in xrange(self.RECT_HEIGHT):
                        draw.line(((self.RECT_BEGIN_X+1, i+self.RECT_BEGIN_Y),(self.RECT_BEGIN_X+int(rect_pos),i+self.RECT_BEGIN_Y)))
                if self.OFFSET > (self.FONTWIDTH*len(title)-self.serdisp.serdisp_getwidth(self.dd)):
                #if self.OFFSET > self.FONTWIDTH*len(title):
                        self.OFFSET = 0
                else:
                        self.OFFSET = self.OFFSET + 2*self.FONTWIDTH
                return draw

        def _drawCurrentTime(self, data, img):
                day = data['day']
                hour = data['hour']
                date = day.split()
                today = date[0]
                num = date[1]
                month = date[2]
                new_day = today+" "+num+" "+month[:3]
                draw = ImageDraw.Draw(img)
                #print day
                if self.FONTWIDTH*len(new_day) > self.serdisp.serdisp_getwidth(self.dd):
                        day_pos = 0
                else:
                        day_pos = (self.serdisp.serdisp_getwidth(self.dd)-self.FONTWIDTH*len(new_day))/2
                #draw.text((day_pos,0),str(day), font = self.FONT)
                draw.text((day_pos,self.LINE_OFFSET),str(new_day), font = self.FONT)
                hour_pos = (self.serdisp.serdisp_getwidth(self.dd)-self.HOUR_FONTWIDTH*len(hour))/2
                draw.text((hour_pos,self.FONTSIZE+2*self.LINE_OFFSET), hour, font=self.HOUR_FONT)
                return draw

        def _updateDisplay(self, pixs):
                for x in xrange(self.serdisp.serdisp_getwidth(self.dd)):
                        for y in xrange(self.serdisp.serdisp_getheight(self.dd)):
                                if pixs[x,y] <> 255:
                                        self.serdisp.serdisp_setpixel(self.dd,x,y,1)
                self.serdisp.serdisp_update(self.dd)
                self.serdisp.serdisp_clearbuffer(self.dd)

        def displayBacklight(self, switch):
                if(switch == True):
                    self.serdisp.serdisp_setoption(self.dd, "BACKLIGHT", 1);
                else:
                    self.serdisp.serdisp_setoption(self.dd, "BACKLIGHT", 0);

        def getFont(self):
                return self.FONT_NAME

        def updateFont(self, ft):
                self.FONT_PATH=os.path.join(self.DATA_DIR,ft+".ttf")
                self.FONT = ImageFont.truetype(self.FONT_PATH, self.FONTSIZE)
                self.HOUR_FONT = ImageFont.truetype(self.FONT_PATH, self.HOUR_FONTSIZE)

        def _write(self, arg):
                print 'DISPLAY:', arg

        def write(self, arg):
                """
                update display and 'last updated' timestamp
                """
                self._write(arg)
                self.updated = time.time()
                self.img = self._createImage()
                try :
                        data = json.loads(arg)
                except ValueError :
                        pass
                else :
                        draw = self._drawVideoTag(json_data=data, img=self.img)
                        pixs = self.img.load()
                        self._updateDisplay(pixs)

        def idle(self, arg):
                """
                update display only if it's been a few seconds
                """
                if time.time() - self.updated >= self.IDLE_TIME:
                        #self._write(arg)
                        self.img = self._createImage()
                        draw = self._drawCurrentTime(data=json.loads(arg), img=self.img)
                        pixs = self.img.load()
                        self.serdisp.serdisp_clearbuffer(self.dd)
                        self.OFFSET = 0
                        self._updateDisplay(pixs)