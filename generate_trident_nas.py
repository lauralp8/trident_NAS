#!/usr/bin/env python3
"""
Script optimizado para generar archivos YAML de configuración de Trident NAS para OpenShift.
Genera dos archivos:
  - backend_storage.yaml: Contiene TridentBackendConfig y StorageClass
  - secret.yaml: Contiene el Secret con credenciales
"""

import yaml
import re
import os
from typing import Dict, Any
from dataclasses import dataclass, asdict, field


# ==================== CONFIGURACIÓN CENTRALIZADA ====================

@dataclass
class BackendDefaults:
    """Valores por defecto para la provisión de volúmenes."""
    spaceReserve: str = 'none'
    spaceAllocation: str = 'false'
    snapshotPolicy: str = 'none'
    snapshotReserve: str = '0'
    unixPermissions: str = '755'
    snapshotDir: str = 'true'
    exportPolicy: str = 'default'
    securityStyle: str = 'unix'
    encryption: str = 'false'
    qosPolicy: str = ''
    adaptiveQosPolicy: str = ''
    nameTemplate: str = ''
    aggregate: str = ''


@dataclass
class DebugTraceFlags:
    """Flags de depuración para Trident."""
    api: bool = False
    method: bool = False


@dataclass
class BackendConfig:
    """Configuración del TridentBackendConfig."""
    name: str = 'backend-jc-nas1200'
    managementLIF: str = ''  # Campo obligatorio - debe especificarse en config.yaml
    dataLIF: str = ''  # Campo obligatorio - debe especificarse en config.yaml
    svm: str = ''  # Campo obligatorio - debe especificarse en config.yaml
    storagePrefix: str = 'trident'
    autoExportPolicy: bool = False
    autoExportCIDRs: list = field(default_factory=lambda: ['0.0.0.0/0', '::/0'])
    credentialsName: str = 'trident-creds'  # Nombre del secret de credenciales
    labels: str = ''
    clientCertificate: str = ''
    clientPrivateKey: str = ''
    trustedCACertificate: str = ''
    limitAggregateUsage: str = ''
    limitVolumeSize: str = ''
    nfsMountOptions: str = ''
    qtreesPerFlexvol: str = '200'
    debugTraceFlags: DebugTraceFlags = field(default_factory=DebugTraceFlags)
    defaults: BackendDefaults = field(default_factory=BackendDefaults)


@dataclass
class StorageClassParameters:
    """Parámetros del StorageClass."""
    backendType: str = 'ontap-nas'
    media: str = 'ssd'
    provisioningType: str = 'thin'
    snapshots: str = 'true'


@dataclass
class StorageClassConfig:
    """Configuración del StorageClass."""
    name: str = 'rhoso-nas'
    isDefault: bool = True
    syncWave: str = '5'
    parameters: StorageClassParameters = field(default_factory=StorageClassParameters)


@dataclass
class SecretConfig:
    """Configuración del Secret."""
    name: str = 'trident-creds'
    username: str = 'edgevsadmin'
    password: str = 'Temporal01'


@dataclass
class TridentConfig:
    """Configuración completa de Trident NAS."""
    backend: BackendConfig = field(default_factory=BackendConfig)
    storageClass: StorageClassConfig = field(default_factory=StorageClassConfig)
    secret: SecretConfig = field(default_factory=SecretConfig)


# ==================== FUNCIONES AUXILIARES ====================

