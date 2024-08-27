import wx
import json
import socket
from pathlib import Path
import os
from datetime import datetime
import sys

class InitialSetup(wx.Dialog):
    """Dialog pro počáteční nastavení aplikace."""
    def __init__(self, parent):
        super().__init__(parent, title="Initial Setup", size=(400, 300))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.fields = {
            'ip': 'IP',
            'port': 'Port',
            'company_name': 'Company Name',
            'ra': 'RA',
            'control': 'Control Provided By'
        }
        
        for key, label in self.fields.items():
            box = wx.BoxSizer(wx.HORIZONTAL)
            lbl = wx.StaticText(panel, label=label)
            txt = wx.TextCtrl(panel)
            self.fields[key] = txt
            box.Add(lbl, flag=wx.RIGHT, border=8)
            box.Add(txt, proportion=1)
            vbox.Add(box, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        
        save_btn = wx.Button(panel, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        vbox.Add(save_btn, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        
        panel.SetSizer(vbox)

    def on_save(self, event):
        settings = {key: txt.GetValue() for key, txt in self.fields.items()}
        settings_file = Path(os.path.expanduser('~')) / 'Documents' / 'app_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        self.EndModal(wx.ID_OK)

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(400, 400))
        self.saved_settings = {}
        settings_file = Path(os.path.expanduser('~')) / 'Documents' / 'app_settings.json'
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    self.saved_settings = json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.fields = {
            'ip': ('IP tiskárny:', self.saved_settings.get('ip', '192.168.1.1')),
            'port': ('Port tiskárny:', self.saved_settings.get('port', '9100')),
            'company_name': ('Jméno společnosti:', self.saved_settings.get('company_name', '')),
            'ra': ('RA:', self.saved_settings.get('ra', '')),
            'control': ('Control Provided By:', self.saved_settings.get('control', ''))
        }
        
        for key, (label, default) in self.fields.items():
            box = wx.BoxSizer(wx.HORIZONTAL)
            lbl = wx.StaticText(panel, label=label)
            txt = wx.TextCtrl(panel, value=default)
            self.fields[key] = txt
            box.Add(lbl, flag=wx.RIGHT, border=8)
            box.Add(txt, proportion=1)
            vbox.Add(box, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        
        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        
        vbox.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        panel.SetSizer(vbox)

    def get_settings(self):
        return {key: txt.GetValue() for key, txt in self.fields.items()}

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(200, 500))
        icon = wx.IconLocation(sys.executable, 0)
        self.SetIcon(wx.Icon(icon))
        self.settings = {}
        self.load_settings()
        self.selected_control = "SPX — XRY"

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.radio_box = wx.RadioBox(panel, label="Vyber kontrolu", choices=["SPX by XRY", "SPX by XRY/ETD", "SPX by PHS/ETD", "SPX by VCK/ETD", "SPX by VCK/PHS", "SPX by KC", "SPX by RA/RCVD", "SPX by EXEMPTED-BIOM", "SPX by EXEMPTED-NUCL"], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.radio_box.Bind(wx.EVT_RADIOBOX, self.on_radio_select)

        self.name_label = wx.StaticText(panel, label="Jméno:")
        self.name_text = wx.TextCtrl(panel)

        self.count_label = wx.StaticText(panel, label="Počet:")
        self.count_text = wx.TextCtrl(panel, value="1")

        self.btn_submit = wx.Button(panel, label="Potvrdit")
        self.btn_submit.Bind(wx.EVT_BUTTON, self.on_submit)

        self.btn_clear = wx.Button(panel, label="Vymazat")
        self.btn_clear.Bind(wx.EVT_BUTTON, self.on_clear)

        self.btn_settings = wx.Button(panel, label="Nastavení")
        self.btn_settings.Bind(wx.EVT_BUTTON, self.on_settings)

        main_sizer.AddStretchSpacer()
        main_sizer.Add(self.radio_box, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.name_label, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.name_text, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.count_label, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.count_text, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.btn_submit, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.btn_clear, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.btn_settings, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.AddStretchSpacer()

        panel.SetSizer(main_sizer)
        self.Show()

    def load_settings(self):
        settings_file = Path(os.path.expanduser('~')) / 'Documents' / 'app_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                self.settings = json.load(f)

    def on_radio_select(self, event):
        self.selected_control = self.radio_box.GetStringSelection()
        if not self.selected_control:  # Přidáno: kontrola, zda je výběr prázdný
            self.selected_control = "SPX by XRY"  # Přidáno: nastavení výchozí hodnoty, pokud je výběr prázdný
        print("Selected:", self.selected_control)


    def print_to_printer(self, ip_address, port, text, copies):
        for _ in range(copies):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ip_address, port))
                    sock.sendall(text.encode('utf-8'))
            except Exception as e:
                print(f"Error printing: {e}")

    def on_submit(self, event):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d%b%y %H:%M").upper()  
        company_name = self.settings.get('company_name', '')
        ra = self.settings.get('ra', '')
        control = self.settings.get('control', '')
        name = self.name_text.GetValue()
        label_number = self.get_next_label_number()  # Replace or generate based on your logic
        copies = int(self.count_text.GetValue())
        selected_control = getattr(self, 'selected_control', 'Not selected')  # Bezpečnostní opatření, pokud by 'selected_control' nebylo definováno


        for _ in range(copies):
            label_number = self.get_next_label_number()  # Generuje nové sériové číslo pro každý štítek
            ip_address = self.settings.get('ip', '192.168.1.1')
            port = int(self.settings.get('port', 9100))
            zpl_code = self.generate_zpl(company_name, ra, control, formatted_datetime, name, label_number, selected_control)  # Vytvoří ZPL kód pro tento štítek
    
            # Logika pro tisk štítku; každý štítek se tiskne jednou
            self.print_to_printer(ip_address, port, zpl_code, 1)
    
            # Výpis dat pro každý štítek pro účely ladění
            print(f"DateTime: {formatted_datetime}, IP: {ip_address}, Port: {port}, Control: {control}, Copies: {copies}, LabelNumber: {label_number}, RA: {ra}, Company: {company_name}, Name: {name}, SelectedControl: {selected_control}")

    
    def get_next_label_number(self):
        # Načte aktuální číslo štítku a převede ho na číslo
        label_number = int(self.settings.get('label_number', '117823'))
        # Zvýší číslo štítku
        label_number = (label_number + 1) % 1000000  # Resetuje se po dosažení 999999
        # Aktualizuje nastavení se novým číslem štítku
        self.settings['label_number'] = f"{label_number:06d}"
        # Uloží nastavení
        settings_file = Path(os.path.expanduser('~')) / 'Documents' / 'app_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
        # Vrátí nové číslo štítku jako řetězec
        return self.settings['label_number']

    def generate_zpl(self, company_name, ra, control, formatted_datetime, name, label_number, selected_control):
        # Implement ZPL code generation here based on your requirements
        # This is a placeholder function. Replace it with actual data.
        return f"""^XA
        ^CI28
        ^FO10,10
^FO10,10^GB730,173,3^FS        ; Vnější rámeček
^FO10,10^GB365,35,3^FS          ; Horní levá buňka
^FO10,10^GB730,35,3^FS          ; Horní pravá buňka
^FO10,10^GB730,70,3^FS          ; Střední buňka
^FO10,10^GB730,140,3^FS         ; Spodní rámeček
^FO105,150^GB0,30,3^FS            ; První vertikální čára
^FO245,150^GB0,30,3^FS            ; Druhá vertikální čára
^FO310,150^GB0,30,3^FS            ; Třetí vertikální čára
^FO545,150^GB0,30,3^FS            ; Čtvrtá vertikální čára
^FO625,150^GB0,30,3^FS            ; Pátá vertikální čára
^CF0,20,20
^FO15,155
^FDDate&Time^FS    ; Datum a čas
^CF0,20,20
^FO115,155
^FD{formatted_datetime}^FS    ; Datum a čas
^CF0,50,50
^FO250,100
^FD{selected_control}^FS                   ; SPX BY XRY
^CF0,30,30
^FO100,15
^FD{company_name}^FS                 ; Název společnosti
^CF0,30,30
^FO30,50
^FD{control}^FS             ; Bezpečnostní kontrola
^CF0,30,30
^FO450,15
^FD{ra}^FS                ; Kód
^CF0,20,20
^FO255,155
^FDNAME^FS               ; Jméno
^CF0,25,25
^FO365,155
^FD{name}^FS               ; Jméno
^CF0,20,20
^FO575,155
^FDNr.^FS                   ; Číslo
^CF0,20,20
^FO650,155
^FD{label_number}^FS                   ; Číslo

        ^XZ"""

    def on_clear(self, event):
        self.name_text.Clear()
        self.count_text.SetValue("1")

    def on_settings(self, event):
        dialog = SettingsDialog(self, "Nastavení")
        if dialog.ShowModal() == wx.ID_OK:
            new_settings = dialog.get_settings()
            settings_file = Path(os.path.expanduser('~')) / 'Documents' / 'app_settings.json'
            with open(settings_file, 'w') as f:
                json.dump(new_settings, f, indent=4)
            self.load_settings()  # Znovu načíst nastavení po jejich změně
            print("Nastavení bylo aktualizováno.")
        dialog.Destroy()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame(None, "Moje Aplikace")
    app.MainLoop()