# Enhanced Import API Documentation

## Overview

The enhanced import system provides flexible data import capabilities supporting both JSON and CSV formats with column mapping functionality. This allows you to import device data from external sources regardless of their column naming conventions.

## New Endpoints

### 1. File-based Import with Column Mapping
**POST** `/admin/import-file`

Import devices from JSON or CSV files with optional column mapping.

#### Parameters:
- `file`: Upload file (JSON or CSV)
- `column_mapping`: JSON string mapping file columns to database fields (optional)

#### Example Column Mapping:
```json
{
    "brand_name": "marque",
    "device_model": "modele", 
    "memory": "emmc",
    "imei_1": "imei1",
    "imei_2": "imei2",
    "owner_id": "utilisateur_id"
}
```

### 2. Preview Import Data
**POST** `/admin/preview-import`

Preview and validate import data before actual import.

#### Parameters:
- `file`: Upload file (JSON or CSV)
- `column_mapping`: JSON string mapping (optional)
- `max_preview_rows`: Number of rows to preview (default: 10)

### 3. Get Import Templates
**GET** `/admin/import-template?format_type=csv|json`

Get template files for proper data formatting.

### 4. Legacy JSON Import (kept for compatibility)
**POST** `/admin/import-lot-appareils`

Original endpoint for structured JSON data import.

## Database Fields

### Required Fields:
- `marque`: Device brand (string)
- `modele`: Device model (string)

### Optional Fields:
- `emmc`: Storage capacity (string)
- `imei1`: First IMEI (14-15 digits)
- `imei2`: Second IMEI (14-15 digits)
- `utilisateur_id`: Owner UUID (string)

## Supported File Formats

### CSV Format
```csv
brand_name,device_model,memory,imei_1,imei_2,owner_id
Samsung,Galaxy S21,128GB,123456789012345,123456789012346,
Apple,iPhone 13,256GB,987654321098765,,
```

### JSON Format
```json
[
    {
        "brand_name": "Samsung",
        "device_model": "Galaxy S21",
        "memory": "128GB",
        "imei_1": "123456789012345",
        "imei_2": "123456789012346",
        "owner_id": ""
    },
    {
        "brand_name": "Apple",
        "device_model": "iPhone 13",
        "memory": "256GB",
        "imei_1": "987654321098765",
        "imei_2": "",
        "owner_id": ""
    }
]
```

## Usage Examples

### Example 1: CSV Import with Column Mapping

1. **Prepare your CSV file** with any column names:
```csv
manufacturer,phone_model,storage_gb,primary_imei,secondary_imei
Samsung,Galaxy S21,128,123456789012345,123456789012346
Apple,iPhone 13,256,987654321098765,
```

2. **Create column mapping**:
```json
{
    "manufacturer": "marque",
    "phone_model": "modele",
    "storage_gb": "emmc",
    "primary_imei": "imei1",
    "secondary_imei": "imei2"
}
```

3. **Preview the import**:
```bash
curl -X POST "http://localhost:8000/admin/preview-import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@devices.csv" \
  -F 'column_mapping={"manufacturer":"marque","phone_model":"modele","storage_gb":"emmc","primary_imei":"imei1","secondary_imei":"imei2"}'
```

4. **Perform the import**:
```bash
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@devices.csv" \
  -F 'column_mapping={"manufacturer":"marque","phone_model":"modele","storage_gb":"emmc","primary_imei":"imei1","secondary_imei":"imei2"}'
```

### Example 2: JSON Import without Mapping

If your JSON file already uses correct field names:

```json
[
    {
        "marque": "Samsung",
        "modele": "Galaxy S21", 
        "emmc": "128GB",
        "imei1": "123456789012345",
        "imei2": "123456789012346"
    }
]
```

Simply upload without column mapping:
```bash
curl -X POST "http://localhost:8000/admin/import-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@devices.json"
```

### Example 3: Get Templates

