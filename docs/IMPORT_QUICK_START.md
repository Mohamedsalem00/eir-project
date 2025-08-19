# Quick Start Guide - Enhanced Import API

## Prerequisites
- Admin authentication token
- EIR API server running (default: http://localhost:8000)

## Step-by-Step Usage

### 1. Get Your Import Template

```bash
# Get CSV template
curl -X GET "http://localhost:8000/admin/import-template?format_type=csv" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Get JSON template
curl -X GET "http://localhost:8000/admin/import-template?format_type=json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 2. Prepare Your Data File

#### Option A: Use Standard Column Names (No Mapping Needed)
Create a CSV file with these exact column names:
```csv
marque,modele,emmc,imei1,imei2,utilisateur_id
Samsung,Galaxy S21,128GB,123456789012345,123456789012346,
Apple,iPhone 13,256GB,987654321098765,,
```

#### Option B: Use Custom Column Names (Mapping Required)
Create a CSV file with any column names:
```csv
manufacturer,phone_model,storage_capacity,primary_imei,secondary_imei
Samsung,Galaxy S21,128GB,123456789012345,123456789012346
Apple,iPhone 13,256GB,987654321098765,
```

### 3. Create Column Mapping (if needed)

For custom column names, create a JSON mapping:
```json
{
    "manufacturer": "marque",
    "phone_model": "modele", 
    "storage_capacity": "emmc",
    "primary_imei": "imei1",
    "secondary_imei": "imei2"
}
```

### 4. Preview Your Import

Always preview before importing:

```bash
# Preview without mapping (standard column names)
curl -X POST "http://localhost:8000/admin/preview-import" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@devices.csv"

# Preview with mapping (custom column names)
curl -X POST "http://localhost:8000/admin/preview-import" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@devices.csv" \
  -F 'column_mapping={"manufacturer":"marque","phone_model":"modele","storage_capacity":"emmc","primary_imei":"imei1","secondary_imei":"imei2"}'
```

### 5. Perform the Import

If preview looks good, do the actual import:

```bash
# Import without mapping
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@devices.csv"

# Import with mapping
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@devices.csv" \
  -F 'column_mapping={"manufacturer":"marque","phone_model":"modele","storage_capacity":"emmc","primary_imei":"imei1","secondary_imei":"imei2"}'
```

## Common Column Mappings

### From External Systems

#### Telecom Operator Export:
```json
{
    "Brand": "marque",
    "Model": "modele",
    "Storage": "emmc", 
    "IMEI1": "imei1",
    "IMEI2": "imei2",
    "CustomerID": "utilisateur_id"
}
```

#### Device Management System:
```json
{
    "marque_appareil": "marque",
    "device_model": "modele",
    "memory_size": "emmc",
    "first_imei": "imei1", 
    "second_imei": "imei2",
    "owner_uuid": "utilisateur_id"
}
```

#### Inventory System:
```json
{
    "manufacturer": "marque",
    "product_name": "modele",
    "capacity": "emmc",
    "imei_primary": "imei1",
    "imei_secondary": "imei2"
}
```

## Field Requirements

### Required Fields:
- **marque** (brand): Device manufacturer
- **modele** (model): Device model name

### Optional Fields:
- **emmc**: Storage capacity (any format)
- **imei1**: Primary IMEI (14-15 digits)
- **imei2**: Secondary IMEI (14-15 digits) 
- **utilisateur_id**: Owner UUID (valid UUID format)

## Sample Files

Use the provided sample files for testing:

### CSV with Standard Names:
```bash
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@data/sample_devices.csv"
```

### CSV with Custom Names (requires mapping):
```bash
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@data/sample_devices_with_mapping.csv" \
  -F 'column_mapping={"manufacturer":"marque","phone_model":"modele","storage_capacity":"emmc","primary_imei":"imei1","secondary_imei":"imei2"}'
```

### JSON with Custom Names:
```bash
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@data/sample_devices_with_mapping.json" \
  -F 'column_mapping={"brand_name":"marque","device_model":"modele","memory":"emmc","imei_1":"imei1","imei_2":"imei2"}'
```

## Response Analysis

### Successful Response:
```json
{
    "message": "Import terminé. 8 appareils importés.",
    "imported_count": 8,
    "total_rows": 10,
    "success_rate": "80.0%",
    "errors": [
        "Ligne 3: Format IMEI invalide pour imei1: 12345",
        "Ligne 7: Champ 'marque' requis"
    ]
}
```

### What to Check:
- **success_rate**: Should be high (>90%)
- **errors**: Review and fix data issues
- **imported_count vs total_rows**: Check for failed imports

## Error Resolution

### Common Issues:

1. **"Format IMEI invalide"**
   - Fix: Ensure IMEIs are 14-15 digits only
   - Remove any dashes, spaces, or letters

2. **"Champ 'marque' requis"**  
   - Fix: Ensure all rows have brand/manufacturer
   - Check column mapping is correct

3. **"Format utilisateur_id invalide"**
   - Fix: Use valid UUID format or leave empty
   - Example: `550e8400-e29b-41d4-a716-446655440000`

4. **"Format de fichier non supporté"**
   - Fix: Use .csv or .json files only
   - Ensure correct Content-Type header

## Troubleshooting

### Test Authentication:
```bash
curl -X GET "http://localhost:8000/admin/import-template?format_type=csv" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Validate File Format:
```bash
# Check if your CSV is valid
head -5 your_file.csv

# Check if your JSON is valid  
python -m json.tool your_file.json
```

### Test with Sample Data:
```bash
# Use the Python test script
python test_enhanced_import.py
```

## Best Practices

1. **Always preview first** - Use `/admin/preview-import`
2. **Start small** - Test with 5-10 records first
3. **Validate data** - Check IMEI format and required fields
4. **Use UTF-8 encoding** - Ensure special characters work
5. **Backup first** - Always backup before bulk operations
6. **Monitor performance** - Large files may take time
7. **Check audit logs** - All imports are logged
