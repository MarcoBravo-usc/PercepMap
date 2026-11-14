
// ================================
// PercepMap
// América
// ================================


// ================================
// MAPA
// ================================

const map = L.map("map", {
    crs: L.CRS.Simple,
    minZoom: -2,
    maxZoom: 3
});

const bounds = [
    [0, 0],
    [1000, 800]
];

L.imageOverlay(
    "img/america.svg",
    bounds
).addTo(map);

map.fitBounds(bounds);
map.setZoom(0);


// ================================
// DATOS
// ================================

let variedades = JSON.parse(
    localStorage.getItem("america") || "[]"
);


// ================================
// CAPA EDITABLE
// ================================

const editableLayers = new L.FeatureGroup();

map.addLayer(editableLayers);


// ================================
// GARDAR DATOS
// ================================

function gardarDatos() {

    localStorage.setItem(
        "america",
        JSON.stringify(variedades)
    );

}


// ================================
// RECUPERAR POLÍGONOS
// ================================

variedades.forEach(function(v) {

    if (!v.xeometria) return;

    const layer = L.geoJSON(v.xeometria);

    layer.eachLayer(function(poligono) {

        poligono.variedadeId = v.id;

        editableLayers.addLayer(poligono);

    });

});


// ================================
// CONTROIS DE DEBUXO
// ================================

const drawControl = new L.Control.Draw({

    draw: {
        polyline: false,
        polygon: true,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false
    },

    edit: {
        featureGroup: editableLayers,
        edit: true,
        remove: true
    }

});

map.addControl(drawControl);


// ================================
// VARIABLES TEMPORAIS
// ================================

let ultimaXeometria = null;
let ultimaLayer = null;


// ================================
// CREAR POLÍGONO
// ================================

map.on(
    L.Draw.Event.CREATED,
    function(e) {

        const layer = e.layer;

        editableLayers.addLayer(layer);

        ultimaLayer = layer;

        ultimaXeometria = layer.toGeoJSON();

        drawControl._toolbars.draw.disable();

        document
            .getElementById("modal")
            .classList
            .remove("oculto");

    }
);


// ================================
// EDITAR POLÍGONOS
// ================================

map.on(
    L.Draw.Event.EDITED,
    function(e) {

        e.layers.eachLayer(function(layer) {

            if (!layer.variedadeId) return;

            const variedade = variedades.find(
                v => v.id === layer.variedadeId
            );

            if (variedade) {

                variedade.xeometria = layer.toGeoJSON();

            }

        });

        gardarDatos();

    }
);


// ================================
// ELIMINAR POLÍGONOS
// ================================

map.on(
    L.Draw.Event.DELETED,
    function(e) {

        e.layers.eachLayer(function(layer) {

            if (layer.variedadeId) {

                variedades = variedades.filter(
                    v => v.id !== layer.variedadeId
                );

            }

        });

        gardarDatos();

        actualizarLista();

    }
);


// ================================
// GARDAR VARIEDADE
// ================================

document
    .getElementById("gardar")
    .addEventListener("click", function() {

        const nome = document
            .getElementById("nome")
            .value
            .trim();

        if (!nome) {

            alert(
                "Debes indicar un nome para a variedade."
            );

            return;

        }

        if (!ultimaLayer || !ultimaXeometria) {

            alert(
                "Non hai ningún polígono para gardar."
            );

            return;

        }

        const descricion = document
            .getElementById("descricion")
            .value;

        const id = crypto.randomUUID();

        ultimaLayer.variedadeId = id;

        const variedade = {

            id: id,
            mapa: "america",
            nome: nome,
            descricion: descricion,
            xeometria: ultimaLayer.toGeoJSON()

        };

        variedades.push(variedade);

        gardarDatos();

        actualizarLista();


        // Limpar campos

        document.getElementById("nome").value = "";

        document.getElementById("descricion").value = "";


        // Pechar modal

        document
            .getElementById("modal")
            .classList
            .add("oculto");


        // Limpar variables temporais

        ultimaLayer = null;

        ultimaXeometria = null;

    });


// ================================
// CANCELAR
// ================================

document
    .getElementById("cancelar")
    .addEventListener("click", function() {

        if (ultimaLayer) {

            editableLayers.removeLayer(ultimaLayer);

        }

        ultimaLayer = null;

        ultimaXeometria = null;

        document.getElementById("nome").value = "";

        document.getElementById("descricion").value = "";

        document
            .getElementById("modal")
            .classList
            .add("oculto");

    });


// ================================
// LISTA LATERAL
// ================================

function actualizarLista() {

    const lista = document.getElementById("variedades");

    lista.innerHTML = "";

    variedades.forEach(function(v, i) {

        const div = document.createElement("div");

        div.className = "variedade";

        const titulo = document.createElement("h4");

        titulo.textContent = `${i + 1}. ${v.nome}`;

        const texto = document.createElement("p");

        texto.textContent = v.descricion || "";

        div.appendChild(titulo);

        div.appendChild(texto);

        lista.appendChild(div);

    });

}

actualizarLista();


// ================================
// NAVEGACIÓN
// ================================

document
    .getElementById("atras")
    .addEventListener("click", function() {

        gardarDatos();

        window.location.href = "españa_leaflet.html";

    });


document
    .getElementById("seguinte")
    .addEventListener("click", function() {

        gardarDatos();

        window.location.href = "galicia_leaflet.html";

    });
