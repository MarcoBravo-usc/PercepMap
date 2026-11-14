# PercepMap

**Ferramenta dixital para a investigación en dialectoloxía perceptiva**

PercepMap é unha aplicación web deseñada para estudar como as persoas perciben as variedades xeolectais. Combina un cuestionario sociolingüístico con tarefas de delimitación de áreas sobre mapas interactivos de España, América e Galicia. As respostas poden exportarse e analizarse para elaborar mapas individuais e representacións agregadas das áreas sinaladas.

O proxecto desenvolveuse no contexto dunha investigación doutoral na Universidade de Santiago de Compostela.

En consonancia cos principios da ciencia aberta, PercepMap publícase como software libre co obxectivo de promover a transparencia e a reproducibilidade. A publicación do código fonte tamén permite documentar os procedementos técnicos empregados na tese, así como facilitar a súa adaptación e mellora por parte da comunidade investigadora.

> **Estado do proxecto:** versión experimental. O código non está preparado para recoller datos persoais reais nun servidor público sen unha revisión adicional de seguridade e unha configuración adecuada. Véxanse [SECURITY.md](SECURITY.md) e [DEPLOYMENT.md](DEPLOYMENT.md).

## Que permite facer?

- Recoller información sociolingüística e respostas abertas sobre a identificación con variedades do español e do galego.
- Debuxar polígonos sobre mapas interactivos de España, América e Galicia para delimitar áreas lingüísticas percibidas.
- Asociar denominacións e descricións ás áreas debuxadas.
- Gardar as respostas estruturadas en JSON mediante un compoñente de servidor en PHP.
- Transformar os resultados a CSV e producir representacións cartográficas individuais e agregadas mediante scripts de Python.

## Como funciona?

1. **Cuestionario:** o informante introduce datos persoais e sociolingüísticos.
2. **Mapas:** delimita as áreas que identifica en cada mapa e engade as denominacións e trazos que considera característicos.
3. **Rexistro:** o cuestionario organiza a información nun formato estruturado para a súa análise.
4. **Análise:** os scripts incluídos permiten exportar datos e representar espacialmente as delimitacións realizadas.

As delimitacións gárdanse como xeometrías de tipo GeoJSON Feature. As coordenadas corresponden ao sistema interno dos mapas SVG e non son coordenadas xeográficas reais; a súa utilización sobre cartografía xeorreferenciada require unha transformación específica.

Os mapas agregados representan a superposición das áreas delimitadas, non necesariamente o acordo entre participantes sobre os nomes das variedades.

## Tecnoloxías

| Compoñente | Tecnoloxías |
| --- | --- |
| Interface e cuestionario | HTML, CSS, JavaScript |
| Mapas interactivos | Leaflet e Leaflet.draw |
| Recepción e almacenamento | PHP e JSON |
| Tratamento e visualización de resultados | Python |
| Cartografía de base | Mapas SVG elaborados en Inkscape |

## Estrutura do repositorio

```text
PercepMap/
├── index.html                 # Páxina inicial
├── datos_persoais.html       # Cuestionario sociolingüístico
├── españa_leaflet.html       # Mapa de España
├── américa_leaflet.html      # Mapa de América
├── galicia_leaflet.html      # Mapa de Galicia
├── gravación.html            # Actividade de gravación
├── fin.html                  # Pantalla final
├── gardar.php                 # Recepción de respostas
├── img/                       # Mapas SVG
├── Provincias/                # Datos auxiliares
├── analizar_mapas.py         # Análise e representación cartográfica
├── json_a_csv.py             # Exportación a CSV
├── SECURITY.md               # Información de seguridade
├── DEPLOYMENT.md             # Notas de despregamento
└── LICENSE                   # Licenza MIT
```

## Instalación e uso

O código pode examinarse e modificarse localmente. Abrir os ficheiros HTML non equivale a dispoñer dunha instalación funcional para recoller respostas: o gardado require un servidor con PHP e un directorio privado configurado mediante a variable de ambiente `PERCEPMAP_DATA_DIR`, fóra do directorio accesible desde a web.

As páxinas cartográficas utilizan actualmente bibliotecas cargadas desde CDN. A súa instalación local, a adaptación a subdirectorios e a preparación dun despregamento con Docker seguen pendentes. Consulta [DEPLOYMENT.md](DEPLOYMENT.md) antes de intentar unha instalación.

Para a análise cartográfica, o script `analizar_mapas.py` emprega NumPy, Pillow e CairoSVG. Exemplo de execución, unha vez instaladas esas dependencias:

```bash
python analizar_mapas.py /ruta/privada/respostas.json
```

O script `json_a_csv.py` está preparado para ler un ficheiro `respostas.json` situado xunto ao propio script; consulta o código antes de utilizalo con datos reais e mantén estes datos fóra do repositorio público.

## Privacidade e seguridade

Antes de utilizar PercepMap nun estudo real cómpre verificar as medidas de protección de datos, os permisos de acceso, a seguridade do servidor e as autorizacións que correspondan.

O código compártese para revisión, non como unha solución auditada ou lista para produción.

## Autoría e desenvolvemento

**Marco Bravo Rodríguez** · Investigador predoutoral na Universidade de Santiago de Compostela.

PercepMap foi desenvolvido con asistencia de IA (modelo GPT-6) na elaboración e revisión do código.

## Contexto académico e financiamento

A investigación na que se encadra PercepMap está vinculada ao proxecto **CESGAL — Actualidad e historia reciente del contacto español-gallego: en la senda de ESLORA** (PID2025-173739NB-I00).

## Licenza e recursos de terceiros

O código orixinal e os mapas SVG incluídos publícanse baixo a [licenza MIT](LICENSE), na medida en que corresponden os dereitos necesarios para autorizar a súa distribución. As bibliotecas externas manteñen as súas propias licenzas; consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

**A marca e o logotipo da USC non están cubertos pola licenza MIT** nin se inclúen nesta distribución.

## Cita

Se utilizas ou adaptas PercepMap nun traballo académico, agradécese que cites o repositorio, indicando o autor, a versión empregada e a ligazón pública. Unha vez publicada unha versión estable ou arquivada cun DOI, engadirase aquí unha referencia bibliográfica completa.

## Contacto

**Marco Bravo Rodríguez**

*Investigador predoutoral*

Universidade de Santiago de Compostela (USC)

**Correo electrónico**: marco.bravo@rai.usc.es

