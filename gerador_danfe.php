<?php
// Gerador de DANFE - Integração com Python
require_once 'vendor/autoload.php';

use NFePHP\DA\NFe\Danfe;

// Habilita exibição de erros para debug
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Verifica se foi passado o arquivo XML como parâmetro
if ($argc < 2) {
    echo "ERROR:Arquivo XML não especificado!\n";
    echo "Uso: php gerador_danfe.php arquivo.xml\n";
    exit(1);
}

$arquivoXML = $argv[1];

// Verifica se arquivo XML existe
if (!file_exists($arquivoXML)) {
    echo "ERROR:Arquivo '$arquivoXML' não encontrado!\n";
    exit(1);
}

try {
    // Carrega o XML da nota fiscal
    $xml = file_get_contents($arquivoXML);
    
    if ($xml === false) {
        throw new Exception("Não foi possível ler o arquivo XML");
    }
    
    if (empty($xml)) {
        throw new Exception("Arquivo XML está vazio");
    }
    
    // Verifica se é um XML válido
    $dom = new DOMDocument();
    libxml_use_internal_errors(true);
    $valid = $dom->loadXML($xml);
    
    if (!$valid) {
        $errors = libxml_get_errors();
        $errorMsg = "XML inválido: ";
        foreach ($errors as $error) {
            $errorMsg .= $error->message . " ";
        }
        throw new Exception($errorMsg);
    }
    
    // Verifica se tem as tags necessárias
    $xpath = new DOMXPath($dom);
    $infNFe = $xpath->query('//*[local-name()="infNFe"]');
    
    if ($infNFe->length == 0) {
        throw new Exception("Tag infNFe não encontrada no XML");
    }
    
    // Verifica modelo
    $modelo = $xpath->query('//*[local-name()="mod"]');
    if ($modelo->length > 0) {
        $mod = $modelo->item(0)->nodeValue;
        if ($mod != '55') {
            throw new Exception("Modelo deve ser 55 (NFe), encontrado: $mod");
        }
    } else {
        throw new Exception("Tag modelo não encontrada no XML");
    }
    
    // Cria o gerador de DANFE
    $danfe = new Danfe($xml);
    
    // Gera o PDF da DANFE
    $pdf = $danfe->render();
    
    if (empty($pdf)) {
        throw new Exception("PDF gerado está vazio");
    }
    
    // Nome do arquivo PDF baseado no XML
    $nomeBase = basename($arquivoXML, '.xml');
    $nomePDF = dirname($arquivoXML) . '/' . $nomeBase . '_DANFE.pdf';
    
    // Salva o PDF
    $bytesEscritos = file_put_contents($nomePDF, $pdf);
    
    if ($bytesEscritos === false) {
        throw new Exception("Não foi possível salvar o arquivo PDF");
    }
    
    if ($bytesEscritos == 0) {
        throw new Exception("PDF salvo está vazio");
    }
    
    // Verifica se o arquivo foi realmente criado
    if (!file_exists($nomePDF)) {
        throw new Exception("Arquivo PDF não foi criado");
    }
    
    // Retorna sucesso para o Python
    echo "SUCCESS:$nomePDF\n";
    
} catch (Exception $e) {
    // Retorna erro para o Python
    echo "ERROR:" . $e->getMessage() . "\n";
    exit(1);
}
?> 