from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from pytube import YouTube, Playlist, request
import time
from threading import Thread
import os

#global variables
mclr = "Seagreen"
l1clr = "white"
l3clr = "white"

#USED IN DOWNLOADING
url=""
resolution=""
d_path=os.getcwd()
type="video"
item_no=0
item_queued=0
var_list_status=""

#list variables
frame4=None
files_in_path=[]
url_list=[]
v_list=[] # to store list variabes
table_list=[] # all widgets in LF2 , this is used when all clear is pressed
resolution_list=["360p"]
#boolen type
d_flag=False
is_pause=False
is_cancel=False
cancel_flag=False
once_info_f=True
allclear_flag=False

# global functions
def error(flag):  # 1 for connection or link erroor #2 for download error
    var_list_status.set("   Error")
    if flag == 1:
        messagebox.showerror("ERROR", "INTERNET CONNECTION ERROR or INVALID LINK")
    elif flag==2:
        messagebox.showerror("ERROR", "RESOLUTION ERROR,TRY ANOTHER RESOLUTION")
    elif flag==3:
        messagebox.showerror("ERROR", "DOWNLOADING ERROR,TRY ANOTHER LINK")
    else:
        pass
def event_in_out(wid, clr):
    wid.bind('<Leave>', lambda e: e.widget.config(bg=clr))
    wid.bind('<Enter>', lambda e: e.widget.config(bg="light blue"))

def download(var_list):
    global item_queued, var_list_status
    var_list_status = var_list[1]
    flag=0
    os.chdir(d_path)
    if "playlist" in url:
        flag=1

    if flag==0 and type=="audio":
        d_flag= audio(var_list)
    elif flag==0 and type=="video":
        d_flag = video(var_list)
    elif flag==1 and type=="audio":
        d_flag = audio_playlist(var_list)
    else:
        d_flag = video_playlist(var_list)

    item_queued+=1
    time.sleep(0.5)
    if d_flag==0:
        var_list[1].set("Task Completed")
        messagebox.showinfo("STATUS", f"Download completed, files are stored at location {d_path}")
    else:
        return

def best_match_mp3(yt):
    flag=0
    try:
        d_lnk = yt.streams.filter(mime_type="audio/mp4", abr="160kbps")
        abr = ["160kbps", "128kbps", "70kbps", "50kbps"]

        if len(d_lnk) == 0:
            for br in abr:
                d_lnk = yt.streams.filter(mime_type="audio/mp4", abr=br)
                if len(d_lnk) != 0:
                    break

        if len(d_lnk) == 0: #any audio file match
            for br in abr:
                d_lnk = yt.streams.filter(type="audio",abr=br)
                if len(d_lnk) != 0:
                    break
        if len(d_lnk) == 0: # any match audio file
            d=yt.streams.filter("audio")

        d=d_lnk.first()

        if d!=None:
            files_in_path=os.listdir(d_path)
            filename=d.default_filename
            if filename in files_in_path:
                flag=1
        return d,flag
    except:
        return -1,None
def best_match_video(yt):
    flag = 0
    global resolution_list
    d_lnk=""
    #trying for exact match of resolution
    try:
        for item in resolution_list:
            d_lnk = yt.streams.filter(progressive=True ,file_extension="mp4",res=item)
            if len(d_lnk) != 0:
                break

        #any resolution match with video and progressive=true
        # if len(d_lnk)== 0:
        # d_lnk =yt.streams.filter(progressive=1, type="video")
        d=d_lnk.first()
        if d != None:
            files_in_path = os.listdir(d_path)
            filename = d.default_filename
            if filename in files_in_path:
                flag = 1
        return d, flag
    except:
        return None,0

def download_file(d,var_list):
    global is_pause,is_cancel,url
    try:
        file =d.default_filename
        size = d.filesize
        var_list[2].set(f"    {int(size / (1024 * 1024))}. MB")

        with open(file,'wb') as f:
            stream=request.stream(d.url)
            downloaded=0

            while True:
                if is_cancel:
                    var_list[1].set("Canceled")
                    return -1
                if is_pause:
                    time.sleep(1)
                    continue
                    # while 1:
                    #     if not is_pause:
                    #         break
                    #     time.sleep(1)
                chunk=next(stream,None)
                if chunk:
                    f.write(chunk)
                    downloaded+=len(chunk)
                    per=int((downloaded/size)*100)
                    per=str(per)
                    per+=" %"
                    per2="     "+per
                    var_list[3].set(per2)
                else:
                    break
        return 0
    except:
        return -3

