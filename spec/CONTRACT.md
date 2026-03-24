# CONTRATO LUM-I/O vΩ.2025-12

**Propósito:** Definir el formato mínimo obligatorio para ejecutar LUM de forma reproducible, antifraude y auditable.

**Regla madre:** Si un bundle no cumple este contrato → dictamen `INVALID` (no se publica semáforo).

**Referencia de esquema:** [`lum_contract_schema.json`](./lum_contract_schema.json)
**Ejemplos:** [`examples/valid.json`](./examples/valid.json) · [`examples/invalid.json`](./examples/invalid.json)

---

## Definiciones

| Término | Definición |
|---|---|
| **Campo** | Lo que se evalúa (subdisciplina, tecnología, práctica), definido por operaciones + evidencias. |
| **Ventana (Δ)** | Período de tiempo dentro del cual el campo debe producir al menos un evento de cierre. |
| **Evento de cierre** | Descripción operacional de "qué cuenta como cierre" — observable, medible, re-ejecutable. |
| **Incompatibilidad** | Regla operacional para decidir "A y B no pueden ser ambas compatibles". |
| **Estado LUM** | `GREEN` \| `AMBER` \| `RED` \| `BLACK` |

**Estados:**

- `GREEN` — cierre operativo
- `AMBER` — señal parcial / proto-espectro
- `RED` — no-cierre (inteligibilidad insuficiente)
- `BLACK` — sobrecierre (cierre patológico, circular o con fuga); prohíbe acción

---

## §1 — Objeto del contrato

Este contrato estandariza:

1. **INPUT** — qué se debe declarar obligatoriamente
2. **CONFIG** — qué parámetros quedan congelados
3. **MODEL** — qué motor se usa y con qué restricciones
4. **OUTPUT** — qué reporte es obligatorio
5. **AUDIT** — cómo se reconstruye el dictamen y se evita fraude

Una ejecución LUM válida es la tupla:

$$\mathcal{L} = \langle \text{INPUT},\ \text{CONFIG},\ \text{MODEL},\ \text{OUTPUT},\ \text{AUDIT} \rangle$$

Si falta algún componente o hay inconsistencia → `validity.status = INVALID`.

LUM no declara verdad, moralidad ni política. Declara **cierre operativo auditable**.

---

## §2 — Definición formal de una ejecución válida

Una ejecución LUM válida es la tupla completa `⟨INPUT, CONFIG, MODEL, OUTPUT, AUDIT⟩`.

Si cualquiera de los cinco componentes falta o es internamente inconsistente → `validity.status = INVALID`.

---

## §3 — INPUT (entrada obligatoria)

### 3.1 Campos mínimos requeridos

**A) `domain`**
- `description` (string): qué es el campo en una frase.
- `scope` (string): límites exactos — qué incluye y qué excluye.

**B) `time_reference`**
- `t` (datetime, ISO 8601): instante "ahora" del dictamen.
- `units` (`days` | `months` | `years`): unidad oficial del análisis.

**C) `window`**
- `Δ` (number > 0): tamaño de ventana.
- `units`: debe coincidir con `time_reference.units`.

**D) `evidence_set`** (enumerable y hasheable)
- `datasets` — lista de hashes SHA-256 o URIs
- `documents` — lista de hashes SHA-256 o URIs
- `protocols` — lista de URIs o IDs

**E) `definitions`** (preregistradas)
- `event_of_closure` (string): definición operacional del evento de cierre.
- `incompatibility` (string): definición operacional de incompatibilidad.

### 3.2 Reglas duras de entrada

- `Δ` no puede cambiarse sin nueva versión (ver §11).
- `event_of_closure` debe ser operacional: observable, medible y re-ejecutable.
- `incompatibility` debe estar preregistrada por dominio.
- `evidence_set` debe ser completo, enumerable y hasheable.

---

## §4 — CONFIG (congelable y versionada)

