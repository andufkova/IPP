<?php

/**
 * IPP project 2018/2019 - 2nd task
 * @author     Aneta Dufkova
 */

const PARAM_ERROR = 10;
const INPUT_ERROR = 11;
const OUTPUT_ERROR = 12;
const SCRIPT_ERROR = 99;
//const PHP_ENGINE = "php7.3";
//const PYTHON_ENGINE = "python3.6";
const PHP_ENGINE = "php";
const PYTHON_ENGINE = "python";
const TMP_OUTPUT_FILE = "tmp_lzvkhfzapa.out";
const TMP_XML_FILE = "tmp_fuofirsdkl.out";
const XML_JEXAM = "jexamxml.jar";
//const XML_JEXAM = "/pub/courses/ipp/jexamxml/jexamxml.jar";
const SPACE_DELIMITER = "\ ";
const HTML_OUTPUT = "results.html";
const TEST_FOLDER_BOTH = "tests/both";
const TEST_FOLDER_INT = "tests/int";
const TEST_FOLDER_PARSE = "tests/parse";

/*****************************************************************
*******                   FILE STRUCTURE                   *******
******************************************************************/

/**
* structure of files to test
*/
class FileStructure{
    private $files;

    public function __construct(){
        $this->files = array();
    }

    /**
     * saves all src files to an array
     * creates missing .rc, .in and .out files 
     */
    private function _extractAndCreateFiles($array, $file){
            preg_match("/.*\.src/m", $file, $matches);
            // add to array
            if(count($matches) != 0){

                // check for in, out and rc
                preg_match("/.*(?=.src)/m", $matches[0], $matches2);
                $in = $matches2[0].".in";
                $out = $matches2[0].".out";
                $rc = $matches2[0].".rc";
                if(!in_array($in, $array)){
                    // create an empty file with input
                    if (!touch($in, time())) {
                        fwrite(STDERR,'Whoops, something went wrong during file creating...\n');
                        exit(INPUT_ERROR);
                    }
                }
                if(!in_array($out, $array)){
                    // create an empty file with output
                    if (!touch($out, time())) {
                        fwrite(STDERR,'Whoops, something went wrong during file creating...\n');
                        exit(OUTPUT_ERROR);
                    }
                }
                if(!in_array($rc, $array)){
                    // create a file
                    if (!$handle = fopen($rc, 'w')) {
                        fwrite(STDERR,"Cannot open file *.rc\n");
                        exit(OUTPUT_ERROR);
                    }
                    if (fwrite($handle, "0") === FALSE) {
                        fwrite(STDERR,"Cannot write to file *.rc\n");
                        exit(OUTPUT_ERROR);
                    }
                    fclose($handle);
                }
                //$matches2[0] = str_replace(" ", "\ ", $matches2[0]);

                array_push($this->files, $matches2[0]);

            }
    }
    
    /**
     * unpacks directory
     */
    private function _unpackDirectory($dir){
        if($dir == false){
            $scan = glob(".".DIRECTORY_SEPARATOR."*");
        } else {
            $scan = glob("$dir".DIRECTORY_SEPARATOR."*");
        }
        foreach($scan as $s){
            if(is_dir($s)) {
                $this->_unpackDirectory($s);
            } else {
                $this->_extractAndCreateFiles($scan, $s);
            }
        }
    }

    /**
     * scan directory
     */
    public function loadFiles($dir, $recursively){
        if($recursively == false){
            if($dir == false){
                $scan = glob(".".DIRECTORY_SEPARATOR."*");
                foreach($scan as $s){
                    $this->_extractAndCreateFiles($scan, $s);
                }
            } else {
                $scan = glob("$dir".DIRECTORY_SEPARATOR."*");
                foreach($scan as $s){
                   $this-> _extractAndCreateFiles($scan, $s);
                }
            }
        } else {
            $this->_unpackDirectory($dir);
        }
    }

