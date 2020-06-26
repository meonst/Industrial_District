import heroprotocol
import heroprotocol.versions.protocol29406 as protocol29406
from heroprotocol.versions import build, latest

import pprint
import json
import tkinter, tkinter.filedialog
import mpyq
print("Hello World")

plane = tkinter.Tk()
plane.title("Replay")
plane.geometry("1000x500")

def open_replay():
    plane.filename = tkinter.filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("replay files","*.StormReplay"),("all files","*.*")))
    archive = mpyq.MPQArchive(plane.filename)
    print(archive)

    # Read the protocol header, this can be read with any protocol
    contents = archive.header['user_data_header']['content']
    header = latest().decode_replay_header(contents)
    pprint.pprint(header)
    

    
    
    
open_replay()
