---
type: 'Concept'
title: 'Cotizador de pedidos con dependencias'
description: 'Producto minimo y protocolo de demostracion de cuatro tareas con bifurcacion y convergencia de dependencias.'
tags: ['product', 'orders', 'dependencies', 'e2e']
---

# Cotizador de pedidos

El producto recibe partidas JSON y devuelve una cotizacion determinista en
centavos enteros. Su objetivo es probar el flujo de varias tareas de KDD con
dependencias reales; los importes y reglas pertenecen a esta demostracion.

## Datos y reglas del producto

La entrada es una lista de 1 a 100 diccionarios, con exactamente las claves
`sku`, `quantity` y `unit_cents`. Cada SKU es unico, ASCII y cumple
`[A-Z][A-Z0-9-]{0,15}`. quantity es un int de 1 a 100 y unit_cents un int de
0 a 1000000; bool no cuenta como int. Cualquier dato invalido produce ValueError.
La entrada original no se modifica.

- normalize_items devuelve una tupla de tuplas (sku, quantity, unit_cents),
  conservando el orden recibido.
- subtotal normaliza la entrada y suma quantity * unit_cents usando enteros.
- shipping normaliza y suma las cantidades. Con seis o mas unidades vale 0;
  con una a cinco vale 250 + 75 * (unidades - 1) centavos.
- quote compone ambos calculos y devuelve exactamente subtotal_cents,
  shipping_cents y total_cents, siendo total la suma de los anteriores.

La CLI `python -m src.quote_cli` lee un documento JSON UTF-8 de stdin e imprime
una sola linea JSON en stdout, con exit 0. Acepta espacios y saltos externos.
Una entrada invalida, JSON malformado o bytes UTF-8 invalidos devuelve exit 2,
stdout vacio y un mensaje que empieza con `Error:` en stderr, sin traceback.
`--help` imprime ayuda y termina en 0; argumentos desconocidos fallan con 2.
El producto no usa red, subprocesos, persistencia ni moneda en coma flotante.

## Grafo y contratos

| Tarea | Resultado | Dependencias |
| --- | --- | --- |
| TASK-001 | [Normalizar partidas](contracts/order-input.md) | Ninguna |
| TASK-002 | [Subtotal](contracts/order-total.md) | TASK-001 |
| TASK-003 | [Envio](contracts/order-shipping.md) | TASK-001 |
| TASK-004 | [Cotizacion y CLI](contracts/order-quote-cli.md) | TASK-002, TASK-003 |

TASK-002 y TASK-003 forman ramas hermanas del grafo; el trabajo lo realizara
un coordinador local, sin afirmar ejecucion distribuida. Cada tarea tendra
su rama task/TASK-NNN y su evidencia de cierre, segun
[tareas Git](git-tasks.md) y [tablero Git](board-git.md).

## Protocolo de aceptacion de la demostracion

1. Congelar estos contratos, oraculos, helper y politica antes de implementar.
   El stub debe ser rechazado por cada oraculo.
2. Crear las cuatro tareas y sus dependencias desde KDD-Board. Marcar como
   ready con el SHA revisado explicitamente por la persona revisora.
3. Intentar iniciar TASK-002 antes de cerrar TASK-001 y TASK-004 antes de
   cerrar ambas dependencias. Debe rechazarse sin commits, ramas ni cambios
   de estado nuevos. Los IDs/dependencias quedan inmutables al crear.
4. Completar TASK-001 y despues iniciar TASK-002 y TASK-003. Mostrar que ambas
   pueden estar in_progress, aunque solo haya un checkout y un coordinador.
   Probar bloqueo/reanudacion en una de ellas, preservando su rama.
5. Cerrar TASK-002 e intentar otra vez iniciar TASK-004 mientras TASK-003
   siga abierta: el inicio todavia debe fallar. Cerrar TASK-003 y luego TASK-004.
6. Conservar commits de estado, implementacion y merge. Verificar mediante
   Git el padre probado de cada cierre, los hashes y el oraculo real; auditar
   todo el rango con validate_tasks.py.
7. Revisar la referencia final de calidad antes de publicar. El CI debe dar
   PASS de quality/product.json en Ubuntu/Windows, con checks de producto
   dos veces, ademas de las dos suites generales y los jobs del tablero.

Las referencias de contratos y calidad tienen funciones distintas:
[aprobacion de calidad](quality-approval.md). Los archivos de evidencia usan
SHAs futuros; se revisara su commit final para la referencia de calidad,
manteniendo la aprobacion historica de cada tarea. La politica usa rutas
exactas y no concede permisos globales a archivos nuevos.

## Oraculos y limites

Pruebas funcionales de los cuatro componentes, pruebas CLI por procesos reales
y mutaciones de funciones en copias temporales. Cada mutacion exige primero
un control sin modificar en verde; se considera detectada solo por una
asercion pertinente, nunca por errores de importacion, transporte o entorno.
El helper decodifica UTF-8 explicitamente y no reutiliza bytecode.

Los mutantes son un conjunto conocido de regresion; no prueban ausencia
universal de defectos. Las pruebas de consola y la observacion de KDD-Board
en navegador aportan evidencias diferentes.
