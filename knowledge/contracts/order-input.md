---
type: 'Task Contract'
title: 'Normalizar partidas de un pedido'
description: 'Contrato de producto para TASK-001, con oraculo independiente e integracion real de dependencias.'
tags: ['product', 'orders', 'dependencies']

task: order-input
intent: 'Validar y normalizar partidas segun el modelo del cotizador.'
target: src/order_input.py
language: python
signature: 'def normalize_items(value: object) -> tuple:'
test_command: 'python -m unittest tests/test_order_input.py'
budget:
  cyclomatic_max: 12
  nesting_max: 4
  lines_max: 150
  params_max: 3
tests: 'tests/test_order_input.py'
tests_sha256: 'ab67e076e2f9d215f32fa59d3f3dceac09939cd259c7b79f7f7d4ba591bede9f'
touch_only: ['src/order_input.py']
deps_allowed: ['stdlib', 'src']
forbids: ['network', 'subprocess', 'llm']
---

## Intent
Aplicar las reglas del [cotizador](../order-quote-demo.md) dentro del grafo
aprobado, usando el [diario Git](../git-tasks.md) para el seguimiento.

## Interface
`def normalize_items(value: object) -> tuple:`. Entrada, errores y salida segun el nodo de producto enlazado.

## Invariants
- Cumplir el modelo de datos y la semantica del nodo de producto.
- Conservar el contrato, oraculo y helper del baseline aprobado.
- Cambiar solo src/order_input.py; el coordinador registra estados y evidencia.
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
15 pruebas: 13 funcionales y 2 mutantes conocidos. El helper tests/order_oracle_support.py esta protegido
por quality/product.json. El stub debe fallar antes de implementar.
La decodificacion UTF-8 explicita pertenece al oraculo y a la interfaz de consola.

## Constraints
Stdlib y modulos propios; produccion sin red, subprocesos ni LLM.
PARAR y reportar si no existe una referencia aprobada o si se requiere
modificar archivos fuera de touch_only. La aprobacion se rige por
[quality-approval](../quality-approval.md).
