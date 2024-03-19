import pygame as pg
from pygame.locals import (K_DOWN, K_UP, K_LEFT, K_RIGHT)
import math as m
import csv

pg.init()

# Definerer noen forskjellige fonter 
font = pg.font.SysFont("calibri", 36)
font_liten = pg.font.SysFont("arial", 24)

class Plassering:
    """
    SuperKlasse som gir posisjon til de ulike figurene
    Attributter
        x - x koordinaten til figuren
        y - y koordinaten til figuren
        vindusobjekt - sier at figurene skal inn i akkurat dette vindusobjektet
    """
    def __init__(self, x, y, vindusobjekt):
        self.x = x
        self.y = y
        self.vindusobjekt = vindusobjekt

class Rektangel(Plassering):
    """Subklasse. Klassen forteller hvordan rektanglene i spillet lages
    Attributter
        x - x koordinaten til figuren
        y - y koordinaten til figuren
        vindusobjekt - sier at figurene skal inn i akkurat dette vindusobjektet
        farge - fargen til sirkelen (R,G,B)
        lengde - sier hvor høy rektangelet skal være
        bredde - sier hvor bred rektangelet skal være

    lager egen metode for tegn til rektangelet
    """
    def __init__(self, x, y,vindusobjekt,farge,lengde,bredde):
        super().__init__(x, y, vindusobjekt)
        self.farge = farge
        self.lengde = lengde
        self.bredde = bredde
    def tegn(self):
        pg.draw.rect(self.vindusobjekt,self.farge,(self.x,self.y,self.bredde,self.lengde))
    def sentrum(self):
        """Finner sentrum av rektangelet"""
        return (self.x + self.bredde / 2, self.y + self.lengde / 2)

class Sirkel(Plassering):
    """Subklasse. Klassen forteller hvordan sirklene i spillet lages
    Attributter
        x - x koordinaten til figuren
        y - y koordinaten til figuren
        vindusobjekt - sier at figurene skal inn i akkurat dette vindusobjektet
        farge - fargen til sirkelen (R,G,B)
        radius - sier hvor stor sirkelen blir

    lager egen metode for tegn til sirkelen
     """
    def __init__(self, x, y,vindusobjekt,farge, radius):
        super().__init__(x, y, vindusobjekt)
        self.farge = farge
        self.radius = radius

    def tegn(self):
        """ Tegner objektet """
        pg.draw.circle(self.vindusobjekt, self.farge, (self.x, self.y), self.radius)

    def finn_avstand(self, annen_ball):
        """Metode for å finne avstanden til en annen ball"""
        xAvstand2 = (self.x - annen_ball.x)**2  # x-avstand i andre
        yAvstand2 = (self.y - annen_ball.y)**2  # y-avstand i andre
        sentrumsavstand = m.sqrt(xAvstand2 + yAvstand2)

        radiuser = self.radius + annen_ball.radius

        avstand = sentrumsavstand - radiuser

        return avstand
    
    def kollisjon(self, annen_ball):
        if self.finn_avstand <= 0:
            return True
        else:
            return False

class Strek(Plassering):
    """Subklasse. Klassen forteller hvordan strekene i spillet lages
    Attributter
        x - x koordinaten til figuren
        y - y koordinaten til figuren
        vindusobjekt - sier at figurene skal inn i akkurat dette vindusobjektet
        farge - fargen til streken (R,G,B)
        bredde - sier hvor bred streken skal være
        slutt_x - x koordinaten til sluttposisjon til streken
        slutt_y - y koordinaten til sluttposisjonen til streken
     
    lager egen metode for tegn til streken
    """
    def __init__(self, x, y,vindusobjekt,farge,bredde, slutt_x,slutt_y):
        super().__init__(x, y, vindusobjekt)
        self.farge = farge
        self.bredde = bredde
        self.slutt_x = slutt_x
        self.slutt_y=slutt_y
    def tegn(self):
         pg.draw.line(self.vindusobjekt, self.farge, (self.x,self.y),(self.slutt_x,self.slutt_y),self.bredde)

