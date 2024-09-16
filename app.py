from __future__ import annotations
import os
import re
from fpdf import FPDF, XPos, YPos
from dotenv import load_dotenv


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
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

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

    def header(self) -> None:
        self.set_font('times', 'B', 20)
        self.cell(0, 10, f'SN {self.detail.serialNumber}', border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font('times', 'I', 10)
        footerText = "Wygenerowane automatycznie przez skrypt w fazie testowej."
        footerText2= "Wszystkie niezgodnosci prosze zglosic do Marka Szlosarka z G9."
        self.cell(0, 5, footerText, border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 5, footerText2, border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20) 
    
    def generateDetailComponentListTable(self) -> None:
        for i, component in enumerate(self.detail.components):
            self.set_line_width(.1)
            self.set_font('times', 'I', 6)
            self.cell(60, 6, "Nazwa:")
            self.cell(30, 6, "Na komplet:")
            # FPDF.ln(0) obniża o wysokość czcionki
            self.ln(1)
            self.ln(-1)

            self.set_font('times', '', 12)
            self.cell(60, 15, component.filename, border=True)
            self.cell(30, 15, str(component.count), border=True)

            self.cell(30, 30, '', border=True)
            self.ln(15)

            self.set_font('times', 'I', 6)
            self.cell(60, 6, "Blacha:")
            self.cell(30, 6, "Grawer:")
            # FPDF.ln(0) obniża o wysokość czcionki
            self.ln(1)
            self.ln(-1)

            self.set_font('times', '', 12)
            self.cell(60, 15, component.sheet, border=True)
            self.cell(30, 15, 'Tak' if component.engraver else 'Nie', border=True)
            self.ln(15)
            pos_size = {
                'x': 100,
                'y': 30*(i%5)+20,
                'w': 30,
                'h': 30
            }
            self.image(os.path.join(IMAGE_FOLDER, component.filename+'.png'), keep_aspect_ratio=True, **pos_size)
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
