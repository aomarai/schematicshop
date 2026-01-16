"""
Celery tasks for virus scanning
"""
from celery import shared_task
from django.utils import timezone
from django.apps import apps
from django.db.models import F
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def scan_file_task(self, schematic_id):
    """
    Asynchronous task to scan uploaded files for viruses
    Implements retry logic and automatic file deletion for infected/error files
    """
    Schematic = apps.get_model('schematics', 'Schematic')
    User = apps.get_model('users', 'User')

    try:
        schematic = Schematic.objects.get(id=schematic_id)

        # Check if max retries exceeded
        if schematic.scan_retry_count >= schematic.max_scan_retries:
            logger.error(f"Max retries exceeded for schematic {schematic_id}, deleting file")
            # Delete the file from storage
            if schematic.file:
                try:
                    schematic.file.delete(save=False)
                    logger.info(f"Deleted file for schematic {schematic_id} after max retries")
                except Exception as delete_error:
                    logger.error(f"Error deleting file for {schematic_id}: {delete_error}")

            schematic.scan_status = 'error'
            schematic.scan_result = {'error': 'Max scan retries exceeded, file deleted'}
            schematic.save(update_fields=['scan_status', 'scan_result'])
            return {'status': 'error', 'reason': 'max_retries_exceeded'}

        # Update status to scanning
        schematic.scan_status = 'scanning'
        schematic.save(update_fields=['scan_status'])

        # Perform scan
        from .scanner import VirusScanner
        scanner = VirusScanner()

        # Get file path
        file_path = schematic.file.path
        scan_result = scanner.scan_file(file_path)

        # Handle scan results
        if scan_result['is_infected']:
            # INFECTED FILE: Delete immediately and flag account
            schematic.scan_status = 'infected'
            schematic.scan_result = scan_result
            schematic.scanned_at = timezone.now()
            schematic.save(update_fields=['scan_status', 'scan_result', 'scanned_at'])

            logger.warning(
                f"Infected file detected: {schematic_id}, "
                f"deleting file and flagging user"
            )

            # Delete the infected file
            if schematic.file:
                try:
                    schematic.file.delete(save=False)
                    logger.info(f"Deleted infected file for schematic {schematic_id}")
                except Exception as delete_error:
                    logger.error(
                        f"Error deleting infected file for {schematic_id}: "
                        f"{delete_error}"
                    )

            # Flag the user account (atomic update to prevent race conditions)
            try:
                user = schematic.owner
                User.objects.filter(id=user.id).update(
                    infected_upload_count=F('infected_upload_count') + 1
                )
                user.refresh_from_db()
                logger.warning(
                    f"Flagged user {user.username} for uploading infected file "
                    f"(total: {user.infected_upload_count})"
                )
            except Exception as flag_error:
                logger.error(
                    f"Error flagging user for {schematic_id}: "
                    f"{flag_error.__class__.__name__}: {flag_error}"
                )

            return scan_result

        elif scan_result['status'] == 'error':
            # ERROR DURING SCAN: Increment retry count and requeue
            schematic.scan_retry_count += 1
            schematic.scan_status = 'pending'  # Reset to pending for retry
            schematic.scan_result = scan_result
            schematic.save(update_fields=['scan_retry_count', 'scan_status', 'scan_result'])

            logger.warning(
                f"Scan error for {schematic_id}, retry {schematic.scan_retry_count}/"
                f"{schematic.max_scan_retries}"
            )

            # Retry with exponential backoff (capped at 15 minutes)
            countdown = min(
                2 ** schematic.scan_retry_count * 60, 900
            )  # Max 15 minutes
            raise self.retry(
                exc=Exception(scan_result.get('error')), countdown=countdown
            )

        else:
            # CLEAN FILE: Move from quarantine to normal storage and mark as clean
            schematic.scan_status = 'clean'
            schematic.scan_result = scan_result
            schematic.scanned_at = timezone.now()
            schematic.save(update_fields=['scan_status', 'scan_result', 'scanned_at'])

            # Note: File movement from quarantine to normal storage would be handled here
            # if using separate storage backends for quarantine and production
            logger.info(f"File {schematic_id} marked as clean")

        return scan_result

    except Schematic.DoesNotExist:
        logger.error(f"Schematic {schematic_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error scanning file {schematic_id}: {str(e)}")
        try:
            schematic = Schematic.objects.get(id=schematic_id)
            schematic.scan_retry_count += 1

            # Check if we should delete due to max retries
            if schematic.scan_retry_count >= schematic.max_scan_retries:
                logger.error(f"Max retries exceeded for {schematic_id}, deleting file")
                if schematic.file:
                    try:
                        schematic.file.delete(save=False)
                        logger.info(f"Deleted file for schematic {schematic_id} after max retries")
                    except Exception as delete_error:
                        logger.error(f"Error deleting file for {schematic_id}: {delete_error}")

                schematic.scan_status = 'error'
                schematic.scan_result = {
                    'error': 'Max scan retries exceeded, file deleted'
                }
                schematic.save(
                    update_fields=['scan_status', 'scan_result',
                                   'scan_retry_count']
                )
            else:
                # Retry
                schematic.scan_status = 'pending'
                schematic.scan_result = {'error': str(e)}
                schematic.save(update_fields=['scan_status', 'scan_result', 'scan_retry_count'])

                # Retry with exponential backoff (capped at 15 minutes)
                countdown = min(2 ** schematic.scan_retry_count * 60, 900)
                raise self.retry(exc=e, countdown=countdown)

        except Exception as inner_exc:
            logger.error(
                f"Failed to update scan error status for schematic {schematic_id}: "
                f"{inner_exc.__class__.__name__}: {inner_exc}"
            )
        return None