def audio_playlist(var_list):
    global is_cancel
    link = url
    d_flag=0
    copy=0
    total_f=0
    error_no2 = False
    error_no3 = False
    try:
        pl = Playlist(link)
        var_list[0].set(f"     {item_no}. {pl.title}")
        vl = pl.videos
        fl=pl.video_urls

    except:
        error(1)
        return -1
    for i in fl:  # countint total files
        total_f += 1
    j = 0
    for item in vl:
        if is_cancel: #if downloading cancel is true then further downloading stops or break
            return -1

        j += 1
        set1 = "On Progress  " + f"{j}/{total_f}"
        var_list[1].set(set1)
        d,flag=best_match_mp3(item)
        if flag:
            copy=1
            continue
        if d!=None:
            var_list[4].set(f"    {d.type}  ,  {d.abr}")
            d_flag=download_file(d, var_list)
            if d_flag==-3:
                error_no3=True
        else:
            d_flag=-1
            error_no2=True
            continue
    if copy:
        messagebox.showinfo("INFORMATION", "NOT DOWNLOADED THOSE FILES, WHICH WERE ALREADY PRESENT IN THE SYSTEM")
    if error_no2:
        error(2)
    elif error_no3:
        error(3)
    else:
        pass
    return d_flag
def video_playlist(var_list):
    global d_path,url,is_cancel
    link = url
    d_flag=0
    copy=False
    total_f=0
    error_no2 = False
    error_no3 = False
    try:
        pl = Playlist(link)
        var_list[0].set(f"     {item_no}. {pl.title}")
        vl = pl.videos
        fl=pl.video_urls
    except:
        error(1)
        return -1
    for i in fl: #countint total files
        total_f += 1
    j = 0
    for item in vl:
        if is_cancel:  # if downloading cancel is true then further downloading stops or break
            return -1
        j += 1
        set1="On Progress  "+f"{j}/{total_f}"
        var_list[1].set(set1)
        d, flag = best_match_video(item)
        if flag == 1:
            copy=True
            continue
        if d != None:
            var_list[4].set(f"    {d.type}  ,  {d.resolution}")
            d_flag=download_file(d, var_list)
            if d_flag == -3:
                error_no3 = True
        else:
            d_flag = -1
            error_no2 = True
            continue
    if copy:
        messagebox.showinfo("INFORMATION", "NOT DOWNLOADED THOSE FILES, WHICH WERE ALREADY PRESENT IN THE SYSTEM")
    if error_no2:
        error(2)
    elif error_no3:
        error(3)
    else:
        pass
    return d_flag

def audio(var_list):
    link = url
    d_flag=0
    try:
        yt = YouTube(link)
        var_list[0].set(f"     {item_no}. {yt.title}")
    except:
        error(1)
        return -1
    set1 = "On Progress  " + f"{1}/{1}"
    var_list[1].set(set1)
    d, flag = best_match_mp3(yt)
    if flag:
        f = messagebox.askyesno("QUESTION",
                                "THIS  FILE  IS  ALREADY  PRESENT IN THE SYSYTEM, DO YOU STILL WANT TO DOWNLOAD?")
        if f ==False:
            var_list[1].set("Cancelled")
            return -1

    if d != None:
            var_list[4].set(f"    {d.type}  ,  {d.abr}")
            d_flag=download_file(d, var_list)
            if d_flag==-3:
                error(3)
    else:
        error(2)
        return -1
    return d_flag
