---
type: 'Task Contract'
title: 'Cotizar pedidos mediante una CLI'
description: 'Contrato de producto para TASK-004, con oraculo independiente e integracion real de dependencias.'
tags: ['product', 'orders', 'dependencies']

task: order-quote-cli
intent: 'Exponer la cotizacion compuesta mediante una CLI JSON UTF-8.'
target: src/quote_cli.py
language: python
signature: 'def quote(items: object) -> dict:'
test_command: 'python -m unittest tests/test_order_quote_cli.py'
budget:
  cyclomatic_max: 12
  nesting_max: 4
  lines_max: 150
  params_max: 3
tests: 'tests/test_order_quote_cli.py'
tests_sha256: '0cd2168f9cbe4a01c718ea2246739f550deea72566a53f44136bfcaa5034332e'
touch_only: ['src/quote_cli.py']
deps_allowed: ['stdlib', 'src']
forbids: ['network', 'subprocess', 'llm']
---

## Intent
Aplicar las reglas del [cotizador](../order-quote-demo.md) dentro del grafo
aprobado, usando el [diario Git](../git-tasks.md) para el seguimiento.

## Interface
`def quote(items: object) -> dict:`. Ademas python -m src.quote_cli y main(argv=None) -> int.

## Invariants
- Cumplir el modelo de datos y la semantica del nodo de producto.
- Conservar el contrato, oraculo y helper del baseline aprobado.
- Cambiar solo src/quote_cli.py; el coordinador registra estados y evidencia.
- Las dependencias se usan realmente: no sustituirlas por mocks ni copiar su logica.
- Las pruebas de mutacion requieren un control verde y fallos de asercion;
  errores de entorno o ejecucion quedan inconclusos y bloquean el oraculo.

## Examples
- Partidas A-1: 2 unidades a 125 y B: 1 unidad a 300 producen subtotal 550,
  envio 400 y total 950; cada componente devuelve su resultado definido.
- Una cantidad booleana es invalida; seis unidades tienen envio gratis.

## Do / Don't
- DO ejecutar procesos y usar importaciones reales de las dependencias.
- DON'T editar los oraculos aprobados ni registrar PASS sin ejecutarlos.

## Tests
20 pruebas: 5 de integracion funcional, 2 mutantes conocidos y 13 de consola por procesos reales. El helper tests/order_oracle_support.py esta protegido
por quality/product.json. El stub debe fallar antes de implementar.
La decodificacion UTF-8 explicita pertenece al oraculo y a la interfaz de consola.

## Constraints
Stdlib y modulos propios; produccion sin red, subprocesos ni LLM.
PARAR y reportar si no existe una referencia aprobada o si se requiere
modificar archivos fuera de touch_only. La aprobacion se rige por
[quality-approval](../quality-approval.md).
