<?php

const PARAM_ERROR = 10;
const HEADER_ERROR = 21;
const OP_CODE_ERROR = 22;
const OTHER_LEX_SEM_ERROR = 23;

// classes and other stuff

class Statistics{
    private $loc;
    private $comments;
    private $labels;
    private $jumps;

    /**
     * Statistics constructor.
     */
    public function __construct(){
        // cause i dont count .ipp2019
        $this->loc = 1;
        $this->comments = 0;
        $this->labels = 0;
        $this->jumps = 0;
    }

    public function incLoc(){
        $this->loc++;
    }

    public function incComments(){
        $this->comments++;
    }

    public function incLabels(){
        $this->labels++;
    }

    public function incJumps(){
        $this->jumps++;
    }

    /**
     * @return int
     */
    public function getLoc(): int
    {
        return $this->loc;
    }

    /**
     * @return int
     */
    public function getComments(): int
    {
        return $this->comments;
    }

    /**
     * @return int
     */
    public function getLabels(): int
    {
        return $this->labels;
    }

    /**
     * @return int
     */
    public function getJumps(): int
    {
        return $this->jumps;
    }


}

class Scanner{
    private $inputLine;
    private $firstLine;
    private $ch;
    private $stats;
    private $xmlGenerator;

    /**
     * Scanner constructor.
     * @param $inputLine
     * @param $firstLine
     */
    public function __construct($stats){
        $this->inputLine= "";
        $this->firstLine = 1;
        $this->stats = $stats;
        $this->xmlGenerator = new XMLWriter();
        $this->xmlGenerator->openMemory();
        $this->xmlGenerator->openUri("php://output");
        $this->xmlGenerator->startDocument("1.0", "UTF-8");
        $this->xmlGenerator->setIndent(4);
        $this->ch = new Checker($stats, $this->xmlGenerator);


    }

    public function readInput(){

        while($this->inputLine = fgets(STDIN)){
            //echo $inputLine;
            $this->ch->checkLine($this->inputLine, $this->firstLine);

            if($this->firstLine == 1){
                $this->firstLine--;
            }
        }

        $this->xmlGenerator->endElement();
        $this->xmlGenerator->endDocument();
        $this->getXML();


    }

    public function getXML()
    {
        return $this->xmlGenerator->outputMemory();
    }

}


class Checker{

    private $instructions;
    private $stats;
    private $xmlGenerator;
    private $counter;

    /**
     * Checker constructor.
     */
    public function __construct($stats, $xmlGenerator)
    {
        $this->stats = $stats;
        $this->xmlGenerator = $xmlGenerator;
        $this->counter = 0;
        $this->instructions = [
            "move" => "v s",
            "createframe" => "",
            "pushframe" => "",
            "popframe" => "",
            "defvar" => "v",
            "call" => "l",
            "return" => "",
            "pushs" => "s",
            "pops" => "v",
            "add" => "v s s",
            "sub" => "v s s",
            "mul" => "v s s",
            "div" => "v s s",
            "idiv" => "v s s",
            "int2float" => "v s",
            "float2int" => "v s",
            "lt" => "v s s",
            "gt" => "v s s",
            "eq" => "v s s",
            "and" => "v s s",
            "or" => "v s s",
            "not" => "v s",
            "int2char" => "v s",
            "stri2int" => "v s s",
            "read" => "v t",
            "write" => "s",
            "concat" => "v s s",
            "strlen" => "v s",
            "getchar" => "v s s",
            "setchar" => "v s s",
            "type" => "v s",
            "label" => "l",
            "jump" => "l",
            "jumpifeq" => "l s s",
            "jumpifneq" => "l s s",
            "exit" => "s",
            "dprint" => "s",
            "break" => "",
        ];


    }

    /**
     * @return int
     */
    public function getCounter()
    {
        return $this->counter;
    }

    /**
     * @param int $counter
     */
    public function incCounter()
    {
        $this->counter = $this->counter + 1;
    }


    public function checkLine($line, $firstLine){
        if($firstLine == 1){
            if(preg_match_all("/\s?[.]ippcode19\s?$/i", $line)){

            } else if(preg_match_all("/\s*[.]ippcode19\s*#?.*/i", $line)){
                $this->stats->incComments();
            } else {
                exit(HEADER_ERROR);
            }
            // TODO: GENERATE XML HEADER

            $this->xmlGenerator->startElement('program');
            $this->xmlGenerator->writeAttribute("language","IPPcode19");
        } else {
            // divide " "
            // extract # comments in the middle of row which dont begin with space
            if(strpos($line, "#") !== false && $line[0] != "#"){
                $line = strstr($line, "#", true);
                $this->stats->incComments();
            }
            $splitted = preg_split("/\s/", $line);
            $splitted = array_values(array_filter($splitted));
            if(count($splitted) != 0){
                $this->checkInstruction($splitted);
            }
        }
    }

