# Seguridade de PercepMap

Esta versión é un **prototipo de investigación**. **NON está auditada nin aprobada para uso público con datos reais.**

## Problemas pendentes antes do despregamento

- Revisión independente de seguridade, privacidade e protección de datos.
- Control de acceso, autenticación e autorización para a exportación das respostas (non se inclúe ningún endpoint público de descarga).
- Protección contra abuso (límite de peticións, control de tamaño e recursos, rexistro de incidencias).
- Validación máis estrita do contido e complexidade das xeometrías e das respostas.
- Revisión do uso de `localStorage` no navegador compartido e da información/consentimento facilitados aos participantes.
- Substitución das dependencias CDN por copias locais verificadas e coa súa licenza.
- Adaptación e probas das rutas para sub-URI; empaquetado Docker e configuración institucional.
- Política de conservación, acceso, copias de seguridade e eliminación de datos.

## Gardado

`gardar.php` require `PERCEPMAP_DATA_DIR`, un directorio existente, escribible polo usuario PHP e **situado fóra do directorio servido por HTTP**. Non inclúe descarga pública dos resultados. Non expoñer ese directorio mediante alias ou rutas do servidor.

Para comunicar vulnerabilidades, contactar coa persoa responsable do proxecto sen incluír datos reais de participantes nunha incidencia pública.