def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusiona dos diccionarios recursivamente.
    Los valores de override tienen prioridad sobre los de base.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_file: str = "config.yaml") -> TridentConfig:
    """
    Carga la configuración desde un archivo YAML.
    Si el archivo no existe, retorna la configuración por defecto.
    """
    if not os.path.exists(config_file):
        return TridentConfig()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        user_config = yaml.safe_load(f) or {}
    
    # Crear configuración por defecto
    default_config = TridentConfig()
    
    # Convertir a diccionario y fusionar
    default_dict = asdict(default_config)
    merged = merge_dicts(default_dict, user_config)
    
    # Reconstruir objetos anidados desde diccionario fusionado
    backend_defaults = BackendDefaults(**merged.get('backend', {}).get('defaults', {}))
    debug_trace_flags = DebugTraceFlags(**merged.get('backend', {}).get('debugTraceFlags', {}))
    backend_data = {
        **merged.get('backend', {}),
        'defaults': backend_defaults,
        'debugTraceFlags': debug_trace_flags
    }
    
    storage_class_params = StorageClassParameters(**merged.get('storageClass', {}).get('parameters', {}))
    storage_class_data = {**merged.get('storageClass', {}), 'parameters': storage_class_params}
    
    backend_config = BackendConfig(**backend_data)
    
    # ===== COMPATIBILIDAD: Manejar credentials.name anidado =====
    backend_config_dict = merged.get('backend', {})
    if 'credentials' in backend_config_dict and isinstance(backend_config_dict['credentials'], dict):
        credentials_name = backend_config_dict['credentials'].get('name', 'trident-creds')
        backend_config.credentialsName = credentials_name
    
    # Si hay secret.name definido, usarlo (tiene prioridad)
    secret_data = merged.get('secret', {})
    if not secret_data.get('name'):
        secret_data['name'] = backend_config.credentialsName
    
    # ===== VALIDACIONES DE CAMPOS OBLIGATORIOS =====
    
    errors = []
    if not backend_config.managementLIF:
        errors.append("  - backend.managementLIF")
    if not backend_config.dataLIF:
        errors.append("  - backend.dataLIF")
    if not backend_config.svm:
        errors.append("  - backend.svm")
    
    if errors:
        raise ValueError(
            "ERROR: Los siguientes campos son obligatorios en config.yaml:\n" +
            "\n".join(errors)
        )
    
    return TridentConfig(
        backend=backend_config,
        storageClass=StorageClassConfig(**storage_class_data),
        secret=SecretConfig(**secret_data)
    )