class Bilde_objekt(Plassering):
    """Subklasse til plassering. Klassen tar inn et bilde/URL (banelinje), 
    bilde får en lengde og en bredde og gjennom tegn metoden skalerer størrelsen på figuren
    Attributter
        x - x koordinaten til figuren
        y - y koordinaten til figuren
        vindusobjekt - sier at figurene skal inn i akkurat dette vindusobjektet
        banelinje - En URL til hvordan figuren ser ut
        lengde - sier hvor høy figuren skal være
        bredde - sier hvor bred figuren skal være

    lager egen metode for tegn til bilde_objektet
    """

    def __init__(self, x, y,vindusobjekt, banelinje, lengde, bredde):
        super().__init__(x, y, vindusobjekt)
        self.banelinje = banelinje
        self.lengde = lengde
        self.bredde = bredde
        self.mittBilde = pg.image.load(self.banelinje)
    def tegn(self):
        ny_storrelse = (self.lengde, self.bredde)  #her kan du endre størrelsen på bildet etter behov
        self.mittBilde = pg.transform.scale(self.mittBilde, ny_storrelse) #skalerer bilde
        self.vindusobjekt.blit(self.mittBilde,(self.x,self.y))  #forteller posisjonen til bilde
    def sentrum(self):
        """Finner sentrum av rektangelet"""
        return (self.x + self.bredde / 2, self.y + self.lengde / 2)

class NPC(Bilde_objekt):
    """
    Subklasse til bilde_objekt. Klassen forteller hvordan en NPC beveger seg i spillet (fiende)
    Attributter:
        x - x koordinaten til figuren
        y - y koordinaten til figuren
        vindusobjekt - sier at figurene skal inn i akkurat dette vindusobjektet
        banelinje - En URL til hvordan figuren ser ut
        lengde - sier hvor høy figuren skal være
        bredde - sier hvor bred figuren skal være
        fartX - gir figuren fart i x retning slik at den beveger seg.
        fartY - gir figuren fart i x retning slik at den beveger seg.

    Metoder (forklaring nede i koden):
        flytt
        skyt
        tegn  
    """
    def __init__(self, x, y,vindusobjekt, banelinje, lengde, bredde,fartX, fartY):
        super().__init__(x, y, vindusobjekt,banelinje,lengde,bredde)
        self.fartX = fartX
        self.fartY = fartY
        self.skudd = []

    def flytt(self):
        """ Flytter objekt i x og y retning 
        i tilleg har vi listen self.skudd som er en liste fylt av 
        instanser av NPC klassen, gjennom metoden skyt.
        """
        self.x += self.fartX
        self.y += self.fartY

        # Flytter skudd
        for skudd in self.skudd:
            skudd.flytt()
    
    def skyt(self,fartX,fartY,filnavn:str, lengde, bredde, flytt_skudd=0):
        """ Danner er skuddobjekt med den gitte farten, oppgi banelinje til bilde av skuddet """
        self.skudd.append(NPC(self.x,self.y + self.lengde/2 + flytt_skudd, self.vindusobjekt, filnavn,lengde,bredde,fartX,fartY))
    
    def tegn(self):
        """ Tegner NPC og skudd """
        # Tegner alle skuddene
        for skudd in self.skudd:
            skudd.tegn()
        return super().tegn()