    private function checkInstruction($splitted){
        $this->stats->incLoc();
        //first field - # or name of instruction
        if($splitted[0][0] == "#"){
            // it s a comment, just let it be
            $this->stats->incComments();
        } else {
            // otestuj, zda jde o platnou instrukci, jinak chyba
            if(isset($this->instructions[strtolower($splitted[0])])){
                // instruction found ! (y)
                $this->incCounter();
                //print_r($splitted);
                // bonus stats counting
                $testedString = strtolower($splitted[0]);
                if($testedString == "label"){
                    $this->stats->incLabels();
                } elseif ($testedString == "jump" || $testedString == "jumpifeq" || $testedString == "jumpifneq" || $testedString == "jumpifneqs" || $testedString == "jumpifeqs" || $testedString == "call" || $testedString == "return"){
                    $this->stats->incJumps($prevValue+1);
                }
                // check arguments of instruction
                $params = $this->instructions[strtolower($splitted[0])];
                $paramsSplitted = preg_split("/\s/", $params);
                //var_dump($paramsSplitted);
                if(count($paramsSplitted) == count($splitted)-1 || $splitted[count($paramsSplitted)+1][0] == "#" || $paramsSplitted[0] == ""){
                    if($splitted[count($paramsSplitted)+1][0] == "#"){
                        $this->stats->incComments();
                    }
                    if($paramsSplitted[0] == ""){
                        // instruction without parameters
                        // TODO: generate XML
                        $this->xmlGenerator->startElement("instruction");
                        $this->xmlGenerator->writeAttribute("order", $this->getCounter());
                        $this->xmlGenerator->writeAttribute("opcode", strtoupper($splitted[0]));
                        $this->xmlGenerator->endElement();

                    } else {
                        // TODO: generate XML for standard instruction
                        $this->xmlGenerator->startElement("instruction");
                        $this->xmlGenerator->writeAttribute("order", $this->getCounter());
                        $this->xmlGenerator->writeAttribute("opcode", strtoupper($splitted[0]));
                        for($i = 0; $i < count($paramsSplitted); $i++){
                            switch($paramsSplitted[$i]){
                                case "l":
                                    $this->checkLabel($splitted[$i+1], $i+1);
                                    break;
                                case "s":
                                    $this->checkConstOrVariable($splitted[$i+1], $i+1);
                                    break;
                                case "v":
                                    $this->checkVariable($splitted[$i+1], $i+1);
                                    break;
                                case "t":
                                    $this->checkType($splitted[$i+1], $i+1);
                                    break;
                                default:
                                    echo "this will never happen, so chill out\n";
                            }
                        }
                        $this->xmlGenerator->endElement();
                    }
                } else {
                    exit(OP_CODE_ERROR);
                }

            } else {
                // unsupported instruction
                exit(OP_CODE_ERROR);
            }
        }
    }

    private function checkConstOrVariable($splitted, $i){
        if(preg_match_all("/^(L|G|T)F@([a-zA-Z]|_|-|\\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\\$|&|%|\*|!|\?)*$/", $splitted) ||
            preg_match_all("/^(bool@true|bool@false|int@(\+|-)?[0-9]*|nil@nil|string@([^\s#\\\]|\\\[0-9][0-9][0-9])([^\s#\\\]|\\\[0-9][0-9][0-9])*)|string@$/", $splitted)){
            // TODO: generate XML
            str_replace("&", "&amp;", $splitted);
            str_replace("<", "&lt;", $splitted);
            str_replace(">", "&gt;", $splitted);
            $this->xmlGenerator->startElement("arg".$i);
            if(preg_match_all("/^(L|G|T)F@([a-zA-Z]|_|-|\\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\\$|&|%|\*|!|\?)*$/", $splitted)){
                $this->xmlGenerator->writeAttribute("type", "var");
                $this->xmlGenerator->text($splitted);
            } else {
                $twoParts = explode("@", $splitted, 2);
                $this->xmlGenerator->writeAttribute("type", $twoParts[0]);
                $this->xmlGenerator->text($twoParts[1]);
            }
            $this->xmlGenerator->endElement();
        } else {
            exit(OTHER_LEX_SEM_ERROR);
        }
    }

