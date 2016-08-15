"""
Fake Webcam Streamer

HTTP Port, camera resolutions and framerate are hardcoded to keep it
simple but the program can be updated to take options.

Default HTTP Port 8080, 320x240 resolution and 6 frames per second.
Point your browser at http://localhost:8080/

Note if you want people to think it's a real camera, you might need to set
things up so that the URL it is found at looks like:
http://<ip-address>/axis-cgi/mjpg/video.cgi

At least for the Axis IP camera.

This is based on the original Trollcam by Tom (fridgehead).
"""

import signal
import sys
import tempfile
import threading
import time

import BaseHTTPServer
import SocketServer
from PIL import Image
import StringIO
from PIL import ImageEnhance
from PIL import ImageFilter
from PIL import ImageFont
from PIL import ImageDraw
import random
import numpy

class HTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
  def __init__(self, server_address):
    SocketServer.TCPServer.__init__(self, server_address, HTTPHandler)

   
class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  """
  HTTP Request Handler
  """
  def do_GET(self): 
    if self.path[:2] == "/":
              # This needs to be checked against the actual IP cam as I'm sure
              # this is wrong.  Very few people are likely to check this
              # closely.
              self.server_version = "nginx/1.11.1"
              self.sys_version = ""
              # mjpeg boundary. LOL
              #boundary = "MPDLHTS" 
              boundary = "myboundary" # From Axis M1011-W IP camera
              self.send_response(200)
              self.send_header("Access-Control-Allow-Origin", "*")
              self.send_header("Content-type",
                               "multipart/x-mixed-replace;boundary=%s"
                               % boundary)
              self.end_headers()        
              # Create a string buffer for the final jpeg encoded image
              sbuf = StringIO.StringIO()
              # Load the background image
              pilimg = Image.open("cam.jpg")
              # Cache the dimensions of the image
              width, height = pilimg.size
              # Get a brightness adjusting thingy
              bright = ImageEnhance.Brightness(pilimg) 
              sbuf.seek(0)
              factor = 0
              while True:
                # Hour and minute for the current time.
                toh = time.gmtime().tm_hour
                tom = time.gmtime().tm_min
                # Set the brightness factor for sunrise, day, sunset and night
                if 7 <= toh < 8 :
                  # sunrise
                  factor = 0.2 + (tom) * (0.4/60) 
                elif 16 <= toh < 17:
                  # sunset
                  factor = 0.2 + (60 - tom) * (0.4/60) 
                elif 8 <= toh <=16:
                  factor = 0.6
                else:
                  factor = 0.2
                # Vary the brightness a little to give the jpeg encoder something to chew on
                factor += (random.random() / 10.0)
                # Blur the image to simulate ebay-camera-lense
                pil = pilimg.filter(ImageFilter.BLUR)
                # Now apply The Darkening
                pil = bright.enhance(factor)

                # Lets caption this so people think its a Motion stream
                t = time.strftime("%H:%M:%S-00", time.gmtime())
                t2 = time.strftime("%d-%m-%Y", time.gmtime())
                draw = ImageDraw.Draw(pil)
                # Font has been processed from silkscr.ttf to a pil and pbm file in this folder
                fn = ImageFont.load('slkscr.pil')
                # The AXIS IP cameras usually draw a black line across the top
                # of the image, and put the text along that.
                # I'm making some assumptions about the minimum image size
                # here. To be robust they should really be corrected, but this
                # should work for any image of a reasonable size for a webcam.
                draw.line([(0,0),(width,0)], fill=000, width=40)
                draw.text((2,7), "AXIS Communications AB", font=fn)
                draw.text(((width-120),7), t2, font=fn)
                draw.text(((width-60),7), t, font=fn)
                del draw

                # Save the processed image to the string buffer, making sure
                # to set the quality low to give it that "just streamed over
                # dialup" feel.
                sbuf.seek(0)
                pil.save(sbuf, format='jpeg', quality=20)

                # Send the data to the client
                response = "Content-type: image/jpeg\n\n"
                response = response + sbuf.getvalue()
                response = response + "\n--%s\n" % boundary
                self.wfile.write(response)    
                # Sleep for 5 secs, otherwise Chrome whinges that the site is in a redirect loop
                time.sleep(5)
                
    else:
      self.send_error(404, "This is not the page you're looking for.")
      self.end_headers()
    
  do_HEAD = do_POST = do_GET

if __name__ == '__main__':
  print "Started webcam streamer"

  def quit(signum, frame):
    print "Quitting..."
    sys.exit(0)

  
  signal.signal(signal.SIGINT, quit)
  signal.signal(signal.SIGTERM, quit)
  
  http_server = HTTPServer(server_address=("",8080)) 

  http_server_thread = threading.Thread(target = http_server.serve_forever())
  http_server_thread.setDaemon(true)
  http_server_thread.start()
  
  try:
    while True:
      http_server_thread.join(60)
  except KeyboardInterrupt:
    quit()