def comment_empty_fields(filepath: str) -> None:
    """
    Comenta las líneas con valores vacíos ('') en el archivo YAML de forma eficiente.
    NO comenta los campos que son contenedores (metadata, annotations, parameters, etc.)
    
    Args:
        filepath: Ruta del archivo YAML a procesar
    """
    # Campos que son contenedores y nunca deben ser comentados
    container_fields = {
        'metadata', 'annotations', 'parameters', 'credentials', 
        'debugTraceFlags', 'spec', 'defaults', 'data', 'stringData'
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines(keepends=True)
    modified = []
    
    for line in lines:
        # Extraer el nombre del campo si existe
        field_match = re.match(r"^\s*(\w+):\s*(.*)$", line)
        
        if field_match:
            field_name = field_match.group(1)
            field_value = field_match.group(2).strip()
            
            # NO comentar si:
            # 1. Es un campo contenedor
            # 2. No tiene valor (es un objeto anidado)
            # 3. Tiene un valor no vacío
            if field_name in container_fields or not field_value or \
               (field_value and field_value not in ["''", '""', "''", '""']):
                modified.append(line)
            else:
                # Comentar solo valores explícitamente vacíos ('', "")
                if field_value in ["''", '""', "''", '""']:
                    modified.append(re.sub(r'^(\s*)', r'\1# ', line))
                else:
                    modified.append(line)
        else:
            modified.append(line)
    
    # Escribir una sola vez
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(modified)


# ==================== GENERADORES DE RECURSOS ====================

def create_backend_yaml(config: BackendConfig, secret_name: str) -> Dict[str, Any]:
    """
    Crea la configuración del TridentBackendConfig.
    
    Args:
        config: Configuración del backend
        secret_name: Nombre del secret con credenciales
    """
    backend = asdict(config)
    defaults = backend.pop('defaults')
    debug_trace_flags = backend.pop('debugTraceFlags')
    credentials_name = backend.pop('credentialsName')  # No incluir en el spec
    
    # Generar backendName automáticamente: ontap-nas_<dataLIF>
    # Reemplazar puntos por guiones bajos para nombres válidos
    data_lif_sanitized = backend['dataLIF'].replace('.', '_')
    auto_backend_name = f"ontap-nas_{data_lif_sanitized}"
    
    return {
        'apiVersion': 'trident.netapp.io/v1',
        'kind': 'TridentBackendConfig',
        'metadata': {'name': backend['name']},
        'spec': {
            'version': 1,
            'backendName': auto_backend_name,
            'storageDriverName': 'ontap-nas',
            'nasType': 'nfs',
            'useREST': True,
            **backend,
            'defaults': defaults,
            'debugTraceFlags': debug_trace_flags,
            'credentials': {'name': secret_name}
        }
    }


def create_storage_class_yaml(config: StorageClassConfig) -> Dict[str, Any]:
    """
    Crea la configuración del StorageClass.
    
    Args:
        config: Configuración del StorageClass
    """
    return {
        'apiVersion': 'storage.k8s.io/v1',
        'kind': 'StorageClass',
        'metadata': {
            'name': config.name,
            'annotations': {
                'storageclass.kubernetes.io/is-default-class': str(config.isDefault).lower(),
                'argocd.argoproj.io/sync-wave': config.syncWave
            }
        },
        'provisioner': 'csi.trident.netapp.io',
        'reclaimPolicy': 'Delete',
        'parameters': asdict(config.parameters),
        'allowVolumeExpansion': True,
        'volumeBindingMode': 'Immediate'
    }


def create_secret_yaml(config: SecretConfig) -> Dict[str, Any]:
    """
    Crea la configuración del Secret con credenciales.
    
    Args:
        config: Configuración del secret
    """
    return {
        'apiVersion': 'v1',
        'kind': 'Secret',
        'metadata': {'name': config.name},
        'type': 'Opaque',
        'stringData': {
            'username': config.username,
            'password': config.password
        }
    }


# ==================== FUNCIÓN PRINCIPAL ====================

def generate_trident_files(
    config: TridentConfig,
    backend_file: str = "backend_storage.yaml",
    secret_file: str = "secret.yaml"
) -> None:
    """
    Genera los archivos YAML para la configuración de Trident NAS.
    
    Args:
        config: Configuración completa de Trident
        backend_file: Nombre del archivo para backend y storage class
        secret_file: Nombre del archivo para el secret
    """
    # Generar recursos
    backend = create_backend_yaml(config.backend, config.secret.name)
    storage_class = create_storage_class_yaml(config.storageClass)
    secret = create_secret_yaml(config.secret)
    
    # Escribir backend y storage class
    with open(backend_file, 'w', encoding='utf-8') as f:
        yaml.dump(backend, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        f.write('\n---\n\n')
        yaml.dump(storage_class, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Comentar campos vacíos
    comment_empty_fields(backend_file)
    print(f"✓ Archivo generado: {backend_file}")
    
    # Escribir secret
    with open(secret_file, 'w', encoding='utf-8') as f:
        yaml.dump(secret, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✓ Archivo generado: {secret_file}")
    print("\n¡Archivos YAML generados exitosamente!")


def main(config_file: str = None) -> None:
    """
    Función principal que carga la configuración y genera los archivos.
    
    Args:
        config_file: Ruta del archivo de configuración YAML (opcional)
    """
    # Si no se especifica archivo, usar config.yaml
    if config_file is None:
        config_file = 'config.yaml'
        
        if not os.path.exists(config_file):
            print("ERROR: No se encontró el archivo de configuración.")
            print("\nCrea el archivo:")
            print("  - config.yaml")
            return
    
    print(f"📄 Usando configuración: {config_file}")
    
    config = load_config(config_file)
    generate_trident_files(config)
    
    print(f"\n💡 Para personalizar:")
    print(f"  1. Edita {config_file}")
    print(f"  2. Ejecuta: python generate_trident_nas.py")


if __name__ == "__main__":
    main()