def video(var_list):
    global d_path,url
    link = url
    d_flag=0
    try:
        yt = YouTube(link)
        var_list[0].set(f"     {item_no}. {yt.title}")
    except:
        error(1)
        return -1

    set1 = "On Progress  " + f"{1}/{1}"
    var_list[1].set(set1)
    d,flag = best_match_video(yt)
    if flag:
        f = messagebox.askyesno("QUESTION",
                                "THIS  FILE  IS  ALREADY  PRESENT IN THE SYSYTEM, DO YOU STILL WANT TO DOWNLOAD?")
        if f ==False:
            var_list[1].set("Canceled")
            return -1

    if d != None:
            var_list[4].set(f"    {d.type}  ,  {d.resolution}")
            d_flag=download_file(d, var_list)
            if d_flag == -3:
                error(3)
    else:
        error(2)
        return -1
    return d_flag


#---gui class------
class gui(Tk):
    def __int__(self):
        super().__init__()

    def run_gui(self):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.config(bg=mclr)
        self.swidth=w
        self.sheight=h
        self.title("Youtube Downloader by P.S.")

        l = Label(self, text="Enter  URLs  here", bg=mclr,font=2,)
        l.pack(anchor="nw", padx=15,pady=3)
        l1=LabelFrame(self,bg=l1clr,height=200,highlightcolor="light blue")
        l1.pack(fill="x",side="top",padx=5)

        self.l2 =Frame(self, bg=mclr, height=60 )
        # l1.place(x=100,y=500,)
        self.l2.pack(fill="x",padx=5,pady=10)

        self.l3 = LabelFrame(self, bg=l3clr, height=h-420, )
        self.l3.pack(fill="x",padx=5 )

        l4=Frame(self,height=100,bg=mclr)
        l4.pack(fill="x",padx=5 )
        global frame4
        frame4=l4