class Spiller(Bilde_objekt):
    """
    Klasse for spiller
    Attributter:
        x - x koordinaten til figuren
        y - y koordinaten til figuren
        vindusobjekt - sier at figurene skal inn i akkurat dette vindusobjektet
        banelinje - En URL til hvordan figuren ser ut
        banelinje_hoppe - Viser til nytt bilde når spiller hopper
        lengde - sier hvor høy figuren skal være
        bredde - sier hvor bred figuren skal være

    metoder (kommenterer nede i koden):
        hopp
        flytt
    """

    def __init__(self, x, y, vindusobjekt, banelinje, banelinje_hoppe, lengde, bredde):
        super().__init__(x, y, vindusobjekt, banelinje, lengde, bredde)
        
        # Last inn bildene en gang under initialisering
        self.bilde_vanlig = pg.image.load(banelinje).convert_alpha()
        self.bilde_hoppe = pg.image.load(banelinje_hoppe).convert_alpha()

        # Hoppe relaterte atributter
        self.tyngdeakselerasjon = 0.003
        self.hopp_hastighet = -1
        self.hopper = False
        self.fart_y = 0
    
    def hopp(self):
        """ Håndterer hopping """
        if not self.hopper:
            self.hopper = True
            self.fart_y = self.hopp_hastighet
    
    def flytt(self, bakke_y_koordinat):
        """ Oppdaterer spillerens posisjon """

        # Hvis spiller hopper
        if self.hopper:
            self.fart_y += self.tyngdeakselerasjon
            self.y += self.fart_y
            # Endrer bilde
            self.mittBilde = self.bilde_hoppe
        else:
            self.y += self.fart_y
 
        # Sjekker om spiller har landet
        if self.y >= bakke_y_koordinat - self.lengde:
            self.y = bakke_y_koordinat - self.lengde
            self.hopper = False
            self.fart_y = 0
            # Endrer bilde
            self.mittBilde = self.bilde_vanlig

class Knapp(Plassering):
    """ Klasse for en knapp som kan trykkes med mus
    Attributter: 
        x - x koordinaten til knappen
        y - y koordinaten til knappen
        vindusobjekt - sier at knappen skal inn i akkurat dette vindusobjektet
        lengde - sier hvor høy knappen skal være
        bredde - sier hvor bred knappen skal være
        farge - gir en bakgrunnsfarge
        tekst - sier hvilke tekst som skal befinne seg på knappen
        tekst_farge - fargen på teksten (R,G,B), vi har satt den til svart (0,0,0)

    metoder (kommentering nede i koden):
        tegn
        er_trykket
    """
    def __init__(self, x, y, vindusobjekt, bredde, lengde, farge, tekst="", tekst_farge=(0,0,0)):
        super().__init__(x, y, vindusobjekt)
        self.rektangel = pg.Rect(x, y, bredde, lengde)
        self.farge = farge
        self.tekst = tekst
        self.tekst_farge = tekst_farge
        self.vindusobjekt = vindusobjekt

    def tegn(self):
        """ Tegner knappen på det gitte vindu """
        pg.draw.rect(self.vindusobjekt, self.farge, self.rektangel)
        if self.tekst:
            font = pg.font.Font(None,36)
            tekst_flate = font.render(self.tekst, True, self.tekst_farge)
            tekst_rektangel = tekst_flate.get_rect(center=self.rektangel.center)
            self.vindusobjekt.blit(tekst_flate, tekst_rektangel)
    
    def er_trykket(self,mus_posisjon) -> bool:
        """ Sjekk om knappen er klikket ved å sammenligne museposisjonen med knappens rektangel """
        print("posisjon:", mus_posisjon)
        return self.rektangel.collidepoint(mus_posisjon)
    