    public function __toString(){
        return implode("\n", $this->files);
    }

    public function getFiles(){
        return $this->files;
    }
}

/*****************************************************************
*******                       TESTER                       *******
******************************************************************/

/**
 * class used for testing
 */
class Tester{
    private $files;
    private $passed;
    private $notPassed;
    private $passedInt;
    private $notPassedInt;
    private $passedBoth;
    private $notPassedBoth;
    private $html;

    public function __construct($files){
        $this->files = $files;
        $this->passed = 0;
        $this->notPassed = 0;
        $this->passedInt = 0;
        $this->notPassedInt = 0;
        $this->passedBoth = 0;
        $this->notPassedBoth = 0;
        $this->html = new HtmlOutput();
    }

    /**
     * tests if XML output is the same as expedted XML output
     */
    private function _testXMLOutput($name){
        $exec = "java -jar ".XML_JEXAM." '".mb_convert_encoding($name, "UTF-8").".out' ".TMP_OUTPUT_FILE;
        exec($exec, $output, $returnedCode);
        if(in_array("Two files are identical", $output)){
            if(file_exists($name.".out.log")){
                unlink($name.".out.log");
            }
            return true;
        } else {
            return false;
        }

    }

    /**
     * tests if  output is the same as expedted output
     */
    private function _testOutput($name){
        $exec = "diff '".$name.".out' ".TMP_OUTPUT_FILE;
        exec($exec, $output, $returnedCode);
        foreach($output as $o){
            echo $o."\n";
        }
        if($output[0] == ""){
            return true;
        } else {
            return false;
        }

    }

    /**
     * tests if return code is the same as expedted return code
     */
    private function _testReturnCode($name, $returnedCode){
        if (!$handle = fopen($name.".rc", 'r')) {
            fwrite(STDERR,"Cannot open file *.rc.\n");
            exit(INPUT_ERROR);
        }
        $content = fread($handle, filesize($name.".rc"));
        if ($content === FALSE) {
            fwrite(STDERR,"Cannot read from file *.rc.\n");
            exit(INPUT_ERROR);
        }
        fclose($handle);

        if(!is_numeric(intval($content))){
            exit(INPUT_ERROR);
        }

        if(intval($content) == $returnedCode){
            return true;
        } else {
            return false;
        }
    }

    /**
     * tests parse.php
     * run parse.php and controls return code and output
     * generates html report
     */
    public function testParse($parser){
        if(!$parser){
            $parser = "parse.php";
        }
        $this->html->addH1("Test PARSE-ONLY");
        foreach($this->files as $file){
            $exec = PHP_ENGINE." ".$parser." < '".$file.".src'";
            //echo $exec."\n";
            exec($exec, $outputFile, $returnedCode);
            $outputFile = implode("\n", $outputFile);
            if (!$handle = fopen(TMP_OUTPUT_FILE, 'w')) {
                fwrite(STDERR,"Cannot open file.\n");
                exit(OUTPUT_ERROR);
            }
            if (fwrite($handle, $outputFile) === FALSE) {
                fwrite(STDERR,"Cannot write to file.\n");
                exit(OUTPUT_ERROR);
            }
            fclose($handle);

            // test rc
            if($this->_testReturnCode($file, $returnedCode)){
                if($returnedCode == 0){

                    // test XML only if rc = 0
                    // test xml
                    if($this->_testXMLOutput($file)){
                        $this->passed++;
                        //echo "---- PASSED!\n";
                        $this->html->addTableRow($file, true, false);
                    } else {
                        //echo "ERROR. NOT PASSED\n";
                        $this->html->addTableRow($file, false, "XML output differs.");
                        $this->notPassed++;
                    }
                } else {
                    $this->passed++;
                    //echo "---- PASSED!\n";
                    $this->html->addTableRow($file, true, false);
                }
            } else {
                //echo "ERROR. NOT PASSED\n";
                $this->html->addTableRow($file, false, "Return code differs.");
                $this->notPassed++;
            }


        }

        if(unlink(TMP_OUTPUT_FILE) == false){
            fwrite(STDERR,"Cannot delete file.\n");
            exit(SCRIPT_ERROR);
        }

        /*echo "-------------------------------------------------\n";
        echo "Passed tests: ".$this->passed."\n";
        echo "Not passed tests: ".$this->notPassed."\n";*/


        $this->html->addStats($this->passed, $this->notPassed);
        $this->html->generateHtml();

    }