    private function checkVariable($splitted, $i){
        if(preg_match_all("/^(L|G|T)F@([a-zA-Z]|_|-|\\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\\$|&|%|\*|!|\?)*$/", $splitted)){
            // TODO: generate XML
            str_replace("&", "&amp;", $splitted);
            str_replace("<", "&lt;", $splitted);
            str_replace(">", "&gt;", $splitted);
            $this->xmlGenerator->startElement("arg".$i);
            $this->xmlGenerator->writeAttribute("type", "var");
            $this->xmlGenerator->text($splitted);
            $this->xmlGenerator->endElement();
        } else {
            exit(OTHER_LEX_SEM_ERROR);
        }
    }

    private function checkLabel($splitted, $i){
        if(preg_match_all("/^([a-zA-Z]|_|-|\\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\\$|&|%|\*|!|\?)*$/", $splitted)){
            // TODO: generate XML
            $this->xmlGenerator->startElement("arg".$i);
            $this->xmlGenerator->writeAttribute("type", "label");
            $this->xmlGenerator->text($splitted);
            $this->xmlGenerator->endElement();
        } else {
            exit(OTHER_LEX_SEM_ERROR);
        }
    }

    private function checkType($splitted, $i){
        if($splitted == "int" || $splitted == "string" || $splitted == "bool"){
            // TODO: generate XML
            $this->xmlGenerator->startElement("arg".$i);
            $this->xmlGenerator->writeAttribute("type", "type");
            $this->xmlGenerator->text($splitted);
            $this->xmlGenerator->endElement();
        } else {
            exit(OTHER_LEX_SEM_ERROR);
        }
    }
}



// parse parameters
$shortOpts = "";

$longOpts = array(
	"help",
	"stats:",
	"loc",
	"comments",
	"labels",
	"jumps",
);

$options = getopt($shortOpts, $longOpts);
//var_dump($options);

//var_dump($argc);

$sLoc = 0;

if(isset($options["help"]) && $argc == 2){
    // doesnt make sense to use help and other args
    echo "********************************************************************************\n".
         "** Run script:                                                                **\n".
         "** 1. without parameters                                                      **\n".
         "** 2. with parameter --help (shows help)                                      **\n".
         "** 3. with parameter --stats=file and --loc|--comments|--jumps|--labels       **\n".
         "**    (saves statistics into file)                                            **\n".
         "**                                                                            **\n".
         "** It is NECESSARY to give an input (code to parse)!                          **\n".
         "**                                                                            **\n".
         "** Examples:                                                                  **\n".
         "** php7.3 parse.php < inputfile.txt                                           **\n".
         "** php7.3 parse.php --help                                                    **\n".
         "** php7.3 parse.php --stats=file.txt --jumps --labels --loc < inputfile.txt   **\n".
         "********************************************************************************\n";
}
elseif (($argc == 1 && empty($options)) || (!empty($options) && isset($options["stats"]) && !isset($options["help"]))){
    // okay, but if stats, check other options
    $outputFile = "";
    if(isset($options["stats"])){
        $outputFile = $options["stats"];

        if(!isset($options["loc"]) && !isset($options["comments"]) && !isset($options["labels"]) && !isset($options["jumps"])){
            echo "What stats do you want? You must specify it. Use --help.\n";
            exit(PARAM_ERROR);
        }

        if((count($options) == 2 && $argc != 3) || (count($options) == 3 && $argc != 4) || (count($options) == 4 && $argc != 5)){
            echo "Wrong parameters. Use --help.\n";
            exit(PARAM_ERROR);
        }

    }

    // okay, run the program

    $stats = new Statistics();
    $scan = new Scanner($stats);
    $scan->readInput();


    // write stats if necessary
    if(isset($options["stats"])){
        $file = fopen($outputFile, "w") or exit(12);
        for($i = 2; $i < $argc; $i++){
            switch (str_replace("-", "", $argv[$i])){
                case "loc":
                    $text = $stats->getLoc()."\n";
                    break;
                case "comments":
                    $text = $stats->getComments()."\n";
                    break;
                case "labels":
                    $text = $stats->getLabels()."\n";
                    break;
                case "jumps":
                    $text = $stats->getJumps()."\n";
                    break;
                default:
                    echo "this will never happen, so chill out";
            }
            fwrite($file, $text);
        }
        fclose($file);
    }


} else {
    echo "It seems you used wrong parameters. Use --help.\n";
    exit(PARAM_ERROR);
}

?>