#------------------------------------------------------design label 1--------------------------------------------
        sv=Scrollbar(l1)
        sv.pack(fill="y",side="right")

        sh = Scrollbar(l1,orient=HORIZONTAL)
        sh.pack(fill="x", side="bottom")

        onepixel=169/1366
        self.onepixel=onepixel
        textwidth=int(onepixel*(w))
        n=Text(l1,height=10,width=textwidth,yscrollcommand=sv.set,xscrollcommand=sh.set,bd=0)
        # n.grid(row=0,column=0,)
        n.pack(fill="x",expand=1)
        sv.config(command=n.yview)
        sh.config(command=n.xview)
        self.main_text_wid=n
        start.label2()

    def take_input_link(self,txt):
        input_link = txt.get("1.0", END)
        if len(input_link)<=1:
            messagebox.showinfo("information","PLEASE  ENTER  THE  LINK, then press the button")
        else:
            txt.delete('1.0',END)
            global url_list
            url_list.append(input_link)
            self.make_table(input_link)

    def label2(self):
        #-ading 2 buttons and entry and path------------
        b1=Button(self.l2,text="ADD TO DOWNLOAD",bg="light goldenrod",height=1,command=lambda txt=self.main_text_wid:self.take_input_link(txt))
        b1.place(x=10,y=15)
        event_in_out(b1,"light goldenrod")

        mypath=StringVar()
        mypath.set(os.getcwd())
        e1=Entry(self.l2,text=mypath,width=50,font=0)
        e1.place(x=230,y=16)
        e1.bind("<Key>",lambda  a:"break")
        event_in_out(e1,"white")

        b2 = Button(self.l2, text="PATH", bg="light goldenrod", height=1, command=lambda p=mypath: self.openpath(p))
        b2.place(x=180, y=15)
        event_in_out(b2,"light goldenrod")
        #-----setting type button and entry--------------------------------------------------------------
        b3 = Button(self.l2, text="TYPE", bg="light goldenrod", height=1)
        b3.place(x=850, y=15)
        event_in_out(b3, "light goldenrod")
        type_var = StringVar()
        e2 = Entry(self.l2,text=type_var, width=15,font="5" )
        e2.insert(0,"default (video)")
        e2.place(x=895, y=16)
        e2.bind("<Key>",lambda  a:"break")
        event_in_out(e2, "white")
        #------setting resolution button and entry--------------------------------------------------------
        # b4 = Button(self.l2, text="RESOLUTION", bg="light goldenrod", height=1,)
        b4=Menubutton(self.l2, text="RESOLUTION", bg="light goldenrod", height=1,relief=RAISED,activebackground="light blue")
        b4.place(x=1100, y=15)
        # event_in_out(b4, "light goldenrod")
        self.b4=b4

        def info1():
            global once_info_f
            if once_info_f == True:
                messagebox.showinfo("Read",
                                    "ON SELECTING MULTIPLE RESOLUTIONS, HEIGHEST RESOLUTION VIDEO MATCH WILL BE DOWNLOAD")
                once_info_f=False
        b4.bind('<Enter>',lambda event:info1())

        res_var = StringVar()
        e3 = Entry(self.l2,text=res_var, width=30,)#font="5" )  # state=DISABLED,bg="white")
        e3.insert(0,"default (360p)")
        e3.place(x=1190, y=16)
        e3.bind("<Key>",lambda  a:"break")
        event_in_out(e3, "white")
        # self.e3=e3
        #--------------1menu for type-------------------------------------------
        m = Menu(self, tearoff=0)
        m.add_command(label=" Video (mp4)",command=lambda opt=1,text="video",wid=e2,var=type_var: self.choose(opt,text,var))
        m.add_command(label=" Audio (mp3)",command=lambda opt=1,text="audio",wid=e2,var=type_var: self.choose(opt,text,var))

        def do_pop1():
            try:
                m.tk_popup(x=920, y=295)
            finally:
                m.grab_release()

        b3.config(command=do_pop1)
        # --------------1menu resolution--------------------------------------------------------
        view_menu = Menu(b4, tearoff=0)
        op=["720p", "480p", "360p", "240p", "144p"]
        vl = []
        for item in op:
            opt2 = BooleanVar(value=False)
            # if item=="360p":
            #     opt2.set(1)
            view_menu.add_checkbutton(label=item, variable=opt2,onvalue=1, offvalue=0,command=self.choose_res)
            vl.append(opt2)
        self.vl=vl
        self.var=res_var
        def y():
            for item in vl:
                item.set(1)
            self.choose_res()
        def ynot():
            for item in vl:
                item.set(0)
            self.choose_res()
            resolution_list.append("360p")
            self.var.set("default (360p)")

        view_menu.add_command(label="Select all", command=y)
        view_menu.add_command(label="Unselect all", command=ynot)
        b4['menu'] = view_menu

        start.label3()

    def choose_res(self):
        global resolution_list
        resolution_list.clear()
        op=["720p", "480p", "360p", "240p", "144p"]
        vl=self.vl
        for i in range(0,5):
            if vl[i].get()==1:
                if op[i] not in resolution_list:
                    resolution_list.append(op[i])
            else:
                if op[i] in resolution_list:
                    resolution_list.remove(op[i])
        res_ = ""
        for i in resolution_list:
            res_ +=i
            res_ +=", "
        self.var.set(res_)
        if len(resolution_list) == 0:
            resolution_list.append("360p")
            self.var.set("default (360p)")

    def choose(self,option,text,var): #optin 1==type,
        if option==1:
            # self.type=text
            global type
            type=text
            var.set(f"  {text}")
            if text=="audio":
                self.b4.config(state=DISABLED,)
            else:
                self.b4.config(state=NORMAL,)

    def openpath(self,var):
        global d_path
        d_path=filedialog.askdirectory()
        var.set(d_path)

    def label3(self):
        c=Canvas(self.l3,height=self.sheight-420,bd=0)
        c.pack(fill="x",expand=1)

        fr1=Frame(c,)
        c.create_window((0,0),window=fr1,anchor="nw",)#height=800,width=3000)
    #-----------------------------------------------------------------------------------
        h=self.onepixel
        w1=int((h*self.swidth)/2)
        _w2=int(h*self.swidth)-w1
        w2=int(_w2/5)

        v1 = StringVar()
        em1 = Entry(fr1, text=v1, font="Arial,10,", width=w1-20, )  # ,width=100)
        em1.grid(row=0,column=0)
        em1.bind('<Key>',lambda a:"break")
        v1.set(" TITLE")

        options=[" STATUS."," SIZE."," % COMPLETE"," EXTENSION"," SPEED"]
        i=1
        for item in options:
            em = Entry(fr1, font="Arial,10,", width=w2, )  # ,width=100)
            em.grid(row=0, column=i)
            em.insert(0,item)
            em.bind('<Key>', lambda a: "break")
            i=i+1
        self.l3_tableframe=fr1
        self.dim=[]
        self.dim.append((w1-20))
        self.dim.append((w2))
        self.row=1

    def make_table(self,link):
        w1=self.dim[0]
        w2=self.dim[1]
        var_list=[]

        v=StringVar()
        em1 = Entry(self.l3_tableframe, text=v, width=w1+32, )  # ,width=100)
        em1.grid(row=self.row, column=0)
        em1.bind('<Key>', lambda a: "break")
        em1.insert(0,f"{self.row}. {link}")
        var_list.append(v)
        table_list.append(em1)

        options = ["QUED.", "SIZE", "% complete", "time left", "speed"]
        i = 1
        for item in options:
            v2 = StringVar()
            em = Entry(self.l3_tableframe,text=v2, width=w2+8, )  # ,width=100)
            em.grid(row=self.row, column=i)
            em.insert(0, "-----")
            em.bind('<Key>', lambda a: "break")
            i = i + 1
            var_list.append(v2)
            table_list.append(em)

        var_list[1].set("   Queued")
        var_list[3].set("   0 %")
        self.row+=1 #d'not delete it
        global item_no,v_list
        item_no+=1
        v_list.append(var_list)
        return