    /**
     * tests interpret.py
     * run interpret.py and controls return code and output
     * generates html report
     */
    public function testInterpret($interpret){
        if(!$interpret){
            $interpret = "interpret.py";
        }

        $this->html->addH1("Test INT-ONLY");
        foreach($this->files as $file){
            $exec = PYTHON_ENGINE." ".$interpret." --source='".$file.".src' --input='".$file.".in'";
            //echo $exec."\n";
            exec($exec, $outputFile, $returnedCode);
            // create a file
            $outputFile = implode("\n", $outputFile);
            if (!$handle = fopen(TMP_OUTPUT_FILE, 'w')) {
                fwrite(STDERR,"Cannot open file.\n");
                exit(OUTPUT_ERROR);
            }
            if (fwrite($handle, $outputFile) === FALSE) {
                fwrite(STDERR,"Cannot write to file.\n");
                exit(OUTPUT_ERROR);
            }
            fclose($handle);

            // test rc
            if($this->_testReturnCode($file, $returnedCode)){
                if($returnedCode == 0){
                    // test XML only if rc = 0
                    // test xml
                    if($this->_testOutput($file)){
                        $this->passedInt++;
                        //echo "---- PASSED!\n";
                        $this->html->addTableRow($file, true, false);
                    } else {
                        //echo "ERROR. NOT PASSED\n";
                        $this->html->addTableRow($file, false, "Output differs.");
                        $this->notPassedInt++;

                    }
                } else {
                    $this->passedInt++;
                    //echo "---- PASSED!\n";
                    $this->html->addTableRow($file, true, false);
                }
            } else {
                //echo "ERROR. NOT PASSED\n";
                $this->html->addTableRow($file, false, "Return code differs.");
                $this->notPassedInt++;
            }


        }

        if(file_exists(TMP_OUTPUT_FILE)){
            if(unlink(TMP_OUTPUT_FILE) == false){
                fwrite(STDERR,"Cannot delete file.\n");
                exit(SCRIPT_ERROR);
            }
        }

        /*echo "-------------------------------------------------\n";
        echo "Passed tests: ".$this->passedInt."\n";
        echo "Not passed tests: ".$this->notPassedInt."\n";*/

        $this->html->addStats($this->passedInt, $this->notPassedInt);
        $this->html->generateHtml();


    }

