"""
Database Helper Functions
Handles all database operations including connections, queries, and data insertion.
"""

import pyodbc
import time
from loguru import logger


class DatabaseHelper:
    def __init__(self, conn_str):
        """Initialize database helper with connection string."""
        self.conn_str = conn_str
    
    def get_connection(self, max_retries=3):
        """
        Establish database connection with retry logic.
        
        Args:
            max_retries (int): Maximum number of connection attempts
            
        Returns:
            pyodbc.Connection or None: Database connection object
        """
        for attempt in range(1, max_retries + 1):
            try:
                conn = pyodbc.connect(self.conn_str, timeout=10)
                logger.success("DB Connected successfully")
                return conn
            except Exception as e:
                logger.error(f"DB connection failed (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    time.sleep(5)
        return None
    
    def fetch_leads(self, campuses, processed_phones, batch_size=5):
        """
        Fetch leads from database based on campus assignments.
        
        Args:
            campuses (list): List of campus names to fetch leads for
            processed_phones (set): Set of already processed phone numbers
            batch_size (int): Number of leads to fetch
            
        Returns:
            list: List of lead records or empty list on error
        """
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            
            # Build exclusion list for processed phones
            placeholders = ','.join('?' for _ in processed_phones)
            
            # Build campus filter
            non_null_campuses = [c for c in campuses if c not in ['NULL', 'NIL']]
            conditions = []
            params = list(processed_phones)
            
            if non_null_campuses:
                conditions.append(f"mx_Program_Campus IN ({','.join('?' * len(non_null_campuses))})")
                params = non_null_campuses + params
            
            if 'NULL' in campuses:
                conditions.append("mx_Program_Campus IS NULL")
            
            if 'NIL' in campuses:
                conditions.append("mx_Program_Campus = 'NIL'")
            
            campus_filter = " OR ".join(conditions) if conditions else "1=0"
            
            # Construct query
            query = f"""
            SELECT TOP {batch_size} 
                Phone, 
                FirstName, 
                OwnerIdName, 
                mx_Program_Name, 
                mx_Program_Campus
            FROM DUMY_LIVEDB
            WHERE Phone IS NOT NULL 
              AND LTRIM(RTRIM(Phone)) <> ''
              AND OwnerIdName IN ('Texila American University', 'System')
              AND mx_Program_Name IS NOT NULL
              AND ({campus_filter})
              {f'AND Phone NOT IN ({placeholders})' if processed_phones else ''}
            ORDER BY Phone
            """
            
            cur.execute(query, params)
            rows = cur.fetchall()
            
            logger.success(f"Fetched {len(rows)} leads from database")
            return rows
            
        except Exception as e:
            logger.error(f"Error fetching leads: {e}")
            return []
        finally:
            conn.close()
    
    def insert_lead_status(self, results, max_retries=3):
        """
        Insert lead status records into database.
        
        Args:
            results (list): List of result dictionaries to insert
            max_retries (int): Maximum number of insertion attempts
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not results:
            return True
        
        for attempt in range(1, max_retries + 1):
            conn = self.get_connection()
            if not conn:
                if attempt < max_retries:
                    time.sleep(10)
                continue
            
            try:
                cur = conn.cursor()
                
                for record in results:
                    cur.execute("""
                    INSERT INTO Lead_status 
                    (lead_name, Phone, Program, Degree_Awarding_Body, 
                     mx_Program_Campus, Status_lead, Date_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record['lead_name'],
                        record['Phone'],
                        record['Program'],
                        record['Degree_Awarding_Body'],
                        record['mx_Program_Campus'],
                        record['Status_lead'],
                        record['Date_time']
                    ))
                
                conn.commit()
                logger.success(f"Inserted {len(results)} records into Lead_status")
                return True
                
            except Exception as e:
                logger.error(f"DB insert failed (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    time.sleep(10)
            finally:
                conn.close()
        
        return False
    
    def get_daily_stats(self):
        """
        Fetch daily statistics for report generation.
        
        Returns:
            list: List of tuples containing campus, status, and count
        """
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    mx_Program_Campus, 
                    Status_lead, 
                    COUNT(*) as cnt
                FROM Lead_status
                WHERE CAST(Date_time AS DATE) = CAST(GETDATE() AS DATE)
                GROUP BY mx_Program_Campus, Status_lead
            """)
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logger.error(f"Error fetching daily stats: {e}")
            return []
        finally:
            conn.close()
