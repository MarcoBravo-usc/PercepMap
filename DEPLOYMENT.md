# Notas de despregamento (para persoal técnico)

**Non publicar a aplicación con datos reais sen auditoría e autorización institucional.**

1. Servir a aplicación con PHP nunha versión actualmente soportada e con parches.
2. Crear un directorio de datos fóra do *document root* (por exemplo, `/var/lib/percepmap` se `/var/www/html` é a raíz pública), propiedade do usuario do proceso PHP, con permisos restrinxidos.
3. Configurar `PERCEPMAP_DATA_DIR` no ambiente do proceso PHP/FPM. Non incluír a ruta privada nun repositorio de produción se revela información sensible.
4. Desactivar listados de directorios, habilitar HTTPS, restrinxir métodos e cabeceiras, e aplicar límites de peticións.
5. Non habilitar unha ruta de descarga pública de respostas. O acceso aos datos debe estar autenticado e autorizado, preferiblemente por canles administrativas independentes da web pública.
6. Revisar CDN, recursos externos, funcionamento baixo sub-URI e configuración Docker co equipo administrador.
7. Verificar backups, retención, borrado, acceso e cumprimento do protocolo ético.

## Dependencias de terceiros

As páxinas actuais cargan Leaflet 1.9.4 e Leaflet.draw 1.0.4 desde un CDN; é un **pendente de adaptación** para o despregamento USC. A súa descarga, inclusión local e avisos de licenza deben facerse verificando os artefactos oficiais. Non se incluíron copias non verificadas.
