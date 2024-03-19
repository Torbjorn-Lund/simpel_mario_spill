"""
Selve spillet

I hoved løkken har programmet har to muligheter, enten kjøres spillet (kjor_spill = True), ellers så vises en start skjerm.
Når spillet er ferdig settes kjor_spill = False, og vi er tilbake til start skjerm. Slik fortsetter spillet så lenge fortsett = True.
For mer innformasjon se README.md eller: https://github.com/Torbjorn-Lund/simpel_mario_spill.git
"""
# Importerer
import pygame as pg
from pygame.locals import (K_UP, K_LEFT, K_RIGHT) # Taster
import random as rd
import math as m
from time import sleep
from objekter import *

# Initialiserer pygame
pg.init()

# Definerer banestørelse
VINDU_BREDDE = 1080
VINDU_HOYDE = VINDU_BREDDE * (1/3)
BAKKE_Y_KOORDINAT = VINDU_HOYDE-35
BANELENGDE = 10000

# Instanser av objekter
vindu = pg.display.set_mode([VINDU_BREDDE,VINDU_HOYDE])
start_skjerm = Start_skjerm(vindu)
spillbrett = Spillbrett(vindu,"bilder/bakgrunn1.jpeg",BANELENGDE)
spiller = Spiller(VINDU_BREDDE/2,BAKKE_Y_KOORDINAT-60,vindu,"bilder/mario.webp", "bilder/mario_hoppe.png",60,60)
klokke = pg.time.Clock()

# Definerer lyder
hit_sound = pg.mixer.Sound("Lyd/hit.mp3")
collect_coin = pg.mixer.Sound("Lyd/collect_points.mp3")
seier_lyd = pg.mixer.Sound("Lyd/success_1.mp3")
game_over_lyd = pg.mixer.Sound("Lyd/game_over.mp3")
game_music = pg.mixer.music.load("Lyd/music.mp3")

pg.mixer.music.play(-1) # Starter bakgrunnsmusikk

# Definerer noen forskjellige fonter 
font = pg.font.SysFont("calibri", 36)
font_liten = pg.font.SysFont("arial", 24)

# Setter variabler
poeng = 0
tid_overlevd = 0
fortsett = True
kjor_spill = False
tid_mellom_skudd = 15
skyte_tid = 0

game_over = False # Ikke i bruk

def avstand_mellom_rektangler(rektangel1, rektangel2) -> tuple:
    """
    Beregner avstanden mellom to rektangler - (avstand,avstand_x,avstand_y)

    Args:
        rektangel1: Det første rektanglet.
        rektangel2: Det andre rektanglet.
    """
    x1, y1 = rektangel1.sentrum()
    x2, y2 = rektangel2.sentrum()

    # Beregn halv bredde og halv lengde av hvert rektangel
    halv_bredde1 = rektangel1.bredde / 2
    halv_lengde1 = rektangel1.lengde / 2
    halv_bredde2 = rektangel2.bredde / 2
    halv_lengde2 = rektangel2.lengde / 2

    # Beregn avstandene mellom rektanglene i x- og y-retning
    avstand_x = abs(x2 - x1)
    avstand_y = abs(y2 - y1)

    # Beregn overlapp i x- og y-retning
    overlap_x = halv_bredde1 + halv_bredde2 - avstand_x
    overlap_y = halv_lengde1 + halv_lengde2 - avstand_y

    # returnerer
    return (m.sqrt((x2 - x1)**2 + (y2 - y1)**2),overlap_x,overlap_y)

def rektangel_kollisjon(rektangel1, rektangel2) -> bool:
    """
    Sjekker om to rektangler kolliderer
    
    Args:
        rektangel1: Det første rektanglet.
        rektangel2: Det andre rektanglet.

    Returns:
        bool: True hvis rektanglene kolliderer, ellers False.
    """

    avstand, overlap_x, overlap_y = avstand_mellom_rektangler(rektangel1,rektangel2)

    # Returner True hvis det er overlapp i begge retningene, ellers False
    return overlap_x > 0 and overlap_y > 0


def kollisjon_bund(rektangel1, rektangel2, toleranse=5) -> bool:
    """ 
    Sjekker for kollisjon mellom toppen og bunden av to rektangler
    rektangel1 - topp objekt
    rektangel2 - bund objekt
    """

    # Beregn den nederste y-koordinaten til rektangel1 og den øverste y-koordinaten til rektangel2
    bunn_rektangel1 = round(rektangel1.y + rektangel1.lengde)
    top_rektangel2 = round(rektangel2.y)
    
    # Hvis rektanglene kolliderer
    if rektangel_kollisjon(rektangel1, rektangel2):
        # Sjekk om den absolutte forskjellen mellom y-koordinatene er innenfor toleranseområdet
        if abs(bunn_rektangel1 - top_rektangel2) <= toleranse:
            return True
    
    return False 