    /**
     * tests parse.php & interpret.py
     * run parse.php then interpret.py and controls return code and output
     * generates html report
     */
    public function testBoth($parser, $interpret){
        if(!$parser){
            $parser = "parse.php";
        }
        if(!$interpret){
            $interpret = "interpret.py";
        }

        $this->html->addH1("Test BOTH");

        foreach($this->files as $file) {
            $exec = PHP_ENGINE." ".$parser." < '".$file.".src'";
            //echo $exec . "\n";
            exec($exec, $outputFile, $returnedCode);
            // create a file
            $outputFile = implode("\n", $outputFile);
            if (!$handle = fopen(TMP_XML_FILE, 'w')) {
                fwrite(STDERR,"Cannot open file\n");
                exit(OUTPUT_ERROR);
            }
            if (fwrite($handle, $outputFile) === FALSE) {
                fwrite(STDERR,"Cannot write to file.\n");
                exit(OUTPUT_ERROR);
            }
            fclose($handle);

            if ($returnedCode != 0) {
                if ($this->_testReturnCode($file, $returnedCode)) {
                    $this->passed++;
                    //echo "---- PASSED!\n";
                    $this->html->addTableRow($file, true, false);
                } else {
                    //echo "ERROR. NOT PASSED\n";
                    $this->html->addTableRow($file, false, "Return code differs.");
                    $this->notPassed++;
                }
            } else {
                // rc was 0, try interpret.py
                $exec = PYTHON_ENGINE." ".$interpret." --source='".TMP_XML_FILE."' --input='".$file.".in'";
                //echo $exec."\n";
                exec($exec, $outputFile, $returnedCode);
                //echo $returnedCode."\n";
                // create a file
                $outputFile = implode("\n", $outputFile);
                if (!$handle = fopen(TMP_OUTPUT_FILE, 'w')) {
                    fwrite(STDERR,"Cannot open file ".TMP_OUTPUT_FILE."TMP_OUTPUT_FILE.\n");
                    exit(OUTPUT_ERROR);
                }
                if (fwrite($handle, $outputFile) === FALSE) {
                    fwrite(STDERR,"Cannot write to file.\n");
                    exit(OUTPUT_ERROR);
                }
                fclose($handle);

                // test rc
                if($this->_testReturnCode($file, $returnedCode)){
                    if($returnedCode == 0){
                        // test XML only if rc = 0
                        // test xml
                        if($this->_testOutput($file)){
                            $this->passedBoth++;
                            //echo "---- PASSED!\n";
                            $this->html->addTableRow($file, true, false);
                        } else {
                            //echo "ERROR. NOT PASSED\n";
                            $this->html->addTableRow($file, false, "Output differs.");
                            $this->notPassedBoth++;

                        }
                    } else {
                        $this->passedBoth++;
                        //echo "---- PASSED!\n";
                        $this->html->addTableRow($file, true, false);
                    }
                } else {
                    //echo "ERROR. NOT PASSED\n";
                    $this->html->addTableRow($file, false, "Return code differs.");
                    $this->notPassedBoth++;
                }

                if(file_exists(TMP_OUTPUT_FILE)){
                    if(unlink(TMP_OUTPUT_FILE) == false){
                        fwrite(STDERR,"Cannot delete file.\n");
                        exit(SCRIPT_ERROR);
                    }
                }
                if(file_exists(TMP_XML_FILE)){
                    if(unlink(TMP_XML_FILE) == false){
                        fwrite(STDERR,"Cannot delete file.\n");
                        exit(SCRIPT_ERROR);
                    }
                }

            }
        }

        /*echo "-------------------------------------------------\n";
        echo "Passed tests: ".$this->passedBoth."\n";
        echo "Not passed tests: ".$this->notPassedBoth."\n";*/

        $this->html->addStats($this->passedBoth, $this->notPassedBoth);
        $this->html->generateHtml();


    }

}

/*****************************************************************
*******                   HTML OUTPUT                      *******
******************************************************************/

/**
* structure of html and css code for report
*/
class HtmlOutput{
    private $cssStyle;
    private $htmlHeader;
    private $htmlTitle;
    private $htmlFooter;
    private $htmlBody;
    private $htmlH1;
    private $htmlTableStart;
    private $htmlStats;
    private $rowCounter;


