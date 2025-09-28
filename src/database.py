import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    """Simple SQLite database manager for PineScript Control Access"""
    
    def __init__(self, db_path: str = "data/pinescript_control.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with foreign keys enabled"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn
    
    def init_database(self):
        """Initialize database with all tables"""
        with self.get_connection() as conn:
            # Migrate existing tables - Add precio column if it doesn't exist
            self._migrate_add_precio_column(conn)
            # Create Indicadores table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS indicadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(200) NOT NULL,
                    version VARCHAR(50) DEFAULT '1.0',
                    pub_id VARCHAR(100) UNIQUE NOT NULL,
                    precio DECIMAL(10,2) DEFAULT 0.00,
                    descripcion TEXT,
                    estado VARCHAR(20) DEFAULT 'activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Clientes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username_tradingview VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255),
                    nombre_completo VARCHAR(200),
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado VARCHAR(20) DEFAULT 'activo',
                    notas TEXT
                )
            """)
            
            # Create Accesos table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accesos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    indicador_id INTEGER NOT NULL,
                    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_fin TIMESTAMP,
                    estado VARCHAR(20) DEFAULT 'activo',
                    tipo_acceso VARCHAR(50) DEFAULT 'temporal',
                    notas TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
                    FOREIGN KEY (indicador_id) REFERENCES indicadores (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accesos_cliente ON accesos (cliente_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accesos_indicador ON accesos (indicador_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accesos_estado ON accesos (estado)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clientes_username ON clientes (username_tradingview)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_indicadores_pub_id ON indicadores (pub_id)")
            
            conn.commit()
            print("✅ Database initialized successfully")
    
    def _migrate_add_precio_column(self, conn):
        """Add precio column to indicadores table if it doesn't exist"""
        try:
            # Check if precio column exists
            cursor = conn.execute("PRAGMA table_info(indicadores)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'precio' not in columns:
                print("🔄 Adding precio column to indicadores table...")
                conn.execute("ALTER TABLE indicadores ADD COLUMN precio DECIMAL(10,2) DEFAULT 0.00")
                print("✅ Added precio column successfully")
        except Exception as e:
            print(f"⚠️ Migration warning (precio column): {e}")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last row id"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/DELETE query and return affected rows count"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics about the database"""
        stats = {}
        
        # Count tables
        stats['total_indicadores'] = self.execute_query("SELECT COUNT(*) as count FROM indicadores")[0]['count']
        stats['indicadores_activos'] = self.execute_query("SELECT COUNT(*) as count FROM indicadores WHERE estado = 'activo'")[0]['count']
        
        stats['total_clientes'] = self.execute_query("SELECT COUNT(*) as count FROM clientes")[0]['count']
        stats['clientes_activos'] = self.execute_query("SELECT COUNT(*) as count FROM clientes WHERE estado = 'activo'")[0]['count']
        
        stats['total_accesos'] = self.execute_query("SELECT COUNT(*) as count FROM accesos")[0]['count']
        stats['accesos_activos'] = self.execute_query("SELECT COUNT(*) as count FROM accesos WHERE estado = 'activo'")[0]['count']
        
        # Próximos a vencer (próximos 7 días)
        stats['proximos_vencimientos'] = self.execute_query("""
            SELECT COUNT(*) as count FROM accesos 
            WHERE estado = 'activo' 
            AND fecha_fin IS NOT NULL 
            AND fecha_fin <= datetime('now', '+7 days')
        """)[0]['count']
        
        return stats

# Global database instance
db = Database()