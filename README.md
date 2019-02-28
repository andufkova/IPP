# Implementační dokumentace k 1. úloze do IPP 2018/2019
Jméno a příjmení: Aneta Dufková  
Login: xdufko02

Ke zpracování projektu byly využity informace z dokumentace na http://php.net. 
Projekt byl vypracován v souladu s verzí PHP 7.3 ve vývojovém prostředí PhpStorm. Zpracovávala jsem i rozšíření `STATP`.

## Struktura kódu
Cílem projektu je mj. procvičit si principy OOP. Z toho důvodu jsem v hlavním těle programu řešila pouze zpracování argumentů, 
zbytek funkcionality je rozdělený do tříd:
- Statistics - třída uchovávající všechny statistiky (počet instrukcí, komentářů atd.) pro rozšíření STATP.
- Scanner - třída, která čte vstup, dělí jej na řádky a ty posílá dále ke zpracování. Zároveň se stará o výpis XML reprezentace. 
- Checker - třída kontrolující jednotlivé řádky. Pomocí různých metod kontroluje zejména správnost instrukcí a jejich parametrů.

## Využité nástroje
Nápomocny mi byly například tyto třídy a funkce: `XMLWriter()`, `preg_match()`, `str_replace()`, `getopt()`, `explode()`, `strtolower()`, `strstr()`, ...  
Velmi nápomocný mi byl online nástroj 
https://regex101.com usnadňující tvrobru regulárních výrazů.  

## Zajímavosti z řešení
Kontrolu instrukcí jsem řešila prostřednictvím pole typu klíč - hodnota.  
Vytvořila jsem si pole, kde klíčem byl název instrukce a hodnotou reprezentace jejích parametrů. Například:  
`$this->instructions = ["move" => "v s", "pops" => "v", "add" => "v s s", ...]`,  
kde v značí \<var\>, s značí \<symb\> atd.  
Pak mi tedy stačilo zjistit, zda je v poli povolených instrukcí klíč s hodnotou právě kontrolované instrukce. Pokud ano, vytáhla jsem si z pole hodnotu, rozdělila ji podle bílých znaků a v cyklu pak zkontrolovala jednotlivé parametry přes regulární výraz.
