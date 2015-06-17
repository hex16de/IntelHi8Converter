##########################################################
#Converter for Intel Hex and Binary files.
#This program converts a Hexfile to binary data and back.
#Version: 1.0.2.3
#Started: 19.07.2014
#Last Edited: 27.07.2014 2:08
#Editor: Eclipse Kepler + Eclipse Luna + PyDev 3.0, Python Version: 3.3.1
#Windows 7 Ultimate 64-bit
###########################################################

import argparse; #ARgparse wird importiert
from os.path import isfile as FileExist; #Import zum testen ob eine Datei vorhanden ist


def ToHex(data, chars = 2): #Funktion zum Konvertieren zu HEX
    if isinstance(data, int): #Bei einem Integer
        n = data >> (chars * 4) #Bits schieben

        while (n > 0):
            chars += 2 #Zaehler
            n >>= 8 #Bits schieben

        return ("{:0" + str(chars) + "X}").format(data); #Wiedergabe
    elif isinstance(data, bytes): #Bei Bytes
        return "".join("{:02X}".format(x) for x in data); #Wiedergabe
    else: #Andernfalls
        return ""; #Wiedergabe

def Checksum(data, tst = False): #Funktion zum berechnen der Checksumme
    res = 0
    for DATA in range(len(data) // 2):
        res += int(data[2 * x:2 * x + 2], 16) #Berechnen

    res = ~res
    if not tst:
        res += 1
        
    return res & 0xFF; #Wiedergabe

def HEX2BIN(inp, outp):
    if not FileExist(inp): #testen ob die Datei existiert
        print("File does not exist")
        return 1;

    data = b'' #Bytearray wird erstellt
    file = open(inp, 'r') #Datei wird geoeffnet

    for line in list(file): #Fuer jede Zeile ausfuehren
        if (len(line) < 12) or (line[0] != ':'): #testen ob das Start Zeichen ":" vorhganden ist sowie die Adresse etc.
            print("Wrong File Format or Wrong starting Character")
            return 2;

        try:
            checksum = int(line[-3:-1], 16) #Checksumme berechnen
            
            line = line[1:-3]
            if (Checksum(line) != checksum): #Wenn die Checksumme falsch ist
                print("Wrong Checksum")
                return 3;
        except ValueError: #Wenn nicht Hex Zeichen enthalten sind
            print("Wrong Characters detected")
            return 2;

        count = int(line[ :2], 16) * 2 #Anzahl lesen
        types = int(line[6:8], 16)

        if (len(line) < (8 + count)) or (types and count): #Daten Laenge wird geprueft sowie falscher typ
            return 2;
        data += bytes.fromhex(line[8:]) #Daten werden hinzugefuegt

    file.close() #Datei wird geschlossen

    file = open(outp, "wb") #Datei wird geschrieben
    file.write(data)
    file.close()
    
    return 0; #Bei einer fehlerlosen Uebertragung

def BIN2HEX(inp, outp, rowCount, address):   
    if (inp[-4:] != ".bin") and (inp[-4:] != ".jpg") : #Wenn die Dateiendung fehlt, wird sie ergaenzt.
        inp += ".bin"
        
    if not FileExist(inp): #Pruefen auf existenz der Datei
        print("File does not exist")
        return 1;
    
    binaryFile = open(inp, "rb"); #Binaere Datei oeffnen

    if (outp[-4:] != ".hex"): #Dateiendung hinzufuegen wenn sie fehlt
        outp += ".hex"
        
    hexFile = open(outp, 'w'); #Hexadezimale Datei oeffnen

    data = binaryFile.read(rowCount) #Ersten DatenChunk lesen
    while (data != b''): #Wenn die daten nicht leer sind.
        line = ':' + ToHex(len(data)) + ToHex(address, 4) + "00" + ToHex(data) #Neue Zeile Konvertieren
        hexFile.write(line + ToHex(Checksum(line[1:])) + '\n') #Daten schreiben

        data = binaryFile.read(rowCount) #Naechsten Chunk lesen
        address = (address + rowCount) & 0xFFFF #Adresse updaten
        
    hexFile.write(":00000001FF\n") #Letzte Zeile schreiben

    binaryFile.close() #Dateien schliessen
    hexFile.close()

    return 0;

parser = argparse.ArgumentParser() #Parser wird gesetzt
group = parser.add_mutually_exclusive_group(required=True) #Eine Gruppe wird erstellt da entweder HI8 oder BIN aufgerufen werden muessen
group.add_argument("-HI8", nargs=2)#HI8 mit mindestens 2 Operanden
group.add_argument("-BIN", nargs=3)#BIN mit 3 Operanden
args = parser.parse_args() #Parser wird geparsed

if args.HI8: #Wenn HI8 gewaehlt wurde
    if args.HI8 == 1: #wenn ein argument gewaehlt wurde
        HEX2BIN(args.HI8[0],args.HI8[0]) #Rufe Funktion mit Parametern auf
    else: #anders
        HEX2BIN(args.HI8[0],args.HI8[1])
elif args.BIN: #wenn BIN gewaehlt wurde
    if args.BIN == 2: #Wenn zwei Argument gewaehlt wurde
        BIN2HEX(args.BIN[0],args.BIN[0],16,int(args.BIN[1]))
    else: #Anders
        BIN2HEX(args.BIN[0],args.BIN[1],16, int(args.BIN[2]))