    public function __construct(){
        $this->cssStyle = "<style>body{font-family: Tahoma, Geneva, sans-serif;} table{margin: 0 auto; border: 1px solid black; border-collapse: collapse;}".
                                "table td{padding: 5px 10px 5px 10px; border: 1px solid black; border-collapse: collapse;} h1{text-align: center;}".
                                ".failed{color: #721c24; background-color: #f8d7da; border-color: #f5c6cb;} .box{padding: .75rem 1.25rem; border-radius: .25rem;}".
                                ".passed{color: #155724; background-color: #d4edda; border-color: #c3e6cb;} .info:hover{text-decoration: underline;}".
                                ".stats{color: #856404; background-color: #fff3cd; border-color: #ffeeba; margin-bottom: 20px;} .wrapper{display: table; margin: 0 auto;}".
                                ".author{text-align: right; margin-top: 10px; margin-bottom: 10px;}".
                                "label{cursor: pointer;} #showblock-1{display: none;} #showblock-1:checked + .more-block-1{height: auto; padding-top: 5px; padding-bottom: 5px;} #showblock-2{display: none;} #showblock-2:checked + .more-block-2{height: auto; padding-top: 5px; padding-bottom: 5px;}".
                                ".more-block{height: 0; color: #818182; overflow: hidden; -webkit-transition: height 300ms linear; -moz-transition: height 300ms linear; -o-transition: height 300ms linear; transition: height 300ms linear;} ";
        $this->htmlHeader = "<html><head><title>IPP project - test results</title><meta charset='UTF-8'>";
        $this->htmlTitle = "</style></head><body>";
        $this->htmlH1 = "<br>";
        $this->htmlTableStart = "<table><tr><td></td><td>Test name</td><td>Result</td><td>Details</td></tr>";
        $this->htmlBody = "<!--<tr><td>1.</td><td>test name - test</td><td><div class='box passed'>PASSED</div></td><td></td></tr>".
                           "<tr><td>2.</td><td>test name - test</td><td><div class='box failed'>FAILED</div></td><td><label for='showblock-1' class='info'>Show details</label><input type='checkbox' id='showblock-1'><div class='more-block-1 more-block'>Error</div></td></tr>"
                            ."<tr><td>2.</td><td>test name - test</td><td><div class='box failed'>FAILED</div></td><td><label for='showblock-2' class='info'>Show details</label><input type='checkbox' id='showblock-2'><div class='more-block-2 more-block'>Tady je důvod chyby</div></td></tr>-->";
        $this->htmlFooter = "</table><div class='author'>Author: Aneta Dufkova (xdufko02)</div></div><br></body>";
        $this->htmlStats = "<div class='wrapper'><div class='stats box'>";
        $this->rowCounter = 1;
    }

    /**
     * generates output to the html file
     */
    public function generateHtml(){
        $fileContent = $this->htmlHeader.$this->cssStyle.$this->jsScript.$this->htmlTitle.$this->htmlH1.$this->htmlStats.$this->htmlTableStart.$this->htmlBody.$this->htmlFooter;

        if (!$handle = fopen(HTML_OUTPUT, 'w')) {
            echo "Cannot open file ".HTML_OUTPUT.".";
            exit(OUTPUT_ERROR);
        }
        if (fwrite($handle, $fileContent) === FALSE) {
            echo "Cannot write to file ".HTML_OUTPUT.".";
            exit(OUTPUT_ERROR);
        }
        fclose($handle);
    }

    /**
     * adds statistics to html body
     */
    public function addStats($passed, $failed){
        $perc = ($passed + $failed)/100;
        if($perc == 0){
            $perc = "NaN";
        } else {
            $perc = round($passed/$perc, 2);
        }
        $this->htmlStats = $this->htmlStats."Passed tests: ".$passed."<br>Failed tests: ".$failed."<br>Success rate: ".$perc." %</div>";
    }

    /**
     * adds heading to html body
     */
    public function addH1($heading){
        $this->htmlH1 = $this->htmlH1."<h1>".$heading."</h1>";
    }

    /**
     * adds css to html body
     */
    private function _addCss(){
        $this->cssStyle = $this->cssStyle."#showblock-".$this->rowCounter."{display: none;} #showblock-".$this->rowCounter.":checked + .more-block-".$this->rowCounter."{height: auto; padding-top: 5px; padding-bottom: 5px;} ";
    }

