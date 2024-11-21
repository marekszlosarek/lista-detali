from __future__ import annotations
import os
import json
import re
from fpdf import FPDF, XPos, YPos
from datetime import datetime
import tkinter as tk


class SettingsHandler:
    def __init__(self) -> None:
        self.settings: dict = self.loadSettings()

    def loadSettings(self) -> dict:
        try:
            with open('settings.json', 'r') as file:
                data= json.load(file)
                return data
        except (FileNotFoundError):
            return self.generateDefaultSettings()

    def generateDefaultSettings(self) -> dict:
        default = {
            'IMAGE_FOLDER': '\\\\server\\Maszyny\\Bysprint Fiber 2000\\Ustawienia Bysoft 7\\Parts\\PRODUKCJA',
        }
        with open('settings.json', 'w') as settings:
            settings.write(json.dumps(default))

        return default
  
    def getImageFolder(self) -> str:
        return self.settings['IMAGE_FOLDER']



class Component:
    def __init__(
            self,
            filename: str,
            count: int,
            thickness: float,
            sheet: str,
            engraver: bool,
            detail: Detail,
        ) -> None:
        self.filename = filename
        self.thickness = thickness
        self.count = count
        self.sheet = sheet
        self.engraver = engraver
        self.detail = detail

    def display(self):
        print(f'Nazwa - {self.filename}:\n\tLiczba na komplet: {self.count}\n\tRodzaj blachy: {self.sheet}\n\tGrawer: {'Tak' if self.engraver else 'Nie'}')


class Detail:
    def __init__(self, serialNumber: str, imagePath: str) -> None:
        self.serialNumber: str = serialNumber
        self.components: list[Component] = [] 
        self.imagePath= imagePath

    def generatePDF(self) -> bool:
        if not self.serialNumber.isnumeric():
            return False

        self.fillComponentList()
        if len(self.components) == 0:
            return False

        pdf = PDF(self, self.imagePath, 'P', 'mm', 'A5')

        pdf.generateDetailComponentListTable()

        if not os.path.exists('output'):
            os.makedirs('output')
        
        self.fileName = f'output\\SN_{self.serialNumber}.pdf'
        pdf.output(self.fileName)
    
        return True


    def fillComponentList(self):
        for root, dirs, files in os.walk(self.imagePath):
            for filename in files:
                if filename.endswith('png') and (
                    filename.startswith(self.serialNumber + ' ') or 
                    filename.startswith(self.serialNumber + '-') or
                    filename.startswith(self.serialNumber + '_') 
                ):
                    self.components.append(self.generateComponent(filename))

        self.components.sort(key=lambda component: component.thickness)

    def generateComponent(self, filename: str) -> Component:
        filename = filename.removesuffix('.png')
        fixedName = filename.replace(' ', '_').replace('#_', '#') + '_'
        while '__' in fixedName:
            fixedName.replace('__', '_')

        # Wartości numeryczne pomiędzy nawiasami
        countSearch = re.findall(r"\((\d+)\)", fixedName) 
        if len(countSearch) > 0:
            count = countSearch[0]
        else:
            count = 1

        # Wartość od "#" do pierwszego podkreślnika
        thicknessSearch: list[str] = re.findall(r"#([^_]*)", fixedName)
        try:
            thickness = float(thicknessSearch[0].replace(',', '.'))
        except (IndexError, ValueError): 
            thickness = 999

        # Wartość od "#" do drugiego podkreślnika
        sheetSearch: list[str] = re.findall(r"(#[^_]*_[^_]*)", fixedName) 
        if len(sheetSearch) > 0:
            sheet = sheetSearch[0].replace('_', ' ')
        else:
            sheet = '???'

        # Jeżeli aluminium, sprawdź czy nie ma konkretnego gatunku później
        if sheet.lower().endswith('almg3'):
            sheetSearch: list[str] = re.findall(r"(#[^_]*_[^_]*_[^_]*)", fixedName) 
            if len(sheetSearch) > 0:
                sheet = sheetSearch[0].replace('_', ' ')
        else:
            index = sheet.lower().find('almg3')
            if index > -1:
                sheet = sheet[:index+5] + ' ' + sheet[index+5:]

        engraver = 'gr' in fixedName.lower()

        return Component(
            filename=filename,
            count=count,
            thickness=thickness,
            sheet=sheet,
            engraver=engraver,
            detail=self
        )
    
    def display(self) -> None:
        print('SN', self.serialNumber)
        for component in self.components:
            component.display()


