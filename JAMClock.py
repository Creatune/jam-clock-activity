#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMClock.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   CeibalJAM! - Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
import os, sys, socket, pygame

from pygame.locals import *
from sugar3.activity import activity

from Main import Main

class JAMClock(activity.Activity):
	def __init__(self, handle):
	        activity.Activity.__init__(self, handle, False)
		self.set_title('JAMClock')
	        self.set_toolbar_box(activity.ActivityToolbox(self))
		self.eventbox= PygameCanvas()
		self.set_canvas(self.eventbox)

		self.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
		self.connect("destroy", self.salir)

		self.show_all()
		self.realize()

	       	os.putenv('SDL_WINDOWID', str(self.eventbox.socket.get_id()))
		GLib.idle_add(self.get_run_game)

	def get_run_game(self):
		print "Lanzando JAMClock."
		pygame.init()
		x, y, w, y=  self.eventbox.get_allocation()
		Main( (w,y) )
		return False

	def salir(self, widget):
		lambda w: Gtk.main_quit()
		sys.exit()

class PygameCanvas(Gtk.EventBox):
	def __init__(self):
		Gtk.EventBox.__init__(self)		
		self.set_can_focus(True)
		self.setup_events()
		self.socket = Gtk.Socket()
		self.add(self.socket)
		self.button_state = [0,0,0]
        	self.mouse_pos = (0,0)
		
	def setup_events(self):

		self.set_events(Gdk.EventType.KEY_PRESS | Gdk.EventType.EXPOSE | Gdk.EventMask.POINTER_MOTION_MASK | \
		            Gdk.EventMask.POINTER_MOTION_HINT_MASK | Gdk.EventMask.BUTTON_MOTION_MASK | \
		            Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
	
		self.connect("key-press-event", self.keypress)
		self.connect("button_press_event", self.mousedown)
		self.connect("motion-notify-event", self.mousemotion)
		self.connect('expose-event', self.expose)
		self.connect('configure-event', self.resize)
		self.connect("focus-in-event", self.set_focus)

	def keypress(self, selfmain, event, parametros= None):
		nombre= Gdk.keyval_name(event.keyval)
		tipo= pygame.KEYDOWN
		unic= str.lower(nombre)
		valor= nombre
		try:
			valor= getattr(pygame, "K_%s" % (str.upper(nombre)))
		except:
			print "no has programado la traduccion de esta tecla: ", nombre
			return False
		evt = pygame.event.Event(tipo, key= valor, unicode= unic, mod=None)
		try:
			pygame.event.post(evt)
		except:
			pass
		return False

	def mousedown(self, widget, event):
		evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button= event.button, pos=(int(event.x), int(event.y)))
		try:
			pygame.event.post(evt)
		except:
			pass
		return False

	def mousemotion(self, widget, event):
		x, y, state = event.window.get_pointer()
        	rel = (x - self.mouse_pos[0], y - self.mouse_pos[1])
        	self.mouse_pos= (int(x), int(y))
        	self.button_state = [
            	state & Gdk.ModifierType.BUTTON1_MASK and 1 or 0,
            	state & Gdk.ModifierType.BUTTON2_MASK and 1 or 0,
            	state & Gdk.ModifierType.BUTTON3_MASK and 1 or 0,
        	]
		evt = pygame.event.Event(pygame.MOUSEMOTION, pos= self.mouse_pos, rel=rel, buttons=self.button_state)
		try:
			pygame.event.post(evt)
		except:
			pass
		return False

	def expose(self, event, widget):
		if pygame.display.get_init():
			try:
				pygame.event.post(pygame.event.Event(pygame.VIDEOEXPOSE))
			except:
				pass
		return False # continue processing

	def resize(self, widget, event):
		evt = pygame.event.Event(pygame.VIDEORESIZE, size=(event.width,event.height), width=event.width, height=event.height)
		try:
			pygame.event.post(evt)
		except:
			pass
		return False # continue processing

	def set_focus(self, container, widget):
		try:
			pygame.display.update()
		except:
			pass
		self.queue_draw()
		return False

# -----------------------------------------------
# 	******** El Juego en gtk ********
# -----------------------------------------------
class VentanaGTK(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)
		self.set_title("JAMClock")
		#self.fullscreen()
		self.set_size_request(800,600)
                self.socket = Gtk.Socket()
                self.add(self.socket)

		self.gtkplug = gtkplug()
		self.socket.add_id(self.gtkplug.get_id())	
		
		self.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
		self.connect("destroy", self.salir)
		self.connect("set-focus-child", self.refresh)
		self.show_all()

	def refresh(self, widget, datos):
		try:
			pygame.display.update()
		except:
			pass
		self.queue_draw()
		return True

	def salir(self, widget):
		pygame.quit()
		sys.exit()

class gtkplug(Gtk.Plug):
	def __init__(self):
		Gtk.Plug.__init__(self, 0L)		
		self.set_title("JAMClock")
		self.eventbox= PygameCanvas()
		self.add(self.eventbox)
		self.ventana= None
		self.show_all()

		self.connect("embedded", self.embed_event)

	       	os.putenv('SDL_WINDOWID', str(self.eventbox.socket.get_id()))
		GLib.idle_add(self.get_run_game)

	def get_run_game(self):
        	self.eventbox.socket.window.set_cursor(None)
		print "Lanzando JAMClock."
		pygame.init()
		x, y, w, y=  self.eventbox.get_allocation()
		Main( (w,y) )
		return False

	def embed_event(self, widget):
	    	print "Juego embebido"

if __name__=="__main__":
	VentanaGTK()
	Gtk.main()
