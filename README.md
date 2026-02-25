# 🚀 Generador Optimizado de Configuración Trident NAS

Generador Python optimizado para crear archivos YAML de configuración de **NetApp Trident NAS** para OpenShift/Kubernetes.

## ✨ Características

- 🎯 **Ultra simple**: Solo 3 campos obligatorios en `config.yaml`
- 🔧 **Configuración inteligente**: Valores por defecto seguros y optimizados
- 📦 **Código optimizado**: 52% menos código que la versión original (280 vs 590 líneas)
- 🏗️ **Dataclasses**: Estructura moderna con tipado fuerte
- ✅ **Validación automática**: Detecta campos faltantes antes de generar
- 🔄 **Auto-generación**: `backendName` se genera automáticamente
- 📝 **A prueba de errores**: Imposible romper el config con formato simple

---

## 📋 Archivos Generados

| Archivo | Contenido |
|---------|-----------|
| **backend_storage.yaml** | TridentBackendConfig + StorageClass |
| **secret.yaml** | Secret con credenciales de NetApp |

---

## 🚀 Inicio Rápido

### 1️⃣ Instalación

```bash
pip install -r requirements.txt
```

### 2️⃣ Configuración Mínima

Edita `config.yaml` con solo **3 valores obligatorios**:

```yaml
backend:
  managementLIF: 192.168.204.203    # IP de gestión del SVM NetApp
  dataLIF: 192.168.205.203          # IP de datos NFS
  svm: SVMv2-cert-rhosoJC-nas1200   # Nombre del SVM

storageClass:
  name: rhoso-nas                    # Nombre del StorageClass
```

### 3️⃣ Generar YAMLs

```bash
python generate_trident_nas.py
```

**Salida:**
```
📄 Usando configuración: config.yaml
✓ Archivo generado: backend_storage.yaml
✓ Archivo generado: secret.yaml

¡Archivos YAML generados exitosamente!
```

---

## 📖 Configuración Detallada

### Estructura de `config.yaml`

El archivo está dividido en **3 secciones**:

#### 🔹 Backend (Obligatorio)

```yaml
backend:
  # === CAMPOS OBLIGATORIOS ===
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVMv2-cert-rhosoJC-nas1200
  
  # === OPCIONALES (con valores por defecto) ===
  # name: backend-jc-nas1200
  # storagePrefix: trident
  # credentialsName: trident-creds
  # autoExportPolicy: false
  # qtreesPerFlexvol: "200"
  
  # === DEFAULTS DE VOLÚMENES ===
  # defaults:
  #   unixPermissions: "755"
  #   spaceReserve: none
  #   snapshotPolicy: none
  #   encryption: "false"
```

#### 🔹 StorageClass (Obligatorio)

```yaml
storageClass:
  name: rhoso-nas
  
  # === OPCIONALES ===
  # isDefault: true
  # syncWave: "5"
  
  # parameters:
  #   backendType: ontap-nas
  #   media: ssd
  #   provisioningType: thin
  #   snapshots: "true"
```

#### 🔹 Secret (Opcional)

```yaml
# Si no se especifica, usa valores por defecto
# secret:
#   name: trident-creds
#   username: edgevsadmin
#   password: Temporal01
```

---

## ⚙️ Valores por Defecto

### Backend

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `name` | `backend-jc-nas1200` | Nombre del TridentBackendConfig |
| `backendName` | `ontap-nas_<dataLIF>` | 🔄 Auto-generado: `ontap-nas_192_168_205_203` |
| `storagePrefix` | `trident` | Prefijo para nombres de volúmenes |
| `credentialsName` | `trident-creds` | Nombre del secret de credenciales |
| `autoExportPolicy` | `false` | Crear políticas de exportación automáticamente |
| `autoExportCIDRs` | `["0.0.0.0/0", "::/0"]` | CIDRs permitidas |
| `qtreesPerFlexvol` | `"200"` | Qtrees por FlexVol |
| `storageDriverName` | `ontap-nas` | Driver de Trident |
| `nasType` | `nfs` | Tipo de protocolo |
| `useREST` | `true` | Usar API REST de ONTAP |