```bash
# Get CSV template
curl -X GET "http://localhost:8000/admin/import-template?format_type=csv" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get JSON template  
curl -X GET "http://localhost:8000/admin/import-template?format_type=json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Response Format

### Successful Import Response:
```json
{
    "message": "Import terminé. 25 appareils importés.",
    "imported_count": 25,
    "total_rows": 30,
    "success_rate": "83.3%",
    "errors": [
        "Ligne 5 (Samsung Galaxy): Format IMEI invalide pour imei1: 12345",
        "Ligne 12 (Apple iPhone): Champ 'marque' requis"
    ],
    "successful_imports": [
        {
            "device_id": "uuid-here",
            "marque": "Samsung",
            "modele": "Galaxy S21",
            "imeis": ["123456789012345", "123456789012346"]
        }
    ],
    "file_info": {
        "filename": "devices.csv",
        "file_type": "CSV",
        "content_type": "text/csv",
        "size_bytes": 1024
    },
    "mapping_applied": {
        "manufacturer": "marque",
        "phone_model": "modele"
    }
}
```

### Preview Response:
```json
{
    "file_info": {
        "filename": "devices.csv",
        "file_type": "CSV",
        "total_rows": 100,
        "preview_rows": 10
    },
    "mapping_info": {
        "mapping_applied": {"manufacturer": "marque"},
        "detected_columns": ["manufacturer", "phone_model", "storage"],
        "target_fields": ["marque", "modele", "emmc", "imei1", "imei2", "utilisateur_id"]
    },
    "validation_summary": {
        "total_rows": 100,
        "valid_rows": 8,
        "invalid_rows": 2,
        "potential_devices": 8,
        "potential_imeis": 15,
        "validation_errors": ["Ligne 3: Format IMEI invalide"]
    },
    "preview_data": [
        {
            "row_number": 1,
            "original_data": {"manufacturer": "Samsung", "phone_model": "Galaxy S21"},
            "mapped_data": {"marque": "Samsung", "modele": "Galaxy S21"},
            "status": "valid",
            "errors": []
        }
    ],
    "recommendations": [
        "Mappage suggéré: {'storage': 'emmc'}",
        "Les données semblent correctes pour l'import"
    ]
}
```

## Error Handling

### Common Errors:
1. **Invalid file format**: File is not JSON or CSV
2. **Invalid column mapping**: JSON parsing error in mapping
3. **Missing required fields**: 'marque' or 'modele' not found
4. **Invalid IMEI format**: IMEI not 14-15 digits
5. **Invalid UUID**: utilisateur_id format error

### Validation Rules:
- **IMEI**: Must be 14 or 15 digits
- **UUID**: Must be valid UUID format for utilisateur_id
- **Required fields**: marque and modele are mandatory
- **File size**: Limited by FastAPI settings
- **Row limit**: No explicit limit, but memory constraints apply

## Best Practices

1. **Always preview first**: Use `/admin/preview-import` before actual import
2. **Use templates**: Get proper format using `/admin/import-template`
3. **Validate mapping**: Ensure column mapping is correct JSON
4. **Check response**: Review errors and success rate
5. **Small batches**: For large files, consider splitting into smaller batches
6. **UTF-8 encoding**: Ensure files are UTF-8 encoded
7. **Backup data**: Always backup before bulk operations

## Security Considerations

- Only administrators can access import endpoints
- All import operations are logged in audit trail
- File uploads are validated for type and content
- Column mapping prevents SQL injection through validation
- UUID validation prevents malformed user references

## Performance Tips

- **CSV vs JSON**: CSV is generally faster for large datasets
- **Column mapping**: Minimal impact on performance
- **Preview limit**: Use reasonable preview limits (10-50 rows)
- **Batch processing**: For very large files, process in batches
- **Memory usage**: Large files are processed in streaming mode where possible

## Migration from Legacy Format

If you have existing import scripts using the legacy format:

**Old format**:
```json
[
    {
        "marque": "Samsung",
        "modele": "Galaxy S21",
        "imeis": ["123456789012345", "123456789012346"]
    }
]
```

**New format**:
```json
[
    {
        "marque": "Samsung", 
        "modele": "Galaxy S21",
        "imei1": "123456789012345",
        "imei2": "123456789012346"
    }
]
```

The legacy endpoint `/admin/import-lot-appareils` still works for backward compatibility.