class Text_input(Plassering):
    """ Klassen konstruerer en input boks for tekst 
    Attributter:
        x - x koordinaten til teksten
        y - y koordinaten til teksten
        vindusobjekt - sier at teksten skal inn i akkurat dette vindusobjektet
        lengde - sier hvor høy teksten skal være
        bredde - sier hvor bred teksten skal være
        tekst_storelse - sier størrelsen på teksten

    metoder (kommentering nede i koden):
        hondter_event
        tegn
    """
    def __init__(self, x, y, vindusobjekt, bredde, lengde, tekst_storelse):
        super().__init__(x, y, vindusobjekt)
        self.rektangel = pg.Rect(x, y, bredde, lengde)
        self.font = pg.font.SysFont("arial", tekst_storelse)
        self.tekst = ""
        self.aktiv = False
    
    def hondter_event(self, event):
        """ Håndterer logikk og eventer, korresponderende med input boks """
        if event.type == pg.MOUSEBUTTONDOWN:
            # Veksle aktiv tilstand når du klikker inne i rektangel
            if self.rektangel.collidepoint(event.pos):
                self.aktiv = not self.aktiv
            else:
                self.aktiv = False
        elif event.type == pg.KEYDOWN and self.aktiv:
            if event.key == pg.K_RETURN:
                # Avslutt redigering ved Enter-tastetrykk
                self.aktiv = False
            elif event.key == pg.K_BACKSPACE:
                # Slett siste tegn ved tilbaketasting
                self.tekst = self.tekst[:-1]
            else:
                # Legg til et skrevet tegn til teksten
                self.tekst += event.unicode
    
    def tegn(self):
        """ Tegner tekst boksen """
        farge = pg.Color("white" if self.aktiv else "lightgrey")
        pg.draw.rect(self.vindusobjekt, farge, self.rektangel, 2)
        tekstflate = self.font.render(self.tekst, True, (255, 255, 255))
        self.vindusobjekt.blit(tekstflate, (self.rektangel.x + 5, self.rektangel.y + 5))

class Poengtavle(Plassering):
    """ Viser en poengtavle 
    Attributter:
        x - x koordinaten til poengtavlen
        y - y koordinaten til poengtavlen
        vindusobjekt - sier at poengtavlen skal inn i akkurat dette vindusobjektet
        filnavn - tar inn en fil
        tekst_storelse - sier størrelse på teksten inni poengtavlen
    """
    def __init__(self, x, y, vindusobjekt, filnavn, tekst_storelse):
        super().__init__(x, y, vindusobjekt)
        self.filnavn = filnavn
        self.font = pg.font.SysFont("arial", tekst_storelse)

        self.poeng_data = self.les_fildata()
    
    def les_fildata(self) -> list:
        """ Leser poengdata fra den opgitte filen og returnerer en liste"""
        data = []
        with open(self.filnavn, "r") as f:
            leser = csv.DictReader(f, delimiter=";")
            for rad in leser:
                data.append(rad)
        
        return data

    def hent_csv_overskrifter(self):
        """ Henter overskriftene i csv filen """
        with open(self.filnavn, "r") as f:
            leser = csv.reader(f, delimiter=";")
            overskrifter = next(leser)  # Get the first row, which contains the headers
        return overskrifter

    def tegn(self):
        """ Tegner en poengtavle """
        y_offset = 50
        x_offset = 100
        overskrifter = self.hent_csv_overskrifter()

        # Tegner overskriftene 
        overskrift1 = self.font.render(overskrifter[0], True, (255, 255, 255))
        overskrift2 = self.font.render(overskrifter[1], True, (255, 255, 255))
        overskrift3 = self.font.render(overskrifter[2], True, (255, 255, 255))

        self.vindusobjekt.blit(overskrift1, (self.x, self.y ))
        self.vindusobjekt.blit(overskrift2, (self.x + x_offset, self.y ))
        self.vindusobjekt.blit(overskrift3, (self.x + x_offset*2, self.y))
        
        # Sorter listen basert på "Poeng"-verdien, så etter "Tid"-verdien
        self.poeng_data.sort(key=lambda x: (int(x["Poeng"]), -int(x["Tid"])), reverse = True)

        # Går gjennom data og skriver ut
        for index, data in enumerate(self.poeng_data):
            _index = index +1 # Overskrifter er alledere skrevet ut
            navn_tekst = self.font.render(data[overskrifter[0]], True, (255, 255, 255))
            poeng_tekst = self.font.render(data[overskrifter[1]], True, (255, 255, 255))
            tid_tekst = self.font.render(data[overskrifter[2]], True, (255, 255, 255))
            
            self.vindusobjekt.blit(navn_tekst, (self.x, y_offset * _index + self.y))
            self.vindusobjekt.blit(poeng_tekst, (self.x + x_offset, y_offset * _index + self.y ))
            self.vindusobjekt.blit(tid_tekst, (self.x + x_offset*2, y_offset * _index + self.y))

