# Generador de Configuración Trident NAS

Script optimizado para generar archivos YAML de configuración de Trident NAS para OpenShift.

## 📋 Archivos de Configuración

Tienes **2 opciones** según tu nivel de experiencia:

### 🟢 **config.simple.yaml** - RECOMENDADO para la mayoría
- Solo 4 campos obligatorios
- A prueba de errores
- Usa valores por defecto seguros
- Ideal para usuarios nuevos

### 🟡 **config.advanced.yaml** - Para usuarios avanzados
- Control completo de todos los parámetros
- Personalización de defaults de volúmenes
- Configuración de debug flags
- Políticas de exportación y QoS

## 🚀 Uso Rápido

### 1. Crea tu archivo de configuración

**Opción Simple (recomendada):**
```bash
cp config.simple.yaml config.yaml
# Edita solo estos 4 valores:
#   - managementLIF
#   - dataLIF
#   - svm
#   - storageClass.name
```

**Opción Avanzada:**
```bash
cp config.advanced.yaml config.yaml
# Personaliza todos los parámetros según necesites
```

### 2. Ejecuta el generador

```bash
python generate_trident_nas_optimized.py
```

### 3. Archivos generados

- **backend_storage.yaml**: TridentBackendConfig + StorageClass
- **secret.yaml**: Credenciales de NetApp

## 📝 Ejemplo Mínimo

```yaml
backend:
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVMv2-cert-rhosoJC-nas1200

storageClass:
  name: rhoso-nas
```

¡Eso es todo! El resto se configura automáticamente con valores seguros.

## 🔧 Valores por Defecto

Cuando uses **config.simple.yaml**, estos son los defaults aplicados:

### Backend
- **backendName**: Se genera automáticamente como `ontap-nas_<dataLIF>`
- **storagePrefix**: `trident`
- **autoExportPolicy**: `false`
- **qtreesPerFlexvol**: `200`

### Defaults de Volúmenes
- **unixPermissions**: `755`
- **spaceReserve**: `none`
- **snapshotPolicy**: `none`
- **encryption**: `false`

### StorageClass
- **isDefault**: `true`
- **backendType**: `ontap-nas`
- **media**: `ssd`
- **provisioningType**: `thin`

## ❓ Preguntas Frecuentes

**¿Puedo cambiar los defaults?**  
Sí, usa `config.advanced.yaml` que incluye todas las opciones.

**¿Qué pasa si borro una línea en config.simple.yaml?**  
El script validará que los 3 campos obligatorios (managementLIF, dataLIF, svm) estén presentes.

**¿Cómo cambio las credenciales?**  
Edita `secret.yaml` después de generarlo, o usa `config.advanced.yaml`.

## 📚 Más Información

Para entender cada parámetro en detalle, consulta:
- Documentación de NetApp Trident
- `config.advanced.yaml` (incluye comentarios detallados)