    /**
     * adds table row with test result to html table
     */
    public function addTableRow($name, $passed, $detail){
        $row = "<tr><td>".$this->rowCounter."</td><td>".$name."</td>";
        if($passed){
            $row = $row."<td><div class='box passed'>PASSED</div></td><td></td></tr>";
        } else {
            $this->_addCss();
            $row = $row."<td><div class='box failed'>FAILED</div></td><td><label for='showblock-".$this->rowCounter."' class='info'>Show details</label><input type='checkbox' id='showblock-".$this->rowCounter."'><div class='more-block-".$this->rowCounter." more-block'>".$detail."</div></td></tr>";
        }

        $this->htmlBody = $this->htmlBody.$row;

        $this->rowCounter++;
    }


}

/*****************************************************************
*******                PARSING PARAMETERS                  *******
******************************************************************/

// parse parameters
$shortOpts = "";
$parseOnly = false;
$intOnly = false;
$directory = false;
$recursive = false;
$parseScript = false;
$intScript = false;

$longOpts = array(
    "help",
    "directory:",
    "recursive",
    "parse-script:",
    "int-script:",
    "parse-only",
    "int-only",
);

$options = getopt($shortOpts, $longOpts);

if(isset($options["help"]) && $argc == 2){
    // doesnt make sense to use help and other args
    echo "********************************************************************************\n".
         "** HELP                                                                       **\n".
         "** Possible parameters:                                                       **\n".
         "** - directory (specifies directory with tests)                               **\n".
         "** - recursive                                                                **\n".
         "** - parse-script (specifies path to parse.php)                               **\n".
         "** - int-script (specifies path to interpret.py)                              **\n".
         "** - parse-only (tests only parse.php)                                        **\n".
         "** - int-only (tests only interpret.py)                                       **\n".
         "**                                                                            **\n".
         "** Examples:                                                                  **\n".
         "** php test.php --directory=dir --recursive                                   **\n".
         "** php test.php --parse-only --parse-script=dir/parse.php                     **\n".
         "********************************************************************************\n";
} else {
    // check if there is unsupported argument
    foreach(array_slice($argv, 1) as $op){
        preg_match("/[a-z]+[-a-z]*/m", $op, $f);
        if($f[0] == "directory" || $f[0] == "parse-script" || $f[0] == "int-script"){
            $f[0] = $f[0] . ":";
        }
        if(!in_array($f[0], $longOpts)){
            exit(PARAM_ERROR);
        }
    }

    if(isset($options["directory"])){
        if(is_dir($options["directory"])){
            $directory = $options["directory"];
        } else {
            fwrite(STDERR,"Directory ".$options["directory"]." does not exist.\n");
            exit(INPUT_ERROR);
        }
    } else {
        if(isset($options["parse-only"])){
            $directory = TEST_FOLDER_PARSE;
        } else if (isset($options["int-only"])){
            $directory = TEST_FOLDER_INT;
        } else $directory = TEST_FOLDER_BOTH;
        
    }
    if(isset($options["recursive"])){
        $recursive = true;
    }
    if(isset($options["parse-script"])){
        $parseScript = $options["parse-script"];
    }
    if(isset($options["int-script"])){
        $intScript = $options["int-script"];
    }
    if(isset($options["parse-only"])){
        $parseOnly = true;
        if(isset($options["int-only"]) || isset($options["int-script"])){
            exit(PARAM_ERROR);
        }
    }
    if(isset($options["int-only"])){
        $parseOnly = true;
        if(isset($options["parse-only"]) || isset($options["parse-script"])){
            exit(PARAM_ERROR);
        }
    }

    //echo "everything is okay\n";

/*****************************************************************
*******                 PROGRAM START                      *******
******************************************************************/

    $fileStructure = new FileStructure();
    $fileStructure->loadFiles($directory, $recursive);
    //echo($fileStructure);
    $tester = new Tester($fileStructure->getFiles());

    if(isset($options["parse-only"])){
        $tester->testParse($parseScript);
    } elseif(isset($options["int-only"])){
        $tester->testInterpret($intScript);
    } else {
        $tester->testBoth($parseScript, $intScript);
    }


}



?>