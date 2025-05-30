import random
from tkinter import *
from tkinter.ttk import *
from ttkbootstrap import *
from pytkUI.widgets import *
class WinGUI(Window):
    def __init__(self):
        super().__init__(themename="cosmo", hdpi=False)
        self.__win()
        self.tk_label_pcap_path_lable = self.__tk_label_pcap_path_lable(self)
        self.tk_text_pcap_path = self.__tk_text_pcap_path(self)
        self.tk_button_analyze_pcap = self.__tk_button_analyze_pcap(self)
        self.tk_label_frame_files_frame = self.__tk_label_frame_files_frame(self)
        self.tk_table_file_list = self.__tk_table_file_list( self.tk_label_frame_files_frame) 
        self.tk_button_export_select_file = self.__tk_button_export_select_file( self.tk_label_frame_files_frame) 
        self.tk_button_export_all_file = self.__tk_button_export_all_file( self.tk_label_frame_files_frame) 
        self.tb_meter_file_completion_rate = self.__tb_meter_file_completion_rate(self)
        self.tk_label_frame_log_frame = self.__tk_label_frame_log_frame(self)
        self.tk_text_log_text = self.__tk_text_log_text( self.tk_label_frame_log_frame) 
    def __win(self):
        self.title("MassRipper")
        # 设置窗口大小、居中
        width = 544
        height = 500
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        
        self.resizable(width=False, height=False)
        
    def scrollbar_autohide(self,vbar, hbar, widget):
        """自动隐藏滚动条"""
        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)
        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)
        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())
    
    def v_scrollbar(self,vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')
    def h_scrollbar(self,hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')
    def create_bar(self,master, widget,is_vbar,is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)
    def new_style(self,widget):
        ctl = widget.cget('style')
        ctl = "".join(random.sample('0123456789',5)) + "." + ctl
        widget.configure(style=ctl)
        return ctl
    def __tk_label_pcap_path_lable(self,parent):
        label = Label(parent,text="btsnoop文件:",anchor="center", bootstyle="default")
        label.place(x=8, y=15, width=97, height=30)
        return label
    def __tk_text_pcap_path(self,parent):
        text = Text(parent)
        text.place(x=99, y=15, width=341, height=30)
        return text
    def __tk_button_analyze_pcap(self,parent):
        btn = Button(parent, text="分析文件", takefocus=False,bootstyle="default")
        btn.place(x=447, y=15, width=75, height=30)
        return btn
    def __tk_label_frame_files_frame(self,parent):
        frame = LabelFrame(parent,text="文件列表",bootstyle="default")
        frame.place(x=11, y=53, width=210, height=265)
        return frame
    def __tk_table_file_list(self,parent):
        # 表头字段 表头宽度
        columns = {"hash":192}
        tk_table = Treeview(parent, show="headings", columns=list(columns),bootstyle="default")
        for text, width in columns.items():  # 批量设置列属性
            tk_table.heading(text, text=text, anchor='center')
            tk_table.column(text, anchor='center', width=width, stretch=False)  # stretch 不自动拉伸
        
        tk_table.place(x=7, y=1, width=195, height=195)
        return tk_table
    def __tk_button_export_select_file(self,parent):
        btn = Button(parent, text="导出选中文件", takefocus=False,bootstyle="default")
        btn.place(x=7, y=206, width=95, height=30)
        return btn
    def __tk_button_export_all_file(self,parent):
        btn = Button(parent, text="导出所有文件", takefocus=False,bootstyle="default")
        btn.place(x=107, y=206, width=95, height=30)
        return btn
    def __tb_meter_file_completion_rate(self,parent):
        meter = Meter(parent,amountused=100, amounttotal=100, subtext="文件完整性", metersize=250,
        textleft="", textright="%", interactive=False,
        bootstyle="default")
        meter.place(x=257, y=65, width=250, height=250)
        return meter
    def __tk_label_frame_log_frame(self,parent):
        frame = LabelFrame(parent,text="日志",bootstyle="default")
        frame.place(x=11, y=322, width=520, height=169)
        return frame
    def __tk_text_log_text(self,parent):
        text = Text(parent)
        text.place(x=7, y=1, width=506, height=142)
        self.create_bar(parent, text,True, False, 7, 1, 506,142,520,169)
        return text
class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.config(menu=self.create_menu())
        self.ctl.init(self)
    def create_menu(self):
        menu = Menu(self,tearoff=False)
        menu.add_cascade(label="文件",menu=self.menu_file(menu))
        return menu
    def menu_file(self,parent):
        menu = Menu(parent,tearoff=False)
        menu.add_command(label="保存项目",command=self.ctl.menu_file_save_project)
        menu.add_command(label="加载项目",command=self.ctl.menu_file_load_project)
        return menu
    def __event_bind(self):
        self.tk_text_pcap_path.bind('<Double-Button-1>',self.ctl.choose_file)
        self.tk_button_analyze_pcap.bind('<Button-1>',self.ctl.analyze_pacp)
        self.tk_table_file_list.bind('<<TreeviewSelect>>',self.ctl.select_file)
        self.tk_button_export_select_file.bind('<Button-1>',self.ctl.export_select_file)
        self.tk_button_export_all_file.bind('<Button-1>',self.ctl.export_all_file)
        pass
    def __style_config(self):
        sty = Style()
        sty.configure(self.new_style(self.tk_label_pcap_path_lable),font=("微软雅黑",-12))
        sty.configure(self.new_style(self.tk_button_analyze_pcap),font=("微软雅黑",-12))
        sty.configure(self.new_style(self.tk_button_export_select_file),font=("微软雅黑",-12))
        sty.configure(self.new_style(self.tk_button_export_all_file),font=("微软雅黑",-12))
        pass
if __name__ == "__main__":
    win = WinGUI()
    win.mainloop()