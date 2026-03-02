# 🔒 Gestión Segura de Credenciales - Trident NAS

## ✅ Método Recomendado (MÁS SEGURO)

### 1. NO incluir credenciales en `config.yaml`

El archivo `config.yaml` solo debe contener la referencia al secret:

```yaml
backend:
  managementLIF: nassvm-mgmt.demo.netapp.com
  dataLIF: nassvm.demo.netapp.com
  svm: nassvm
  credentials:
    name: trident-creds  # ← Solo la referencia
```

### 2. Crear `secret.yaml` manualmente (UNA VEZ)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
type: Opaque
stringData:
  username: vsadmin
  password: Netapp1!
```

### 3. Aplicar el secret al cluster (UNA VEZ)

```bash
kubectl apply -f secret.yaml -n trident
```

### 4. Verificar que el secret existe

```bash
kubectl get secret trident-creds -n trident
```

### 5. Generar el backend (SIN credenciales)

```bash
python generate_trident_nas.py
```

**Resultado:**
- ✅ `backend_storage.yaml` generado (solo referencia al secret)
- ℹ️ `secret.yaml` NO generado (se usa el existente)

### 6. Aplicar el backend

```bash
kubectl apply -f backend_storage.yaml
kubectl get tbc -n trident
```

---

## 🔐 Ventajas de este método

1. **Seguridad**: Las credenciales NO están en `config.yaml` ni en Git
2. **Separación**: El secret se gestiona independientemente del backend
3. **Rotación**: Puedes cambiar las credenciales sin modificar `config.yaml`
4. **Kubernetes-native**: Aprovecha los secretos de Kubernetes

---

## ⚠️ Método Alternativo (SOLO DESARROLLO)

Si necesitas generar `secret.yaml` automáticamente (NO recomendado para producción):

1. Descomentar en `config.yaml`:
```yaml
secret:
  username: vsadmin
  password: Netapp1!
```

2. El script generará tanto `backend_storage.yaml` como `secret.yaml`

**ADVERTENCIA:** Las credenciales quedan expuestas en `config.yaml`

---

## 📝 Workflow Completo

```bash
# 1. Crear y aplicar secret manualmente (SOLO UNA VEZ)
kubectl apply -f secret.yaml -n trident

# 2. Verificar el secret
kubectl get secret trident-creds -n trident

# 3. Generar backend (sin credenciales en config.yaml)
python generate_trident_nas.py

# 4. Aplicar backend
kubectl apply -f backend_storage.yaml

# 5. Verificar estado
kubectl get tbc -n trident

# Debería aparecer: PHASE = Bound, STATUS = Success
```

---

## 🔄 Rotación de Credenciales

Para cambiar las credenciales sin modificar el backend:

```bash
# 1. Editar secret.yaml con nuevas credenciales

# 2. Aplicar cambios
kubectl apply -f secret.yaml -n trident

# 3. Reiniciar pods de Trident (opcional)
kubectl rollout restart deployment trident-controller -n trident
```

---

## 🎯 Resumen

| Método | Seguridad | Uso |
|--------|-----------|-----|
| **Secret manual** | ✅ Alta | Producción |
| **Secret auto-generado** | ⚠️ Baja | Solo desarrollo |
