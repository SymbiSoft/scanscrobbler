"""

~~~~~~~~~~~~~
ScanScrobbler
~~~~~~~~~~~~~


Description
~~~~~~~~~~~

ScanScrobbler is a simple script designed to make it possible to submit an 
albums worth of tracks to a last.fm account.
The premise behind the script is that it is not usually possible to scrobble 
things you hav listened to from CD on any non-data drive (eg on a regular car 
or domestic hifi).
The script aims to identify the CD you wish to scrobble by scanning the 
barcode, using a free third party application, 'UpCode', available from the 
Ovi Store. This must be downloaded and installed on your phone for this part 
of the scipt to work.
The script will also allow you to input the barcode digits manually, although 
this is not a guaranteed way to work, as digits displayed under barcodes 
frequently omit a checksum digit only readable using a barcode reader (such 
as UpCode).


Script Requirements
~~~~~~~~~~~~~~~~~~~

The script uses 3 external libraries which must be installed in your path for 
the script to function.

Beautiful Soup -  http://www.crummy.com/software/BeautifulSoup/
    An html/xml parser
Pyscrobbler - http://code.google.com/p/pyscrobbler/
    a set of python classes for interacting with the last.fm audioscrobbler services
PowerClipboard - http://cyke64.googlepages.com/clipboard.py
    for retrieving info from the phone's clipboard

In order to scan a barcode, the script also requires installation of the 
barcode reader 'UpCode'
   http://www.upcode.fi/mobile/pc_download.asp?language=1
   UpCode is also available at the Ovi Store

   
Last.fm accounts and privacy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Account details (usernames and passwords) are currently stored in an 
UNENCRYPTED database.
If this concerns you, don't use ScanScrobbler.


Coding TODO
~~~~~~~~~~~

* Add option for scrobbling just some tracks from the album
* Provide handling for multiple matches in the database for one barcode
  I have yet to encounter this behaviour, please let me know if you experience
  it. 
* Encrypt stored last.fm passwords
* Find python native barcode reading library that works on S60


Further Info
~~~~~~~~~~~~

http://www.moppy.co.uk/projects/scancscrobbler/


License
~~~~~~~

This software is distributed under the MIT license:

Copyright (c) 2009 Martin Hatfield

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

# import stuff
import sys, urllib2, appuifw, scriptext, e32, e32dbm, pickle
from time import time, strftime
from datetime import *

# sys.path.append("e:\\Python\\lib")

import BeautifulSoup, clipboard
from audioscrobbler import *

lfm_user = 'none selected'
lfm_pass = 'no pass'

# Version no. 
SIS_VERSION = "0.0.1"
# application lock
lock = e32.Ao_lock()
# external application launch lock
launchlock = e32.Ao_lock()
# define the database
user_db = u'e:\\python\\lastfmusers.e32dbm' 
prefs_file = u'e:\\python\\ss_prefs.txt'
prefs = {}


def quit():
    '''
    Exit the application
    '''  
    lock.signal()
    

def msg(text):
    '''
    Simple wrapper for displaying messages to the user
    
    @type text: string
    @param text: The message to display to the user
    '''
    
    appuifw.note(unicode(text), 'info')
   
   
def tip(text):
    '''
    Simple wrapper for displaying tips, (user can choose to hide these in 
    settings)
    
    @type text: string
    @param text: The message to display to the user
    '''
    if prefs.get('show_tips') == True:
        msg(text)

        
def info(text):
    '''
    Displays tool-tip like info to the user (usually to display scrobbling 
    progress)
    
    @type text: unicode string
    @param text: The message to display to the user
    '''
    
    # Get screen dimensions to determine orientation
    screen_size, screen_position = appuifw.app.layout(appuifw.EScreen)
    # Get  application title  pane dimensions
    title_size, title_position = appuifw.app.layout(appuifw.ETitlePane)
    # Get universal indicator pane (where eg new message icon displays) dimensions
    indicator_size, indicator_position = appuifw.app.layout(appuifw.EUniversalIndicatorPane)
    # Determine the orientation
    if (screen_size[0] > screen_size[1]):
        orient = 'landscape'
        # Display popup to right of title
        popup_position = (title_size[0] + title_position[0], indicator_position[1])
    else:
        orient = 'portrait'
        # Display popup below title (long tooltips will overlap top listbox item on main pane)
        popup_position = (title_position[0], title_size[1] + title_position[1])
    popup.show(text, popup_position)
    
    
def load_prefs():
    '''
    Attempts to load preferences from the pref file, and the account details 
    from the user database
    '''
    try:
        global prefs
        global lfm_user
        global lfm_pass
        # open the preference file, and load them into the prefs dictionary variable
        file = open(prefs_file, 'r')
        prefs = pickle.load(file)
        # Get the last used last.fm user account
        lfm_user = prefs.get('default_user')
        # Get the password for that account
        db = e32dbm.open(user_db,"r")
        lfm_pass = db.get(lfm_user)
        db.close()
        file.close()
    except:
        msg('Please add a last.fm user account')
        add_user()

        
def add_user():
    '''
    Adds a last fm user account name and password to the database
    '''
    # Query for account name and password
    myuser = appuifw.query(u'user?', 'text')
    mypwd = appuifw.query(u'password', 'code')
    #store them in the database
    db = e32dbm.open(user_db,"c") 
    db[unicode(myuser)] = unicode(mypwd)
    db.close()
    select_user()

    
def select_user():
    '''
    Allows user to select which last.fm account to scrobble to. If only one 
    user exists in the 
    database, it is selected automatically
    '''
    global prefs
    users = []
    # Open the user database
    db = e32dbm.open(user_db,"r")
    # Compile a list of user names
    for key, value in db.items():
        users.append(unicode(key))
    # If only one user exists, select it automatically
    if len(users) == 1:
        selected_user = 0
    else:
    # otherwise give the user a choice
        selected_user = appuifw.popup_menu(users, u"Select a user:") 
    # Save the selected account to prefs
    prefs['default_user'] = str(users[selected_user])
    file = open(prefs_file, 'w')
    pickle.dump(prefs, file)
    file.close()
    # Load the prefs again to regoster the user change
    load_prefs()
    # Update the screen for user
    draw_screen()

	
def delete_user():
    '''
    Prompts the user to select a last.fm account to delete from the database
    '''
    users = []
    # Open the user account database
    db = e32dbm.open(user_db,"c")
    # Compile a list of account names
    for key, value in db.items():
        users.append(unicode(key))
    # Prompt the user
    selected_user = appuifw.popup_menu(users, u"Select a user to delete:")
    # Convert to unicode to display confirmation prompt
    uni_user = unicode(users[selected_user])
    proceed = appuifw.query(u'Delete account and password for ' + uni_user + u'?', 'query')
    if proceed == 1:
        #delete user from db
        del db[unicode(users[selected_user])]
        msg('deleted!')
    db.close()
    # Select user
    select_user() # TODO: Calling this here may trigger an error if you have deleted all user accounts

    
def about():
    '''
    Displays a short message about scanscrobbler
    '''
    msg('Scan Scrobbler v' + SIS_VERSION + '\ntwitter.com/hairyhatfield\n(c)Martin Hatfield')

    
    
def identify_release(barcode):
    '''
    Takes a barcode string and submits it as a query to musicbrainz.org 
    webservice to determine the release details - artist, title and mbid (musicbrainz id)
    
    @type barcode: string
    @param barcode: a string of digits (usually 12-13 digits) corresponding to a barcode on a CD
    
    @rtype found: bool
    @return found: True if a match was found in the musicbrainz database for the submitted barcode, 
    otherwise False
    @rtype mbid: string
    @return mbid: the unique musicbrainz id of the release with the matching barcode. 0 if no match found
    @rtype title: string
    @return title: title of the release. 0 if no match found
    @rtype artist: string
    @return artist: artist name of release. 0 if no match found
    '''
    # Construct the query
    query = 'http://musicbrainz.org/ws/1/release/?typeso=xml&query=barcode:' + barcode
    # Let the user know we're doing something
    info(u'Finding release details...')
    # required to enable popup to show!
    e32.ao_sleep(0.1)
    
    try:
        # Send the query request
        f = urllib2.urlopen(query)
    except urllib2.URLError:
        msg('No connection made. Maybe you cancelled the connection or your connection settings need adjustment.')
        # No match found due to error, return appropriate value
        return False, 0, 0, 0
        
    # parse the query results as an xml file
    soup = BeautifulSoup.BeautifulStoneSoup(f.read())

    # Count the matches, let the user know
    try:
        matches = soup.first('release-list')['count']
        # Have yet to encounter a situation where (matches > 1) please let me know of any barcodes where this is the case!!
        msg(matches + ' match(es) found\n')
    except TypeError:
        msg('no match found for\n' + barcode)
        return False, 0, 0, 0

    # get the important values of the first release
    title = str(soup.first('title').string)
    # This is "Various Artists" for compilations
    artist = str(soup.first('artist').first('name').string)
    mbid = str(soup.first('release')['id'])
    # return a successful match
    return True, mbid, title, artist

    
def scrobble_tracks(mbid, title, artist, now):
    '''
    Scrobbles the tracks to last.fm from the given musicbrainz release id
    
    @type mbid: string
    @param mbid: the unique musicbrainz id of the release to scrobble.
    @type title: string
    @param title: title of the release.
    @type artist: string
    @param artist: artist name of release.
    @type now: datetime.utcnow
    @param now: current time, used to determine time tracks were played
    '''
    # Construct the query
    query = 'http://musicbrainz.org/ws/1/release/' + str(mbid) + '?type=xml&inc=tracks'
    try:
        # send the query request
        f = urllib2.urlopen(query)
    except urllib2.URLError:
        msg('No connection made. Maybe you cancelled the connection or your connection settings need adjustment.')
        return

    # Parse the results as xml
    soup = BeautifulSoup.BeautifulStoneSoup(f.read())
    # Locate all the tracks for this release
    tracks = soup.findAll('track')
    
    # initialise a variable
    album_duration = 0
    
    # Calculate the length of the album
    for track in tracks:
        album_duration = album_duration + (int(track.duration.string) / 1000)

    # Convert this to a timedelta 
    alb_td_duration = timedelta(seconds=album_duration)
    # Subtract from current time  to give the time the album started playing
    start_time = now - alb_td_duration    
        
    for track in tracks:
        # Get the info needed for scrobbling each track
        track_id = str(track['id']) # the unique musicbrainz track id
        track_title = str(track.title.string)
        track_duration = int(track.duration.string) / 1000
        # artist only appears within track on compilation albums
        track_artist = track.find('artist')
        if (track_artist > 0):
            # Its a compilation, use the track specific artist
            artist =  str(track.artist.first('name').string)
        # Feedback to the user
        info(u'Scrobbling "' + track_title.decode('utf-8') + u'"')
        # Not sure why this is so, but the tootltip gets hidden without an ao_sleep
        e32.ao_sleep(0.01)
        
        # Calculate the track length and time started playing
        td_duration = timedelta(seconds=track_duration)
        strdate_played = start_time.strftime("%Y-%m-%d %H:%M:%S")

        # Compile the track info for scrobbling
        trk_obj = dict(artist_name=artist,
                         song_title=track_title,
                         length=track_duration,
                         date_played=strdate_played, 
                         album=title,
                         mbid=track_id
                        )
        # Scrobble it
        post = AudioScrobblerPost(username=lfm_user, password=lfm_pass)
        post(**trk_obj)
        
        # Reset start time for next track
        start_time = start_time + td_duration
    # Let the user know we're done
    info(u'Scrobbling complete!')

    
def launch_app_callback(trans_id, event_id, input_params):
    '''
    Called when UpCode quits, releases the lock
    '''
    #if trans_id != appmanager_id and event_id != scriptext.EventCompleted:
    #    print "Error in servicing the request"
    #    print "Error code is: " + str(input_params["ReturnValue"]["ErrorCode"])
    #    if "ErrorMessage" in input_params["ReturnValue"]:
    #        print "Error message is: " + input_params["ReturnValue"]["ErrorMessage"]
    #else:
    #    print "\nWaiting for UpCode to close"
    
    # Release the lock
    launchlock.signal()


def scan_barcode():
    '''
    Launches UpCode to scan a barcode, and then returns barcode string, as copied from clipboard
    
    @rtype: string
    @return: barcode digits from the clipboard
    '''
    
    # Tell the user what they need to do in the upcode application
    tip('Launching UpCode to scan barcode.\nAlter the UpCode settings to scan as a 1D barcode')
    tip('Select "No" when prompted "Open site?", and then exit UpCode')
    # Load appmanage service
    appmanager_handle = scriptext.load('Service.AppManager', 'IAppManager')
    # Make a request to query the required information in asynchronous mode
    appmanager_id = appmanager_handle.call('LaunchApp', {'ApplicationID': u's60uid://0x2000c83e'}, callback=launch_app_callback)
    launchlock.wait()
    
    # Get the barcode form the clipboard (UpCode pastes it there when you select 'No' to the prompt "Open Site?")
    barcode = clipboard.Get()
    return barcode


def input_barcode():
    '''
    Allows user to enter barcode digits by hand
    
    @rtype: string
    @return: barcode as a string of digits
    '''
    # This needs to be a query of type 'text' and not 'number' as 'number' will not accept 12 digits!
    barcode = appuifw.query(u'Please enter a 12 or 13 digit barcode', 'text')
    
    # return as a string
    return str(barcode)
    

def is_barcode(barcode):
    '''
    Checks to see if a value matches a barcode acceptable format - 12-13 numeric digits
    
    @type barcode: string
    @param barcode: value to check
    @rtype: bool
    @return: True if matches barcoe format, False otherwise
    '''

    if (type(barcode) is str) and ((len(barcode) == 12) or (len(barcode) == 13)) and barcode.isdigit:
        return True
    else:
        return False

        
def handle_selection():
    '''
    Handles the selections made from the main body listbox, triggering main program actions
    '''
    lb = appuifw.app.body
    if (lb.current() == 0): # Scan a barcode
        barcode = scan_barcode()
    elif (lb.current() == 1): # Submit barcoe from clipboard
        barcode = clipboard.Get()
    elif (lb.current() == 2): # Input barcode by hand
        barcode = input_barcode()
    elif (lb.current() == 3): # Change user
        users = []
        # Open the user database
        db = e32dbm.open(user_db,"r")
        # Compile a list of user names
        for key, value in db.items():
            users.append(unicode(key))
        # If only one (user exists, , or no user has yet been input, prompt to add another one
        if (len(users) == 1) or lfm_user == 'none selected':
            msg('please add a new last.fm account.\nYou can switch between them at any time')
            add_user()
        else:
            select_user()
        return
    # elif (lb.current() == 4):
        # Debuging stuff goes here!
        # return 
    
    # Initialise a variable
    found = False
    # Test for barcode format compliance
    if is_barcode(barcode):
        found, mbid, album, artist = identify_release(barcode)
    else:
        tip('Valid barcodes should be 12 or 13 numeric characters long.')
        try_anyway = appuifw.query(u'Some barcode entries on musicbrainz are incorrectly formatted. Attempt to match your input against these?', 'query')
        if (try_anyway == 1):
            found, mbid, album, artist = identify_release(barcode)
        else:
            return
    # Let the user know what we found and see if they want to scrobble it
    if found:
        go = appuifw.query(u'Found: ' + artist.decode('utf-8') + u' - ' + album.decode('utf-8') + u'\nScrobble tracks to ' + lfm_user.decode('utf-8') + u' account?', 'query')
        # Initiate the scrobbling function
        if (go == 1):
            # senc the time to the function to enable submission of time played to last.fm
            now = datetime.datetime.utcnow()
            scrobble_tracks(mbid, album, artist, now)
        else:
            msg('Scrobbling cancelled')
            
def switch_tips():
    '''
    Toggles showing/hiding of tips
    '''
    global prefs
    # Get the current preference, and toggle it
    if prefs.get('show_tips') == True:
        prefs['show_tips'] = False
    else:
        prefs['show_tips'] = True
    # resave the preferences
    file = open(prefs_file, 'w')
    pickle.dump(prefs, file)
    file.close()
    # draw the screen to update the menu
    draw_screen()
    
def draw_screen():
    '''
    Draws the screen contents. Needs calling on startup, and once preferences are changed, to ensure 
    that the display of variables onscreen (eg lfm_user and tip_action) are up to date
    '''
    # Set the application body up
    appuifw.app.exit_key_handler = quit
    appuifw.app.title = u'ScanScrobbler'
    appuifw.app.screen = 'normal'
    entries = [(u'Scan a barcode', u'Opens UpCode for scanning'),
               (u'Submit barcode from clipboard', u"If you've already copied a barcode there"),
               (u'Enter barcode by hand', u'Using numeric keypad'),
               (u'Change last.fm account', unicode('currently ' + lfm_user)),
               #(u'Do debugging stuff', u"Let's get happy"), # Enable this entry for custom debugging stuff
              ]
    # Compile the listbox
    lb = appuifw.Listbox(entries, handle_selection)
    # Set the listbox to display in the main body
    appuifw.app.body = lb
    # Determine current status of tips and associated action to display in user Options menu
    if prefs.get('show_tips') == True:
        tip_action = u'Hide'
    else:
        tip_action = u'Show'
    # Set up the Options menu
    appuifw.app.menu = [(u'last.fm settings', 
                            ((u'Enter last.fm settings', add_user),
                            (u'Select last.fm user', select_user),
                            (u'Delete user', delete_user))), 
                        (tip_action + u' tips', switch_tips),
                        (u'About', about)]
# Startup stuff
load_prefs()
draw_screen()
popup = appuifw.InfoPopup()
lock.wait()