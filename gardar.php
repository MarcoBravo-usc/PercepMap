
<?php

header("Content-Type: application/json; charset=utf-8");
header("Cache-Control: no-store, private");
header("X-Content-Type-Options: nosniff");

// Responder sempre en formato JSON.
function responder($ok, $mensaxe, $codigo = 200) {
    http_response_code($codigo);

    echo json_encode(
        [
            "ok" => $ok,
            "mensaxe" => $mensaxe
        ],
        JSON_UNESCAPED_UNICODE
    );

    exit;
}


// Comprobar que a petición é POST.
if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    responder(false, "Método non permitido.", 405);
}


// Límite de tamaño para reducir o risco de abuso de recursos.
$maxBytes = 1024 * 1024; // 1 MiB por entrega
if (isset($_SERVER['CONTENT_LENGTH']) && (int) $_SERVER['CONTENT_LENGTH'] > $maxBytes) {
    responder(false, "A entrega supera o tamaño permitido.", 413);
}
// Recibir os datos enviados desde gravación.html.
$corpo = file_get_contents("php://input");

if ($corpo === false || strlen($corpo) > $maxBytes) {
    responder(false, "A entrega supera o tamaño permitido.", 413);
}
$datos = json_decode($corpo, true, 64);

if (!is_array($datos)) {
    responder(false, "Non se recibiron datos JSON válidos.", 400);
}


// Limitar os identificadores para evitar entradas anómalas.
if (!is_string($datos['participanteId'] ?? null) || strlen($datos['participanteId']) > 128) {
    responder(false, "Identificador de participante non válido.", 400);
}
if (isset($datos['tokenEntrega']) && (!is_string($datos['tokenEntrega']) || strlen($datos['tokenEntrega']) > 128)) {
    responder(false, "Token de entrega non válido.", 400);
}
// Comprobar os datos obrigatorios.
if (
    empty($datos["participanteId"]) ||
    !isset($datos["datosPersoais"]) ||
    !is_array($datos["datosPersoais"])
) {
    responder(false, "Faltan os datos obrigatorios do participante.", 400);
}


// Comprobar os tres mapas.
$mapas = ["espana", "america", "galicia"];

foreach ($mapas as $mapa) {
    if (!isset($datos[$mapa])) {
        $datos[$mapa] = [];
    }

    if (!is_array($datos[$mapa])) {
        responder(false, "Os datos do mapa " . $mapa . " non son válidos.", 400);
    }
}


// Validar cada variedade sen modificar os datos orixinais.
foreach ($mapas as $mapa) {
    foreach ($datos[$mapa] as $variedade) {
        if (!is_array($variedade) || !is_string($variedade["nome"] ?? null)
            || trim($variedade["nome"]) === ""
            || !is_array($variedade["xeometria"] ?? null)
            || ($variedade["xeometria"]["type"] ?? null) !== "Feature"
            || ($variedade["xeometria"]["geometry"]["type"] ?? null) !== "Polygon"
            || !is_array($variedade["xeometria"]["geometry"]["coordinates"] ?? null)) {
            responder(false, "Unha variedade do mapa " . $mapa . " ten datos incompletos.", 400);
        }
    }
}

// Engadir data de entrega se non chegou desde o navegador.
if (empty($datos["dataEntrega"])) {
    $datos["dataEntrega"] = date("c");
}


// Crear un identificador único para esta entrega.
try {
    $datos["idEntrega"] = bin2hex(random_bytes(16));
} catch (Exception $erro) {
    responder(false, "Non se puido crear o identificador da entrega.", 500);
}


// Un bloqueo separado permite substituír atomicamente respostas.json.
$directorio = getenv('PERCEPMAP_DATA_DIR');
if (!$directorio || !is_dir($directorio) || !is_writable($directorio)) {
    error_log('PercepMap: PERCEPMAP_DATA_DIR non configurado ou non escribible');
    responder(false, "O almacenamento non está configurado.", 503);
}
$directorio = realpath($directorio);
// O administrador debe situar este directorio FÓRA da raíz pública do servidor.
$ficheiro = $directorio . DIRECTORY_SEPARATOR . "respostas.json";
$bloqueo = fopen($directorio . DIRECTORY_SEPARATOR . ".respostas.lock", "c");
if ($bloqueo === false || !flock($bloqueo, LOCK_EX)) {
    responder(false, "Non se puido bloquear o almacenamento.", 500);
}

try {
    if (!file_exists($ficheiro)) {
        $respostas = [];
    } else {
        $contido = file_get_contents($ficheiro);
        if ($contido === false) {
            throw new RuntimeException("Non se puideron ler as respostas anteriores.");
        }
        $respostas = json_decode($contido, true);
        if (json_last_error() !== JSON_ERROR_NONE || !is_array($respostas) || !array_is_list($respostas)) {
            throw new RuntimeException("respostas.json non contén unha lista JSON válida. Non se modificou.");
        }
    }

    // Reintentar a mesma entrega non debe crear duplicados.
    $token = $datos["tokenEntrega"] ?? null;
    if (is_string($token) && $token !== "") {
        foreach ($respostas as $anterior) {
            if (is_array($anterior) && ($anterior["tokenEntrega"] ?? null) === $token) {
                flock($bloqueo, LOCK_UN);
                fclose($bloqueo);
                responder(true, "Esta entrega xa estaba gardada.");
            }
        }
    }

    $respostas[] = $datos;
    $json = json_encode($respostas, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
    $temporal = tempnam($directorio, ".respostas-temp-");
    if ($temporal === false) {
        throw new RuntimeException("Non se puido preparar o gardado.");
    }
    try {
        // Escribir completamente antes de substituír o ficheiro orixinal.
        if (file_put_contents($temporal, $json) !== strlen($json)) {
            throw new RuntimeException("Non se puido escribir a entrega completa.");
        }
        if (file_exists($ficheiro)) {
            @chmod($temporal, fileperms($ficheiro) & 0777);
        } else {
            @chmod($temporal, 0600);
        }
        if (!rename($temporal, $ficheiro)) {
            throw new RuntimeException("Non se puido actualizar respostas.json.");
        }
    } finally {
        if (file_exists($temporal)) @unlink($temporal);
    }
} catch (Throwable $erro) {
    flock($bloqueo, LOCK_UN);
    fclose($bloqueo);
    error_log("PercepMap: " . $erro->getMessage());
    responder(false, "Non foi posible gardar a entrega. As respostas anteriores mantéñense.", 500);
}
flock($bloqueo, LOCK_UN);
fclose($bloqueo);
responder(true, "A entrega gardouse correctamente.");