"""
De kommende objektene er brukt for å vise en sammensatt bakgrunn
"""

class Start_skjerm():
    """ Denne klassen brukes for å vise start skjærmen
    Attributter:
        vindu_obj - skal inn i akkurat dette vindusobjektet

    metoder (kommentering står nede i koden):
        tegn
    """
    def __init__(self, vindu_obj) -> None:
        self.vindu_obj = vindu_obj

        # Knapper
        self.start_knapp = Knapp(150,100,self.vindu_obj,200,50,(255,0,0),"Start spillet")
        self.avslutt_knapp = Knapp(150,200,self.vindu_obj,200,50,(255,0,0),"Avslutt")
        
        # Tekst
        self.overskrift = font.render(f"VELKOMMEN!", True, (255, 0, 0))
        self.under_overskrift = font_liten.render(f"High Score", True, (255, 0, 0))
        
        # Poengtavle
        self.poeng_tavle = Poengtavle(600,100,self.vindu_obj,"score.csv",20)
 
    def tegn(self):
        """ Tegner start skjerm på vindu objekt """

        # Knapper
        self.start_knapp.tegn()
        self.avslutt_knapp.tegn()

        # Tavle
        self.poeng_tavle.tegn()

        # Tekst
        self.vindu_obj.blit(self.overskrift, (150, 20))
        self.vindu_obj.blit(self.under_overskrift, (660, 50))

class Registrer_data():
    """ Viser et input felt for registrering av tid, poeng og navn og lagrer i opgitt fil
    Attributter:
        vindu_obj - skal inn i akkurat dette vindusobjektet
        tid_overlevd - Viser tiden du har brukt
        poeng - Viser poengene du har

    Metoder (kommentering står nede i koden):
        lagre_data
        tegn
    """
    def __init__(self, vindu_obj, tid_overlevd, poeng) -> None:
        """ Konstruktør """
        self.vindu_obj = vindu_obj

        # Lag en semi-transparent overflate for å gjøre bakgrunnen mørkere
        self.mork_flate = pg.Surface((vindu_obj.get_width(), vindu_obj.get_height()))
        self.mork_flate.set_alpha(150)  # Juster alfaverdien for å kontrollere mørkhet
        self.mork_flate.fill((0,0,0))

        # Knapper
        self.ok_knapp = Knapp(10,150,self.vindu_obj,200,50,(255,0,0),"OK")

        # Tekst input
        self.tekst_input = Text_input(300,150,vindu_obj,200,50,25)

        # Tekst
        self.overskrift = font.render("Skriv inn navnet dit", True, (255, 255, 255))
        self.info_tekst = font_liten.render(f"Din tid: {tid_overlevd} s. Antall mynter: {poeng}", True, (255, 255, 255))
    
    def lagre_data(self, overskrifter:list, data:dict, filnavn:str):
        """ Lagrer data i opgitt fil """
        with open("score.csv", "a", newline="") as f:
            skriver = csv.DictWriter(f, fieldnames=overskrifter, delimiter=";")
            # Append data til CSV fil
            skriver.writerow(data)

    def tegn(self):
        """ Tegner objekter """
        self.vindu_obj.blit(self.mork_flate, (0, 0))
        self.ok_knapp.tegn()

        self.tekst_input.tegn()

        # Tekst
        self.vindu_obj.blit(self.overskrift, (10, 10))
        self.vindu_obj.blit(self.info_tekst, (10, 50))

