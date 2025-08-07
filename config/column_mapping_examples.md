# Column Mapping Configuration Examples

This file contains pre-defined column mappings for common external systems and file formats.

## Database Fields Reference

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| marque | string | Yes | Device manufacturer/brand | Samsung, Apple, Huawei |
| modele | string | Yes | Device model name | Galaxy S21, iPhone 13 |
| emmc | string | No | Storage capacity | 128GB, 256GB, 512GB |
| imei1 | string | No | Primary IMEI (14-15 digits) | 123456789012345 |
| imei2 | string | No | Secondary IMEI (14-15 digits) | 123456789012346 |
| utilisateur_id | string | No | Owner UUID | 550e8400-e29b-41d4-a716-446655440000 |

## Common Column Mappings

### 1. Telecom Operator Systems

#### Orange/France Telecom Export
```json
{
    "Marque": "marque",
    "Modèle": "modele", 
    "Capacité": "emmc",
    "IMEI_Principal": "imei1",
    "IMEI_Secondaire": "imei2",
    "ID_Client": "utilisateur_id"
}
```

#### SFR Export Format
```json
{
    "Brand": "marque",
    "Model": "modele",
    "Storage": "emmc",
    "Primary_IMEI": "imei1", 
    "Secondary_IMEI": "imei2",
    "Customer_ID": "utilisateur_id"
}
```

#### Free Mobile Format
```json
{
    "fabricant": "marque",
    "modele_appareil": "modele",
    "memoire": "emmc",
    "imei_1": "imei1",
    "imei_2": "imei2",
    "abonne_id": "utilisateur_id"
}
```

### 2. Device Management Systems

#### Microsoft Intune Export
```json
{
    "Manufacturer": "marque",
    "Model": "modele",
    "TotalStorageSpaceInBytes": "emmc",
    "IMEI": "imei1",
    "UserPrincipalName": "utilisateur_id"
}
```

#### VMware Workspace ONE
```json
{
    "DeviceManufacturer": "marque",
    "DeviceModel": "modele",
    "DeviceCapacity": "emmc", 
    "DeviceIMEI": "imei1",
    "EnrolledUserUuid": "utilisateur_id"
}
```

#### Google Workspace (G Suite)
```json
{
    "manufacturer": "marque",
    "model": "modele",
    "storage": "emmc",
    "imei": "imei1",
    "userId": "utilisateur_id"
}
```

### 3. Inventory Management Systems

#### SAP Asset Management
```json
{
    "EQUIPMENT_MANUFACTURER": "marque",
    "EQUIPMENT_MODEL": "modele",
    "MEMORY_CAPACITY": "emmc",
    "IMEI_PRIMARY": "imei1",
    "IMEI_SECONDARY": "imei2",
    "ASSIGNED_USER": "utilisateur_id"
}
```

#### ServiceNow CMDB
```json
{
    "manufacturer": "marque",
    "model_id": "modele",
    "disk_space": "emmc",
    "serial_number": "imei1",
    "assigned_to": "utilisateur_id"
}
```

#### Lansweeper
```json
{
    "Manufacturer": "marque",
    "Model": "modele",
    "TotalPhysicalMemory": "emmc",
    "SerialNumber": "imei1",
    "AssetOwner": "utilisateur_id"
}
```

### 4. Retailer Systems

#### Amazon Business Export
```json
{
    "Brand": "marque",
    "Product Name": "modele",
    "Storage Capacity": "emmc",
    "Device IMEI": "imei1",
    "Purchaser ID": "utilisateur_id"
}
```

#### Best Buy Business
```json
{
    "device_brand": "marque",
    "device_name": "modele",
    "memory_size": "emmc",
    "device_imei": "imei1",
    "customer_account": "utilisateur_id"
}
```

### 5. Enterprise Systems

#### HR/Employee Database Export
```json
{
    "phone_brand": "marque",
    "phone_model": "modele", 
    "storage_gb": "emmc",
    "primary_imei": "imei1",
    "secondary_imei": "imei2",
    "employee_uuid": "utilisateur_id"
}
```

