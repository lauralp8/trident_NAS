# Generador de Configuración NetApp Trident NAS

**Versión:** 2.0 (Optimizada)  
**Autor:** Professional Services NetApp  
**Fecha:** Marzo 2026

---

## Tabla de Contenidos

1. [Descripción Funcional](#descripción-funcional)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Guía de Uso Rápido](#guía-de-uso-rápido)
5. [Arquitectura y Componentes](#arquitectura-y-componentes)
6. [Parametrización Detallada](#parametrización-detallada)
7. [Configuración Avanzada](#configuración-avanzada)
8. [Flujo Interno del Proceso](#flujo-interno-del-proceso)
9. [Logs y Diagnóstico](#logs-y-diagnóstico)
10. [Catálogo de Errores](#catálogo-de-errores)
11. [Consideraciones de Seguridad](#consideraciones-de-seguridad)
12. [Mejores Prácticas](#mejores-prácticas)
13. [Referencias](#referencias)

---

## Descripción Funcional

### Propósito

Generador automatizado y optimizado de configuraciones YAML para NetApp Trident CSI (Container Storage Interface) en entornos Kubernetes y OpenShift. Basado en arquitectura moderna con Python dataclasses, tipado fuerte y validación automática para garantizar configuraciones seguras y estandarizadas.

### Funcionalidades Principales

**Generación Automática de Recursos:**
- **TridentBackendConfig**: Define la conexión y parámetros del backend de almacenamiento ONTAP
- **StorageClass**: Configura clases de almacenamiento consumibles por aplicaciones
- **Secret**: Auto-generado desde `config.yaml` con credenciales cifradas

**Arquitectura Moderna:**
- **Dataclasses Python**: Tipado fuerte y validación automática de tipos
- **Configuración Unificada**: Todo en un solo archivo `config.yaml` (incluyendo credenciales)
- **Fusión Inteligente**: Combina valores de usuario con defaults sin sobrescribir configuraciones
- **Auto-Generación de Nombres**: BackendName generado automáticamente desde managementLIF

**Validación y Seguridad:**
- Validación automática de campos obligatorios antes de la generación
- Verificación de tipos de datos y formatos con Python type hints
- Soporte para autenticación dual: usuario/contraseña o certificados TLS
- Credenciales almacenadas en `config.yaml` y auto-generadas en `secret.yaml`
- Comentado automático de campos opcionales no utilizados para mejor legibilidad

**Características Optimizadas:**
- Configuración centralizada: define credenciales una sola vez en `config.yaml`
- Auto-generación de `secret.yaml` con credenciales desde `config.yaml`
- Compatibilidad con formatos legacy (backend.credentials anidado)
- Sin necesidad de editar múltiples archivos
- Comentado inteligente de campos vacíos en YAML generado

### Casos de Uso

- **Despliegue Inicial**: Configuración rápida de backends Trident NAS en nuevos clusters
- **Estandarización**: Configuraciones uniformes en múltiples entornos (dev, test, prod)
- **Migración**: Conversión de configuraciones legacy a TridentBackendConfig moderno
- **CI/CD**: Automatización de aprovisionamiento de almacenamiento en pipelines
- **Laboratorios**: Generación rápida de configuraciones para entornos de prueba
- **Rotación de Credenciales**: Actualización centralizada desde un solo archivo

---

## Requisitos del Sistema

### Software Requerido

**Python:**
- Versión: Python 3.9
- Librerías: PyYAML >= 6.0

**Plataforma de Contenedores:**
- Kubernetes 1.29.4+ o OpenShift 4.x
- NetApp Trident CSI 24.02
- Acceso con permisos de administrador al namespace `trident`

**Conectividad de Red:**
- Conectividad TCP/IP entre pods de Trident y Management LIF del SVM (puerto 443 para HTTPS)
- Conectividad NFS entre nodos de Kubernetes y Data LIF del SVM (puertos 111, 2049, 4045-4046)
- Resolución DNS funcional si se utilizan nombres de host en lugar de IPs

---

## Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone <URL_REPOSITORIO>
cd trident_nas
```

### Paso 2: Instalar Dependencias Python

```bash
# Usando pip
pip install -r requirements.txt

# O usando pip3 explícitamente
pip3 install -r requirements.txt
```

**Contenido de requirements.txt:**
```
PyYAML>=6.0
```

### Paso 3: Verificar Instalación

```bash
# Verificar versión de Python
python --version

# Verificar PyYAML instalado
python -c "import yaml; print(yaml.__version__)"

# Verificar acceso a Kubernetes/OpenShift
kubectl version --client
oc version  # Si usa OpenShift
```

---

## Guía de Uso Rápido

### Inicio Rápido (3 Pasos)

```bash
# 1. Editar configuración (solo necesitas tocar este archivo)
nano config.yaml

# 2. Generar archivos YAML
python generate_trident_nas.py

# 3. Aplicar en Kubernetes
kubectl apply -f secret.yaml -n trident
kubectl apply -f backend_storage_nas.yaml -n trident
```

### Configuración Mínima Requerida

Edita `config.yaml` con estos valores mínimos:

```yaml
backend:
  managementLIF: 192.168.0.135     # IP de gestión del SVM
  dataLIF: nassvm.demo.netapp.com  # IP/hostname para montajes NFS
  svm: nassvm                       # Nombre del SVM en ONTAP
  
  credentials:
    name: trident-creds
    username: vsadmin
    password: Netapp1!

storageClass:
  name: rhoso-nas
```

### Archivos Generados

El script genera automáticamente:

```
✓ backend_storage_nas.yaml  # TridentBackendConfig + StorageClass
✓ secret.yaml               # Credenciales (auto-generado desde config.yaml)
```

### Verificación Post-Despliegue

```bash
# Verificar Secret creado
kubectl get secret trident-creds -n trident

# Verificar TridentBackendConfig
kubectl get tbc -n trident

# Verificar StorageClass
kubectl get storageclass

# Ver estado del backend
kubectl describe tbc <nombre-backend> -n trident
```
# Usando pip
pip install -r requirements.txt

# O usando pip3 explícitamente
pip3 install -r requirements.txt
```

**Contenido de requirements.txt:**
```
PyYAML>=6.0
```

### Paso 3: Verificar Instalación

```bash
# Verificar versión de Python
python --version

# Verificar PyYAML instalado
python -c "import yaml; print(yaml.__version__)"

# Verificar acceso a Kubernetes/OpenShift
kubectl version --client
oc version  # Si usa OpenShift
```

---

## Creación de Archivos desde Cero

Esta sección explica cómo crear los archivos de configuración necesarios cuando se empieza desde cero.

### Archivos Requeridos

Para utilizar el generador, necesitas crear **dos archivos** en el directorio del proyecto:

1. **config.yaml**: Configuración del backend Trident y StorageClass
2. **secret.yaml**: Credenciales de acceso al backend ONTAP (siempre creado manualmente)

---

### 1. Crear config.yaml

El archivo `config.yaml` contiene toda la configuración del backend y StorageClass. A continuación se muestra la estructura completa con todos los campos disponibles.

#### Estructura Mínima (Solo Campos Obligatorios)

```yaml
# config.yaml - Configuración mínima
backend:
  managementLIF: "192.168.1.100"
  dataLIF: "192.168.1.101"
  svm: "svm_prod"
  
  credentials:
    name: "ontap-credentials"

storageClass:
  name: "ontap-nas-storage"
```

#### Estructura Completa (Todos los Campos)

```yaml
# config.yaml - Configuración completa con todos los parámetros

# ========================================
# CONFIGURACIÓN DEL BACKEND TRIDENT
# ========================================
backend:
  # --- CAMPOS OBLIGATORIOS ---
  
  # IP de gestión del SVM (Storage Virtual Machine)
  managementLIF: "192.168.1.100"
  
  # IP de datos NFS del SVM
  dataLIF: "192.168.1.101"
  
  # Nombre del SVM en ONTAP
  svm: "svm_prod"
  
  # Referencia al Secret de Kubernetes con las credenciales
  credentials:
    name: "ontap-credentials"
  
  # --- CAMPOS OPCIONALES CON VALORES POR DEFECTO ---
  
  # Namespace donde se despliega Trident (default: trident)
  namespace: "trident"
  
  # Versión de la API de TridentBackendConfig (default: trident.netapp.io/v1)
  version: "trident.netapp.io/v1"
  
  # Nombre del backend (si está vacío, se auto-genera como "ontap-nas_<dataLIF>")
  backendName: ""
  
  # Driver de almacenamiento (default: ontap-nas)
  storageDriverName: "ontap-nas"
  
  # Tipo de NAS: nfs o smb (default: nfs)
  nasType: "nfs"
  
  # Usar API REST en lugar de ZAPI (default: false)
  useREST: false
  
  # Límite de volúmenes concurrentes (default: 200)
  limitVolumeSize: "200Gi"
  
  # Tamaño máximo de volumen (default: 10Ti)
  limitAggregateUsage: "80%"
  
  # Exportación NFS automática de volúmenes (default: false)
  autoExportPolicy: false
  
  # CIDR de política de exportación (ejemplo: "10.0.0.0/8")
  autoExportCIDRs: ""
  
  # --- DEFAULTS (Valores por defecto para volúmenes) ---
  defaults:
    # Reserva de espacio para snapshots (default: none)
    snapshotReserve: "none"
    
    # Política de snapshots (default: none)
    snapshotPolicy: "none"
    
    # Política de exportación NFS (default: default)
    exportPolicy: "default"
    
    # Nivel de seguridad NFS: sys, krb5, krb5i, krb5p (default: sys)
    securityStyle: "unix"
    
    # Permisos Unix de volúmenes (default: 0755)
    unixPermissions: "0755"
    
    # Garantía de espacio: none, volume, file (default: none)
    spaceReserve: "none"
    
    # Habilitar cifrado de volumen (default: false)
    encryption: false
    
    # Tipo de volumen de ONTAP: rw, dp (default: rw)
    tieringPolicy: "none"

# ========================================
# CONFIGURACIÓN DE STORAGECLASS
# ========================================
storageClass:
  # --- CAMPO OBLIGATORIO ---
  
  # Nombre de la StorageClass
  name: "ontap-nas-storage"
  
  # --- CAMPOS OPCIONALES ---
  
  # Política de reclamación: Delete o Retain (default: Delete)
  reclaimPolicy: "Delete"
  
  # Permitir expansión dinámica de volúmenes (default: true)
  allowVolumeExpansion: true
  
  # Modo de vinculación: Immediate o WaitForFirstConsumer (default: Immediate)
  volumeBindingMode: "Immediate"
```

#### Campos Obligatorios vs Opcionales

**CAMPOS OBLIGATORIOS (sin estos el script fallará):**
- `backend.managementLIF`
- `backend.dataLIF`
- `backend.svm`
- `backend.credentials.name`
- `storageClass.name`

**CAMPOS OPCIONALES (si no se especifican, se usan valores por defecto):**
- Todos los demás campos tienen valores predefinidos

#### Pasos para Crear config.yaml

```bash
# 1. Crear el archivo vacío
touch config.yaml

# 2. Editar con tu editor preferido
nano config.yaml
# o
vim config.yaml
# o
code config.yaml  # VSCode

# 3. Copiar la estructura mínima o completa según necesites

# 4. Reemplazar los valores de ejemplo con tus valores reales:
#    - IPs de managementLIF y dataLIF de tu SVM ONTAP
#    - Nombre de tu SVM
#    - Nombre del Secret (debe coincidir con el que crearás)
#    - Nombre de la StorageClass

# 5. Verificar sintaxis YAML
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

---

## Arquitectura y Componentes

### Cambio Importante en Versión 2.0

**Nueva Arquitectura Centralizada:**

En la versión 2.0, se ha simplificado radicalmente la configuración:

- **Antes (v1.x)**: Credenciales en `secret.yaml` (manual) + configuración en `config.yaml`
- **Ahora (v2.0)**: Todo en `config.yaml` → Script genera automáticamente `secret.yaml`

**Beneficios:**
- ✅ Un solo archivo para editar (`config.yaml`)
- ✅ Secret auto-generado con credenciales de `config.yaml`
- ✅ Sin necesidad de mantener sincronizados múltiples archivos
- ✅ Rotación de credenciales más simple
- ✅ Dataclasses con tipado fuerte y validación automática

### Estructura del Proyecto

```
trident_nas/
├── generate_trident_nas.py      # Script principal (optimizado v2.0)
├── config.yaml                  # Configuración unificada (incluye credenciales)
├── requirements.txt             # Dependencias Python
├── README.md                    # Este archivo
├── backend_storage_nas.yaml     # GENERADO: TridentBackendConfig + StorageClass
└── secret.yaml                  # GENERADO: Credenciales (auto-creado desde config.yaml)
```

### Componentes del Sistema

#### 1. config.yaml (Configuración Única)

Archivo de configuración unificado que contiene:

```yaml
backend:
  managementLIF: "..."         # Conexión al SVM
  svm: "..."                   # Storage Virtual Machine
  credentials:                 # ⚠️ Credenciales ahora aquí
    name: trident-creds
    username: vsadmin
    password: Netapp1!
  defaults:                    # Configuraciones de volúmenes
    spaceReserve: none
    snapshotPolicy: none
    # ... más opciones

storageClass:
  name: "rhoso-nas"
  reclaimPolicy: Delete
  # ... más opciones
```

**Campos Obligatorios:**
- `backend.managementLIF`: IP de gestión del SVM
- `backend.svm`: Nombre del SVM en ONTAP
- `backend.credentials.username`: Usuario ONTAP (si no usas certificados)
- `backend.credentials.password`: Contraseña (si no usas certificados)
- `storageClass.name`: Nombre del StorageClass en K8s

#### 2. generate_trident_nas.py (Script Optimizado)

Script Python moderno con arquitectura basada en dataclasses:

**Clases Principales:**
- `BackendConfig`: Configuración del TridentBackendConfig
- `StorageClassConfig`: Configuración del StorageClass
- `SecretConfig`: Credenciales (auto-extraídas de config.yaml)
- `BackendDefaults`: Valores por defecto de volúmenes
- `DebugTraceFlags`: Flags de depuración

**Funciones Clave:**
- `load_config()`: Carga y fusiona configuración con defaults
- `merge_dicts()`: Fusión recursiva inteligente de configuraciones
- `create_backend_yaml()`: Genera TridentBackendConfig
- `create_storage_class_yaml()`: Genera StorageClass
- `create_secret_yaml()`: **NUEVO** - Auto-genera Secret desde config.yaml
- `comment_empty_fields()`: Comenta campos vacíos en YAML final

**Características:**
- Validación automática de tipos con Python type hints
- Auto-generación de backendName desde managementLIF
- Compatible con formato legacy (credentials anidado)
- Comentado inteligente de campos opcionales no usados

#### 3. backend_storage_nas.yaml (Generado)

Contiene dos recursos Kubernetes:

**a) TridentBackendConfig:**
```yaml
apiVersion: trident.netapp.io/v1
kind: TridentBackendConfig
metadata:
  name: backend-jc-nas1200
  namespace: trident
spec:
  version: 1
  backendName: ontap-nas_192_168_0_135  # Auto-generado
  storageDriverName: ontap-nas
  managementLIF: 192.168.0.135
  svm: nassvm
  credentials:
    name: trident-creds  # Referencia al Secret
  defaults:
    spaceReserve: none
    # ... valores por defecto
```

**b) StorageClass:**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rhoso-nas
provisioner: csi.trident.netapp.io
parameters:
  backendType: ontap-nas
  media: ssd
```

#### 4. secret.yaml (Auto-Generado) ⭐ NUEVO

**Auto-generado desde config.yaml**. Ya no es necesario crearlo manualmente.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  username: vsadmin      # Extraído de config.yaml
  password: Netapp1!     # Extraído de config.yaml
```

**Importante:** Si usas certificados TLS, inclúyelos en `config.yaml`:
```yaml
backend:
  credentials:
    name: trident-creds
    clientCertificate: |
      -----BEGIN CERTIFICATE-----
      ...
      -----END CERTIFICATE-----
    clientPrivateKey: |
      -----BEGIN PRIVATE KEY-----
      ...
      -----END PRIVATE KEY-----
```

---

## Parametrización Detallada

### Configuración del Backend

#### Campos Obligatorios

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `managementLIF` | string | IP de gestión del SVM | `192.168.0.135` |
| `svm` | string | Storage Virtual Machine | `nassvm` |
| `credentials.username` | string | Usuario ONTAP (si no usas certs) | `vsadmin` |
| `credentials.password` | string | Contraseña (si no usas certs) | `Netapp1!` |

#### Campos Opcionales Comunes

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `backendName` | string | auto | Nombre del backend (auto-genera desde managementLIF) |
| `storagePrefix` | string | `trident` | Prefijo de volúmenes ONTAP |
| `storageDriverName` | string | `ontap-nas` | Driver: `ontap-nas`, `ontap-nas-economy`, `ontap-nas-flexgroup` |
| `nasType` | string | `nfs` | Protocolo: `nfs` o `smb` |
| `useREST` | bool | `true` | Usar REST API (ONTAP 9.11.1+) en lugar de ZAPI |
| `autoExportPolicy` | bool | `false` | Auto-crear export policies para volúmenes |
| `autoExportCIDRs` | list | `['0.0.0.0/0']` | CIDRs permitidos en export policy |
| `limitVolumeSize` | string | `""` | Tamaño máximo de volumen (ej: `10Ti`) |
| `limitAggregateUsage` | string | `""` | Límite de uso de agregado (ej: `80%`) |
| `qtreesPerFlexvol` | string | `200` | Qtrees por FlexVol (ontap-nas-economy) |
| `nfsMountOptions` | string | `""` | Opciones de montaje NFS |
| `labels` | dict | `{}` | Labels para selección en StorageClass |

#### Configuración de Labels

Los labels se usan para filtrar backends en StorageClass:

```yaml
backend:
  labels:
    environment: production
    tier: gold
    location: us-east1
    backend: ontap-nas
```

Uso en StorageClass:
```yaml
storageClass:
  parameters:
    selector: "environment=production; tier=gold"
```

#### Defaults de Volúmenes

Valores aplicados a todos los PVs creados con este backend:

```yaml
backend:
  defaults:
    # Gestión de espacio
    spaceReserve: none              # none | volume | file
    spaceAllocation: "false"        # Thin provisioning
    
    # Snapshots
    snapshotPolicy: none            # none | default | daily | weekly
    snapshotReserve: none           # none | 5% | 10%
    snapshotDir: "true"             # Visibilidad de .snapshot
    
    # Seguridad y permisos
    unixPermissions: "755"          # Permisos Unix del volumen
    exportPolicy: default           # Export policy NFS de ONTAP
    securityStyle: unix             # unix | ntfs | mixed
    encryption: "false"             # NetApp Volume Encryption (NVE)
    
    # Performance (QoS)
    qosPolicy: ""                   # Traditional QoS (ej: extreme)
    adaptiveQosPolicy: ""           # Adaptive QoS (ej: extreme-performance)
    
    # Ubicación
    aggregate: ""                   # Agregado específico (ej: aggr1)
    tieringPolicy: none             # none | snapshot-only | auto | all
    
    # Plantilla de nombres
    nameTemplate: ""                # Ej: "{{.volume.Namespace}}_{{.volume.Name}}"
```

#### Debug Flags

Para troubleshooting avanzado:

```yaml
backend:
  debugTraceFlags:
    api: false      # Traza llamadas API ONTAP
    method: false   # Traza métodos internos de Trident
```

**⚠️ Advertencia:** Solo habilitar en troubleshooting, genera logs masivos.

ción
  name: rhoso-nas                   # Nombre visible en K8s
  
  # Comportamiento
  isDefault: true                   # StorageClass por defecto del cluster
  reclaimPolicy: Delete             # Delete | Retain (al borrar PVC)
  allowVolumeExpansion: true        # Permitir resize de PVs
  volumeBindingMode: Immediate      # Immediate | WaitForFirstConsumer
  
  # Para GitOps/ArgoCD
  syncWave: "5"                     # Orden de sincronización
  
  # Filtros de selección de backend
  parameters:
    backendType: ontap-nas          # Driver requerido
    media: ssd                      # ssd | hdd | hybrid
    provisioningType: thin          # thin | thick
    snapshots: "true"               # Soporte de snapshots
```

---

## Ejemplo Completo de Uso

### Escenario: Configurar Backend NAS para Cluster Kubernetes

**Paso 1: Editar config.yaml**

```yaml
backend:
  managementLIF: 192.168.0.135
  dataLIF: nassvm.demo.netapp.com
  svm: nassvm
  
  credentials:
    name: trident-creds
    username: vsadmin
    password: Netapp1!

storageClass:
  name: rhoso-nas
  isDefault: true
```

**Paso 2: Generar archivos**

```bash
python generate_trident_nas.py
```

**Salida esperada:**
```
Usando configuración: config.yaml
✓ Archivo generado: backend_storage_nas.yaml
✓ Archivo generado: secret.yaml

 ------------------------------------------------------------------

 Instrucciones:
  1. Edita config.yaml con tus valores (managementLIF, svm, credenciales)
  2. Ejecuta: python generate_trident_nas.py  
  3. Aplica los archivos generados:
     - kubectl apply -f secret.yaml -n trident
     - kubectl apply -f backend_storage_nas.yaml -n trident
  4. Verifica los recursos creados:
     - kubectl get secret trident-creds -n trident
     - kubectl get tridentbackendconfig -n trident
     - kubectl get storageclass

 ------------------------------------------------------------------
```

**Paso 3: Aplicar en Kubernetes**

```bash
# Aplicar secret con credenciales
kubectl apply -f secret.yaml -n trident

# Aplicar backend y storageclass
kubectl apply -f backend_storage_nas.yaml -n trident

# Verificar recursos creados
kubectl get tbc -n trident
kubectl get sc
```

---

## Mejores Prácticas de Seguridad

### Gestión de Credenciales

**✅ HACER:**
- Definir credenciales en `config.yaml` (centralizado)
- Usar certificados TLS en producción
- Rotar contraseñas periódicamente
- Agregar `config.yaml` y `secret.yaml` a `.gitignore`
- Usar herramientas de gestión de secrets (HashiCorp Vault, Sealed Secrets)
- Restringir permisos de archivos: `chmod 600 config.yaml`

**❌ NO HACER:**
- Commitear `config.yaml` con credenciales a Git
- Compartir credenciales en texto plano
- Usar contraseñas débiles
- Dejar `secret.yaml` generado en repositorios públicos
- Usar mismo usuario para múltiples entornos

### Ejemplo con Sealed Secrets

```bash
# Generar secret.yaml
python generate_trident_nas.py

# Encriptar con kubeseal
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Commitear sealed-secret.yaml (seguro)
git add sealed-secret.yaml
git commit -m "Add encrypted trident credentials"
```

### Rotación de Credenciales

```bash
# 1. Actualizar credenciales en config.yaml
nano config.yaml  # Cambiar password

# 2. Regenerar secret.yaml
python generate_trident_nas.py

# 3. Aplicar nuevo secret
kubectl apply -f secret.yaml -n trident

# 4. Reiniciar Trident controller
kubectl rollout restart deployment/trident-controller -n trident
```

---

## Consideraciones de Seguridad

### NetworkPolicies

Restringir acceso a pods de Trident:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: trident-egress
  namespace: trident
spec:
  podSelector:
    matchLabels:
      app: trident
  policyTypes:
    - Egress
  egress:
    - to:
      - ipBlock:
          cidr: 192.168.0.0/24  # Red del SVM
      ports:
      - protocol: TCP
        port: 443  # Management LIF
```

### RBAC

Limitar acceso a secrets de Trident:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: trident-secret-reader
  namespace: trident
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["trident-creds"]
  verbs: ["get", "list"]
```

### Audit Logging

Habilitar audit logs en ONTAP:

```bash
# En ONTAP CLI
vserver audit create -vserver nassvm \
  -destination /audit_logs \
  -events file-ops,cifs-logon-logoff,cap-staging \
  -format xml
  
vserver audit enable -vserver nassvm
```

---

## Mejores Prácticas

### Naming Conventions

```yaml
# Backend
backend:
  name: backend-<environment>-<location>-nas
  # Ejemplo: backend-prod-us-east-nas

# StorageClass
storageClass:
  name: <tier>-<protocol>-<performance>
  # Ejemplo: gold-nas-ssd

# Labels
backend:
  labels:
    environment: prod
    location: us-east1
    tier: gold
    protocol: nfs
```

### Múltiples Entornos

Estructura recomendada:

```
trident_configs/
├── generate_trident_nas.py
├── environments/
│   ├── dev/
│   │   ├── config.yaml
│   │   └── .gitignore
│   ├── test/
│   │   ├── config.yaml
│   │   └── .gitignore
│   └── prod/
│       ├── config.yaml
│       └── .gitignore
```

Generar por entorno:

```bash
# Para development
cd environments/dev
python ../../generate_trident_nas.py

# Para production
cd environments/prod
python ../../generate_trident_nas.py
```

### CI/CD Integration

**GitLab CI ejemplo:**

```yaml
.generate_trident:
  image: python:3.9
  before_script:
    - pip install PyYAML
  script:
    - python generate_trident_nas.py
    - kubectl apply -f secret.yaml -n trident
    - kubectl apply -f backend_storage_nas.yaml -n trident

deploy_dev:
  extends: .generate_trident
  only:
    - develop
  environment:
    name: development

deploy_prod:
  extends: .generate_trident
  only:
    - main
  environment:
    name: production
  when: manual
```

### Monitoring

```bash
# Verificar salud del backend
kubectl get tbc -n trident -w

# Métricas de Trident
kubectl port-forward -n trident svc/trident-metrics 8443:8443
curl -k https://localhost:8443/metrics

# Eventos de Kubernetes
kubectl get events -n trident --sort-by='.lastTimestamp'
```

---

## Troubleshooting

### Problemas Comunes

#### 1. Backend en estado "Failed"

```bash
# Diagnóstico
kubectl describe tbc <backend-name> -n trident
kubectl logs -n trident deployment/trident-controller --tail=100

# Solución: Verificar credenciales
kubectl get secret trident-creds -n trident -o jsonpath='{.data.username}' | base64 -d
```

#### 2. PVC en estado "Pending"

```bash
# Diagnóstico
kubectl describe pvc <pvc-name>

# Verificar StorageClass
kubectl get sc
kubectl describe sc rhoso-nas

# Verificar eventos
kubectl get events --field-selector involvedObject.name=<pvc-name>
```

#### 3. Export Policy Errors

```bash
# En ONTAP, verificar y agregar regla
ssh admin@ontap
vserver export-policy rule create \
  -vserver nassvm \
  -policyname default \
  -clientmatch 192.168.0.0/24 \
  -rorule sys \
  -rwrule sys \
  -superuser sys
```

---

## Referencias

### Documentación Oficial

- [NetApp Trident Documentation](https://docs.netapp.com/us-en/trident/)
- [ONTAP NAS Configuration Guide](https://docs.netapp.com/ontap-9/index.jsp)
- [Kubernetes Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

### NetApp Labs

- **Astra Trident Advanced Features v6.0**
  - Lab Environment: cluster1 (ONTAP 9.14.1)
  - SVM: nassvm
  - IPs: Basadas en `demo.netapp.com`

### Recursos Adicionales

- [Trident GitHub Repository](https://github.com/NetApp/trident)
- [NetApp Community Forums](https://community.netapp.com/)
- [NetApp Pub (Slack)](https://netapppub.slack.com/)

---

## Changelog

### Versión 2.0 (Optimizada) - Marzo 2026

**Cambios Mayores:**
- ✨ Arquitectura basada en dataclasses con tipado fuerte
- ✨ Auto-generación de `secret.yaml` desde `config.yaml`
- ✨ Configuración unificada (credentials en config.yaml)
- ✨ Fusión inteligente recursiva de configuraciones
- ✨ Compatibilidad con formato legacy (credentials anidado)
- ✨ Auto-generación de backendName desde managementLIF

**Mejoras:**
- 🔧 Validación automática de tipos con Python type hints
- 🔧 Comentado inteligente de campos vacíos
- 🔧 Manejo mejorado de errores y mensajes descriptivos
- 🔧 Documentación actualizada y completa

**Deprecado:**
- ❌ Creación manual de `secret.yaml` (ahora auto-generado)

### Versión 1.x - 2025

- Versión inicial con configuración separada
- Credenciales en `secret.yaml` manual

---

## Contribuciones

Para reportar issues o sugerencias:

1. Contactar al equipo de Professional Services NetApp
2. Usar el sistema de tickets interno
3. Documentar el caso de uso y configuración utilizada

---

## Licencia

© 2026 NetApp Professional Services. Todos los derechos reservados.

Este software es propiedad de NetApp Inc. y se proporciona "tal cual" sin garantías de ningún tipo.
grep "name:" secret.yaml
```

**Checklist de Validación:**
- [ ] config.yaml existe y tiene sintaxis YAML válida
- [ ] secret.yaml existe y tiene sintaxis YAML válida
- [ ] `backend.credentials.name` en config.yaml coincide con `metadata.name` en secret.yaml
- [ ] `backend.namespace` en config.yaml coincide con `metadata.namespace` en secret.yaml
- [ ] Todos los campos obligatorios están presentes en config.yaml
- [ ] secret.yaml contiene credenciales válidas (usuario/password O certificados)
- [ ] secret.yaml NO está commiteado en Git (verificar .gitignore)

---

### 4. Ejemplo Completo: Configuración Mínima Funcional

#### config.yaml
```yaml
backend:
  managementLIF: "192.168.100.10"
  dataLIF: "192.168.100.11"
  svm: "svm_kubernetes"
  credentials:
    name: "ontap-creds"

storageClass:
  name: "nas-storage"
```

#### secret.yaml
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ontap-creds
  namespace: trident
type: Opaque
stringData:
  username: "vsadmin"
  password: "NetApp123"
```

Con estos dos archivos mínimos, puedes ejecutar el generador:
```bash
python generate_trident_nas.py
```

### 5. Ejemplo con Labels (Organización y Filtrado)

Las **labels** permiten etiquetar backends para organización y uso en selectores de StorageClass.

#### config.yaml con labels
```yaml
backend:
  managementLIF: "192.168.100.10"
  dataLIF: "192.168.100.11"
  svm: "svm_kubernetes"
  
  # ⚠️ IMPORTANTE: labels debe ser un objeto (mapa clave-valor), NO un string
  labels:
    environment: production
    tier: gold
    location: us-east1
    team: platform
  
  credentials:
    name: "ontap-creds"

storageClass:
  name: "nas-gold-storage"
  parameters:
    selector: "tier=gold; location=us-east1"  # Filtra backends con estas labels
```

**Formato correcto de labels:**
- ✅ **Correcto**: Objeto con pares clave-valor
  ```yaml
  labels:
    key1: value1
    key2: value2
  ```
- ❌ **Incorrecto**: String (causa error de unmarshal)
  ```yaml
  labels: "key1=value1,key2=value2"  # ❌ NO USAR
  ```

---

## Arquitectura y Componentes

### Estructura del Proyecto

```
trident_nas/
├── generate_trident_nas.py    # Script principal generador
├── config.yaml                # Archivo de configuración de entrada
├── secret.yaml                # Plantilla de Secret con credenciales
├── requirements.txt           # Dependencias Python
├── README.md                  # Esta documentación
├── SEGURIDAD_SECRETS.md       # Guía de gestión segura de credenciales
├── backend_storage.yaml       # Archivo generado (salida)
└── .gitignore                 # Exclusiones de Git

```

### Archivos de Entrada

**config.yaml**
- Configuración centralizada de todos los parámetros
- Estructura jerárquica: backend, storageClass
- Soporte para valores por defecto y sobrescritura selectiva

**secret.yaml (plantilla manual)**
- Credenciales sensibles (usuario/contraseña o certificados)
- Debe crearse manualmente por el administrador
- No se genera automáticamente por motivos de seguridad

### Archivos de Salida

**backend_storage.yaml**
- Contiene dos recursos Kubernetes separados por `---`:
  1. TridentBackendConfig: Configuración del backend ONTAP
  2. StorageClass: Clase de almacenamiento para aplicaciones
- Listo para aplicar con `kubectl apply`

### Dataclasses Python

### Dataclasses Python

El código utiliza dataclasses Python para estructuración y validación:

**BackendConfig**
- Almacena configuración del TridentBackendConfig
- Validaciones de campos obligatorios
- Valores por defecto optimizados para producción

**BackendDefaults**
- Parámetros aplicados a todos los volúmenes creados
- Configuraciones de seguridad, snapshots, permisos

**StorageClassConfig**
- Configuración del StorageClass de Kubernetes
- Parámetros de selección de backend

**SecretConfig**
- Credenciales de autenticación
- Soporte para usuario/contraseña y certificados TLS

**TridentConfig**
- Contenedor principal que agrupa todas las configuraciones
- Facilita paso de datos entre funciones

### Flujo de Datos

```
config.yaml  ─────┐
                  ├──> load_config() ──> TridentConfig
secret.yaml  ─────┘                          │
                                             │
                                             ├──> create_backend_yaml()
                                             ├──> create_storage_class_yaml()
                                             │
                                             ▼
                                  backend_storage.yaml
```

---

## Parametrización Detallada

### Campos Obligatorios

Los siguientes campos son **obligatorios** en config.yaml y el script fallará si faltan:

| Campo | Ubicación | Descripción | Ejemplo |
|-------|-----------|-------------|---------|
| `managementLIF` | backend | IP o FQDN del LIF de gestión del SVM | `192.168.1.100` |
| `dataLIF` | backend | IP o FQDN del LIF de datos NFS | `192.168.1.101` |
| `svm` | backend | Nombre del Storage Virtual Machine | `svm-nas-prod` |
| `name` | storageClass | Nombre de la StorageClass | `netapp-nas` |

**Nota sobre credenciales:** Las credenciales (username/password o certificados) se definen en secret.yaml, no en config.yaml.

### Backend - Configuración de Identificación

**Parámetros de Metadata Kubernetes:**

| Parámetro | Tipo | Por Defecto | Modificable | Descripción |
|-----------|------|-------------|-------------|-------------|
| `namespace` | string | `trident` | Sí | Namespace donde se crea el TridentBackendConfig |
| `name` | string | `backend-jc-nas1200` | Sí | Nombre del recurso TridentBackendConfig en K8s |
| `backendName` | string | `ontap-nas_<dataLIF>` | Sí | Identificador interno del backend. Se auto-genera si vacío |

**Parámetros Técnicos del Driver:**

| Parámetro | Tipo | Por Defecto | Modificable | Descripción |
|-----------|------|-------------|-------------|-------------|
| `version` | integer | `1` | Sí | Versión del spec de TridentBackendConfig |
| `storageDriverName` | string | `ontap-nas` | Sí | Driver de Trident a utilizar |
| `nasType` | string | `nfs` | Sí | Tipo de protocolo NAS (nfs o smb) |
| `useREST` | boolean | `true` | Sí | Usar API REST de ONTAP en lugar de ZAPI |

### Backend - Configuración de Conexión

| Parámetro | Tipo | Por Defecto | Descripción |
|-----------|------|-------------|-------------|
| `managementLIF` | string | *obligatorio* | IP o hostname del LIF de gestión ONTAP |
| `dataLIF` | string | *obligatorio* | IP o hostname del LIF de datos para montajes NFS |
| `svm` | string | *obligatorio* | Nombre de la SVM en ONTAP |
| `storagePrefix` | string | `trident` | Prefijo para nombres de volúmenes creados en ONTAP |

### Backend - Políticas de Exportación

| Parámetro | Tipo | Por Defecto | Descripción |
|-----------|------|-------------|-------------|
| `autoExportPolicy` | boolean | `false` | Auto-crear export policies para acceso desde nodos K8s |
| `autoExportCIDRs` | list | `["0.0.0.0/0", "::/0"]` | Rangos CIDR permitidos cuando autoExportPolicy=true |

**Importante:** Si `autoExportPolicy: false`, debe existir una export policy en ONTAP accesible desde los nodos, configurada en `defaults.exportPolicy`.

### Backend - Límites y Cuotas

| Parámetro | Tipo | Por Defecto | Descripción |
|-----------|------|-------------|-------------|
| `limitAggregateUsage` | string | `""` (sin límite) | Porcentaje máximo de uso del aggregate (ej: "80%") |
| `limitVolumeSize` | string | `""` (sin límite) | Tamaño máximo para volúmenes individuales (ej: "500Gi") |
| `qtreesPerFlexvol` | string | `"200"` | Número máximo de qtrees por FlexVol |

### Backend - Opciones Avanzadas

| Parámetro | Tipo | Por Defecto | Descripción |
|-----------|------|-------------|-------------|
| `nfsMountOptions` | string | `""` | Opciones de montaje NFS adicionales |
| `labels` | object (map) | `{}` | Etiquetas clave-valor para organización y filtrado del backend. Formato: `{key1: value1, key2: value2}` |

### Backend - Debug y Troubleshooting

| Parámetro | Tipo | Por Defecto | Descripción |
|-----------|------|-------------|-------------|
| `debugTraceFlags.api` | boolean | `false` | Trazar llamadas API a ONTAP en logs de Trident |
| `debugTraceFlags.method` | boolean | `false` | Trazar métodos internos de Trident en logs |

**Advertencia:** Habilitar debug genera logs muy verbosos. Usar solo para troubleshooting activo.

### Backend - Defaults (Configuración de Volúmenes)

Estos parámetros se aplican automáticamente a todos los volúmenes creados por este backend:

| Parámetro | Tipo | Por Defecto | Descripción |
|-----------|------|-------------|-------------|
| `spaceReserve` | string | `none` | Reserva de espacio (none, volume, file) |
| `spaceAllocation` | string | `false` | Habilitar space allocation en volúmenes |
| `snapshotPolicy` | string | `none` | Política de snapshots de ONTAP |
| `snapshotReserve` | string | `none` | Porcentaje reservado para snapshots |
| `snapshotDir` | string | `true` | Visibilidad del directorio .snapshot |
| `unixPermissions` | string | `755` | Permisos Unix iniciales del volumen |
| `exportPolicy` | string | `default` | Export policy de NFS a aplicar |
| `securityStyle` | string | `unix` | Security style (unix, ntfs, mixed) |
| `encryption` | string | `false` | Cifrado en reposo (requiere licencia NVE) |
| `qosPolicy` | string | `""` | QoS policy de ONTAP a aplicar |
| `adaptiveQosPolicy` | string | `""` | QoS policy adaptativa de ONTAP |
| `nameTemplate` | string | `""` | Patrón para nombres de volumen personalizados |
| `aggregate` | string | `""` | Aggregate específico (vacío = auto-selección) |

### StorageClass - Configuración

### StorageClass - Configuración

| Parámetro | Tipo | Por Defecto | Modificable | Descripción |
|-----------|------|-------------|-------------|-------------|
| `name` | string | `rhoso-nas` | Sí | Nombre de la StorageClass (obligatorio) |
| `isDefault` | boolean | `true` | Sí | Marcar como StorageClass predeterminada |
| `syncWave` | string | `"5"` | Sí | Orden de sincronización para ArgoCD |
| `reclaimPolicy` | string | `Delete` | Sí | Política de reclamación (Delete o Retain) |
| `allowVolumeExpansion` | boolean | `true` | Sí | Permitir expansión de volúmenes tras creación |
| `volumeBindingMode` | string | `Immediate` | Sí | Modo de binding (Immediate o WaitForFirstConsumer) |

**Parámetros de Selección de Backend:**

| Parámetro | Tipo | Por Defecto | Descripción |
|-----------|------|-------------|-------------|
| `backendType` | string | `ontap-nas` | Tipo de driver de backend |
| `media` | string | `ssd` | Tipo de medio de almacenamiento |
| `provisioningType` | string | `thin` | Tipo de aprovisionamiento (thin o thick) |
| `snapshots` | string | `"true"` | Soporte de snapshots de Kubernetes |

**Valores No Modificables (Hardcoded):**

| Parámetro | Valor | Razón |
|-----------|-------|--------|
| `apiVersion` | `storage.k8s.io/v1` | Especificación de Kubernetes |
| `kind` | `StorageClass` | Tipo de recurso Kubernetes |
| `provisioner` | `csi.trident.netapp.io` | Provisioner CSI de Trident |

### Secret - Autenticación

**Estructura del Secret:**

El Secret debe crearse **manualmente** en el archivo `secret.yaml` y aplicarse antes que el backend.

**Opción A: Autenticación con Usuario/Contraseña** (más común)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  username: vsadmin
  password: NetApp123!
```

**Opción B: Autenticación con Certificados TLS** (más segura)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  clientCertificate: |
    -----BEGIN CERTIFICATE-----
    <CONTENIDO_CERTIFICADO_CLIENTE>
    -----END CERTIFICATE-----
  clientPrivateKey: |
    -----BEGIN PRIVATE KEY-----
    <CONTENIDO_CLAVE_PRIVADA>
    -----END PRIVATE KEY-----
  trustedCACertificate: |
    -----BEGIN CERTIFICATE-----
    <CONTENIDO_CERTIFICADO_CA>
    -----END CERTIFICATE-----
```

**Campos del Secret:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `username` | string | Sí (Opción A) | Usuario con permisos en el SVM |
| `password` | string | Sí (Opción A) | Contraseña del usuario |
| `clientCertificate` | string | Sí (Opción B) | Certificado cliente en formato PEM |
| `clientPrivateKey` | string | Sí (Opción B) | Clave privada en formato PEM |
| `trustedCACertificate` | string | Sí (Opción B) | Certificado CA raíz en formato PEM |

**Importante:** El nombre del Secret (metadata.name) debe coincidir con `credentials.name` en config.yaml.

---

## Guía de Uso

### Flujo de Trabajo Estándar

#### Paso 1: Preparar Configuración

Editar `config.yaml` con los parámetros de su entorno:

```yaml
backend:
  managementLIF: 192.168.100.50
  dataLIF: 192.168.100.51
  svm: svm-nas-prod

storageClass:
  name: netapp-nas-gold

credentials:
  name: trident-creds
```

#### Paso 2: Crear Secret con Credenciales

Editar `secret.yaml` con credenciales reales:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  username: svm-admin
  password: <PASSWORD_REAL>
```

#### Paso 3: Generar Archivos YAML

```bash
python generate_trident_nas.py
```

**Salida esperada:**
```
Usando configuración: config.yaml
Archivo generado: backend_storage.yaml

 ------------------------------------------------------------------

 Instrucciones:
  1. Edita config.yaml si necesitas ajustar la configuración
  2. Crea/edita secret.yaml con tus credenciales reales
  3. Aplica los archivos en el siguiente ORDEN:
     a) kubectl apply -f secret.yaml -n trident
     b) kubectl apply -f backend_storage.yaml -n trident
     IMPORTANTE: El Secret debe existir ANTES del Backend
  4. Verifica los recursos creados:
     - kubectl get tridentbackendconfig -n trident
     - kubectl get storageclass

 ------------------------------------------------------------------
```

#### Paso 4: Aplicar Secret (PRIMERO)

```bash
# Aplicar el Secret antes del backend
kubectl apply -f secret.yaml -n trident

# Verificar creación
kubectl get secret trident-creds -n trident
```

#### Paso 5: Aplicar Backend y StorageClass

```bash
# Aplicar backend y StorageClass
kubectl apply -f backend_storage.yaml -n trident

# Verificar backend
kubectl get tridentbackendconfig -n trident
kubectl get tbc -n trident  # Forma abreviada

# Verificar StorageClass
kubectl get storageclass
kubectl get sc  # Forma abreviada
```

#### Paso 6: Validar Estado del Backend

```bash
# Ver estado detallado
kubectl describe tbc <nombre-backend> -n trident

# Buscar estas líneas en el output:
# Phase: Bound
# Last Operation Status: Success
# Message: Backend '<backendName>' created
```

**Estado esperado:**
```yaml
Status:
  Backend Info:
    Backend Name:         ontap-nas_192_168_100_51
    Backend UUID:         <UUID>
  Last Operation Status:  Success
  Message:                Backend 'ontap-nas_192_168_100_51' created
  Phase:                  Bound
```

### Comandos de Verificación

```bash
# Ver backends de Trident
kubectl get tbc -n trident
kubectl get tridentbackends -n trident
kubectl get tbe -n trident

# Ver StorageClasses
kubectl get sc

# Ver detalles específicos
kubectl get tbc <nombre> -n trident -o yaml
kubectl get sc <nombre> -o yaml

# Ver logs de Trident
kubectl logs -n trident deployment/trident-controller
kubectl logs -n trident deployment/trident-controller --follow

# Ver eventos del backend
kubectl describe tbc <nombre> -n trident | grep Events -A 10
```

### Prueba de Provisionamiento

Crear un PVC de prueba:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: netapp-nas-gold
```

Aplicar y verificar:
```bash
kubectl apply -f test-pvc.yaml
kubectl get pvc test-pvc
kubectl describe pvc test-pvc
```

---

## Flujo Interno del Proceso

### Diagrama de Flujo

```
┌──────────────────┐
│  main()            │
│  - Verificar args  │
│  - Buscar config   │
└───────┬──────────┘
        │
        ↓
┌───────┴───────────────────────┐
│  load_config(config.yaml)      │
│  1. Leer YAML                  │
│  2. Fusionar con defaults      │
│  3. Construir dataclasses      │
│  4. Validar campos obligatorios│
└────────────┬──────────────────┘
              │
              ↓ TridentConfig
┌─────────────┴──────────────────────────┐
│  generate_trident_files()                  │
│  ┌───────────────────────────────┐ │
│  │ create_backend_yaml()        │ │
│  │ - Extraer config backend     │ │
│  │ - Auto-generar backendName   │ │
│  │ - Construir estructura YAML  │ │
│  └───────────┬───────────────────┘ │
│              │ Dict                       │
│  ┌───────────┴──────────────────────┐ │
│  │ create_storage_class_yaml()   │ │
│  │ - Extraer config StorageClass │ │
│  │ - Añadir annotations K8s       │ │
│  │ - Construir estructura YAML   │ │
│  └───────────┬─────────────────────┘ │
│              │ Dict                        │
│  ┌───────────┴────────────────────────┐ │
│  │ yaml.dump()                    │ │
│  │ - Serializar backend a YAML    │ │
│  │ - Añadir separador '---'        │ │
│  │ - Serializar StorageClass      │ │
│  │ - Escribir archivo             │ │
│  └───────────┬───────────────────────┘ │
│              │ backend_storage.yaml       │
│  ┌───────────┴────────────────────────┐ │
│  │ comment_empty_fields()         │ │
│  │ - Leer archivo generado        │ │
│  │ - Comentar líneas con ''       │ │
│  │ - Preservar contenedores       │ │
│  │ - Sobrescribir archivo         │ │
│  └──────────────────────────────────┘ │
└───────────────────────────────────────────┘
        │
        ↓
┌───────┴──────────────────┐
│  Confirmación e        │
│  Instrucciones           │
└──────────────────────────┘
```

### Detalles de Funciones Clave

**load_config()**
1. Verificar existencia de config.yaml
2. Parsear YAML a diccionario Python
3. Crear objetos dataclass con valores por defecto
4. Fusionar configuración de usuario con defaults usando merge_dicts()
5. Reconstruir objetos anidados (BackendDefaults, DebugTraceFlags, StorageClassParameters)
6. Manejar compatibilidad de formato credentials (anidado vs flat)
7. Validar campos obligatorios (managementLIF, dataLIF, svm)
8. Retornar objeto TridentConfig completo

**create_backend_yaml()**
1. Convertir BackendConfig a diccionario con asdict()
2. Extraer subsecciones (defaults, debugTraceFlags, credentials)
3. Extraer campos de metadata/spec (namespace, version, backendName, etc.)
4. Auto-generar backendName si está vacío:
   - Sanitizar dataLIF (reemplazar '.' por '_')
   - Formato: `ontap-nas_<dataLIF_sanitizada>`
5. Construir estructura de TridentBackendConfig:
   - apiVersion, kind, metadata
   - spec con todos los parámetros
6. Retornar diccionario listo para YAML

**create_storage_class_yaml()**
1. Extraer configuración de StorageClassConfig
2. Construir annotations:
   - is-default-class (convertir bool a string)
   - sync-wave para ArgoCD
3. Construir parámetros de selección de backend
4. Inyectar campos estáticos (provisioner, reclaimPolicy, etc.)
5. Retornar diccionario listo para YAML

**comment_empty_fields()**
1. Leer archivo YAML generado línea por línea
2. Identificar campos con valores vacíos ('', "")
3. Excluir campos contenedores (metadata, spec, defaults, etc.)
4. Comentar líneas con valores vacíos añadiendo '# ' al inicio
5. Preservar indentación original
6. Sobrescribir archivo con versión procesada

5. Preservar indentación original
6. Sobrescribir archivo con versión procesada

---

## Logs y Diagnóstico

### Niveles de Logging

El generador Python produce output en consola con diferentes niveles:

**Nivel INFO (normal):**
```
Usando configuración: config.yaml
Archivo generado: backend_storage.yaml
```

**Nivel ERROR (validación fallida):**
```
ERROR: Los siguientes campos son obligatorios en config.yaml:
  - backend.managementLIF
  - backend.dataLIF
```

### Logs de Trident

**Ver logs del controlador de Trident:**
```bash
# Logs en tiempo real
kubectl logs -n trident deployment/trident-controller --follow

# Últimas 100 líneas
kubectl logs -n trident deployment/trident-controller --tail=100

# Logs de un pod específico
kubectl logs -n trident <pod-name>
```

**Patrones de log importantes:**

**Backend creado exitosamente:**
```
INFO Successfully reconciled backend 'ontap-nas_192_168_1_101'
INFO Backend 'ontap-nas_192_168_1_101' created
```

**Credenciales faltantes:**
```
WARN  Failed to create backend: backend credentials not found
ERROR Secret 'trident-creds' not found in namespace 'trident'
```

**Error de conectividad:**
```
ERROR Failed to initialize ONTAP API client
ERROR Timeout connecting to management LIF 192.168.1.100
```

**Error de autenticación:**
```
ERROR Authentication failed for user 'vsadmin'
WARN  API error 13005: Unauthorized
```

**Volumen provisionado:**
```
INFO  Allocated volume 'trident_pvc_abc123' on backend 'ontap-nas_192_168_1_101'
INFO  Volume created successfully: svm=svm-nas-prod, volume=trident_pvc_abc123, size=10Gi
```

### Debug Avanzado

**Habilitar debug en el backend:**

Editar config.yaml:
```yaml
backend:
  debugTraceFlags:
    api: true
    method: true
```

Regenerar y aplicar el backend.

**Advertencia:** Esto genera logs extremadamente verbosos. Usar solo para troubleshooting activo y deshabilitar después.

**Inspeccionar recursos Kubernetes:**

```bash
# Ver todas las propiedades del backend
kubectl get tbc <nombre> -n trident -o yaml

# Ver eventos del namespace trident
kubectl get events -n trident --sort-by='.lastTimestamp'

# Describir PVC en Pending
kubectl describe pvc <nombre-pvc>

# Ver detalles del PV creado
kubectl get pv -o yaml | grep -A 20 <nombre-pvc>
```

**Validar conectividad desde el cluster:**

```bash
# Crear pod de debug temporal
kubectl run -it --rm debug --image=busybox --restart=Never -- sh

# Dentro del pod:
ping <managementLIF>
nslookup <managementLIF>
nc -zv <managementLIF> 443
```

### Métricas y Monitoreo

**Ver estado de backends:**
```bash
# Listar todos los backends con estado
kubectl get tbc -n trident -o custom-columns=NAME:.metadata.name,PHASE:.status.phase,STATUS:.status.lastOperationStatus

# Ver backends internos de Trident
kubectl get tridentbackends -n trident -o custom-columns=NAME:.metadata.name,BACKEND:.backendName,ONLINE:.online,STATE:.state
```

**Verificar StorageClasses activas:**
```bash
kubectl get sc -o custom-columns=NAME:.metadata.name,PROVISIONER:.provisioner,DEFAULT:.metadata.annotations.storageclass\.kubernetes\.io/is-default-class
```

---

## Catálogo de Errores

### 1. Validación del Script Python

**Error 1.1: Campos obligatorios faltantes**
```
ERROR: Los siguientes campos son obligatorios en config.yaml:
  - backend.managementLIF
  - backend.dataLIF
  - backend.svm
```
- **Causa:** Uno o más campos obligatorios están ausentes o vacíos en config.yaml
- **Solución:** Completar todos los campos obligatorios en la sección backend

**Error 1.2: Archivo config.yaml no encontrado**
```
ERROR: No se encontró el archivo de configuración.
```
- **Causa:** El archivo config.yaml no existe en el directorio actual
- **Solución:** Verificar que se ejecuta el script desde el directorio correcto, o crear config.yaml

**Error 1.3: Librería PyYAML no instalada**
```
ModuleNotFoundError: No module named 'yaml'
```
- **Causa:** La dependencia PyYAML no está instalada
- **Solución:** Ejecutar `pip install pyyaml` o `pip install -r requirements.txt`

### 2. Credenciales y Autenticación

**Error 2.1: Secret no encontrado**
```
Failed to create backend: backend credentials not found
```
- **Causa:** El Secret especificado no existe en el namespace trident
- **Solución:**
  1. Verificar existencia: `kubectl get secret trident-creds -n trident`
  2. Aplicar secret.yaml antes del backend
  3. Verificar que `credentials.name` coincide con el nombre del Secret

**Error 2.2: Credenciales inválidas**
```
Error verifying trident state: unauthorized
```
- **Causa:** Usuario o contraseña incorrectos en el Secret
- **Solución:**
  1. Verificar credenciales en ONTAP
  2. Actualizar secret.yaml con credenciales correctas
  3. Reaplicar: `kubectl apply -f secret.yaml -n trident`

**Error 2.3: Permisos insuficientes en ONTAP**
```
Error creating volume: insufficient permissions
```
- **Causa:** El usuario no tiene permisos suficientes en el SVM
- **Solución:**
  1. Verificar rol del usuario: debe ser vsadmin o equivalente
  2. Asignar permisos necesarios desde ONTAP CLI

**Error 2.4: Orden incorrecto de aplicación**
```
Events:
  Warning  Failed  Multiple  backend credentials not found
```
- **Causa:** Se aplicó el backend antes que el Secret
- **Solución:** Aplicar siempre el Secret primero, luego el backend

### 3. Conectividad de Red

**Error 3.1: Management LIF no alcanzable**
```
Backend status: Failed - cannot resolve management LIF
```
- **Causa:** La IP/hostname del managementLIF no es accesible
- **Solución:**
  1. Verificar conectividad: `ping <managementLIF>` desde los pods de Trident
  2. Verificar DNS si usa hostname
  3. Comprobar reglas de firewall

**Error 3.2: Data LIF no alcanzable**
```
mount: wrong fs type, bad option, bad superblock
```
- **Causa:** Los nodos no pueden conectar al dataLIF
- **Solución:**
  1. Verificar conectividad desde nodos: `ping <dataLIF>`
  2. Verificar que dataLIF está en red accesible
  3. Comprobar VLANs y routing

**Error 3.3: Timeout de conexión**
```
Timeout connecting to management LIF
```
- **Causa:** No hay respuesta del sistema de almacenamiento
- **Solución:**
  1. Verificar que el SVM y LIFs están operativos
  2. Comprobar latencia de red
  3. Revisar configuración de firewall/ACL

### 4. Configuración del Backend

**Error 4.1: SVM no encontrado**
```
Backend status: Failed - SVM not found
```
- **Causa:** El nombre del SVM es incorrecto o el SVM no existe
- **Solución:**
  1. Verificar SVM desde ONTAP CLI: `vserver show`
  2. Corregir nombre en config.yaml
  3. Regenerar y reaplicar backend

**Error 4.2: Backend duplicado**
```
Backend already exists with different UUID
```
- **Causa:** Ya existe un backend con el mismo backendName
- **Solución:**
  1. Eliminar backend anterior: `kubectl delete tbc <nombre> -n trident`
  2. O cambiar `backendName` en config.yaml

**Error 4.3: Namespace trident no existe**
```
namespaces "trident" not found
```
- **Causa:** Trident no está instalado o el namespace no existe
- **Solución:** Instalar NetApp Trident según documentación oficial

**Error 4.4: Export policy inexistente**
```
Export policy creation failed
```
- **Causa:** La export policy referenciada no existe en ONTAP
- **Solución:**
  1. Crear export policy en ONTAP
  2. O habilitar `autoExportPolicy: true` en config.yaml

### 5. Storage Class

**Error 5.1: StorageClass duplicada**
```
StorageClass already exists
```
- **Causa:** Ya existe una StorageClass con el mismo nombre
- **Solución:**
  1. Eliminar StorageClass existente: `kubectl delete sc <nombre>`
  2. O cambiar `storageClass.name` en config.yaml

**Error 5.2: Parámetros incompatibles**
```
No available backends
```
- **Causa:** Los parameters de la StorageClass no coinciden con ningún backend
- **Solución:** Verificar que los parameters (backendType, media, etc.) son compatibles con el backend

### 6. Provisión de Volúmenes (PVC)

**Error 6.1: PVC en Pending - No available backends**
```
Status: Pending
Events: no available backends
```
- **Causa:** Ningún backend cumple los requisitos del StorageClass
- **Solución:**
  1. Verificar estado del backend: `kubectl get tbc -n trident`
  2. Verificar que Phase: Bound
  3. Revisar parameters de la StorageClass

**Error 6.2: Tamaño excede límite**
```
Failed to provision volume: volume size exceeds limit
```
- **Causa:** El tamaño solicitado supera `limitVolumeSize`
- **Solución:**
  1. Aumentar `limitVolumeSize` en config.yaml
  2. O reducir el tamaño solicitado en el PVC

**Error 6.3: Error de montaje NFS**
```
mount.nfs: Connection timed out
```
- **Causa:** Problemas de conectividad NFS
- **Solución:**
  1. Verificar que servicio NFS está activo en el SVM
  2. Verificar export policy permite acceso desde nodos
  3. Comprobar puertos NFS (111, 2049, 4045-4046)

### 7. Permisos y RBAC

**Error 7.1: Sin permisos en namespace trident**
```
User cannot create resource "secrets" in namespace "trident"
```
- **Causa:** El usuario no tiene permisos RBAC suficientes
- **Solución:** Usar un usuario con permisos de administrador o solicitar permisos

**Error 7.2: TridentBackendConfig no reconocido**
```
no matches for kind "TridentBackendConfig" in version "trident.netapp.io/v1"
```
- **Causa:** Trident no está instalado o es versión muy antigua (<21.01)
- **Solución:**
  1. Verificar instalación: `kubectl get pods -n trident`
  2. Actualizar Trident a versión 21.01 o superior

### 8. Configuración de ONTAP

**Error 8.1: Servicio NFS no habilitado**
```
Protocol NFS is not enabled on SVM
```
- **Causa:** El protocolo NFS no está activo en el SVM
- **Solución:** Habilitar NFS en el SVM desde ONTAP CLI o System Manager

**Error 8.2: Aggregate no asignado**
```
No aggregates available for volume creation
```
- **Causa:** El SVM no tiene aggregates asignados
- **Solución:** Asignar aggregates al SVM desde ONTAP CLI

**Error 8.3: LIF en estado down**
```
LIF is not operational
```
- **Causa:** Las interfaces de red no están activas
- **Solución:** Verificar y corregir estado de LIFs en ONTAP

---

---

## Consideraciones de Seguridad

### Gestión de Credenciales

**Principios Fundamentales:**

1. **Nunca versionar credenciales en Git**
```bash
# Añadir a .gitignore
echo "secret.yaml" >> .gitignore
echo "config.yaml" >> .gitignore  # Si contiene credenciales
```

2. **Usar Secrets de Kubernetes de forma nativa**
- Kubernetes cifra Secrets en etcd (si está habilitado)
- Los Secrets se montan en memoria, no se escriben en disco de nodos
- Acceso controlado por RBAC

3. **Separar configuración de credenciales**
- Config.yaml: Parámetros técnicos (puede versionarse)
- Secret.yaml: Credenciales sensibles (NUNCA versionar)

4. **Rotación de credenciales**
```bash
# Actualizar credenciales sin recrear backend
kubectl delete secret trident-creds -n trident
kubectl apply -f secret.yaml -n trident

# Trident detectará el cambio automáticamente
```

### Autenticación Segura

**Opción 1: Usuario dedicado con permisos mínimos**

Crear usuario específico para Trident en ONTAP con solo los permisos necesarios:

```
security login role create -role trident-role -cmddirname DEFAULT -access none
security login role create -role trident-role -cmddirname "volume" -access all
security login role create -role trident-role -cmddirname "qtree" -access all
security login role create -role trident-role -cmddirname "lun" -access all
security login role create -role trident-role -cmddirname "snapmirror" -query "-destination true" -access all

security login create -user-or-group-name trident-user -application ontapi -authentication-method password -role trident-role
security login create -user-or-group-name trident-user -application http -authentication-method password -role trident-role
```

**Opción 2: Autenticación basada en certificados (recomendado para producción)**

Ventajas:
- No requiere gestión de contraseñas
- Certificados con fecha de expiración
- Más difícil de comprometer
- Trazabilidad mejorada

Proceso:
1. Generar certificado cliente
2. Instalar certificado en ONTAP
3. Configurar Secret con certificados en lugar de password

### Cifrado de Datos

**Cifrado en tránsito:**
- NetApp ONTAP soporta NFS sobre TLS (NFS 4.x)
- Configurar con `nfsMountOptions`

**Cifrado en reposo:**
- Habilitar NVE (NetApp Volume Encryption) en ONTAP
- Configurar `encryption: "true"` en defaults
- Requiere licencia NVE

### Network Policies

Limitar tráfico entre pods y almacenamiento:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: trident-network-policy
  namespace: trident
spec:
  podSelector:
    matchLabels:
      app: trident
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 192.168.1.0/24  # Red del almacenamiento
    ports:
    - protocol: TCP
      port: 443  # HTTPS para management
    - protocol: TCP
      port: 2049  # NFS
```

### Auditoría y Cumplimiento

**Logging de accesos:**
- Habilitar audit logging en ONTAP para rastrear operaciones
- Revisar logs periódicamente

**Eventos de Kubernetes:**
```bash
# Revisar eventos relacionados con Trident
kubectl get events -n trident --sort-by='.lastTimestamp'

# Filtrar eventos de backends
kubectl get events -n trident --field-selector involvedObject.kind=TridentBackendConfig
```

**Compliance:**
- Documentar configuraciones aplicadas
- Mantener registro de cambios en backends
- Implementar aprobaciones para cambios en producción

### Hardening

**1. Reducir superficie de ataque:**
- Deshabilitar autoExportPolicy en producción
- Crear export policies restrictivas manualmente
- Limitar rangos CIDR permitidos

**2. Limitar recursos:**
```yaml
backend:
  limitAggregateUsage: "80%"
  limitVolumeSize: "500Gi"
  qtreesPerFlexvol: "100"
```

**3. Permisos Unix restrictivos:**
```yaml
defaults:
  unixPermissions: "750"  # Más restrictivo que 755
  securityStyle: unix
```

**4. Deshabilitar snapshots si no son necesarias:**
```yaml
defaults:
  snapshotDir: "false"
  snapshotPolicy: none
```

### Gestión de Secrets con Herramientas Externas

**Integración con Vault, Sealed Secrets, etc.:**

Ejemplo con Sealed Secrets:
```bash
# Cifrar secret.yaml
kubeseal -f secret.yaml -w sealed-secret.yaml

# Versionar sealed-secret.yaml en Git (es seguro)
git add sealed-secret.yaml
git commit -m "Add sealed secret for Trident"

# El controlador de Sealed Secrets descifrará automáticamente
```

---

## Mejores Prácticas

### Planificación y Diseño

**1. Nomenclatura consistente:**
- Backend: `<entorno>-<ubicación>-ontap-nas` (ej: prod-dc1-ontap-nas)
- StorageClass: `<tier>-<protocolo>` (ej: gold-nfs, silver-nfs)
- Prefijo de volúmenes: Incluir identificador del cluster

**2. Separación por entornos:**
- SVM dedicado por entorno (dev, test, prod)
- Backends separados con políticas diferentes
- StorageClasses diferenciadas por tier de servicio

**3. Estrategia de StorageClasses:**
```yaml
# Gold Tier - Alto rendimiento
storageClass:
  name: netapp-gold
  parameters:
    media: ssd
    provisioningType: thin
    snapshots: "true"

# Silver Tier - Uso general
storageClass:
  name: netapp-silver
  parameters:
    media: hybrid
    provisioningType: thin

# Bronze Tier - Archivo
storageClass:
  name: netapp-bronze
  parameters:
    media: hdd
```

### Configuración de Producción

**Valores recomendados para producción:**

```yaml
backend:
  autoExportPolicy: false  # Crear policies manualmente
  limitAggregateUsage: "85%"
  limitVolumeSize: "1Ti"
  qtreesPerFlexvol: "100"
  
  defaults:
    snapshotPolicy: hourly  # Protección de datos
    snapshotReserve: "10"
    encryption: "true"  # Si hay licencia NVE
    unixPermissions: "750"
    exportPolicy: prod-k8s-export  # Policy específica
    qosPolicy: prod-workload-qos  # Control de QoS
```

### Alta Disponibilidad

**1. Múltiples LIFs:**
```yaml
backend:
  dataLIF: 192.168.1.101,192.168.1.102  # Failover automático
```

**2. Múltiples backends:**
- Configurar backends en diferentes agregados/nodos
- StorageClass puede seleccionar entre múltiples backends
- Redundancia automática

**3. MetroCluster/SnapMirror:**
- Replicación síncrona o asíncrona
- Disaster recovery automatizado

### Monitoreo y Observabilidad

**Métricas clave a monitorear:**

1. **Estado de backends:**
```bash
kubectl get tbc -n trident -w
```

2. **Uso de capacidad:**
- Verificar agregados no superen 80% de uso
- Monitorear crecimiento de volúmenes

3. **Latencia de aprovisionamiento:**
- Tiempo desde PVC Pending hasta Bound
- Alertar si supera umbrales

4. **Tasas de error:**
- Fallos de aprovisionamiento
- Errores de montaje

**Integración con Prometheus:**
- Trident expone métricas en formato Prometheus
- Configurar ServiceMonitor para scraping

### Disaster Recovery

**Backup de configuraciones:**
```bash
# Exportar configuración del backend
kubectl get tbc <nombre> -n trident -o yaml > backup-backend.yaml

# Exportar StorageClass
kubectl get sc <nombre> -o yaml > backup-storageclass.yaml

# Backup periódico automatizado
kubectl get tbc,sc -A -o yaml > backup-trident-$(date +%Y%m%d).yaml
```

**Procedimiento de recuperación:**
1. Instalar Trident en nuevo cluster
2. Aplicar Secrets
3. Aplicar configuraciones de backends
4. Aplicar StorageClasses
5. Importar volúmenes existentes (si aplicable)

### Pruebas y Validación

**Pre-producción:**
1. Probar aprovisionamiento de volúmenes
2. Validar montaje en pods
3. Probar expansión de volúmenes
4. Verificar snapshots (si habilitados)
5. Simular fallos de red
6. Validar performance bajo carga

**Suite de pruebas:**
```bash
# Crear PVC de prueba
kubectl apply -f test-pvc.yaml

# Crear pod consumidor
kubectl apply -f test-consumer.yaml

# Verificar escritura
kubectl exec test-pod -- dd if=/dev/zero of=/mnt/test bs=1M count=100

# Verificar lectura
kubectl exec test-pod -- dd if=/mnt/test of=/dev/null bs=1M

# Limpiar
kubectl delete pod test-pod
kubectl delete pvc test-pvc
```

### Documentación

**Mantener documentado:**
1. Inventario de backends (SVM, LIFs, propósito)
2. Mapeo de StorageClasses a backends
3. Export policies y sus reglas
4. Procedimientos de troubleshooting específicos del entorno
5. Contactos de soporte NetApp
6. Calendario de mantenimientos

---

## Referencias

### Documentación Oficial NetApp

**Trident:**
- Documentación principal: https://docs.netapp.com/us-en/trident/
- Guías de instalación: https://docs.netapp.com/us-en/trident/trident-get-started/
- Backend configuration ONTAP NAS: https://docs.netapp.com/us-en/trident/trident-use/ontap-nas.html
- Ejemplos de configuración: https://docs.netapp.com/us-en/trident/trident-use/ontap-nas-examples.html

**ONTAP:**
- Documentación ONTAP: https://docs.netapp.com/us-en/ontap/
- NFS Configuration: https://docs.netapp.com/us-en/ontap/nfs-config/
- Security Hardening Guide: https://docs.netapp.com/us-en/ontap/security-hardening/

### Documentación Kubernetes

**Storage:**
- Storage Classes: https://kubernetes.io/docs/concepts/storage/storage-classes/
- Persistent Volumes: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
- CSI Documentation: https://kubernetes.io/blog/2019/01/15/container-storage-interface-ga/

**Security:**
- Secrets: https://kubernetes.io/docs/concepts/configuration/secret/
- RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- Network Policies: https://kubernetes.io/docs/concepts/services-networking/network-policies/

### Comunidad y Soporte

**NetApp Community:**
- NetApp Community Forums: https://community.netapp.com/
- GitHub Trident: https://github.com/NetApp/trident
- Slack Channel: NetApp's Pub (https://netapppub.slack.com)

**Soporte Técnico:**
- Para clientes con contrato de soporte activo
- Portal de soporte: https://mysupport.netapp.com/
- Número de teléfono según región

### Recursos Adicionales

**Videos y Tutoriales:**
- NetApp YouTube Channel: Tutoriales de Trident
- NetApp TV: Webinars y demos

**Blogs y Artículos:**
- NetApp Blog: https://blog.netapp.com/
- ThePub by NetApp: Artículos técnicos de la comunidad

### Changelog del Proyecto

**Versión 2.1 (Marzo 2026)**
- Añadido soporte para autenticación con certificados TLS
- Certificados (clientCertificate, clientPrivateKey, trustedCACertificate) movidos a Secret
- Parametrización completa de campos anteriormente hardcodeados (namespace, version, backendName, etc.)
- Mejoras en la documentación y catálogo de errores
- Actualización de instrucciones de aplicación (Secret primero, backend después)

**Versión 2.0 (Febrero 2026)**
- Arquitectura basada en dataclasses Python
- Validación automática de campos obligatorios
- Auto-generación de backendName
- Comentado automático de campos vacíos
- Fusión inteligente de configuración

---

## Contacto y Soporte

**Para consultas sobre esta herramienta:**
- Repositorio: [URL del repositorio]
- Issues: [URL de issues]

**Para soporte de NetApp Trident:**
- Documentación: https://docs.netapp.com/us-en/trident/
- Soporte: https://mysupport.netapp.com/

**Para soporte de NetApp ONTAP:**
- Contactar con su Partner o Representante de NetApp
- Portal de soporte: https://mysupport.netapp.com/

---

**Última actualización:** Marzo 2026  
**Versión del generador:** 2.1  
**Licencia:** [Especificar licencia]

---

## Apéndice A: Ejemplo Completo

### config.yaml
```yaml
backend:
  managementLIF: 192.168.100.50
  dataLIF: 192.168.100.51
  svm: svm-nas-prod
  storagePrefix: k8s-prod
  autoExportPolicy: false
  limitAggregateUsage: "85%"
  limitVolumeSize: "1Ti"
  
  defaults:
    snapshotPolicy: hourly
    snapshotReserve: "10"
    encryption: "true"
    unixPermissions: "750"
    exportPolicy: k8s-prod-export
  
  credentials:
    name: trident-prod-creds

storageClass:
  name: netapp-gold
  isDefault: true
  reclaimPolicy: Retain
  
  parameters:
    media: ssd
    provisioningType: thin
    snapshots: "true"
```

### secret.yaml
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-prod-creds
  namespace: trident
type: Opaque
stringData:
  username: trident-admin
  password: SecurePassword123!
```

### Comandos de despliegue
```bash
# 1. Generar configuración
python generate_trident_nas.py

# 2. Aplicar Secret
kubectl apply -f secret.yaml -n trident

# 3. Aplicar Backend y StorageClass
kubectl apply -f backend_storage.yaml -n trident

# 4. Verificar
kubectl get tbc -n trident
kubectl get sc
kubectl describe tbc backend-jc-nas1200 -n trident
```

---