def registrer_score(overlegg:object) -> bool:
    """ 
    Tegner et bilde over det eksisterende. Brukes for å registrere score.
    
    Returns:
        bool: True hvis navn er registrert, ellers False
    """

    mus_trykket = False

    # Tegner bakgrunn
    overlegg.tegn()

    # Går gjennopm event
    for event in pg.event.get():
        if event.type == pg.QUIT: # Avslutter
            return True
        if event.type == pg.MOUSEBUTTONDOWN: # Sjekk fo museklikk
            if event.button == 1:  # Venstre muse knapp
                mus_pos = pg.mouse.get_pos()
                mus_trykket = True
        overlegg.tekst_input.hondter_event(event) # Sjekker for tekst input
    
    # Sjekker om OK knapp er trykket og om vi har tekst input
    if mus_trykket and overlegg.ok_knapp.er_trykket(mus_pos) and overlegg.tekst_input.tekst != "":
        # Data som skal legges til
        data = {"Navn": overlegg.tekst_input.tekst, "Poeng": poeng, "Tid": tid_overlevd}
        overskrifter = ["Navn", "Poeng", "Tid"]
        
        # Legger til ny data
        overlegg.lagre_data(overskrifter,data,"score.csv")
        
        # Oppdater poeng tavlen
        start_skjerm.poeng_tavle.les_fildata()

        # Avslutter løkken
        return True
    
    else:
        return False

def reset_spill():
    """ Resetter spill variablene """
    global spillbrett, spiller, poeng
    
    pg.mixer.music.play(-1) # Starter bakgrunnsmusikk

    # Reset spiller og spillbrett
    spillbrett = Spillbrett(vindu,"bilder/bakgrunn1.jpeg",BANELENGDE)
    spiller = Spiller(VINDU_BREDDE/2,BAKKE_Y_KOORDINAT-60,vindu,"bilder/mario.webp", "bilder/mario_hoppe.png",60,60)
    
    # Nulstiller poeng score
    poeng = 0

def nytt_skudd():
    """ Lager et nytt skudd fra alle npc """
    # Sjekker skyte NPC
    for npc in spillbrett.gjennstander["NPCer"]["skyte"]:
        npc.skyt(-0.2,0.001,"bilder/ildkule.webp",30,30,-30)


def bevegelse(trykkede_taster, bakke_y_koordinat):
    """ Funksjon for å styre bevegelse """
    # Flyter spiller mot venstre
    if trykkede_taster[K_LEFT]:
        spillbrett.flytt_venstre()
    
    # Flyter spiller mot høyre
    if trykkede_taster[K_RIGHT]:
        spillbrett.flytt_hoyre()
    
    # Får spiller til hoppe
    if trykkede_taster[K_UP]:
        spiller.hopp()
    
    # Flytter spiller, hvis nødvendig
    spiller.flytt(bakke_y_koordinat)

def oppdater_logikk(trykkede_taster, bakke_y_koordinat):
    """ 
    Oppdaterer spill logikken 
    
    1. Sjekker for kollisjon med diverse objekter
    2. Sørger for at spiller faller hvis ikke i kontakt
    3. Kaller funksjon som oppdaterer possisjon, basert på tastetrykk
    """
    global poeng, game_over

    kollisjon_oppdaget = False

    # Sjekker om spiller er under vinduet
    if spiller.y >= VINDU_HOYDE:
        game_over = True

    # Sjekker for kollisjon med hindre
    for hinder in spillbrett.gjennstander["hindre"]:
        # Topp kollisjon
        if kollisjon_bund(hinder,spiller):
            spiller.fart_y = 0.5
        # Bund kollisjon
        elif kollisjon_bund(spiller, hinder):
            bakke_y_koordinat = hinder.y
            kollisjon_oppdaget = True
    
    # Sjekker for kollisjon med fallgruver
    for hull in spillbrett.gjennstander["huller"]:
        if rektangel_kollisjon(spiller,hull):
            spiller.fart_y = 0.5
            bakke_y_koordinat = VINDU_HOYDE + spiller.lengde
    
    # Sjekker kollisjon med NPC
    for npc in spillbrett.gjennstander["NPCer"]["vanlig"]:
        if rektangel_kollisjon(spiller,npc):
            # Hvis treffer topp, slett NPC
            if kollisjon_bund(spiller, npc):
                spillbrett.gjennstander["NPCer"]["vanlig"].remove(npc) # Fjern element
                hit_sound.play() # Spill lyd
                spiller.fart_y = -0.5 # Lager et lite hopp
            else:
                game_over = True
        
    # Sjekker skyte NPC
    for npc in spillbrett.gjennstander["NPCer"]["skyte"]:
        if rektangel_kollisjon(spiller,npc):
            # Hvis treffer topp, slett NPC
            if kollisjon_bund(spiller, npc):
                spillbrett.gjennstander["NPCer"]["skyte"].remove(npc) # Fjern element
                hit_sound.play() # Spill lyd
                poeng += 10 # Ekstra poeng for å ta
                spiller.fart_y = -0.5 # Lager et lite hopp
            else:
                game_over = True
            # Sjekker for kollisjon med skuddene til NPC
        for skudd in npc.skudd:
            if rektangel_kollisjon(spiller,skudd):
                game_over = True

    # Sjekker for kollisjon med mynter
    for mynt in spillbrett.gjennstander["mynter"]:
        if rektangel_kollisjon(spiller, mynt):
            poeng += 1
            collect_coin.play() # Spill lyd
            spillbrett.gjennstander["mynter"].remove(mynt) # Fjern element
    
    # Hvis ikke i kontakt med et hinder eller bakken og ikke hopper (Slik at spiller faller)
    if not kollisjon_oppdaget and spiller.y + spiller.lengde < BAKKE_Y_KOORDINAT and spiller.hopper == False:
        spiller.fart_y += spiller.tyngdeakselerasjon

    bevegelse(trykkede_taster, bakke_y_koordinat)

