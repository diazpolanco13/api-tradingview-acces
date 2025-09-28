from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .database import db

class BaseModel:
    """Base model with common functionality"""
    table_name = ""
    
    @classmethod
    def create(cls, **kwargs) -> int:
        """Create a new record and return its ID"""
        # Filter only valid columns for this table
        filtered_kwargs = cls._filter_columns(**kwargs)
        
        columns = list(filtered_kwargs.keys())
        placeholders = ['?' for _ in columns]
        values = list(filtered_kwargs.values())
        
        query = f"""
            INSERT INTO {cls.table_name} ({', '.join(columns)}) 
            VALUES ({', '.join(placeholders)})
        """
        
        return db.execute_insert(query, tuple(values))
    
    @classmethod
    def get_by_id(cls, record_id: int) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        query = f"SELECT * FROM {cls.table_name} WHERE id = ?"
        results = db.execute_query(query, (record_id,))
        return results[0] if results else None
    
    @classmethod
    def get_all(cls, where_clause: str = "", params: tuple = ()) -> List[Dict[str, Any]]:
        """Get all records, optionally with WHERE clause"""
        query = f"SELECT * FROM {cls.table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += " ORDER BY id DESC"
        
        return db.execute_query(query, params)
    
    @classmethod
    def update(cls, record_id: int, **kwargs) -> bool:
        """Update a record by ID"""
        filtered_kwargs = cls._filter_columns(**kwargs)
        
        if not filtered_kwargs:
            return False
            
        set_clause = ', '.join([f"{col} = ?" for col in filtered_kwargs.keys()])
        values = list(filtered_kwargs.values()) + [record_id]
        
        query = f"UPDATE {cls.table_name} SET {set_clause} WHERE id = ?"
        return db.execute_update(query, tuple(values)) > 0
    
    @classmethod
    def delete(cls, record_id: int) -> bool:
        """Delete a record by ID"""
        query = f"DELETE FROM {cls.table_name} WHERE id = ?"
        return db.execute_update(query, (record_id,)) > 0
    
    @classmethod
    def _filter_columns(cls, **kwargs) -> Dict[str, Any]:
        """Filter kwargs to include only valid columns - override in subclasses"""
        return kwargs

class Indicador(BaseModel):
    """Model for managing TradingView indicators"""
    table_name = "indicadores"
    
    @classmethod
    def _filter_columns(cls, **kwargs) -> Dict[str, Any]:
        valid_columns = {
            'nombre', 'version', 'pub_id', 'descripcion', 'estado', 'ultima_actualizacion'
        }
        return {k: v for k, v in kwargs.items() if k in valid_columns}
    
    @classmethod
    def get_by_pub_id(cls, pub_id: str) -> Optional[Dict[str, Any]]:
        """Get indicator by PUB ID"""
        query = f"SELECT * FROM {cls.table_name} WHERE pub_id = ?"
        results = db.execute_query(query, (pub_id,))
        return results[0] if results else None
    
    @classmethod
    def get_active(cls) -> List[Dict[str, Any]]:
        """Get all active indicators"""
        return cls.get_all("estado = 'activo'")
    
    @classmethod
    def search(cls, term: str) -> List[Dict[str, Any]]:
        """Search indicators by name or description"""
        query = f"""
            SELECT * FROM {cls.table_name} 
            WHERE nombre LIKE ? OR descripcion LIKE ? OR pub_id LIKE ?
            ORDER BY nombre
        """
        search_term = f"%{term}%"
        return db.execute_query(query, (search_term, search_term, search_term))

class Cliente(BaseModel):
    """Model for managing clients"""
    table_name = "clientes"
    
    @classmethod
    def _filter_columns(cls, **kwargs) -> Dict[str, Any]:
        valid_columns = {
            'username_tradingview', 'email', 'nombre_completo', 'estado', 'notas'
        }
        return {k: v for k, v in kwargs.items() if k in valid_columns}
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional[Dict[str, Any]]:
        """Get client by TradingView username"""
        query = f"SELECT * FROM {cls.table_name} WHERE username_tradingview = ?"
        results = db.execute_query(query, (username,))
        return results[0] if results else None
    
    @classmethod
    def get_active(cls) -> List[Dict[str, Any]]:
        """Get all active clients"""
        return cls.get_all("estado = 'activo'")
    
    @classmethod
    def search(cls, term: str) -> List[Dict[str, Any]]:
        """Search clients by username, email, or name"""
        query = f"""
            SELECT * FROM {cls.table_name} 
            WHERE username_tradingview LIKE ? OR email LIKE ? OR nombre_completo LIKE ?
            ORDER BY username_tradingview
        """
        search_term = f"%{term}%"
        return db.execute_query(query, (search_term, search_term, search_term))
    
    @classmethod
    def get_with_access_count(cls) -> List[Dict[str, Any]]:
        """Get clients with their active access count"""
        query = """
            SELECT c.*, 
                   COUNT(a.id) as accesos_activos
            FROM clientes c
            LEFT JOIN accesos a ON c.id = a.cliente_id AND a.estado = 'activo'
            GROUP BY c.id
            ORDER BY c.username_tradingview
        """
        return db.execute_query(query)