def start_down_2():
    global url,url_list,is_cancel,is_pause,allclear_flag
    for item in url_list:
        if allclear_flag:
            break
        url = item
        is_pause = is_cancel = False
        pause_button['text'] = "PAUSE"
        var = v_list[item_queued]
        download(var)

    url_list.clear()
    start_download['state'] = NORMAL

def start_down():
    global url,url_list, is_cancel, is_pause, item_queued,allclear_flag

    if len(url_list)==0:
        messagebox.showwarning("warning","NO ITEM TO DOWNLOAD")
    else:
        allclear_flag=False
        pause_button['text'] = "PAUSE"
        pause_button['state'] = NORMAL
        delete_button['state'] = NORMAL
        start_download['state'] = DISABLED

        Thread(target=start_down_2,daemon=True).start()

def pause_res():
    global is_pause
    is_pause=not is_pause
    pause_button['text']="RESUME" if is_pause else 'PAUSE'

def cancel_():
    global is_cancel
    res=messagebox.askyesno("DELETE","YOU,CAN NOT UNDO THIS ACTION,DO YOU WANT TO STOP DOWNLOADING")
    if res==True:
        is_cancel=1

def clear_():
    res = messagebox.askyesno("DELETE", "YOU,CAN NOT UNDO THIS ACTION,DO YOU WANT TO STOP DOWNLOADING")
    if res == True:
        global allclear_flag,table_list,is_cancel

        allclear_flag=True
        is_cancel=True
        url_list.clear()
        for item in table_list:
            item.destroy()
        table_list.clear()
        start_download['state'] = NORMAL

def exit_():
    res = messagebox.askyesno("EXIT", "ARE YOU SURE WANT TO EXIT")
    if res == True:
        exit()

start=gui()
start.run_gui()

clr="light goldenrod"
exit_=Button(frame4,text="EXIT",bg=clr,command=exit_)
exit_.grid(row=0,column=10,sticky=E,padx=30,pady=10)
event_in_out(exit_,clr)

start_download=Button(frame4,text="START  DOWNLOAD",bg=clr,command=start_down)
start_download.grid(row=0,column=1,padx=20,pady=10)
event_in_out(start_download,clr)

pause_button=Button(frame4,text="PAUSE",bg=clr,state="disabled",command=pause_res)
pause_button.grid(row=0,column=2,padx=20,pady=10)
event_in_out(pause_button,clr)

delete_button=Button(frame4,text="CANCEL",bg=clr,state=DISABLED,command=cancel_)
delete_button.grid(row=0,column=3,padx=20,pady=10)
event_in_out(delete_button,clr)

allclear_button=Button(frame4,text="CLEAR ALL",bg=clr,command=clear_)
allclear_button.grid(row=0,column=4)


start.mainloop()