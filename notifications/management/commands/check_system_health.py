"""
Management command to check system health and create notifications.
"""
from django.core.management.base import BaseCommand
from notifications.system_monitor import SystemMonitor
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check system health and create notifications for problems'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        
        if verbose:
            self.stdout.write("Starting system health check...")
        
        try:
            system_monitor = SystemMonitor()
            health_status = system_monitor.check_system_health()
            
            if verbose:
                self.stdout.write(f"System healthy: {health_status['healthy']}")
                self.stdout.write(f"Issues found: {len(health_status['issues'])}")
                self.stdout.write(f"Warnings found: {len(health_status['warnings'])}")
                
                for issue in health_status['issues']:
                    self.stdout.write(
                        self.style.ERROR(f"ISSUE: {issue['component']} - {issue['error']}")
                    )
                
                for warning in health_status['warnings']:
                    self.stdout.write(
                        self.style.WARNING(f"WARNING: {warning['component']} - {warning['error']}")
                    )
            
            if health_status['healthy']:
                self.stdout.write(
                    self.style.SUCCESS("System health check completed successfully")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"System health check found {len(health_status['issues'])} issues")
                )
            
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f"System health check failed: {str(e)}")
            )