class Acceso(BaseModel):
    """Model for managing access permissions"""
    table_name = "accesos"
    
    @classmethod
    def _filter_columns(cls, **kwargs) -> Dict[str, Any]:
        valid_columns = {
            'cliente_id', 'indicador_id', 'fecha_inicio', 'fecha_fin', 
            'estado', 'tipo_acceso', 'notas'
        }
        return {k: v for k, v in kwargs.items() if k in valid_columns}
    
    @classmethod
    def get_by_client_and_indicator(cls, cliente_id: int, indicador_id: int) -> Optional[Dict[str, Any]]:
        """Get access record for specific client and indicator"""
        query = f"""
            SELECT * FROM {cls.table_name} 
            WHERE cliente_id = ? AND indicador_id = ? AND estado = 'activo'
        """
        results = db.execute_query(query, (cliente_id, indicador_id))
        return results[0] if results else None
    
    @classmethod
    def get_client_accesses(cls, cliente_id: int) -> List[Dict[str, Any]]:
        """Get all accesses for a specific client with indicator details"""
        query = """
            SELECT a.*, i.nombre as indicador_nombre, i.pub_id
            FROM accesos a
            JOIN indicadores i ON a.indicador_id = i.id
            WHERE a.cliente_id = ?
            ORDER BY a.fecha_creacion DESC
        """
        return db.execute_query(query, (cliente_id,))
    
    @classmethod
    def get_indicator_accesses(cls, indicador_id: int) -> List[Dict[str, Any]]:
        """Get all accesses for a specific indicator with client details"""
        query = """
            SELECT a.*, c.username_tradingview, c.nombre_completo
            FROM accesos a
            JOIN clientes c ON a.cliente_id = c.id
            WHERE a.indicador_id = ?
            ORDER BY a.fecha_creacion DESC
        """
        return db.execute_query(query, (indicador_id,))
    
    @classmethod
    def get_active_accesses(cls) -> List[Dict[str, Any]]:
        """Get all active accesses with client and indicator details"""
        query = """
            SELECT a.*, 
                   c.username_tradingview, c.nombre_completo,
                   i.nombre as indicador_nombre, i.pub_id
            FROM accesos a
            JOIN clientes c ON a.cliente_id = c.id
            JOIN indicadores i ON a.indicador_id = i.id
            WHERE a.estado = 'activo'
            ORDER BY a.fecha_fin ASC
        """
        return db.execute_query(query)
    
    @classmethod
    def get_expiring_soon(cls, days: int = 7) -> List[Dict[str, Any]]:
        """Get accesses expiring in the next N days"""
        query = """
            SELECT a.*, 
                   c.username_tradingview, c.nombre_completo,
                   i.nombre as indicador_nombre, i.pub_id
            FROM accesos a
            JOIN clientes c ON a.cliente_id = c.id
            JOIN indicadores i ON a.indicador_id = i.id
            WHERE a.estado = 'activo' 
            AND a.fecha_fin IS NOT NULL 
            AND a.fecha_fin <= datetime('now', '+{days} days')
            ORDER BY a.fecha_fin ASC
        """
        return db.execute_query(query)
    
    @classmethod
    def get_expired(cls) -> List[Dict[str, Any]]:
        """Get expired accesses that need to be marked as expired"""
        query = """
            SELECT a.*, 
                   c.username_tradingview, c.nombre_completo,
                   i.nombre as indicador_nombre, i.pub_id
            FROM accesos a
            JOIN clientes c ON a.cliente_id = c.id
            JOIN indicadores i ON a.indicador_id = i.id
            WHERE a.estado = 'activo' 
            AND a.fecha_fin IS NOT NULL 
            AND a.fecha_fin <= datetime('now')
            ORDER BY a.fecha_fin DESC
        """
        return db.execute_query(query)
    
    @classmethod
    def grant_access(cls, cliente_id: int, indicador_id: int, days: int, tipo_acceso: str = "temporal") -> int:
        """Grant access to a client for specific days"""
        fecha_inicio = datetime.now()
        fecha_fin = fecha_inicio + timedelta(days=days) if days > 0 else None
        
        # Check if there's already an active access
        existing = cls.get_by_client_and_indicator(cliente_id, indicador_id)
        if existing:
            # Update existing access
            cls.update(existing['id'], 
                      fecha_fin=fecha_fin.isoformat() if fecha_fin else None,
                      tipo_acceso=tipo_acceso,
                      notas=f"Renovado por {days} días" if days > 0 else "Convertido a acceso permanente")
            return existing['id']
        else:
            # Create new access
            return cls.create(
                cliente_id=cliente_id,
                indicador_id=indicador_id,
                fecha_inicio=fecha_inicio.isoformat(),
                fecha_fin=fecha_fin.isoformat() if fecha_fin else None,
                tipo_acceso=tipo_acceso,
                notas=f"Acceso inicial por {days} días" if days > 0 else "Acceso permanente"
            )
    
    @classmethod
    def revoke_access(cls, cliente_id: int, indicador_id: int) -> bool:
        """Revoke access for a client to specific indicator"""
        existing = cls.get_by_client_and_indicator(cliente_id, indicador_id)
        if existing:
            return cls.update(existing['id'], estado='revocado', notas="Acceso revocado manualmente")
        return False
    
    @classmethod
    def mark_expired(cls) -> int:
        """Mark expired accesses as expired and return count"""
        query = """
            UPDATE accesos 
            SET estado = 'expirado' 
            WHERE estado = 'activo' 
            AND fecha_fin IS NOT NULL 
            AND fecha_fin <= datetime('now')
        """
        return db.execute_update(query)