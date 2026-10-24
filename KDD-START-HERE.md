# Primeros pasos con KDD

Este proyecto (Cotizador con dependencias) fue inicializado con el perfil `standard`.

## Qué hacer ahora

1. Lee `knowledge/index.md` para conocer las reglas del proyecto.
2. Crea un test que describa el resultado esperado.
3. Crea un contrato en `knowledge/contracts/` y sella su test.
4. Si usas `standard` o `strict`, pide a una persona que apruebe el commit
   con contrato y test y te entregue su SHA completo.
5. Ejecuta el perfil elegido:

```text
python scripts/run_profile.py --profile standard --approved-ref <SHA_APROBADO>
```

## Calidad del producto en CI

El CI exige `quality/product.json` y una referencia revisada, tambien con
el perfil local minimal. Define contratos, oraculos y checks funcionales,
adversariales y de interfaz propios antes de implementar. Protege el
workflow generado, el runner y las dependencias de esas pruebas.

La persona revisora aprueba el commit que contiene esa politica y registra
su SHA completo en las variables de Actions `KDD_APPROVED_BASELINE_REF` y
`KDD_QUALITY_APPROVED_REF` del repositorio nuevo. El CI verifica el checkout
actual con el runner de ese commit y ejecuta los checks dos veces.
Si falta configuracion, el CI falla antes de los oraculos.

Consulta `knowledge/bootstrap-product-quality-ci.md` para preparar la
politica, el inventario protegido y las referencias de aprobacion.

Para una tarea concreta, valida también su budget:

```text
python scripts/validate_budgets.py knowledge/contracts --repo-root . --contract <task>
```

KDD comprueba las reglas declaradas; una persona sigue revisando si esas reglas
representan la necesidad real del producto. Consulta `docs/KDD-PARA-PERSONAS.md`
si quieres una explicación sin tecnicismos.
