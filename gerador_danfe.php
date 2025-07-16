<?php
// Gerador de DANFE - Integração com Python
// Verificar se autoloader existe (pode estar no diretório atual ou pai)
$autoload_paths = ['vendor/autoload.php', '../vendor/autoload.php'];
$autoload_found = false;

foreach ($autoload_paths as $path) {
    if (file_exists($path)) {
        require_once $path;
        $autoload_found = true;
        break;
    }
}

if (!$autoload_found) {
    echo "ERROR:Dependências PHP não instaladas! Execute: composer install\n";
    exit(1);
}

use NFePHP\DA\NFe\Danfe;

// Configurar codificação
mb_internal_encoding('UTF-8');
mb_http_output('UTF-8');

// Habilita exibição de erros para debug
error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('memory_limit', '512M');  // Aumentar limite de memória

// Verifica se foi passado o arquivo XML como parâmetro
if ($argc < 2) {
    echo "ERROR:Arquivo XML não especificado!\n";
    echo "Uso: php gerador_danfe.php arquivo.xml [nome_personalizado]\n";
    exit(1);
}

$arquivoXML = $argv[1];
$nomePersonalizado = isset($argv[2]) ? $argv[2] : null; // Nome personalizado opcional

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
    
    // CUSTOMIZAÇÃO: Processar XML para incluir dados de rastro na descrição
    $xml_customizado = adicionarDadosRastroNaDescricao($xml);
    
    // Cria o gerador de DANFE com XML customizado
    $danfe = new Danfe($xml_customizado);
    
    // Ativar concatenação automática de informações sobre rastro e medicamento
    $danfe->descProdInfoLoteTxt = true;
    
    // Gera o PDF da DANFE (formato A4 retrato - padrão Receita Federal)
    $pdf = $danfe->render();
    
    if (empty($pdf)) {
        throw new Exception("PDF gerado está vazio");
    }
    
    // Nome do arquivo PDF - LÓGICA CORRIGIDA SEM _DANFE
    if ($nomePersonalizado) {
        // Se nome personalizado foi fornecido, usar ele (sem extensão)
        $nomeBase = basename($nomePersonalizado, '.pdf'); // Remove .pdf se fornecido
        $nomePDF = dirname($arquivoXML) . '/' . $nomeBase . '.pdf';
    } else {
        // Comportamento padrão - apenas o nome do XML (SEM _DANFE)
        $nomeBase = basename($arquivoXML, '.xml');
        $nomePDF = dirname($arquivoXML) . '/' . $nomeBase . '.pdf';
    }
    
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

/**
 * Função para adicionar dados de rastro na descrição do produto
 * Inclui: nLote, qLote, dFab, dVal dentro da descrição do produto
 */
function adicionarDadosRastroNaDescricao($xml) {
    try {
        $dom = new DOMDocument();
        $dom->preserveWhiteSpace = false;
        $dom->formatOutput = true;
        
        if (!$dom->loadXML($xml)) {
            return $xml; // Retorna XML original se não conseguir processar
        }
        
        $xpath = new DOMXPath($dom);
        
        // Registrar namespaces se necessário
        $xpath->registerNamespace('nfe', 'http://www.portalfiscal.inf.br/nfe');
        
        // Buscar todos os produtos
        $produtos = $xpath->query('//det/prod | //nfe:det/nfe:prod');
        
        foreach ($produtos as $prod) {
            // Buscar elemento rastro
            $rastros = $xpath->query('.//rastro | .//nfe:rastro', $prod);
            
            if ($rastros->length > 0) {
                $rastroInfo = [];
                
                foreach ($rastros as $rastro) {
                    $infoRastro = [];
                    
                    // Extrair dados de rastro
                    $nLote = $xpath->query('.//nLote | .//nfe:nLote', $rastro);
                    $qLote = $xpath->query('.//qLote | .//nfe:qLote', $rastro);
                    $dFab = $xpath->query('.//dFab | .//nfe:dFab', $rastro);
                    $dVal = $xpath->query('.//dVal | .//nfe:dVal', $rastro);
                    
                    if ($nLote->length > 0) {
                        $infoRastro[] = "LOTE: " . trim($nLote->item(0)->nodeValue);
                    }
                    
                    if ($qLote->length > 0) {
                        $qtd = number_format(floatval($qLote->item(0)->nodeValue), 3, ',', '.');
                        $infoRastro[] = "QTD LOTE: " . $qtd;
                    }
                    
                    if ($dFab->length > 0) {
                        $dataFab = formatarData($dFab->item(0)->nodeValue);
                        $infoRastro[] = "FAB: " . $dataFab;
                    }
                    
                    if ($dVal->length > 0) {
                        $dataVal = formatarData($dVal->item(0)->nodeValue);
                        $infoRastro[] = "VAL: " . $dataVal;
                    }
                    
                    if (!empty($infoRastro)) {
                        $rastroInfo[] = implode(' | ', $infoRastro);
                    }
                }
                
                // Adicionar informações de rastro à descrição do produto
                if (!empty($rastroInfo)) {
                    $xProd = $xpath->query('.//xProd | .//nfe:xProd', $prod);
                    
                    if ($xProd->length > 0) {
                        $descricaoOriginal = trim($xProd->item(0)->nodeValue);
                        
                        // Criar box visual para os dados de rastro
                        $dadosRastro = "\n" . str_repeat("-", 45) . "\n";
                        $dadosRastro .= "📋 DADOS DE RASTRO:\n";
                        $dadosRastro .= implode("\n", $rastroInfo) . "\n";
                        $dadosRastro .= str_repeat("-", 45);
                        
                        $novaDescricao = $descricaoOriginal . $dadosRastro;
                        $xProd->item(0)->nodeValue = $novaDescricao;
                    }
                }
            }
        }
        
        return $dom->saveXML();
        
    } catch (Exception $e) {
        // Em caso de erro, retorna XML original
        return $xml;
    }
}

/**
 * Formatar data do formato YYYY-MM-DD para DD/MM/YYYY
 */
function formatarData($data) {
    try {
        if (strlen($data) >= 10) {
            $ano = substr($data, 0, 4);
            $mes = substr($data, 5, 2);
            $dia = substr($data, 8, 2);
            return "$dia/$mes/$ano";
        }
        return $data;
    } catch (Exception $e) {
        return $data;
    }
}

?>
