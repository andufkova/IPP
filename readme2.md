# Implementační dokumentace k 2. úloze do IPP 2018/2019
Jméno a příjmení: Aneta Dufková  
Login: xdufko02


## interpret.py
Projekt byl vypracován v souladu s verzí Python 3.7 ve vývojovém prostředí PyCharm. Zpracováno je i rozšíření `STATI`.

### Struktura programu
Nejdříve se zkontrolují argumenty pomocí `argparse`, načte se XML a vytvoří se z něj strom. Jednotlivé instrukce a jejich argumenty jsou zkontrolovány přes regulární výrazy.
Při prvním průchodu stromem se uloží všechna návěští, na něž se může během toku programu skákat. Při druhém průchodu už se interpretují jednotlivé instrukce.
Program je rozdělený do tříd:
- Instruction - reprezentuje jednotlivé instrukce, stará se o kontrolu platnosti instrukce a argumentů.
- XMLTree - obsahuje celé XML načtené do stromu, kontroluje syntaxi XML.
- Frame - reprezentuje globální, lokální a dočasný rámec, má metody na kontrolu existence proměnné v daném rámci, vytvoření proměnné, získání a nastavení její hodnoty.
Kódem se prochází v cyklu podle ukazatele na další instrukci. Ten se inkrementuje vždy o 1 kromě případů, kdy byla načtená skoková instrukce.


### Využité konstrukce jazyka Python
Spoustu práce ušetřily některé konstrukce a nástroje jazyka Python, například:
- tuples - pro rozdělení rámce a názvu proměnné: `frame, at, name = instructionTree[keyValue].arg1Val.partition('@')`
- dictionaries - ve slovnících jsou sdružovány např. proměnné v jednotlivých rámcích
- lists - pracuji s nimi jako se zásobníkem a využívám pro zásobník rámců, volání i programový zásobník
- slices - hodilo se u instrukcí pro práci s řetězci, jako jsou `getchar` či `setchar`

### Rozšíření STATI
Pro zjištění maximálního počtu inicializovnaných proměnných se při každé inicializaci dívám, jestli je počet větší než doposud zjištěné maximum. Vykonané instrukce počítám při každé nově načtené a rozpoznané instrukci.

## test.php
Projekt byl vypracován v souladu s verzí PHP7.3 ve vývojovém prostředí PhpStorm.

### Struktura programu
Nejdříve se zkontrolují argumenty programu a podle nich přiřadí hodnoty, případně výchozí hodnoty (např. složka s testy). Následně se vytvoří celá struktura souborů k testování. Pokud je zadána možnost `recursive`, rozbalí se rekurzivně i podsložky. Vytvoří se chybějící soubory .in a .out. 
Struktura souborů k otestování se pak předá další třídě, která provede testy podle toho, zda se testuje pouze `interpret.py`, `parse.php` nebo oba. Spouští skripty, kontroluje návratové kódy a výstupy.
Následně se vygeneruje HTML zpráva s výsledky testování. 
Program je rozdělený do tříd:
- FileStructure - spravuje soubory k testování, vytváří chybějící, rekurzivně prohledává podsložky
- Tester - má na starosti provedení samotných testů
- HtmlOutput - generuje výsledný dokument s vyhodnocením

### Konvence pojmenování
Metody, které jsou volané pouze uvnitř dané třídy, začínají své jméno podtržítkem.

### Několik řešení konkrétních problémů
- Dočasné soubory: Výsledek skriptu `parse.php` je ukládán do dočasných souborů, které jsou po zpracování interpretem vymazány. Soubor je tedy stále jeden se stejným jménem, po každém testu smazán.
- Konstanty: Verze Pythonu, umístění archivu `JExamXML.jar` nebo (zpětné) lomítko nutné k oddělení mezer v názvech souborů. Tyto atributy se nastavují v konstantách na začátku kódu, protože jsou proměnné v závislosti na prostředí (školní server Merlin vs. domácí počítač, Linux vs. Windows).
- HTML výsledek: Obsah HTML se generuje v průběhu testování. Na konci testu se pouze vypíše do souboru.
- Kontroly souborů: Každá operace se souborem je pečlivě kontrolována. Kde je to možné, je ověřena i validita souboru (např. u souboru .rc zda obsahuje číslo).

### Použité zdroje
Zdrojem informací byl obyčejný manuál k PHP. Ukázalo se ale, že až tak obyčejný není, někdy dokáže pobavit - viz https://www.php.net/delete.