### Defaults de Volúmenes

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `unixPermissions` | `"755"` | Permisos UNIX (más restrictivo que 777) |
| `spaceReserve` | `none` | Sin reserva de espacio |
| `spaceAllocation` | `"false"` | Thin provisioning habilitado |
| `snapshotPolicy` | `none` | Sin snapshots automáticos |
| `snapshotReserve` | `"0"` | 0% reservado para snapshots |
| `snapshotDir` | `"true"` | Directorio .snapshot visible |
| `exportPolicy` | `default` | Política de exportación por defecto |
| `securityStyle` | `unix` | Estilo de seguridad UNIX |
| `encryption` | `"false"` | Sin encriptación ONTAP NVE |

### StorageClass

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `isDefault` | `true` | Marcar como StorageClass por defecto |
| `syncWave` | `"5"` | Orden de sincronización ArgoCD |
| `backendType` | `ontap-nas` | Tipo de backend Trident |
| `media` | `ssd` | Tipo de medio |
| `provisioningType` | `thin` | Thin provisioning |
| `snapshots` | `"true"` | Soporte de snapshots K8s |
| `reclaimPolicy` | `Delete` | Borrar volumen al eliminar PVC |
| `volumeBindingMode` | `Immediate` | Vinculación inmediata |
| `allowVolumeExpansion` | `true` | Permitir expansión de volúmenes |

---

## 🏗️ Arquitectura del Código

### Clases Principales

```python
@dataclass
class BackendConfig:
    """Configuración del TridentBackendConfig"""
    managementLIF: str
    dataLIF: str
    svm: str
    # ... más campos con defaults

@dataclass
class StorageClassConfig:
    """Configuración del StorageClass"""
    name: str
    isDefault: bool = True
    # ... más campos

@dataclass
class SecretConfig:
    """Configuración del Secret"""
    name: str = 'trident-creds'
    username: str = 'edgevsadmin'
    password: str = 'Temporal01'
```

### Flujo de Ejecución

1. **Cargar** `config.yaml`
2. **Fusionar** con valores por defecto
3. **Validar** campos obligatorios
4. **Generar** estructuras YAML
5. **Comentar** campos vacíos (documentación)
6. **Escribir** archivos

---

## 📦 Despliegue en OpenShift/Kubernetes

### Aplicar Configuración

```bash
# 1. Aplicar secret primero
oc apply -f secret.yaml

# 2. Aplicar backend y storage class
oc apply -f backend_storage.yaml
```

### Verificar Instalación

```bash
# Ver backend
oc get tridentbackendconfig

# Ver storage class
oc get sc

# Ver secret
oc get secret trident-creds
```

### Crear PVC de Prueba

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: rhoso-nas
  resources:
    requests:
      storage: 10Gi
```

---

## 🔍 Ejemplos Avanzados

### Configuración Completa

Ver archivo `config.yaml` para todos los parámetros disponibles comentados.

### Certificados SSL/TLS

```yaml
backend:
  managementLIF: 192.168.1.100
  dataLIF: 192.168.1.100
  svm: my-svm
  clientCertificate: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
  clientPrivateKey: |
    -----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----
```

### Políticas de QoS

```yaml
backend:
  defaults:
    adaptiveQosPolicy: "gold-tier"
    # o QoS estática:
    # qosPolicy: "max-throughput-100MB"
```

---

## 📂 Estructura del Proyecto

```
trident_nas/
├── generate_trident_nas.py    # Script principal optimizado
├── config.yaml                 # Configuración completa (con ejemplos)
├── requirements.txt            # Dependencias Python
├── README.md                   # Esta documentación
├── backend_storage.yaml        # ✅ Generado
└── secret.yaml                 # ✅ Generado
```

---

## 🛠️ Troubleshooting

### Error: "campos obligatorios"

```
ERROR: Los siguientes campos son obligatorios en config.yaml:
  - backend.managementLIF
```

**Solución**: Asegúrate de tener los 3 campos obligatorios en `config.yaml`.

### Campos vacíos comentados en YAML generado

Es **normal**. Los campos con valores vacíos `''` se comentan automáticamente para:
- ✅ Mantener documentación visible
- ✅ No afectar la ejecución
- ✅ Facilitar personalización futura

### Regenerar archivos

Simplemente ejecuta de nuevo:
```bash
python generate_trident_nas.py
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Añadir nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

---

## 📄 Licencia

Este proyecto está bajo licencia MIT.

---

## 🔗 Referencias

- [NetApp Trident Documentation](https://docs.netapp.com/us-en/trident/)
- [ONTAP NAS Driver](https://docs.netapp.com/us-en/trident/trident-use/ontap-nas.html)
- [Kubernetes Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
