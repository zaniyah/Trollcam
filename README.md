
A fairly basic, fake MJPEG camera stream. Loads the "cam.jpg" file and attempts
to make it "webcammy".  It implements a basic day/night cycle and fake auto-gain
spazzes.

Serves this on its own HTTP server on port 8080, though you can get it to use
a different port by passing --port X.

./trollcam.py --port 9000

Remember that on Linux you won't be able to use ports <1024 without some extra
work.  You may want to consider running this as a user with minimal
privileges, perhaps within some kind of container, and port-forwarding the
relevant ports (eg 80) to whichever port it is listening on.

This was originally forked from Trollcam, with the idea that it would be fun
to create a minimalistic honeypot IP camera capable of being listed on shodan.io
and convincing the more than mildly nosy.

== Wishlist ==

* Make camera model specific details something that can be configured, perhaps
  in a yaml config file.
* Add support for RTSP
* Output interesting information about accesses to the camera, in a format
  that can be munged with a script to give interesting stats on where those
  attempts originate from, and what form they take.

