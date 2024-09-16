from __future__ import annotations
import os
import re
from fpdf import FPDF, XPos, YPos
from dotenv import load_dotenv
from datetime import datetime


"""
Copyright (C) Marek Szlosarek, 2024

Niniejsza licencja udziela firmie CZEKAMET PL Sp. z o.o. Sp. K. prawa do korzystania, modyfikowania i dystrybucji tego kodu wyłącznie w okresie zatrudnienia licencjodawcy (twórcy kodu) w firmie.

Zabrania się korzystania, modyfikowania oraz dystrybucji tego kodu przez firmę lub jej przedstawicieli po zakończeniu współpracy (umowy) z licencjodawcą.

Kod nie może być przekazywany osobom trzecim ani używany poza firmą bez wyraźnej, pisemnej zgody licencjodawcy.

W przypadku zakończenia współpracy wszystkie kopie kodu muszą zostać zwrócone lub zniszczone, chyba że licencjodawca wyrazi zgodę na inne warunki na piśmie.

Naruszenie tych warunków spowoduje natychmiastowe unieważnienie licencji.

Marek Szlosarek
14.09.2024
"""


load_dotenv()
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER')


class Component:
    def __init__(
            self,
            filename: str,
            count: int,
            sheet: str,
            engraver: bool,
            detail: Detail,
        ) -> None:
        self.filename = filename
        self.count = count
        self.sheet = sheet
        self.engraver = engraver
        self.detail = detail

    def display(self):
        print(f'Nazwa - {self.filename}:\n\tLiczba na komplet: {self.count}\n\tRodzaj blachy: {self.sheet}\n\tGrawer: {'Tak' if self.engraver else 'Nie'}')


class Detail:
    def __init__(self, serialNumber: str) -> None:
        self.serialNumber: str = serialNumber
        self.components: list[Component] = [] 

    def generatePDF(self) -> None:
        self.fillComponentList()

        if len(self.components) == 0:
            print(f'Detal "SN {self.serialNumber}" nie znaleziony.')
            return

        pdf = PDF(self, 'P', 'mm', 'A5')

        pdf.generateDetailComponentListTable()

        if not os.path.exists('output'):
            os.makedirs('output')

        pdf.output(fileName := f'output\\SN_{self.serialNumber}.pdf')

        print(f'Zapisano w pliku "{fileName}"')

        return fileName

    def fillComponentList(self):
        for root, dirs, files in os.walk(IMAGE_FOLDER):
            for filename in files:
                if filename.startswith(self.serialNumber) and filename.endswith('png'):
                    self.components.append(self.generateComponent(filename))

        self.components.sort(key=lambda component: component.sheet)

    def generateComponent(self, filename: str) -> Component:
        filename = filename.removesuffix('.png')
        fixedName = filename.replace(' ', '_').replace('#_', '#') + '_'

        # Wartości numeryczne pomiędzy nawiasami
        countSearch = re.findall(r"\((\d+)\)", fixedName) 
        if len(countSearch) > 0:
            count = countSearch[0]
        else:
            count = 1

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
            sheet=sheet,
            engraver=engraver,
            detail=self
        )
    
    def display(self) -> None:
        print('SN', self.serialNumber)
        for component in self.components:
            component.display()


class PDF(FPDF):
    def __init__(self, detail: Detail, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.detail = detail
        self.supported_characters = set("""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-!? '"()[]{}""")

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
        self.add_page()
        self.set_fill_color(255, 255, 255)

        for i, component in enumerate(self.detail.components):
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
            self.image(os.path.join(IMAGE_FOLDER, component.filename+'.png'), keep_aspect_ratio=True, **img_pos_size)

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

            if not (i+1)%5:
                self.add_page()


if __name__ == '__main__':
    sn = input('Podaj numer detalu:\nSN ')
    d = Detail(sn)
    fileName = d.generatePDF()
    if fileName:
        os.startfile(fileName)
    input('Wciśnij Enter, żeby zamknąć...')