#### Asset Tracking System
```json
{
    "asset_manufacturer": "marque",
    "asset_model": "modele",
    "capacity": "emmc",
    "unique_identifier": "imei1",
    "assigned_employee": "utilisateur_id"
}
```

### 6. Mobile Carrier Systems

#### Verizon Enterprise
```json
{
    "Device Make": "marque",
    "Device Model": "modele",
    "Memory": "emmc",
    "Equipment ID": "imei1",
    "Account Owner": "utilisateur_id"
}
```

#### AT&T Business
```json
{
    "Make": "marque",
    "Model": "modele",
    "Storage": "emmc",
    "IMEI": "imei1",
    "Subscriber ID": "utilisateur_id"
}
```

### 7. International Formats

#### European Format (GDPR Compliant)
```json
{
    "Hersteller": "marque",
    "Modell": "modele",
    "Speicher": "emmc",
    "IMEI_Primär": "imei1",
    "IMEI_Sekundär": "imei2",
    "Benutzer_UUID": "utilisateur_id"
}
```

#### Asian Markets Format
```json
{
    "制造商": "marque",
    "型号": "modele",
    "存储": "emmc",
    "主IMEI": "imei1",
    "副IMEI": "imei2",
    "用户ID": "utilisateur_id"
}
```

## Usage Examples

### Using Predefined Mappings

1. **Copy the appropriate mapping** from above
2. **Save it as a JSON file** (e.g., `orange_mapping.json`)
3. **Use it in your import**:

```bash
# With file
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@devices.csv" \
  -F "column_mapping=@orange_mapping.json"

# Inline
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@devices.csv" \
  -F 'column_mapping={"Marque":"marque","Modèle":"modele"}'
```

## Custom Mapping Creation

### Step 1: Identify Your Column Names
```bash
# Check first line of CSV
head -1 your_file.csv

# Or use the preview endpoint
curl -X POST "http://localhost:8000/admin/preview-import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@your_file.csv"
```

### Step 2: Create Mapping
```json
{
    "your_brand_column": "marque",
    "your_model_column": "modele",
    "your_storage_column": "emmc",
    "your_imei_column": "imei1",
    "your_second_imei_column": "imei2",
    "your_user_column": "utilisateur_id"
}
```

### Step 3: Test with Preview
```bash
curl -X POST "http://localhost:8000/admin/preview-import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@your_file.csv" \
  -F 'column_mapping={"your_brand_column":"marque",...}'
```

## Validation Rules

### Field Validation
- **marque**: Non-empty string, max 100 characters
- **modele**: Non-empty string, max 100 characters  
- **emmc**: Any string format (e.g., "128GB", "256 GB", "512")
- **imei1/imei2**: Exactly 14 or 15 digits, no letters/symbols
- **utilisateur_id**: Valid UUID format or empty

### Common Issues
- **Mixed case columns**: Mapping is case-sensitive
- **Special characters**: Use UTF-8 encoding
- **Empty values**: Use empty string `""` not `null`
- **Number formatting**: IMEIs as strings, not numbers

## Advanced Scenarios

### Multiple IMEI Fields
If source has more than 2 IMEI fields:
```json
{
    "primary_imei": "imei1",
    "backup_imei": "imei2"
    // Additional IMEIs are ignored
}
```

### Computed Fields
For calculated storage values:
```json
{
    "storage_bytes": "emmc"
    // Will import as-is, e.g., "137438953472" 
    // Consider preprocessing to "128GB"
}
```

### Missing Fields
If source lacks required fields:
```json
{
    "device_name": "modele"
    // Missing marque - will cause validation error
    // Consider setting default via preprocessing
}
```

## Best Practices

1. **Test with preview** before importing
2. **Use consistent naming** across your organization
3. **Document your mappings** for future use
4. **Validate external data** before import
5. **Preprocess if needed** (e.g., convert bytes to GB)
6. **Use standard UUID format** for user IDs
7. **Handle missing data** appropriately
