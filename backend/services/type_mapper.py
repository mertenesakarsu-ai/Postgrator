"""MSSQL to PostgreSQL type mapping"""

def map_mssql_to_pg_type(mssql_type: str, max_length: int = None, precision: int = None, scale: int = None) -> str:
    """
    Convert MSSQL data type to PostgreSQL equivalent
    """
    mssql_type_lower = mssql_type.lower()
    
    # Integer types
    if mssql_type_lower == 'int':
        return 'INTEGER'
    elif mssql_type_lower == 'bigint':
        return 'BIGINT'
    elif mssql_type_lower == 'smallint':
        return 'SMALLINT'
    elif mssql_type_lower == 'tinyint':
        return 'SMALLINT'  # PG doesn't have tinyint
    elif mssql_type_lower == 'bit':
        return 'BOOLEAN'
    
    # Decimal/Numeric types
    elif mssql_type_lower in ['decimal', 'numeric']:
        if precision and scale is not None:
            return f'NUMERIC({precision},{scale})'
        return 'NUMERIC'
    elif mssql_type_lower == 'money':
        return 'NUMERIC(19,4)'
    elif mssql_type_lower == 'smallmoney':
        return 'NUMERIC(10,4)'
    elif mssql_type_lower == 'float':
        return 'DOUBLE PRECISION'
    elif mssql_type_lower == 'real':
        return 'REAL'
    
    # String types
    elif mssql_type_lower in ['varchar', 'nvarchar']:
        if max_length == -1:
            return 'TEXT'
        elif max_length:
            return f'VARCHAR({max_length})'
        return 'VARCHAR(255)'
    elif mssql_type_lower in ['char', 'nchar']:
        if max_length:
            return f'CHAR({max_length})'
        return 'CHAR(1)'
    elif mssql_type_lower in ['text', 'ntext']:
        return 'TEXT'
    
    # Binary types
    elif mssql_type_lower in ['varbinary', 'binary', 'image']:
        return 'BYTEA'
    
    # Date/Time types
    elif mssql_type_lower in ['datetime', 'datetime2', 'smalldatetime']:
        return 'TIMESTAMP'
    elif mssql_type_lower == 'date':
        return 'DATE'
    elif mssql_type_lower == 'time':
        return 'TIME'
    elif mssql_type_lower == 'datetimeoffset':
        return 'TIMESTAMP WITH TIME ZONE'
    
    # UUID
    elif mssql_type_lower == 'uniqueidentifier':
        return 'UUID'
    
    # XML/JSON
    elif mssql_type_lower == 'xml':
        return 'XML'
    
    # Default fallback
    else:
        return 'TEXT'
