"""
Virus scanning service
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class VirusScanner:
    """
    Wrapper for ClamAV virus scanner
    """
    
    def __init__(self):
        self.enabled = settings.CLAMAV_ENABLED
        self.host = settings.CLAMAV_HOST
        self.port = settings.CLAMAV_PORT
    
    def scan_file(self, file_path):
        """
        Scan a file for viruses
        
        Returns:
            dict: {
                'is_infected': bool,
                'virus_name': str or None,
                'status': str
            }
        """
        if not self.enabled:
            logger.info(f"ClamAV disabled, skipping scan for {file_path}")
            return {
                'is_infected': False,
                'virus_name': None,
                'status': 'skipped'
            }
        
        try:
            import clamd
            cd = clamd.ClamdNetworkSocket(self.host, self.port)
            
            # Check if ClamAV is available
            cd.ping()
            
            # Scan the file
            result = cd.scan(file_path)
            
            if result:
                file_result = result.get(file_path)
                if file_result:
                    status, virus_name = file_result
                    if status == 'FOUND':
                        logger.warning(f"Virus found in {file_path}: {virus_name}")
                        return {
                            'is_infected': True,
                            'virus_name': virus_name,
                            'status': 'infected'
                        }
            
            logger.info(f"File {file_path} is clean")
            return {
                'is_infected': False,
                'virus_name': None,
                'status': 'clean'
            }
            
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {str(e)}")
            return {
                'is_infected': False,
                'virus_name': None,
                'status': 'error',
                'error': str(e)
            }
    
    def scan_stream(self, file_stream):
        """
        Scan a file stream for viruses
        """
        if not self.enabled:
            return {
                'is_infected': False,
                'virus_name': None,
                'status': 'skipped'
            }
        
        try:
            import clamd
            cd = clamd.ClamdNetworkSocket(self.host, self.port)
            cd.ping()
            
            result = cd.instream(file_stream)
            
            if result and result.get('stream'):
                status, virus_name = result['stream']
                if status == 'FOUND':
                    return {
                        'is_infected': True,
                        'virus_name': virus_name,
                        'status': 'infected'
                    }
            
            return {
                'is_infected': False,
                'virus_name': None,
                'status': 'clean'
            }
            
        except Exception as e:
            logger.error(f"Error scanning stream: {str(e)}")
            return {
                'is_infected': False,
                'virus_name': None,
                'status': 'error',
                'error': str(e)
            }
