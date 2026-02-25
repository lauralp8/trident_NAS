# Generador de Configuración Trident NAS

Script en Python para generar archivos YAML de configuración de Trident NAS para OpenShift.

## Descripción

Este script genera automáticamente dos archivos YAML:
- **backend_storage.yaml**: Contiene TridentBackendConfig y StorageClass
- **secret.yaml**: Contiene el Secret con credenciales

Los valores se leen desde **config.yaml** y se aplican valores por defecto para campos no especificados.

## Requisitos

```bash
pip install pyyaml
```

O instalar desde requirements.txt:

```bash
pip install -r requirements.txt
```

## Uso

### 1. Uso Básico con config.yaml (Recomendado)

Edita [config.yaml](config.yaml) con tus valores:

```yaml
backend:
  name: mi-backend
  managementLIF: 192.168.1.100
  dataLIF: 192.168.1.101
  svm: mi-svm
  
secret:
  username: admin
  password: MiPassword123
```

Luego ejecuta:

```bash
python generate_trident_nas.py
```

**Ventajas:**
- Solo especifica los valores que quieres cambiar
- Puedes eliminar líneas que no necesites
- Añadir o quitar parámetros no rompe nada
- Fácil mantener diferentes configuraciones

### 2. Estructura del config.yaml

El archivo está dividido en tres secciones:

#### Backend
Configuración del TridentBackendConfig:
```yaml
backend:
  name: backend-jc-nas1200
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVMv2-cert-rhosoJC-nas1200
  storagePrefix: trident
  # ... más parámetros
  
  defaults:  # Configuración de volúmenes
    spaceReserve: none
    unixPermissions: "777"
    # ... más parámetros
```

#### Storage Class
Configuración del StorageClass Kubernetes:
```yaml
storageClass:
  name: rhoso-nas
  isDefault: true
  syncWave: "5"
  
  parameters:
    backendType: ontap-nas
    media: ssd
```

#### Secret
Credenciales de acceso:
```yaml
secret:
  name: trident-creds
  username: edgevsadmin
  password: Temporal01
```

### 3. Uso desde código Python

```python
from generate_trident_nas import generate_from_config, generate_trident_nas_files

# Generar desde config.yaml
generate_from_config("config.yaml")

# O llamar directamente con parámetros
generate_trident_nas_files(
    backend_name="mi-backend",
    management_lif="192.168.1.100",
    username="admin",
    password="MiPassword123"
)
```

## Valores por Defecto

### Configuración del Backend

| Parámetro | Valor por Defecto | Descripción |
|-----------|-------------------|-------------|
| backend_name | backend-jc-nas1200 | Nombre del backend |
| management_lif | 192.168.204.203 | IP de gestión del LIF |
| data_lif | 192.168.205.203 | IP de datos del LIF |
| svm | SVMv2-cert-rhosoJC-nas1200 | Storage Virtual Machine |
| storage_prefix | trident | Prefijo para los volúmenes |
| storage_class_name | rhoso-nas | Nombre del StorageClass |
| secret_name | trident-creds | Nombre del secret |
| username | edgevsadmin | Usuario de NetApp |
| password | Temporal01 | Contraseña |
| auto_export_policy | True | Habilita políticas de exportación automáticas |
| auto_export_cidrs | ["0.0.0.0/0", "::/0"] | CIDRs para exportación automática |
| labels | "" | Etiquetas personalizadas |
| client_certificate | "" | Certificado del cliente (autenticación basada en certificado) |
| client_private_key | "" | Clave privada del cliente |
| trusted_ca_certificate | "" | Certificado CA de confianza |
| aggregate | "" | Agregado específico (vacío = auto) |
| limit_aggregate_usage | "" | Límite de uso del agregado (ej: "75%") |
| limit_volume_size | "" | Tamaño máximo de volumen (ej: "10Ti") |
| nfs_mount_options | "" | Opciones de montaje NFS |
| qtrees_per_flexvol | "200" | Qtrees por FlexVol |
| useREST | True | Usar API REST de ONTAP |
| nasType | nfs | Tipo de NAS |
| version | 1 | Versión del backend |

### Parámetros de Provisión de Volúmenes (defaults)

| Parámetro | Valor por Defecto | Descripción |
|-----------|-------------------|-------------|
| space_reserve | none | Reserva de espacio (none, volume) |
| space_allocation | false | Asignación de espacio (thin provisioning) |
| snapshot_policy | none | Política de snapshots |
| qos_policy | "" | Política de QoS estática |
| adaptive_qos_policy | "" | Política de QoS adaptativa |
| snapshot_reserve | "0" | Porcentaje de espacio reservado para snapshots |
| split_on_clone | false | División automática de clones del volumen padre |
| encryption | false | Encriptación de volúmenes ONTAP (NVE) |
| luks_encryption | false | Encriptación LUKS a nivel de SO |
| tier_policy | "" | Política de tiering (none, snapshot-only, auto, all, backup) |
| unix_permissions | "777" | Permisos UNIX de los volúmenes |
| snapshot_dir | true | Visibilidad del directorio .snapshot |
| export_policy | default | Política de exportación NFS |
| security_style | unix | Estilo de seguridad (unix/ntfs/mixed) |
| name_template | "" | Plantilla de nombres para volúmenes |
| file_system_type | ext4 | Tipo de sistema de archivos (ext3, ext4, xfs) |

## Estructura de Archivos Generados

### backend_storage.yaml
Contiene dos recursos separados por `---`:
1. **TridentBackendConfig**: Configuración del backend de NetApp ONTAP NAS
2. **StorageClass**: Clase de almacenamiento de Kubernetes

### secret.yaml
Contiene el Secret con las credenciales de usuario y contraseña.

## Aplicar en OpenShift/Kubernetes

```bash
# Aplicar el secret primero
kubectl apply -f secret.yaml

# Aplicar backend y storage class
kubectl apply -f backend_storage.yaml
```

## Funciones Disponibles

- `create_backend_config()`: Crea la configuración del TridentBackendConfig
- `create_storage_class()`: Crea la configuración del StorageClass
- `create_secret()`: Crea la configuración del Secret
- `generate_trident_nas_files()`: Función principal que genera ambos archivos

## Notas

- El StorageClass está configurado como clase por defecto
- Utiliza el driver `ontap-nas` con NFS
- Política de reclamación configurada como `Delete`
- Expansión de volúmenes habilitada
- Modo de vinculación inmediato