# HOVED LØKKE
while fortsett:
    
    # Variabler
    mus_pos = None
    mus_trykket = False
    trykkede_taster = pg.key.get_pressed() # Henter tastetrykk
    bakke_y_koordinat = BAKKE_Y_KOORDINAT # Setter bakke høyde

    # Hvis bruker har lukket programmet
    for event in pg.event.get():
        if event.type == pg.QUIT:
            fortsett = False
        # Sjekk fo museklikk
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:  # Venstre muse knapp
                mus_pos = pg.mouse.get_pos()
                mus_trykket = True
                  
    # Hvis spillet ikke skal kjøres, vis startskjerm
    if kjor_spill != True:
        if mus_trykket: 
            # Sjekker hvilke knapp som er trykket
            if start_skjerm.start_knapp.er_trykket(mus_pos):
                # Hvis knapp er trykket, start spill
                kjor_spill = True
                start_tid = pg.time.get_ticks() # For tidtakning av spillet
            elif start_skjerm.avslutt_knapp.er_trykket(mus_pos):
                fortsett = False
            else:
                pass
                        
        vindu.fill((0,0,0))
        start_skjerm.tegn()

    # Kjør selve spillet
    else:
        # Oppdaterer spill logikken
        oppdater_logikk(trykkede_taster, bakke_y_koordinat)

        # Kalkulerer spill tid i sekunder
        tid_now = pg.time.get_ticks()
        tid_overlevd = (tid_now - start_tid) // 1000
        
        # Element for tidtakning og mynter
        tekstflate = font.render(f"tid: {tid_overlevd} s", True, (255, 255, 255))
        tekstflate2 = font.render(f"mynter: {poeng}", True, (255, 255, 255))

        # Hvis det har gått lang nok tid, skyt
        if (tid_now - skyte_tid) // 1000 > tid_mellom_skudd:
            skyte_tid = tid_now
            nytt_skudd()

        # Tegner elementer
        spillbrett.tegn()
        spiller.tegn()
        vindu.blit(tekstflate, (10, 10))
        vindu.blit(tekstflate2, (900, 10))

        # Hvis spillet er tapt
        if game_over:
            pg.mixer.music.stop() # Stopp bakgrunnsmusikk
            game_over_lyd.play() # Spiller lyd
            game_over_tekst = Bilde_objekt(150,-60,vindu,"bilder/game_over.png",500,500)
            game_over_tekst.tegn()
            pg.display.flip() # Viser innhold

            sleep(3) # Vent 3s før reset

            # Resetter objekter og variabler
            reset_spill()
            game_over = False
            kjor_spill = False
        
        # Hvis spiller har nådd målet
        if rektangel_kollisjon(spiller, spillbrett.gjennstander["maal"][0]):
            pg.mixer.music.stop() # Stopp bakgrunnsmusikk
            seier_lyd.play() # Spiller lyd

            slutt_tekst = font.render("Banen er ferdig!", True, (255, 255, 255))
            vindu.blit(slutt_tekst, (500, VINDU_HOYDE/2))
            
            pg.display.flip() # Må oppdatere med en gang
            
            sleep(1) # Sover i 1s før spillet slutter

            # Kjører intill et brukernavn er opgitt
            overlegg = Registrer_data(vindu,tid_overlevd,poeng)
            navn_oppgitt = registrer_score(overlegg)
            while not navn_oppgitt:
                navn_oppgitt = registrer_score(overlegg)
                pg.display.flip() # Tegner innhold
            
            kjor_spill = False

            # Resetter spillet
            reset_spill()
            
    pg.display.flip() # Viser innhold
    klokke.tick()

# Lukker spillet
pg.quit()