class PDF(FPDF):
    def __init__(self, detail: Detail, imagePath: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.detail = detail
        self.imagePath = imagePath
        self.supported_characters = set("""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-!? '"()[]{}#_+""")

    def header(self) -> None:
        self.set_font('times', 'B', 20)
        self.cell(0, 10, f'SN {self.detail.serialNumber}', border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font('times', 'I', 10)
        footerText = "Wygenerowane automatycznie przez skrypt w fazie testowej."
        footerText2= "Wygenerowano:"
        footerText3= "Wszystkie niezgodnosci prosze zglosic do Marka Szlosarka z G9."
        footerTimestamp = datetime.now().strftime('%d.%m.%y %H:%M')
        self.cell(0, 5, footerText, border=False)
        self.cell(0, 5, footerText2, border=False, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.cell(0, 5, footerText3, border=False)
        self.cell(0, 5, footerTimestamp, border=False, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(20) 

    def generateDetailComponentListTable(self) -> None:
        gap = '\t'
        self.set_auto_page_break(auto=True, margin=15)
        self.set_fill_color(255, 255, 255)

        for i, component in enumerate(self.detail.components):
            # Dodaj strony przy pierwszym i co szóstym detalu
            if not i%5:
                self.add_page()

            # Dane detalu
            self.set_line_width(.05)
            self.set_font('times', 'I', 6)
            self.cell(75, 6, "Nazwa:")
            self.cell(15, 6, "Na komplet:")
            self.set_x(10)

            self.set_font('times', '', 12)
            self.cell(75, 15, gap+''.join(c for c in component.filename if c in self.supported_characters))
            self.cell(15, 15, gap+str(component.count))

            self.cell(30, 30, '', border=True)
            self.ln(15)

            self.set_font('times', 'I', 6)
            self.cell(75, 6, "Blacha:")
            self.cell(15, 6, "Grawer:")
            self.set_x(10)

            self.set_font('times', '', 12)
            self.cell(75, 15, gap+component.sheet)
            self.cell(15, 15, gap+('Tak' if component.engraver else 'Nie'))
            


            # Obrazek
            img_pos_size = {
                'x': 100,
                'y': 30*(i%5)+20,
                'w': 30,
                'h': 30
            }
            self.image(os.path.join(self.imagePath, component.filename+'.png'), keep_aspect_ratio=True, **img_pos_size)

            # Numer składowej
            self.ln(10.5)
            self.set_x(100)
            self.cell(None, None, f'{i+1}/{len(self.detail.components)}', border=True, fill=True)
            self.ln(4.5)

            # Linie przerywane między komórkami
            line_pos = [
                {
                    'x1': 10,
                    'y1': 30*(i%5)+35,
                    'x2': 100,
                    'y2': 30*(i%5)+35,
                },
                {
                    'x1': 85,
                    'y1': 30*(i%5)+20,
                    'x2': 85,
                    'y2': 30*(i%5)+50,
                },
            ]

            self.set_dash_pattern(1, 1)
            for pos in line_pos:
                self.line(**pos)
            self.set_dash_pattern()

            self.set_line_width(.4)
            self.ln(-30)
            self.cell(120, 30, '', border=True)
            self.ln(30)


class MainWindow:
    def __init__(self, root: tk.Tk, settings: SettingsHandler) -> None:
        self.root = root
        self.root.resizable(width=False, height=False)
        self.root.title('Lista Składowych Detalu')
        self.root.geometry('448x317')
        root.iconbitmap("_internal\\resources\\icon.ico")
        self.root.bind('<Key>', self.keyPress)
        
        self.background = tk.PhotoImage(file = '.\\_internal\\resources\\background.png')
        self.canvas = tk.Canvas(self.root, width=450, height=317)
        self.canvas.place(x=-2, y=0)
        self.canvas.create_image(0, 0, image=self.background, anchor='nw')
        
        self.snLabel = tk.Label(self.root, font=['Times', 20, 'bold'], width=3, text = 'SN ', bg='#FFFFFF')
        self.snLabel.place(x=300, y=190)

        self.checkEntryText = tk.StringVar()
        self.checkEntryText.trace_add('write', self.checkEntry)
        self.snEntry = tk.Entry(self.root, font=['Times', 20, 'bold'], width=5, textvariable=self.checkEntryText)
        self.snEntry.config(borderwidth=0)
        self.snEntry.place(x=345, y=190, height=37)

        self.snButton = tk.Button(self.root, text='Generuj PDF', font=['Times', 13, 'bold'], command=self.generatePDF, state=tk.DISABLED)
        self.canvasSnButton = self.canvas.create_window(
            302, 230,
            anchor='nw',
            window=self.snButton,
            width=118,
            height=37
        ) 

        self.snResultId = self.canvas.create_text(360, 280, text='', fill='#ffffff', font='Times') 

        self.snExplanationFrame = tk.Frame(root, width=135, height=50, bg="#fffdaf")
        self.snExplanationFrame.place(x=300, y=138)
        self.snExplanation = tk.Label(self.snExplanationFrame, text="Wprowadź SN detalu,\nktórego listę składowych\nchcesz wygenerować:", bg="#fffdaf", fg="#000000", bd=1, relief="solid", anchor='ne', justify=tk.LEFT, height=3, borderwidth=0)
        self.snExplanation.place(x=0, y=0)
        self.snExplanationInit = True

        self.imagePath = settings.getImageFolder()


    def generatePDF(self) -> None:
        sn = self.snEntry.get()
        detail = Detail(sn, self.imagePath)
        self.canvas.itemconfig(self.snResultId, text = 'Generuję PDF...')
        self.root.update()
        if detail.generatePDF():
            os.startfile(detail.fileName)
            self.checkEntryText.set('')
            self.canvas.itemconfig(self.snResultId, text = 'PDF wygenerowany')
            return
        
        self.canvas.itemconfig(self.snResultId, text = 'SN nie znaleziony')
        
    def checkEntry(self, *args) -> None:
        if self.snExplanationInit:
            self.snExplanationInit = False
            self.phase = 1
            self.boxColor = 0x000000
            self.height = 50
            self.width = 135
            self.disableSnExplanation()
        if self.checkEntryText.get():
            self.snButton.config(state=tk.NORMAL)
        else:
            self.snButton.config(state=tk.DISABLED)

        if len(self.checkEntryText.get()) > 5:
            self.checkEntryText.set(self.checkEntryText.get()[:5])

        self.canvas.itemconfig(self.snResultId, text = '')
            
    def keyPress(self, event: tk.Event) -> None:
        if not event.keysym == 'Return':
            return

        if self.checkEntryText.get():
            self.generatePDF()

    def disableSnExplanation(self) -> None:
        match self.phase:
            case 1:
                self.boxColor += int(0x111108)
                if self.boxColor > 0xfffdaf:
                    self.boxColor = 0xfffdaf
                    self.phase = 2
                self.snExplanation.config(fg=f'#{self.boxColor:02x}')
                self.root.after(25, self.disableSnExplanation)
            case 2:
                self.height -= 4
                if self.height <= 0:
                    self.height = 0
                self.width -= 10
                if self.width <= 0:
                    self.width = 0
                if self.width == self.height == 0:
                    self.phase = 3
                self.snExplanationFrame.config(height=self.height, width=self.width)
                self.snExplanationFrame.place(x=300, y=187-self.height)
                self.root.after(15, self.disableSnExplanation)
            case 3:
                self.snExplanationFrame.destroy()



if __name__ == '__main__':
    root = tk.Tk()
    settings = SettingsHandler()
    app = MainWindow(root, settings)
    root.mainloop()

