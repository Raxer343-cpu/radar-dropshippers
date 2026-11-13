# Radar de dropshippers · Tu Manito / Raíz Lab

Sigue lo que hace la competencia con **información pública**, para saber qué sí vende y qué no antes de gastar.

## Las 3 capas

| Capa | Qué mira | Quién lo corre | Cada cuánto |
|---|---|---|---|
| 1. Anuncios | Biblioteca de anuncios de Meta: quién pauta, desde cuándo, cuántas copias, a qué tienda lleva | Claude en Chrome con `radar/extractor_biblioteca_meta.js` | Cada lunes |
| 2. Tiendas | Catálogo público de tiendas Shopify (`/products.json`): productos nuevos, retirados, cambios de precio, agotados | GitHub Actions (este repo), solo | Todos los días, 6 a. m. |
| 3. Ciclo | Cruza 1 y 2 con nuestros pedidos por anuncio | Claude en el cierre semanal | Cada semana |

## Cómo se lee (qué es "sí" y qué es "no")

| Señal | Lectura |
|---|---|
| Anuncio activo ≥ 30 días y ≥ 3 copias | **Sí:** alguien lo paga hace un mes, está vendiendo |
| Anuncio que desaparece antes de 7 días | **No:** prueba que murió |
| Producto nuevo en la tienda + anuncio nuevo la misma semana | Lo están probando: vigilar 2–3 semanas |
| Producto retirado del catálogo | **No:** murió |
| Precio que sube y el producto sigue | Aguanta margen |
| Agotado y reactivado varias veces | Vende (o el proveedor falla) |
| El mismo producto en 4+ tiendas | Validado, pero competido: entrar solo con mejor oferta |

## Reglas nuestras

- Solo información pública de tiendas y anuncios. Nada de datos de personas ni de clientes ajenos.
- Se copia la **idea** (producto, ángulo, precio), nunca creativos, fotos, textos ni marcas ajenas.
- Nada de productos con promesas médicas, aunque vendan.

## Archivos

- `radar/tiendas.csv`: lista de tiendas a vigilar (agregar una fila por tienda; `activa=no` para pausar).
- `data/resumen.md`: foto del último día. `data/cambios.csv`: historial de cambios. `data/snapshots/`: catálogo de cada tienda.
