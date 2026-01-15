"""
Celery tasks for virus scanning
"""
from celery import shared_task
from django.utils import timezone
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


@shared_task
def scan_file_task(schematic_id):
    """
    Asynchronous task to scan uploaded files for viruses
    """
    Schematic = apps.get_model('schematics', 'Schematic')
    
    try:
        schematic = Schematic.objects.get(id=schematic_id)
        
        # Update status to scanning
        schematic.scan_status = 'scanning'
        schematic.save(update_fields=['scan_status'])
        
        # Perform scan
        from .scanner import VirusScanner
        scanner = VirusScanner()
        
        # Get file path
        file_path = schematic.file.path
        scan_result = scanner.scan_file(file_path)
        
        # Update schematic with scan result
        if scan_result['is_infected']:
            schematic.scan_status = 'infected'
            # In production, you might want to quarantine/delete the file
            logger.warning(f"Infected file detected: {schematic_id}")
        elif scan_result['status'] == 'error':
            schematic.scan_status = 'error'
        else:
            schematic.scan_status = 'clean'
        
        schematic.scan_result = scan_result
        schematic.scanned_at = timezone.now()
        schematic.save(update_fields=['scan_status', 'scan_result', 'scanned_at'])
        
        logger.info(f"Scan completed for {schematic_id}: {scan_result['status']}")
        return scan_result
        
    except Schematic.DoesNotExist:
        logger.error(f"Schematic {schematic_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error scanning file {schematic_id}: {str(e)}")
        try:
            schematic = Schematic.objects.get(id=schematic_id)
            schematic.scan_status = 'error'
            schematic.scan_result = {'error': str(e)}
            schematic.save(update_fields=['scan_status', 'scan_result'])
        except:
            pass
        return None