class Spillbrett():
    """ I denne klassen ligger banen til spillet, bakgrunn med hindre 
    Attributter:
        vindu_obj - skal inn i akkurat dette vindusobjektet
        bakgrunn_url - tar inn URL til bakgrunn som brukes på banen
        banelengde - forteller hvor lang banen skal være
        pos_x - sier x posisjonen til bakgrunnen som skal bevege seg i forhold til spilleren
        pos_y - sier y posisjonen til bakgrunnen som skal bevege seg i forhold til spilleren

    Metoder (kommentering nede i koden):
        flytt_hoyre
        flytt_venstre
        flytt
        tegn
    """
    def __init__(self, vindu_obj:object, bakgrunn_url:str, banelengde, pos_x=0, pos_y=0) -> None:
        self.vindu_obj = vindu_obj
        self.pos_x = pos_x # Posisjonen starter på null
        self.pos_y = pos_y
        self.bakgrunnsbilde = pg.image.load(bakgrunn_url) # konverterer til gitt skjærmstørrelse, kan fjærnes
        self.bakgrunnsbilde = pg.transform.scale(self.bakgrunnsbilde, (vindu_obj.get_width(), vindu_obj.get_height()))
        self.bredde_bakgrunnsbilde = self.bakgrunnsbilde.get_width()
        self.hoyde_bakgrunnsbilde = self.bakgrunnsbilde.get_height()

        self.banelengde = banelengde # Banelengde i pixler
        self.hastighet = 0.25

        self.hindre_farge = (128,128,128)

        # Ordbok med alle elementene på spilbrettet
        self.gjennstander = {
            "hindre": [
                Rektangel(800, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 100),
                Rektangel(900, self.vindu_obj.get_height()-200, self.vindu_obj, self.hindre_farge, 20, 100),
                Rektangel(1000, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 100),

                Rektangel(3600, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 100),
                Rektangel(3750, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 20),
                Rektangel(3850, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 20),
                Rektangel(3950, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 20),
                Rektangel(4050, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 20),
                Rektangel(4150, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 200),

                Rektangel(5500, self.vindu_obj.get_height()-150, self.vindu_obj, self.hindre_farge, 20, 100),
                Rektangel(5700, self.vindu_obj.get_height()-200, self.vindu_obj, self.hindre_farge, 20, 100),
                Rektangel(5900, self.vindu_obj.get_height()-300, self.vindu_obj, self.hindre_farge, 20, 200),

                Rektangel(6500, self.vindu_obj.get_height()-100, self.vindu_obj, self.hindre_farge, 20, 100),
                Rektangel(6700, self.vindu_obj.get_height()-150, self.vindu_obj, self.hindre_farge, 150, 20),
                Rektangel(6800, self.vindu_obj.get_height()-200, self.vindu_obj, self.hindre_farge, 200, 20),
                Rektangel(6900, self.vindu_obj.get_height()-250, self.vindu_obj, self.hindre_farge, 250, 20),
                Rektangel(7000, self.vindu_obj.get_height()-250, self.vindu_obj, self.hindre_farge, 250, 20),
                Rektangel(7100, self.vindu_obj.get_height()-250, self.vindu_obj, self.hindre_farge, 250, 20),
                Rektangel(7200, self.vindu_obj.get_height()-150, self.vindu_obj, self.hindre_farge, 150, 20),
                Rektangel(7300, self.vindu_obj.get_height()-150, self.vindu_obj, self.hindre_farge, 150, 20),
                
            ],
            "huller": [
                Rektangel(900, self.vindu_obj.get_height()-39, self.vindu_obj, (0, 0, 0), 100, 100),
                Rektangel(3500, self.vindu_obj.get_height()-39, self.vindu_obj, (0, 0, 0), 100, 1000)
            ],
            "NPCer": {
                "vanlig": [
                    NPC(1250,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(1500,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(1850,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    
                    NPC(3000,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(3500,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(3850,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    
                    NPC(6000,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(6500,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(6850,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),

                    NPC(8000,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(8500,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(8850,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),

                    NPC(11000,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(11500,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    NPC(11850,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/goomba.png",100,100,-0.1,0),
                    
                ],
                "skyte": [
                    NPC(6000,self.vindu_obj.get_height()-130,self.vindu_obj,"bilder/bowser.png",100,100,0,0),
                    NPC(8000,self.vindu_obj.get_height()-130,self.vindu_obj,"bilder/bowser.png",100,100,0,0)
                ]
            },
            "mynter": [
                Bilde_objekt(850,100,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(1000,50,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(750,120,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(800,10,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(950,100,self.vindu_obj,"bilder/Coin_mario.png",30,30),

                Bilde_objekt(2000,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(2050,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(2100,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(2150,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(2200,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),

                Bilde_objekt(3000,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(3050,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(3100,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(3150,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(3200,self.vindu_obj.get_height()-110,self.vindu_obj,"bilder/Coin_mario.png",30,30),

                Bilde_objekt(3800,self.vindu_obj.get_height()-210,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(4050,self.vindu_obj.get_height()-340,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(5800,self.vindu_obj.get_height()-210,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(6050,self.vindu_obj.get_height()-360,self.vindu_obj,"bilder/Coin_mario.png",30,30),

                Bilde_objekt(6600,self.vindu_obj.get_height()-300,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(6650,self.vindu_obj.get_height()-330,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(6690,self.vindu_obj.get_height()-300,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(6770,self.vindu_obj.get_height()-360,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(7200,self.vindu_obj.get_height()-200,self.vindu_obj,"bilder/Coin_mario.png",30,30),
                Bilde_objekt(7300,self.vindu_obj.get_height()-200,self.vindu_obj,"bilder/Coin_mario.png",30,30),

            ],
            "maal": [Bilde_objekt(self.banelengde-500,vindu_obj.get_height()-270,self.vindu_obj,"bilder/goal_pole.png",100,270)]
        }

    def flytt_hoyre(self):
        """ Metode for å flytte bakgrunnen mot venstre, men skaper en illusjon av at karakteren beveger seg mot høyre """

        # Setter bevegelsesrettning
        if self.pos_x > -self.banelengde: # Hvis du ikke er ved enden
            # Hvis høyre, sett negativt fortegn
            self.hastighet = -abs(self.hastighet)
            # Flytter
            self.flytt()
    
    def flytt_venstre(self):
        """ Metode for å flytte bakgrunnen mot høyre, 
        men skaper en illusjon av at karakteren beveger seg mot venstre 
        """
        
        # Setter bevegelsesrettning
        if self.pos_x < 0:
            # Hvis venstre, sett positivt fortegn
            self.hastighet = abs(self.hastighet)
            # Flytter
            self.flytt()

    def flytt(self):
        """ Metode for å flytte bakgrunnen i x retning """

        # Oppdaterer bakgrunnens possisjon
        self.pos_x += self.hastighet
        
        # Oppdaterer possisjonen til ellementer i self.gjennstander
        for key in self.gjennstander:
            for item in self.gjennstander[key]:
                
                # Hvis vi er ved NPC må vi ned et nivå
                if key == "NPCer":
                    for npc in self.gjennstander[key][item]:
                        npc.x += self.hastighet
                        for skudd in npc.skudd:
                            skudd.x += self.hastighet
                else:
                    item.x += self.hastighet

    def tegn(self):
        """ Tegner bakgrunnen """

        # Finn ut hvor mange ganger bakgrunnen må repeteres for å fylle hele vinduet
        antall_repetisjoner = self.banelengde // self.bredde_bakgrunnsbilde + 1

        # Tegn bakgrunnen flere ganger for å dekke hele vinduet
        for i in range(antall_repetisjoner):
            self.vindu_obj.blit(self.bakgrunnsbilde, (self.pos_x + i * self.bredde_bakgrunnsbilde, self.pos_y))
        
        # Tegner elementer i self.gjennstander
        for key in self.gjennstander:
            for item in self.gjennstander[key]:

                # Hvis vi er ved NPC må vi ned et nivå
                if key == "NPCer":
                    for npc in self.gjennstander[key][item]:
                        npc.tegn()
                        npc.flytt()
                else:
                    item.tegn()
