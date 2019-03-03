# Implementační dokumentace k 2. úloze do IPP 2018/2019
Jméno a příjmení: Aneta Dufková  
Login: xdufko02


## interpret.py
Projekt byl vypracován v souladu s verzí Python 3.7 ve vývojovém prostředí PyCharm. Zpracovávala jsem i rozšíření `STATI`.

### Struktura kódu
Nejdříve se zkontrolují argumenty pomocí `argparse`, načte se XML a vytvoří se z něj strom. Jednotlivé instrukce a jejich argumenty jsou zkontrolovány přes regulární výrazy.
Při prvním průchodu stromem se uloží všechna návěští, na něž se může během toku programu skákat. Při druhém průchodu už se interpretují jednotlivé instrukce.
Využila jsem třídy:
- Instruction - reprezentuje jednotlivé instrukce, stará se o kontrolu platnosti instrukce a argumentů.
- XMLTree - obsahuje celé XML načtené do stromu, kontroluje syntaxi XML.
- Frame - reprezentuje globální, lokální a dočasný rámec, má metody na kontrolu existence proměnné v daném rámci, vytvoření proměnné, získání a nastavení její hodnoty.
Kódem se prochází v cyklu podle ukazatele na další instrukci. Ten se inkrementuje vždy o 1 kromě případů, kdy byla načtená skoková instrukce.


### Využité konstrukce jazyka Python
Spoustu práce mi ušetřily některé konstrukce a nástroje jazyka Python, například:
- tuples - pro rozdělení rámce a názvu proměnné: `frame, at, name = instructionTree[keyValue].arg1Val.partition('@')`
- dictionaries - ve slovnících sdružuji např. proměnné v jednotlivých rámcích
- lists - pracuji s nimi jako se zásobníkem a využívám pro zásobník rámců, volání i programový zásobník
- slices - hodilo se u instrukcí pro práci s řetězci, jako jsou `getchar` či `setchar`

### Zajímavosti z řešení
Kontrolu instrukcí jsem řešila prostřednictvím pole typu klíč - hodnota.  
Vytvořila jsem si pole, kde klíčem byl název instrukce a hodnotou reprezentace jejích parametrů. Například:  
`$this->instructions = ["move" => "v s", "pops" => "v", "add" => "v s s", ...]`,  
kde v značí \<var\>, s značí \<symb\> atd.  
Pak mi tedy stačilo zjistit, zda je v poli povolených instrukcí klíč s hodnotou právě kontrolované instrukce. Pokud ano, vytáhla jsem si z pole hodnotu, rozdělila ji podle bílých znaků a v cyklu pak zkontrolovala jednotlivé parametry přes regulární výraz.