# Projektidee
- Flet-App, um eine Übersicht über die Patienten der Intensivstation zu erstellen.
- Die App soll als single-file-app mit github actions gebaut werden (Windows .exe).
- Datenspeicherung: Eine `patients.yaml` im gleichen Verzeichnis wie die Anwendung.
- User-Workflow: Daten eingeben, editieren, ergänzen, via Quick-Add befüllen.
- Export: Übersicht einer Auswahl von Patienten als strukturierter Plain-Text (eingerückt wie YAML) zum Drucken/Kopieren.

# Datenmodell & Storage
- **Speicherung:** Automatisch (Autosave) bei Feldänderungen oder via "Hinzufügen" im Quick-Add.
- **YAML-Struktur:** 
  - Jeder Patient erhält eine eindeutige, versteckte `id` (UUID).
  - Felder: Name, Station, Bettplatz, Diagnosen, Operationen, Kardiale Funktion, Antiinfektiva, Diagnostik, Verlauf, Probleme/Aufgaben.
  - Status: `hidden` (boolean).
- **Dateipfad:** Relativ zur EXE im gleichen Ordner. Falls nicht vorhanden -> initial erstellen.
- **Handling:** Zeilenumbrüche in Multi-line-Feldern werden technisch sauber (YAML Block Scalars) gespeichert.

# GUI Struktur
## Sidebar (Links)
- **Branding:** App-Logo (`logo.png`) oben zentriert.
- Scrollbar, falls Liste zu lang.
- "Add Patient" Button.
- Link zur Startseite ("Übersicht").
- Liste aller **aktiven** Patienten (nicht ausgeblendet). Klick navigiert zur jeweiligen Patienten-Seite.
- Aktualisiert sich in Echtzeit bei Namensänderungen oder Statusänderungen (Hide/Search).

## Startseite (Zentral)
- **Suche:** Suchfeld, um Patienten (auch ausgeblendete) zu finden.
- **Patienten-Liste:** Alle Patienten untereinander.
  - Sortierung: Alphabetisch nach Station, dann numerisch/alphabetisch nach Bettplatz.
  - Pro Zeile: Patientenname + Station/Bett.
  - Buttons pro Patient: 
    - "Hide" (setzt Status auf hidden, entfernt ihn aus Sidebar/Standardliste).
    - "Quick Add" (Grünes Plus-Icon).
- **Export Button:** Führt zur Export-Konfiguration.

## Patienten-Seite
- Formular mit allen Feldern aus dem Datenmodell.
- Textfelder:
  - Name (Multi-line)
  - Station (Single-line)
  - Bettplatz (Single-line)
  - Alle weiteren (Multi-line)
- Änderungen werden per Autosave direkt in die YAML geschrieben.

## Quick-Add (Popover auf Startseite)
- Wird über das "+" Icon beim Patienten in der Liste geöffnet.
- Radio-Button Auswahl für das Ziel-Feld (Default: "Verlauf").
- Textfeld für die Information.
- Funktionsweise: Fügt neue Zeile an das gewählte Feld an: `[DD.MM.] <Eingegebener Text>`.
- Zeitstempel: Tagesaktuelles Datum (DD.MM.), händisch nach der Anlage änderbar.

## Export-Seite/Bereich
- Checkbox-Liste aller Patienten (Default: alle aktiven Patienten ausgewählt).
- Checkbox-Liste der Parameter (Default: Name, Diagnosen, Operationen, Kardiale Funktion, Antiinfektiva).
- Output-Feld: Read-only Textfeld mit dem generierten Plain-Text.
  - Formatierung: Strukturiert und eingerückt (YAML-Stil), optimiert für Druck/Copy-Paste.
- **Direktdruck (PDF):** Button zum Generieren einer A4-PDF.
  - Schriftgröße 10pt.
  - Seitenumbrüche werden so gesteuert, dass Patientenblöcke möglichst nicht zerrissen werden.
  - Automatisches Öffnen der PDF nach Erstellung.

# Technische Details
- **Build:** PyInstaller/Flet Pack via GitHub Actions für Windows.
- **Sortierlogik:** Alphabetisch nach Station, dann Bettplatz.
- **Suche:** Filtert die Liste der Startseite in Echtzeit. Ausgeblendete Patienten werden bei Treffern wieder eingeblendet (Option zur Re-Aktivierung).