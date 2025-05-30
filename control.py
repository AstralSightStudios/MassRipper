import os
import ripper
import version
import webbrowser
import tkinter as tk
from loguru import logger
from tkinter import messagebox
from tkinter import filedialog

class Controller:
    # 导入UI类后，替换以下的 object 类型，将获得 IDE 属性提示功能
    ui: object

    def __init__(self):
        pass

    def log(self, text):

        output = self.ui.tk_text_log_text

        output.config(state=tk.NORMAL)
        output.insert(tk.END, text)
        output.config(state=tk.DISABLED)
    
    def init(self, ui):
        self.ui = ui

        logger.add(self.log, level="INFO")
        logger.add("massripper.log", rotation="1 MB")
        
        self.ripper = ripper.MassRipper()
        self.cur_file = ""
        self.ui.tk_text_log_text.config(state=tk.DISABLED)
        self.ui.tb_meter_file_completion_rate.configure(amountused = 0)
        
        logger.info("MassRipper %s 初始化完毕!" % version.version)
        logger.info("\n提示:\n1.双击文本框可快速选择文件\n2.使用前请先安装wireshark否则无法正常解析捕获文件\n3.右上角菜单可保存目前已分析的数据\n4.可通过继续添加捕获文件来补全文件完整度与识别新文件")
    
    def menu_file_save_project(self):
        try:
            path = filedialog.asksaveasfilename(filetypes=(("project file", "*.mass"),))

            if path == "":
                return

            if not path.endswith(".mass"):
                path += ".mass"
            open(path, 'wb').write(self.ripper.dump_files())
            messagebox.showinfo('提示', '项目文件保存成功!')
        except Exception as e:
            logger.error(e)
            messagebox.showerror('错误', '项目文件保存失败!')
    
    def menu_file_load_project(self):
        try:
            path = filedialog.askopenfilename(filetypes=(("project file", "*.mass"),))

            if path == "":
                return

            data = open(path, 'rb').read()
            self.ripper.load_files(data)
            self.refresh_list()
            messagebox.showinfo('提示', '项目文件加载成功!')
        except Exception as e:
            logger.error(e)
            messagebox.showerror('错误', '项目文件加载失败!')

    def choose_file(self,evt):

        input_text = self.ui.tk_text_pcap_path

        path = filedialog.askopenfilename(filetypes=(("btsnoop file", "*.log;*.pcap"),))
        if path != "":
            input_text.delete('1.0', tk.END)
            input_text.insert(tk.END, path)
    
    def analyze_pacp(self,evt):
        try:
            path = self.ui.tk_text_pcap_path.get("1.0","end").strip()

            if path == "":
                messagebox.showerror('错误', '请先选择追踪文件后再进行分析!')
                return
            
            if not os.path.exists(path):
                messagebox.showerror('错误', '路径错误文件不存在!')
                return

            succ = self.ripper.load_pcap(path)
            if succ:
                self.refresh_list()
                messagebox.showinfo('提示', '追踪文件分析成功!')
            else:
                messagebox.showerror('错误', '追踪文件分析失败!')
        except ripper.WireSharkError:
            messagebox.showerror('错误', '请先安装wireshark后再进行分析!')
            webbrowser.open("https://www.wireshark.org/download.html")
        except Exception as e:
            logger.error(e)
            messagebox.showerror('错误', '追踪文件分析失败!')
    
    def refresh_list(self):
        
        table = self.ui.tk_table_file_list

        table.delete(*table.get_children())

        for file in self.ripper.get_file_list():
            table.insert('', 'end', values=(file))
        
        self.cur_file = ""
        self.ui.tb_meter_file_completion_rate.configure(amountused = 0)

    def select_file(self,evt):

        table = self.ui.tk_table_file_list

        if len(table.selection()) >= 1:
            
            selected_item = table.selection()[0]
            item = table.item(selected_item)
            text = list(item.values())[2][0]
            self.cur_file = text

            file = self.ripper.get_file(self.cur_file)
            self.ui.tb_meter_file_completion_rate.configure(amountused = (len(file["blocks"]) / file["total"]) * 100)

            logger.info("已选中 %s" % self.cur_file)

    
    def export_select_file(self,evt):
        try:
            path = filedialog.asksaveasfilename(filetypes=(("export file", "*.rpk;*.bin"),))

            if path == "":
                return
            
            if not (path.endswith(".bin") or path.endswith(".rpk")):
                info = self.ripper.get_file(self.cur_file)
                if info["data_type"] == ripper.MassDataType.ThirdpartyApp:
                    path += ".rpk"
                else:
                    path += ".bin"

            data = self.ripper.export_file(self.cur_file)
            if data != b'':
                open(path, 'wb').write(data)
                messagebox.showinfo('提示', '文件导出成功!')
            else:
                messagebox.showerror('错误', '文件导出失败!')
        except Exception as e:
            logger.error(e)
            messagebox.showerror('错误', '文件导出失败!')
        
    
    def export_all_file(self,evt):
        try:
            path = filedialog.askdirectory()

            if path == "":
                return

            for file in self.ripper.get_file_list():
                try:
                    data = self.ripper.export_file(file)
                    info = self.ripper.get_file(file)

                    if info["data_type"] == ripper.MassDataType.ThirdpartyApp:
                        save_path = os.path.join(path, file + ".rpk")
                    else:
                        save_path = os.path.join(path, file + ".bin")
                    
                    if data != b'':
                        open(save_path, 'wb').write(data)
                    else:
                        messagebox.showerror('错误', '文件 %s 导出失败!' % file)
                except Exception as e:
                    logger.error(e)
                    messagebox.showerror('错误', '文件 %s 导出失败!' % file)

            messagebox.showinfo('提示', '批量导出完毕!')

        except Exception as e:
            logger.error(e)
            messagebox.showerror('错误', '文件导出失败!')
    