### 4.1 `thresholds` (semáforo)
- `τ_V` ∈ (0, 1): umbral GREEN. **Restricción: `τ_V > τ_R`** (post-check #1).
- `τ_R` ∈ (0, 1): umbral RED.

### 4.2 `minimums` (guardarraíles AND_min)
- `θ_IPU` ∈ [0, 1]
- `θ_A` ∈ [0, 1]
- `θ_Conf` ∈ [0, 1]

### 4.3 `normalization`
- `clipping.ε_low` y `clipping.ε_high` ∈ (0, 1). **Restricción: `ε_low < ε_high`** (post-check #2).
- `z_scales_id` (string): ID de escalas z congeladas y accesibles para auditoría.

### 4.4 `overclosure_thresholds` (para BLACK)
- `θ_H` — umbral de entropía de protocolos (monocriterio)
- `θ_S` — umbral de comparaciones suprimidas
- `θ_L` — umbral de leakage_score
- `θ_C` — umbral de circularidad (validation_dependency)

### 4.5 `CI_policy` (intervalos de confianza)
- `level` ∈ [0.5, 0.9999] (típico: 0.95)
- `method`: `block_bootstrap` | `bootstrap_bca`
- `B` (int ≥ 2000): iteraciones bootstrap
- `block_size` (int ≥ 1): requerido si `method = block_bootstrap`
- `seed` (int)

### 4.6 `hashing_policy` (antifraude)
- `hash_algo`: SIEMPRE `"SHA-256"`
- `canonicalization` (string): regla de canonización declarada (ver §9.2)

### 4.7 Reglas de versionado

Cualquier cambio en `thresholds`, `minimums`, `normalization`, `overclosure_thresholds`, `CI_policy` o `hashing_policy` → **nueva versión MAJOR**.

---

## §5 — MODEL (motor obligatorio)

### 5.1 Especificación mínima

- `type`: SIEMPRE `"hazard_cloglog"`
- `offset`: SIEMPRE `"log(Δ)"`
- `predictors` (obligatorios, en z): `IPU_z`, `CPV_z`, `A_norm_z`, `Cons_z`
- `coefficients`: `α`, `β`, `γ`, `β_κ`, `β_0`

### 5.2 Restricciones normativas

- `β_κ ≥ 0` — más consistencia no puede reducir la probabilidad de cierre.
- Si `Conf < θ_Conf` → bloqueo automático de GREEN (degrada a AMBER como mínimo).
- Recalibración en flujo → nueva versión MAJOR y declaración obligatoria en `calibration`.

### 5.3 `calibration` (obligatoria si se reporta `p_close_calibrated`)

- `method`: `platt` | `isotonic`
- `calibration_dataset_hash` (SHA-256)
- `split_rule` (string): cómo se separó el set de calibración
- `timestamp` (datetime ISO 8601)
- `metrics`: `ECE` (≤ 0.05 recomendado) y `Brier`

---

## §6 — OUTPUT (salida obligatoria)

La salida es un único objeto `LUM_REPORT`.

### 6.1 Encabezado
- `domain` (copia de `INPUT.domain`)
- `t` (copia de `INPUT.time_reference.t`)
- `Δ` (copia de `INPUT.window`)

### 6.2 Índices (todos con CI)
- `IPU.value` ∈ [0, 1] + CI
- `CPV.value` (real) + CI
- `A_norm.value` ∈ [0, 1] + CI
- `κ_conf.value` ∈ [0, 1] + CI
- `Conf.value` ∈ [0, 1] + CI (si aplica)

**Derivado obligatorio:**
- `derived.Cons = 1 − κ_conf.value` (post-check #3, tolerancia numérica permitida)

### 6.3 Probabilidades (con CI)
- `probability.p_close` ∈ [0, 1] + CI
- `probability.p_close_calibrated` ∈ [0, 1] + CI _(si se aplica calibración)_

### 6.4 Estado (semáforo)
- `state.LUM_STATE`: `GREEN` | `AMBER` | `RED` | `BLACK`
- `state.justification` (string): condición que disparó el estado — corta y verificable.

### 6.5 Diagnósticos
- `diagnostics.shadow_Sh` ∈ [0, 1]
- `diagnostics.entropy_Hs` ∈ [0, 1]
- `diagnostics.SNR` ≥ 0
- `diagnostics.interference_I` ≥ 0

### 6.6 PSNC (si aplica)
- `PSNC.required` (boolean)
- `PSNC.actions` (lista de strings accionables; al menos 1 si `required = true`)

### 6.7 Validez
- `validity.status`: `VALID` | `INVALID`
- `validity.reason_if_invalid` (string): obligatorio si `status = INVALID`

---

## §7 — Reglas de estado (decisión)

Usa `p_close_calibrated` si existe; si no, usa `p_close`.

| Estado | Condición |
|---|---|
| **GREEN** | p̃ ≥ τ_V **Y** AND_min: IPU ≥ θ_IPU, A_norm ≥ θ_A, Conf ≥ θ_Conf |
| **RED** | p̃ < τ_R |
| **AMBER** | Cualquier otro caso (incluye "verde provisional" bloqueado por AND_min) |
| **BLACK** | Se detecta sobrecierre (ver §8) — no invalida, pero **prohíbe acción** |

---

## §8 — BLACK (sobrecierre) — condiciones computables

BLACK se activa si cualquiera de las siguientes condiciones se cumple:

**1. Monocriterio** — `entropy_protocols < θ_H`
Donde `entropy_protocols` = entropía de Shannon de la distribución de protocolos usados (normalizada 0..1).

**2. Supresión** — `missing_comparisons_ratio > θ_S`
Donde `missing_comparisons_ratio = missing_expected / expected_total`.

**3. Leakage** — `leakage_score > θ_L`
Calculado con test temporal mínimo: entrenar/validar respetando orden temporal, repetir con permutación que rompe causalidad; si la performance no cae como debería, hay fuga.

**4. Circularidad** — `validation_dependency > θ_C`
Donde `validation_dependency` = proporción de validaciones que dependen del mismo dataset/pipeline sin independencia real.

**Efecto de BLACK:**
- `state.LUM_STATE = "BLACK"`
- `PSNC.required = true`
- `PSNC.actions` incluye: "romper circularidad / añadir contrastes independientes / auditar leakage"

---

## §9 — AUDIT (trazabilidad obligatoria)

### 9.1 Huella criptográfica (`footprint`)

`footprint.hash = SHA-256(…)` sobre la concatenación canonizada de:

- `version`, `t`, `Δ`, `thresholds`, `minimums`, `normalization`, `overclosure_thresholds`, `CI_policy`
- hashes de `evidence_set`, `model_coefficients`, `z_scales_id`
- `calibration` (si existe)

Si no se puede reconstruir exactamente lo hasheado → `INVALID`.

### 9.2 Canonización

Todo objeto se canoniza así:
- Codificación: UTF-8
- Claves ordenadas alfabéticamente
- Sin espacios ni saltos de línea irrelevantes
- Números en formato fijo (máximo 10 decimales)
- Timestamps en ISO 8601 normalizado (UTC con `Z`)

### 9.3 Publicación mínima requerida

Sin estos campos, `validity = INVALID`:

| Campo | Descripción |
|---|---|
| `has_footprint` | `true` |
| `has_full_config` | `true` |
| `has_ci_policy` | `true` |
| `has_uncertainty` | `true` |
| `has_evidence` | `true` |
| `has_calibration_metrics` | `true` _(si hay `p_close_calibrated`)_ |

---

## §10 — Criterios de invalidación

Un dictamen es `INVALID` si:

- `Δ` cambió sin versionar
- `definitions` no preregistradas
- `evidence_set` incompleto o no hasheable
- Calibración aplicada pero no declarada en `MODEL.calibration`
- Falta `footprint`
- Falta `CI_policy` o CI no reportado donde es obligatorio
- No se puede canonizar/reconstruir lo hasheado

`INVALID` → **no se publica semáforo**.

---

## §11 — Versionado

| Cambio | Tipo de versión |
|---|---|
| Cambio de `Δ` | MAJOR |
| Cambio de `thresholds`, `minimums`, `normalization`, `overclosure_thresholds`, `CI_policy`, `hashing_policy` | MAJOR |
| Recalibración | MAJOR |
| Cambios solo de redacción o documentación | MINOR |

---

## §12 — Cláusula IA (compatibilidad)

Cualquier modelo de IA que ejecute LUM **debe**:

- Rechazar ejecuciones inválidas antes de emitir dictamen.
- Respetar AND_min y reglas BLACK sin excepción.
- Producir salida exactamente en formato `OUTPUT`.
- **No inferir** verdad, moralidad ni política como parte del dictamen.

---

## §13 — Cierre del contrato

Este contrato define la frontera operativa de LUM. Fuera de él hay interpretación, comentario o filosofía — pero no dictamen metrológico.

---

## Post-checks (reglas anti-trampa)

Estas reglas se ejecutan **después** de validar con JSON Schema. JSON Schema estándar no puede imponer relaciones matemáticas entre campos sin extensiones.

| # | Regla | Fallo |
|---|---|---|
| 1 | `CONFIG.thresholds.τ_V > CONFIG.thresholds.τ_R` | Config inválida → INVALID |
| 2 | `CONFIG.normalization.clipping.ε_low < ε_high` | Config inválida → INVALID |
| 3 | `OUTPUT.derived.Cons ≈ 1 − OUTPUT.indices.κ_conf.value` | Consistencia rota → INVALID |
| 4 | Si `LUM_STATE = GREEN` → AND_min pasa: IPU ≥ θ_IPU, A_norm ≥ θ_A, Conf ≥ θ_Conf | Estado falso → INVALID |
| 5 | Si `p_close_calibrated` existe → `MODEL.calibration` existe _(el schema ya lo fuerza)_ | — |
| 6 | `CI.low ≤ CI.high` para todos los CIs | CI invertido → INVALID |

---

*LUM-I/O vΩ.2025-12 — © Julio David Rojas Aguayo (jules_pintor@outlook.com) — MIT License*
*ORCID: [0009-0001-0800-5303](https://orcid.org/0009-0001-0800-5303) · DOI: [10.5281/zenodo.19142481](https://doi.org/10.5281/zenodo.19142481)*
