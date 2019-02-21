import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk
from gi.repository import Gdk

from enum import Enum
#set up window
import cairo
from cmath import *
import math

funcString = "z**2"

i = 0 + 1j

CLAMP_VAL = 100000

def clamp(x):
	return min(CLAMP_VAL,max(-CLAMP_VAL,x))

class GraphType(Enum):
	CARTESIAN = 1
	POLAR = 2
	
class Rect:
	def __init__(self,x=0,y=0,w=0,h=0):
		self.x = x;
		self.y = y;
		self.w = w;
		self.h = h;
		
	def contains(self,x,y):
		return self.x<x and self.x+self.width>x and self.y<y and self.y+self.height>y 
		
	def collision(self,rect):
		return self.x<rect.x+rect.width and self.x+self.width>rect.x and self.y<rect.y+rect.height and self.y+self.height>rect.y 
	
	
class Graph:
	def __init__(self,area,left):
		area.set_hexpand(True)
		area.set_vexpand(True)
		self.offset = [0.5,0.5]
		self.gridSize = [0.1,0.1]
		self.gridMin = [-1,-1]
		self.gridMax = [1,1]
		dim = area.get_size_request();
		self.scale = max(dim)
		self.type = GraphType.CARTESIAN
		self.points = []
		self.area = area
		self.grabbed = False
		self.drawAxis = True
		self.drawGrid = True
		area.add_events(Gdk.EventMask.EXPOSURE_MASK
                                | Gdk.EventMask.LEAVE_NOTIFY_MASK
                                | Gdk.EventMask.BUTTON_PRESS_MASK
                                | Gdk.EventMask.POINTER_MOTION_MASK
                                | Gdk.EventMask.POINTER_MOTION_HINT_MASK
								| Gdk.EventMask.BUTTON_RELEASE_MASK
								| Gdk.EventMask.KEY_PRESS_MASK
								| Gdk.EventMask.KEY_RELEASE_MASK)
		area.connect('draw',lambda wid,cr : self.do_draw(wid,cr))
		area.connect('motion-notify-event',lambda wid,evt : self.dragHandle(wid,evt))
		area.connect('button-press-event',lambda wid,evt : self.grab(evt))
		area.connect('button-release-event',lambda wid,evt : self.release(evt))
		self.left = left
		self.shift = False
		self.lineStep = 0.1
		self.addPoints = False
	
	def grab(self,evt):
		self.grabbed = True;
		self.mx = evt.x
		self.my = evt.y
		if(self.addPoints and self.left):
			self.points.append(((evt.x*1/self.scale)-self.offset[0],(evt.y*1/self.scale)-self.offset[1]))
			self.draw()
			window.rightGraph.draw()
	
	def release(self,evt):
		self.grabbed = False;
		
	def do_draw(self,wid,cr):
		dim = self.area.get_allocation()
		cr.set_source_rgb(1,1,1)
		cr.rectangle(0,0,dim.width,dim.height)
		cr.fill()
		cr.scale(self.scale,self.scale)
		cr.set_line_width(1/self.scale)
		#drawAxis
		if(self.drawAxis):
			rect  = Rect(0,0,dim.width/self.scale,dim.height/self.scale)
			cr.set_source_rgb(0.2,0.2,0.2)
			if(rect.x<self.offset[0] and rect.x+rect.w>self.offset[0]):
				cr.move_to(self.offset[0],0)
				cr.line_to(self.offset[0],rect.h)
				cr.stroke()
			if(rect.y<self.offset[1] and rect.y+rect.h>self.offset[1]):
				cr.move_to(rect.x,self.offset[1])
				cr.line_to(rect.x+rect.w,self.offset[1])
				cr.stroke()
		#cr.move_to(0,0)
		cr.set_source_rgb(0.5,0.5,0.5)
		if(self.left):
			if(self.drawGrid):
				if(self.type == GraphType.CARTESIAN):
					xpos = self.gridMin[0]
					while(xpos<=self.gridMax[1]):
						cr.move_to(xpos+self.offset[0],self.gridMin[1]+self.offset[1])
						cr.line_to(xpos+self.offset[0],self.gridMax[1]+self.offset[1])
						xpos+=self.gridSize[0] 
					cr.stroke()	
					
					#draw the horizontal lines
					
					ypos = self.gridMin[1]
					while(ypos<=self.gridMax[1]):
						cr.move_to(self.gridMin[0]+self.offset[0],ypos+self.offset[1])
						cr.line_to(self.gridMax[0]+self.offset[0],ypos+self.offset[1])
						ypos+=self.gridSize[1] 
					cr.stroke()	
				else: #polar
					#draw circles
					
					r = self.gridMin[0];
					while(r<=self.gridMax[0]):
						cr.arc(self.offset[0],self.offset[1],r,self.gridMin[1],self.gridMax[1])
						r+=self.gridSize[0]
						cr.stroke()	
					
					#draw lines
					theta = self.gridMin[1]
					while(theta<=self.gridMax[1]):
						c = math.cos(theta)
						s = math.sin(theta)
						cr.move_to((c*self.gridMin[0]) + self.offset[0],(s*self.gridMin[0]) + self.offset[1])
						cr.line_to((c*self.gridMax[0]) + self.offset[0],(s*self.gridMax[0]) + self.offset[1])
						theta+=self.gridSize[1]
						cr.stroke()	
			
			cr.move_to(0,0)
			#draw points
			cr.set_source_rgb(0.2,0.2,1)
			for p in self.points:
				cr.arc(p[0]+self.offset[0],p[1]+self.offset[1], 3*(1/self.scale) , 0, pi*2)
				cr.fill()
				
		else:
			if(self.drawGrid):
				if(self.type == GraphType.CARTESIAN):
					#draw the vertical lines
					xpos = self.gridMin[0]
					while(xpos<=self.gridMax[1]):
						t = 0
						
						z = (xpos) + i*(self.gridMin[1])
						z = eval(funcString)
						cr.move_to(clamp(z.real+self.offset[0]),clamp(z.imag+self.offset[1]))
						while(t<=1):
							z = (xpos) + i*((1-t)*self.gridMin[1] + t*self.gridMax[1])
							try:
								z = eval(funcString)
								cr.line_to(clamp(z.real+self.offset[0]),clamp(z.imag+self.offset[1]))
							except Exception:
								print("error evaluating function")
							t+=self.lineStep
						xpos+=self.gridSize[0] 
					cr.stroke()	
					
					#draw the horizontal lines
					
					ypos = self.gridMin[1]
					while(ypos<=self.gridMax[1]):
						t = 0
						z = (self.gridMin[0]) + i*(ypos)
						z = eval(funcString)
						cr.move_to(clamp(z.real+self.offset[0]),clamp(z.imag+self.offset[1]))
						while(t<=1):
							z = ((1-t)*(self.gridMin[0]) + t*(self.gridMax[0])) + i*(ypos)
							try:
								z = eval(funcString)
								cr.line_to(clamp(z.real+self.offset[0]),clamp(z.imag+self.offset[1]))
							except Exception:
								print("error evaluating function")
							t+=self.lineStep
						ypos+=self.gridSize[1] 
					cr.stroke()	
				else:
					
					#draw circles
					
					r = self.gridMin[0];
					while(r<=self.gridMax[0]):
						t = 0;
						z = math.cos(self.gridMin[1]) + i*math.sin(self.gridMin[1])#eliminates some errors
						z = eval(funcString)
						cr.move_to(clamp(z.real+self.offset[0]),clamp(z.imag+self.offset[1]))
						while(t <= 1):
							theta = (1-t)*self.gridMin[1] + t*self.gridMax[1]
							z = math.cos(theta)*r + i*(math.sin(theta)*r)
							try:
								z = eval(funcString)
								cr.line_to(clamp(z.real*r+self.offset[0]),clamp(z.imag*r+self.offset[1]))
							except Exception:
								print("error evaluating function")
							t+=self.lineStep
						r+=self.gridSize[0]
						cr.stroke()	
					
					#draw lines
					theta = self.gridMin[1]
					while(theta<=self.gridMax[1]):
						c = math.cos(theta)
						s = math.sin(theta)
						z = c*self.gridMax[0] + i*(s*self.gridMax[0])
						try:
							z = eval(funcString)
							cr.move_to(clamp(z.real+self.offset[0]),clamp(z.imag+self.offset[1]))
						except Exception:
							print("error evaluating function")
							theta+=self.gridSize[1]
							continue
						t = 0
						while(t<=1):
							r = (t)*self.gridMin[0] + (1-t)*self.gridMax[0]
							z = c*r + i*(s*r)
							try:
								z = eval(funcString)
								cr.line_to(clamp(z.real+self.offset[0]),clamp(z.imag+self.offset[1]))
							except Exception:
								print("error evaluating function")
								
							t+=self.lineStep
						cr.stroke()	
						theta+=self.gridSize[1]
			
			#draw points
			cr.set_source_rgb(0.2,0.2,1)
			for p in self.points:
				z = p[0] + i*p[1]
				try:
					z=eval(funcString)
					cr.arc(z.real + self.offset[0],z.imag + self.offset[1], 3 *(1/self.scale) , 0, pi*2)
					cr.fill()
				except Exception:
							print("error evaluating function")

	
	def drawRight(self,func,area):
		return
		
	def dragHandle(self,wid,evt):
		if(self.grabbed ):
			if(self.addPoints):
				self.points.append(((evt.x*1/self.scale)-self.offset[0],(evt.y*1/self.scale)-self.offset[1]))
				self.draw()
				window.rightGraph.draw()
			else:
				nx =evt.x 
				ny = evt.y 
				if(self.shift):
					dy = (ny-self.my)*(self.scale)
					self.scale += dy/100
				else:
					dx = (nx-self.mx)*(1/self.scale)
					dy = (ny-self.my)*(1/self.scale)
					self.offset[0]+=dx;
					self.offset[1]+=dy;
				self.mx = nx
				self.my = ny
				self.draw()
			
			
	def keyPressHandler(self,evt):
		if(evt.keyval==65505):
			self.shift = True
			
	def keyReleaseHandler(self,evt):
		if(evt.keyval==65505):
			self.shift = False
	
	def draw(self):
		dim = self.area.get_allocation();
		self.area.queue_draw_area(0,0,dim.width,dim.height)

class GrapherWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="Complex Graphing Tool")
		box = Gtk.Box(spacing=2)
		box.set_homogeneous(False)
		self.connect("delete-event",Gtk.main_quit)
		self.leftArea = Gtk.DrawingArea()
		self.leftArea.set_size_request(500,500)
		self.rightArea = Gtk.DrawingArea()
		self.rightArea.set_size_request(500,500)
		rBox = Gtk.Box()
		rBox.set_homogeneous(False)
		rBox.pack_start(self.rightArea,True,True,0)
		lBox = Gtk.Box()
		lBox.set_homogeneous(False)
		lBox.pack_start(self.leftArea,True,True,0)
		
		self.leftGraph = Graph(self.leftArea,True)
		self.connect('key-press-event',lambda wid,evt : self.leftGraph.keyPressHandler(evt))
		self.connect('key-release-event',lambda wid,evt : self.leftGraph.keyReleaseHandler(evt))
		self.rightGraph = Graph(self.rightArea,False)
		self.connect('key-press-event',lambda wid,evt : self.rightGraph.keyPressHandler(evt))
		self.connect('key-release-event',lambda wid,evt : self.rightGraph.keyReleaseHandler(evt))
		
		self.rightGraph.points = self.leftGraph.points
		
		mainBox = Gtk.Box(spacing=2, orientation=Gtk.Orientation.VERTICAL);
		
		#add function input
		functionBox = Gtk.Box();
		functionBox.pack_start(Gtk.Label("function"),True,True,0)
		functionEntry = Gtk.Entry();
		self.functionEntry = functionEntry
		functionEntry.set_text(funcString);
		def functionEntryPress(wid,evt):
			nonlocal functionEntry
			if(evt.keyval ==  Gdk.KEY_Return):
				global funcString
				funcString	= self.functionEntry.get_text()
				print(funcString)
				self.leftGraph.draw()
				self.rightGraph.draw()		
		functionEntry.connect("key-press-event",functionEntryPress)
		functionBox.pack_start(functionEntry,True,True,0)
		mainBox.add(functionBox)
		
		#add step
		stepBox = Gtk.Box()
		stepLabel = Gtk.Label("step")
		stepBox.pack_start(stepLabel,True,True,0)
		self.stepEntry = Gtk.Entry()
		self.stepEntry.set_text(str(self.rightGraph.lineStep)+"")
		def handleStepChange(wid,evt):
			if(evt.keyval ==  Gdk.KEY_Return):
				step = eval(self.stepEntry.get_text())
				self.leftGraph.lineStep = step
				self.rightGraph.lineStep = step
				self.leftGraph.draw()
				self.rightGraph.draw()	
		self.stepEntry.connect("key-press-event",handleStepChange)
		stepBox.pack_start(self.stepEntry,True,True,0)
		mainBox.add(stepBox)
		
		#add grid controls
		self.gridMinXEntry = Gtk.Entry()
		self.gridMinXEntry.set_text(str(self.leftGraph.gridMin[0]))
		self.gridMinYEntry = Gtk.Entry()
		self.gridMinYEntry.set_text(str(self.leftGraph.gridMin[1]))
		self.gridMaxXEntry = Gtk.Entry()
		self.gridMaxXEntry.set_text(str(self.leftGraph.gridMax[0]))
		self.gridMaxYEntry = Gtk.Entry()
		self.gridMaxYEntry.set_text(str(self.leftGraph.gridMax[1]))
		self.gridStepXEntry = Gtk.Entry()
		self.gridStepXEntry.set_text(str(self.leftGraph.gridSize[0]))
		self.gridStepYEntry = Gtk.Entry()
		self.gridStepYEntry.set_text(str(self.leftGraph.gridSize[1]))
		
		def updateGrid(wid,evt):
			if(evt.keyval ==  Gdk.KEY_Return):
				gridMinX = eval(self.gridMinXEntry.get_text())
				gridMinY = eval(self.gridMinYEntry.get_text())
				gridMaxX = eval(self.gridMaxXEntry.get_text())
				gridMaxY = eval(self.gridMaxYEntry.get_text())
				gridStepX = eval(self.gridStepXEntry.get_text())
				gridStepY = eval(self.gridStepYEntry.get_text())
				self.leftGraph.gridMin = [gridMinX,gridMinY]
				self.leftGraph.gridMax = [gridMaxX,gridMaxY]
				self.leftGraph.gridSize = [gridStepX,gridStepY]
				self.rightGraph.gridMin = [gridMinX,gridMinY]
				self.rightGraph.gridMax = [gridMaxX,gridMaxY]
				self.rightGraph.gridSize = [gridStepX,gridStepY]
				self.leftGraph.draw()
				self.rightGraph.draw()

		self.gridMinXEntry.connect("key-press-event",updateGrid)	
		self.gridMinYEntry.connect("key-press-event",updateGrid)	
		self.gridMaxXEntry.connect("key-press-event",updateGrid)	
		self.gridMaxYEntry.connect("key-press-event",updateGrid)	
		self.gridStepXEntry.connect("key-press-event",updateGrid)	
		self.gridStepYEntry.connect("key-press-event",updateGrid)		
			
		gridMinBox = Gtk.Box();
		gridMinBox.add(Gtk.Label("grid mins"));
		gridMinBox.add(self.gridMinXEntry)
		gridMinBox.add(self.gridMinYEntry)
		mainBox.add(gridMinBox)
		gridMaxBox = Gtk.Box();
		gridMaxBox.add(Gtk.Label("grid maxes"));
		gridMaxBox.add(self.gridMaxXEntry)
		gridMaxBox.add(self.gridMaxYEntry)
		mainBox.add(gridMaxBox)
		gridStepBox = Gtk.Box();
		gridStepBox.add(Gtk.Label("grid steps"));
		gridStepBox.add(self.gridStepXEntry)
		gridStepBox.add(self.gridStepYEntry)
		mainBox.add(gridStepBox)
		
		#gridType controls
			
		gridTypeBox = Gtk.Box()
		gridTypeBox.pack_start(Gtk.Label("Grid Type: "),True,True,0)
		self.cartGridButton = Gtk.RadioButton.new_with_label_from_widget(None, "Cartesian")
		self.polarGridButton = Gtk.RadioButton.new_with_label_from_widget(self.cartGridButton, "Polar")
		def gridTypeUpdate(wid):
			if(self.cartGridButton.get_active() and self.leftGraph.type==GraphType.POLAR):
				self.leftGraph.type = GraphType.CARTESIAN
				self.rightGraph.type = GraphType.CARTESIAN
				self.leftGraph.gridMin[0] = -self.leftGraph.gridMax[0]
				self.leftGraph.gridMin[1] = self.leftGraph.gridMin[0]
				self.leftGraph.gridMax[1] = self.leftGraph.gridMax[0]
				self.leftGraph.gridSize[1] = self.leftGraph.gridSize[0] 
				self.rightGraph.gridMin[0] = -self.leftGraph.gridMax[0]
				self.rightGraph.gridMin[1] = self.leftGraph.gridMin[0]
				self.rightGraph.gridMax[1] = self.leftGraph.gridMax[0]
				self.rightGraph.gridSize[1] = self.leftGraph.gridSize[0]
				self.gridMinXEntry.set_text(str(self.leftGraph.gridMin[0])) 
				self.gridMinYEntry.set_text(str(self.leftGraph.gridMin[0]))
				self.gridMaxYEntry.set_text(str(self.leftGraph.gridMax[0]))
				self.gridStepYEntry.set_text(str(self.leftGraph.gridSize[0]))
				self.leftGraph.draw()
				self.rightGraph.draw()
			elif(self.polarGridButton.get_active() and self.leftGraph.type==GraphType.CARTESIAN):
				self.leftGraph.type = GraphType.POLAR
				self.rightGraph.type = GraphType.POLAR
				self.leftGraph.gridMin[1] = 0
				self.leftGraph.gridMin[0] = 0
				self.leftGraph.gridMax[1] = pi*2
				self.leftGraph.gridSize[1] = pi/5
				self.rightGraph.gridMin[0] = 0
				self.rightGraph.gridMin[1] = 0
				self.rightGraph.gridMax[1] = pi*2
				self.rightGraph.gridSize[1] = pi/5
				self.gridMinXEntry.set_text(str(0))
				self.gridMinYEntry.set_text(str(0))
				self.gridMaxYEntry.set_text("pi*2")
				self.gridStepYEntry.set_text("pi/5")
				self.leftGraph.draw()
				self.rightGraph.draw()
		self.cartGridButton.connect("toggled",gridTypeUpdate)
		self.polarGridButton.connect("toggled",gridTypeUpdate)
		gridTypeBox.pack_start(self.cartGridButton,True,True,0)
		gridTypeBox.pack_start(self.polarGridButton,True,True,0)
		mainBox.add(gridTypeBox)
		
		self.addPointsToggle = Gtk.ToggleButton("add points")
		self.addPointsToggle.set_active(False)
		def toggleAddPoints(wid):
			self.leftGraph.addPoints = self.addPointsToggle.get_active()
		self.addPointsToggle.connect("toggled",toggleAddPoints)
		mainBox.add(self.addPointsToggle)
		
		def reset(wid):
			self.leftGraph.offset = [0.5,0.5]
			dm = self.leftGraph.area.get_allocation()
			self.leftGraph.scale = max(dm.width,dm.height)
			self.rightGraph.offset = [0.5,0.5]
			self.rightGraph.scale = max(dm.width,dm.height)
			self.leftGraph.draw()
			self.rightGraph.draw()
		resetButton = Gtk.Button.new_with_label("reset position")
		resetButton.connect("clicked",reset)
		mainBox.add(resetButton)
		
		clearButton = Gtk.Button.new_with_label("clear points")
		def clear(wid):
			del self.leftGraph.points[:]
			self.leftGraph.draw()
			self.rightGraph.draw()
		clearButton.connect("clicked", clear)
		mainBox.add(clearButton)
		
		
		gridTogglesBox = Gtk.Box();
		self.gridToggle = Gtk.ToggleButton("Grid")
		self.gridToggle.set_active(True)
		self.axisToggle = Gtk.ToggleButton("Axis")
		self.axisToggle.set_active(True)
		def updateGridToggles(wid):
			self.leftGraph.drawGrid = self.gridToggle.get_active()
			self.rightGraph.drawGrid = self.gridToggle.get_active()
			self.leftGraph.drawAxis = self.axisToggle.get_active()
			self.rightGraph.drawAxis = self.axisToggle.get_active()
			self.leftGraph.draw()
			self.rightGraph.draw()
		self.gridToggle.connect("toggled",updateGridToggles)
		self.axisToggle.connect("toggled",updateGridToggles)
		gridTogglesBox.pack_start(self.gridToggle,True,True,0)
		gridTogglesBox.pack_start(self.axisToggle,True,True,0)
		mainBox.add(gridTogglesBox)
		
		box.pack_start(lBox,True,True,0)
		box.pack_start(mainBox,True,True,0)
		box.pack_start(rBox,True,True,0)
		self.add(box)
		
		
		
		
		
		
window = GrapherWindow()
window.show_all()
Gtk.main()
