#!/usr/bin/env python3
"""
Settings tab for Scentinel application.
Handles export/import functionality, CSV uploads, and import history tracking.
"""
from typing import Any, Optional, Dict, List
import csv
import io
import json

from nicegui import ui
from .base_tab import BaseTab


class SettingsTab(BaseTab):
    """Settings and data management tab"""

    def __init__(self, database):
        super().__init__(database)

    def setup_tab_content(self, container: Any) -> None:
        """Setup the settings tab content"""
        with container:
            with ui.column().classes('w-full max-w-2xl mx-auto p-6 gap-6'):
                ui.label('Settings & Data Management').classes(
                    'text-3xl font-bold text-gray-800 dark:text-gray-200 mb-6 text-center'
                )

                # Export Collection Section
                with ui.card().classes(
                    'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                    'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                ):
                    with ui.card_section().classes('p-6'):
                        ui.label('Export Collection').classes(
                            'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                        )
                        ui.label('Download your complete collection as JSON backup').classes(
                            'text-gray-600 dark:text-gray-400 mb-4'
                        )
                        ui.button('Export Collection', on_click=self.export_collection, icon='download').classes(
                            'bg-green-600 hover:bg-green-700 text-white font-medium px-6 py-3 '
                            'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                        )

                # Import Collection Section
                with ui.card().classes(
                    'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                    'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                ):
                    with ui.card_section().classes('p-6'):
                        ui.label('Import Collection').classes(
                            'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                        )
                        ui.label('Import from JSON backup file').classes(
                            'text-gray-600 dark:text-gray-400 mb-4'
                        )
                        ui.button('Import Collection', on_click=self.show_import_dialog, icon='upload').classes(
                            'bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 '
                            'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                        )

                # CSV Import Section
                with ui.card().classes(
                    'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                    'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                ):
                    with ui.card_section().classes('p-6'):
                        ui.label('CSV Import').classes(
                            'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                        )
                        ui.label('Import colognes from CSV file (basic data only)').classes(
                            'text-gray-600 dark:text-gray-400 mb-4'
                        )
                        ui.upload(on_upload=self.handle_csv_upload, multiple=False).props('flat accept=".csv"').classes(
                            'bg-orange-50 dark:bg-orange-900 border-2 border-dashed border-orange-300 '
                            'dark:border-orange-700 rounded-lg p-6 text-orange-700 dark:text-orange-300 '
                            'hover:bg-orange-100 dark:hover:bg-orange-800 smooth-transition'
                        ).tooltip('Upload CSV with columns: name, brand, notes (semicolon separated), classifications (semicolon separated)')

                # Import History Section
                with ui.card().classes(
                    'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                    'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                ):
                    with ui.card_section().classes('p-6'):
                        ui.label('Import History').classes(
                            'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                        )
                        ui.label('Track and review your import transactions').classes(
                            'text-gray-600 dark:text-gray-400 mb-4'
                        )

                        # Import statistics summary
                        import_stats = self.db.get_import_statistics()

                        with ui.row().classes('w-full gap-4 mb-4'):
                            with ui.card().classes('flex-1 bg-blue-50 dark:bg-blue-900 border border-blue-200'):
                                with ui.card_section().classes('p-3 text-center'):
                                    ui.label(f"{import_stats['total_imports']}").classes('text-2xl font-bold text-blue-600')
                                    ui.label('Total Imports').classes('text-xs text-blue-800 dark:text-blue-300')

                            with ui.card().classes('flex-1 bg-green-50 dark:bg-green-900 border border-green-200'):
                                with ui.card_section().classes('p-3 text-center'):
                                    ui.label(f"{import_stats['total_colognes_imported']}").classes('text-2xl font-bold text-green-600')
                                    ui.label('Colognes Imported').classes('text-xs text-green-800 dark:text-green-300')

                            with ui.card().classes('flex-1 bg-orange-50 dark:bg-orange-900 border border-orange-200'):
                                with ui.card_section().classes('p-3 text-center'):
                                    ui.label(f"{import_stats['success_rate']}%").classes('text-2xl font-bold text-orange-600')
                                    ui.label('Success Rate').classes('text-xs text-orange-800 dark:text-orange-300')

                        # Expandable import history
                        with ui.expansion('View Import History', icon='history').classes('w-full'):
                            self.setup_import_history_content()

    def setup_import_history_content(self):
        """Setup the import history content inside the expansion"""
        import_history = self.db.get_import_history(limit=20)  # Last 20 imports

        if not import_history:
            ui.label('No import history found').classes('text-center text-gray-500 p-4')
            return

        # Header row
        with ui.row().classes('w-full bg-gray-100 dark:bg-gray-700 p-2 rounded-t-lg font-semibold text-sm'):
            ui.label('Date/Time').classes('flex-1')
            ui.label('Type').classes('w-16 text-center')
            ui.label('Added').classes('w-16 text-center')
            ui.label('Updated').classes('w-16 text-center')
            ui.label('Status').classes('w-20 text-center')
            ui.label('Actions').classes('w-24 text-center')

        # Import history rows
        for import_record in import_history:
            with ui.row().classes('w-full border-b border-gray-200 dark:border-gray-600 p-2 hover:bg-gray-50 dark:hover:bg-gray-800'):
                # Date/time
                ui.label(import_record.timestamp.strftime('%m/%d %H:%M')).classes('flex-1 text-sm')

                # Type
                type_color = 'text-blue-600' if import_record.import_type == 'json' else 'text-green-600'  # type: ignore
                ui.label(str(import_record.import_type).upper()).classes(f'w-16 text-center text-xs font-medium {type_color}')

                # Added count
                ui.label(str(import_record.colognes_added)).classes('w-16 text-center text-sm')

                # Updated count
                ui.label(str(import_record.colognes_updated)).classes('w-16 text-center text-sm')

                # Status
                if import_record.status == 'completed':  # type: ignore
                    status_color = 'text-green-600 bg-green-100 dark:bg-green-900'
                    status_icon = 'check_circle'
                elif import_record.status == 'failed':  # type: ignore
                    status_color = 'text-red-600 bg-red-100 dark:bg-red-900'
                    status_icon = 'error'
                else:
                    status_color = 'text-orange-600 bg-orange-100 dark:bg-orange-900'
                    status_icon = 'warning'

                with ui.row().classes('w-20 justify-center'):
                    ui.icon(status_icon, size='sm').classes(f'{status_color} rounded px-1')

                # Actions
                with ui.row().classes('w-24 justify-center gap-1'):
                    ui.button(
                        icon='info',
                        on_click=lambda r=import_record: self.show_import_details(r)
                    ).props('flat size=sm').classes('text-xs').tooltip('View Details')

                    if import_record.errors_count > 0:  # type: ignore
                        ui.button(
                            icon='warning',
                            on_click=lambda r=import_record: self.show_import_errors(r)
                        ).props('flat size=sm').classes('text-xs text-orange-600').tooltip('View Errors')

    def export_collection(self):
        """Export the entire collection as JSON"""
        try:
            json_data = self.db.export_to_json()

            # Trigger download
            ui.download(json_data.encode(), filename='scentinel_collection.json', media_type='application/json')
            ui.notify('Collection exported successfully!', type='positive')

        except Exception as ex:
            ui.notify(f'Error exporting collection: {str(ex)}', type='negative')

    def show_import_dialog(self):
        """Show dialog for importing JSON collection"""
        with ui.dialog() as dialog, ui.card():
            ui.label('Import Collection').classes('text-h5 mb-4')
            ui.label('Select a JSON backup file to import:').classes('mb-4')

            ui.upload(
                on_upload=lambda e: self.handle_json_import(e, dialog),
                multiple=False,
                auto_upload=True
            ).props('accept=".json"').classes('w-full')

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')

        dialog.open()

    def handle_json_import(self, e: Any, dialog: Any):
        """Handle JSON file import with duplicate resolution"""
        try:
            content = e.content.decode('utf-8')

            # First, analyze the import data to check for duplicates
            analysis = self.db.analyze_import_data(content)

            if not analysis["success"]:
                ui.notify(f'Import failed: {analysis["error"]}', type='negative')
                dialog.close()
                return

            dialog.close()  # Close the file selection dialog

            # If there are duplicates, show the resolution dialog
            if analysis["duplicates"]:
                self.show_duplicate_resolution_dialog(content, analysis)
            else:
                # No duplicates, proceed with normal import
                self.proceed_with_import(content, {}, analysis)

        except Exception as ex:
            ui.notify(f'Error analyzing import file: {str(ex)}', type='negative')
            dialog.close()

    def handle_csv_upload(self, e: Any):
        """Handle CSV file upload"""
        try:
            content = e.content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))

            added_count = 0
            errors = []

            for row in csv_reader:
                try:
                    name = row.get('name', '').strip()
                    brand = row.get('brand', '').strip()

                    if not name or not brand:
                        continue

                    notes_str = row.get('notes', '')
                    classifications_str = row.get('classifications', '')

                    notes = [n.strip() for n in notes_str.split(';') if n.strip()] if notes_str else None
                    classifications = [c.strip() for c in classifications_str.split(';') if c.strip()] if classifications_str else None

                    self.db.add_cologne(name, brand, notes, classifications)
                    added_count += 1
                except Exception as row_ex:
                    errors.append(f"Error importing row {name or 'Unknown'}: {str(row_ex)}")

            # Log the CSV import transaction
            result = {
                'success': True,
                'colognes_added': added_count,
                'colognes_updated': 0,
                'wear_history_added': 0,
                'errors': errors
            }

            self.db.log_import_transaction(
                import_type='csv',
                result=result,
                filename=getattr(e, 'name', 'uploaded_file.csv')
            )

            # Trigger refresh of other components (this will need to be handled via callbacks)
            if hasattr(self, '_on_data_change'):
                self._on_data_change()

            if errors:
                ui.notify(f'Added {added_count} colognes from CSV with {len(errors)} errors', type='warning')
            else:
                ui.notify(f'Added {added_count} colognes from CSV', type='positive')

        except Exception as ex:
            # Log failed import
            result = {
                'success': False,
                'colognes_added': 0,
                'colognes_updated': 0,
                'wear_history_added': 0,
                'errors': [str(ex)]
            }

            self.db.log_import_transaction(
                import_type='csv',
                result=result,
                filename=getattr(e, 'name', 'uploaded_file.csv')
            )

            ui.notify(f'Error uploading CSV: {str(ex)}', type='negative')

    def show_duplicate_resolution_dialog(self, json_content: str, analysis: dict):
        """Show dialog for resolving duplicate colognes"""
        duplicate_resolutions = {}  # cologne_key -> resolution

        with ui.dialog().props('maximized') as duplicate_dialog, ui.card().classes('w-full h-full'):
            with ui.column().classes('w-full h-full p-6'):
                # Header
                ui.label('🔍 Import Analysis - Duplicates Detected').classes('text-h4 mb-4 text-center')

                # Summary stats
                with ui.card().classes('w-full mb-6 bg-blue-50 dark:bg-blue-900'):
                    with ui.card_section().classes('p-4'):
                        with ui.row().classes('justify-around text-center'):
                            with ui.column():
                                ui.label(f"{len(analysis['new_colognes'])}").classes('text-h5 font-bold text-green-600')
                                ui.label('New Colognes').classes('text-caption')
                            with ui.column():
                                ui.label(f"{len(analysis['duplicates'])}").classes('text-h5 font-bold text-orange-600')
                                ui.label('Duplicates Found').classes('text-caption')
                            with ui.column():
                                ui.label(f"{len(analysis.get('errors', []))}").classes('text-h5 font-bold text-red-600')
                                ui.label('Errors').classes('text-caption')

                # Quick action buttons
                with ui.row().classes('w-full justify-center gap-4 mb-6'):
                    ui.button(
                        'Skip All Duplicates',
                        on_click=lambda: self.set_all_resolutions(duplicate_resolutions, analysis['duplicates'], 'skip', duplicate_dialog, json_content, analysis),
                        icon='cancel'
                    ).classes('bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg')

                    ui.button(
                        'Overwrite All Duplicates',
                        on_click=lambda: self.set_all_resolutions(duplicate_resolutions, analysis['duplicates'], 'overwrite', duplicate_dialog, json_content, analysis),
                        icon='swap_horiz'
                    ).classes('bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg')

                    ui.button(
                        'Merge All Duplicates',
                        on_click=lambda: self.set_all_resolutions(duplicate_resolutions, analysis['duplicates'], 'merge', duplicate_dialog, json_content, analysis),
                        icon='merge_type'
                    ).classes('bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg')

                ui.separator().classes('mb-4')
                ui.label('Review Individual Duplicates:').classes('text-h6 mb-4')

                # Scrollable area for individual duplicates
                with ui.scroll_area().classes('w-full flex-1'):
                    self.create_duplicate_comparison_cards(analysis['duplicates'], duplicate_resolutions)

                # Bottom action bar
                with ui.row().classes('w-full justify-between mt-6 pt-4 border-t'):
                    ui.button(
                        'Cancel Import',
                        on_click=duplicate_dialog.close,
                        icon='cancel'
                    ).classes('bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg')

                    ui.button(
                        'Proceed with Import',
                        on_click=lambda: self.finalize_import_with_resolutions(duplicate_dialog, json_content, duplicate_resolutions, analysis),
                        icon='upload'
                    ).classes('bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg')

        duplicate_dialog.open()

    def create_duplicate_comparison_cards(self, duplicates: list, resolutions: dict):
        """Create comparison cards for each duplicate"""
        for i, duplicate in enumerate(duplicates):
            cologne_key = f"{duplicate['name']}|{duplicate['brand']}"

            with ui.card().classes('w-full mb-4 border-2 border-orange-200 dark:border-orange-700'):
                with ui.card_section().classes('p-4'):
                    # Header with cologne name
                    with ui.row().classes('items-center justify-between mb-4'):
                        ui.label(f"{duplicate['name']} - {duplicate['brand']}").classes('text-h6 font-bold')
                        if duplicate['conflicts']:
                            ui.badge(f"{len(duplicate['conflicts'])} conflicts", color='orange').classes('text-xs')

                    # Side-by-side comparison
                    with ui.row().classes('w-full gap-6'):
                        # Existing data column
                        with ui.column().classes('flex-1'):
                            ui.label('📦 Your Current Data').classes('text-subtitle1 font-semibold text-blue-600 mb-2')

                            with ui.card().classes('bg-blue-50 dark:bg-blue-900 border border-blue-200'):
                                with ui.card_section().classes('p-3'):
                                    existing = duplicate['existing']

                                    if existing['notes']:
                                        ui.label('Notes:').classes('font-medium text-xs text-gray-700 dark:text-gray-300')
                                        ui.label(', '.join(existing['notes'])).classes('text-sm mb-2')
                                    else:
                                        ui.label('Notes: None').classes('text-sm text-gray-500 mb-2')

                                    if existing['classifications']:
                                        ui.label('Classifications:').classes('font-medium text-xs text-gray-700 dark:text-gray-300')
                                        ui.label(', '.join(existing['classifications'])).classes('text-sm mb-2')
                                    else:
                                        ui.label('Classifications: None').classes('text-sm text-gray-500 mb-2')

                                    ui.label(f"Wear History: {existing['wear_history_count']} records").classes('text-sm font-medium')

                        # New data column
                        with ui.column().classes('flex-1'):
                            ui.label('📥 Incoming Data').classes('text-subtitle1 font-semibold text-green-600 mb-2')

                            with ui.card().classes('bg-green-50 dark:bg-green-900 border border-green-200'):
                                with ui.card_section().classes('p-3'):
                                    incoming = duplicate['incoming']

                                    if incoming['notes']:
                                        ui.label('Notes:').classes('font-medium text-xs text-gray-700 dark:text-gray-300')
                                        ui.label(', '.join(incoming['notes'])).classes('text-sm mb-2')
                                    else:
                                        ui.label('Notes: None').classes('text-sm text-gray-500 mb-2')

                                    if incoming['classifications']:
                                        ui.label('Classifications:').classes('font-medium text-xs text-gray-700 dark:text-gray-300')
                                        ui.label(', '.join(incoming['classifications'])).classes('text-sm mb-2')
                                    else:
                                        ui.label('Classifications: None').classes('text-sm text-gray-500 mb-2')

                                    ui.label(f"Wear History: {incoming['wear_history_count']} records").classes('text-sm font-medium')

                    # Action buttons for this duplicate
                    with ui.row().classes('justify-center gap-3 mt-4 pt-3 border-t'):
                        ui.button(
                            'Keep Current',
                            on_click=lambda e, key=cologne_key: self.set_resolution(resolutions, key, 'skip'),
                            icon='cancel'
                        ).classes('bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm')

                        ui.button(
                            'Use New Data',
                            on_click=lambda e, key=cologne_key: self.set_resolution(resolutions, key, 'overwrite'),
                            icon='swap_horiz'
                        ).classes('bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded text-sm')

                        ui.button(
                            'Merge Both',
                            on_click=lambda e, key=cologne_key: self.set_resolution(resolutions, key, 'merge'),
                            icon='merge_type'
                        ).classes('bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded text-sm')

                    # Show current selection
                    current_resolution = resolutions.get(cologne_key, 'skip')
                    resolution_text = {
                        'skip': 'Will keep current data',
                        'overwrite': 'Will use new data',
                        'merge': 'Will merge both datasets'
                    }
                    ui.label(f"Current selection: {resolution_text[current_resolution]}").classes('text-xs text-center mt-2 font-medium')

    def set_resolution(self, resolutions: Dict[str, str], cologne_key: str, resolution: str):
        """Set resolution for a specific cologne"""
        resolutions[cologne_key] = resolution
        ui.notify(f'Set to {resolution}', type='info')

    def set_all_resolutions(self, resolutions: Dict[str, str], duplicates: List[Dict[str, Any]], resolution: str, dialog: Any, json_content: str, analysis: Optional[Dict[str, Any]] = None):
        """Set the same resolution for all duplicates"""
        for duplicate in duplicates:
            cologne_key = f"{duplicate['name']}|{duplicate['brand']}"
            resolutions[cologne_key] = resolution

        # Close dialog and proceed
        dialog.close()
        self.proceed_with_import(json_content, resolutions, analysis)

    def finalize_import_with_resolutions(self, dialog: Any, json_content: str, resolutions: Dict[str, str], analysis: Optional[Dict[str, Any]] = None):
        """Finalize import with user-selected resolutions"""
        dialog.close()
        self.proceed_with_import(json_content, resolutions, analysis)

    def proceed_with_import(self, json_content: str, resolutions: Dict[str, str], analysis: Optional[Dict[str, Any]] = None):
        """Execute the actual import with resolved duplicates"""
        try:
            result = self.db.import_from_json(json_content, resolutions)

            # Log the import transaction
            self.db.log_import_transaction(
                import_type='json',
                result=result,
                filename='imported_file.json',  # Could be enhanced to capture actual filename
                resolutions=resolutions,
                analysis=analysis
            )

            if result["success"]:
                # Trigger refresh of other components (this will need to be handled via callbacks)
                if hasattr(self, '_on_data_change'):
                    self._on_data_change()

                # Show enhanced success dialog
                self.show_import_results_dialog(result)

            else:
                ui.notify(f'Import failed: {result["error"]}', type='negative')

        except Exception as ex:
            ui.notify(f'Error during import: {str(ex)}', type='negative')

    def show_import_results_dialog(self, result: dict):
        """Show detailed import results in a dialog"""
        with ui.dialog() as results_dialog, ui.card():
            ui.label('✅ Import Completed Successfully!').classes('text-h5 mb-4 text-center text-green-600')

            # Summary stats
            with ui.card().classes('w-full mb-4 bg-green-50 dark:bg-green-900'):
                with ui.card_section().classes('p-4'):
                    ui.label('Import Summary').classes('text-h6 font-bold mb-3')

                    stats = [
                        (result.get('colognes_added', 0), 'New colognes added', 'add_circle', 'text-green-600'),
                        (result.get('colognes_updated', 0), 'Colognes updated', 'update', 'text-blue-600'),
                        (result.get('wear_history_added', 0), 'Wear records added', 'event', 'text-purple-600'),
                        (len(result.get('errors', [])), 'Items with errors', 'error', 'text-red-600')
                    ]

                    for count, label, icon, color_class in stats:
                        if count > 0 or label == 'Items with errors':
                            with ui.row().classes('items-center gap-2 mb-2'):
                                ui.icon(icon).classes(f'text-lg {color_class}')
                                ui.label(f'{count} {label}').classes('text-sm')

            # Show errors if any
            if result.get("errors"):
                with ui.expansion('View Errors/Warnings', icon='warning').classes('w-full'):
                    for error in result["errors"]:
                        ui.label(f'• {error}').classes('text-sm text-orange-600 dark:text-orange-400 mb-1')

            # Close button
            with ui.row().classes('w-full justify-center mt-4'):
                ui.button('Close', on_click=results_dialog.close).classes('bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg')

        results_dialog.open()

    def show_import_details(self, import_record):
        """Show detailed information about a specific import"""
        with ui.dialog() as details_dialog, ui.card():
            ui.label(f'Import Details - {import_record.timestamp.strftime("%B %d, %Y at %I:%M %p")}').classes('text-h6 mb-4')

            with ui.row().classes('w-full gap-6'):
                # Left column - Basic info
                with ui.column().classes('flex-1'):
                    ui.label('Import Information').classes('text-subtitle1 font-semibold mb-3')

                    info_items = [
                        ('Type', import_record.import_type.upper()),
                        ('Filename', import_record.filename or 'Unknown'),
                        ('Status', import_record.status.title()),
                        ('Timestamp', import_record.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                    ]

                    for label, value in info_items:
                        with ui.row().classes('mb-2'):
                            ui.label(f'{label}:').classes('font-medium text-gray-700 dark:text-gray-300 w-20')
                            ui.label(str(value)).classes('text-gray-600 dark:text-gray-400')

                # Right column - Statistics
                with ui.column().classes('flex-1'):
                    ui.label('Import Statistics').classes('text-subtitle1 font-semibold mb-3')

                    with ui.grid(columns=2).classes('gap-2'):
                        stats = [
                            ('Colognes Added', import_record.colognes_added, 'text-green-600'),
                            ('Colognes Updated', import_record.colognes_updated, 'text-blue-600'),
                            ('Wear Records', import_record.wear_history_added, 'text-purple-600'),
                            ('Duplicates Found', import_record.duplicates_found, 'text-orange-600'),
                            ('Errors/Warnings', import_record.errors_count, 'text-red-600')
                        ]

                        for label, count, color in stats:
                            with ui.card().classes('p-3 text-center'):
                                ui.label(str(count)).classes(f'text-xl font-bold {color}')
                                ui.label(label).classes('text-xs text-gray-600 dark:text-gray-400')

            # Resolutions applied (if any)
            if import_record.resolutions_applied:
                ui.separator().classes('my-4')
                ui.label('Duplicate Resolutions Applied').classes('text-subtitle1 font-semibold mb-2')

                try:
                    resolutions = json.loads(import_record.resolutions_applied)
                    if resolutions:
                        with ui.scroll_area().classes('h-32'):
                            for cologne_key, resolution in resolutions.items():
                                parts = cologne_key.split('|')
                                name = parts[0] if len(parts) > 0 else 'Unknown'
                                brand = parts[1] if len(parts) > 1 else 'Unknown'
                                resolution_text = {
                                    'skip': 'Kept existing data',
                                    'overwrite': 'Replaced with new data',
                                    'merge': 'Merged both datasets'
                                }.get(resolution, resolution or 'Unknown action')

                                with ui.row().classes('mb-1 text-sm'):
                                    ui.label(f'{name} ({brand}):').classes('font-medium')
                                    ui.label(resolution_text).classes('text-gray-600 dark:text-gray-400 ml-2')
                    else:
                        ui.label('No duplicate resolutions were needed').classes('text-gray-500 text-sm')
                except:
                    ui.label('Resolution data could not be parsed').classes('text-red-500 text-sm')

            # Notes section
            if import_record.notes:
                ui.separator().classes('my-4')
                ui.label('Notes').classes('text-subtitle1 font-semibold mb-2')
                ui.label(import_record.notes).classes('text-sm text-gray-600 dark:text-gray-400')

            # Close button
            with ui.row().classes('w-full justify-end mt-6'):
                ui.button('Close', on_click=details_dialog.close).classes('bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded')

        details_dialog.open()

    def show_import_errors(self, import_record):
        """Show errors/warnings from a specific import"""
        with ui.dialog() as errors_dialog, ui.card():
            ui.label(f'Import Errors/Warnings - {import_record.timestamp.strftime("%m/%d/%Y %H:%M")}').classes('text-h6 mb-4')

            try:
                errors = json.loads(import_record.error_log) if import_record.error_log else []

                if errors:
                    ui.label(f'Found {len(errors)} issues during import:').classes('text-sm text-gray-600 mb-4')

                    with ui.scroll_area().classes('h-64 w-full'):
                        for i, error in enumerate(errors, 1):
                            with ui.row().classes('mb-3 p-3 bg-orange-50 dark:bg-orange-900 rounded border-l-4 border-orange-400'):
                                ui.label(f'{i}.').classes('font-bold text-orange-600 w-6')
                                ui.label(error).classes('text-sm text-gray-700 dark:text-gray-300 flex-1')
                else:
                    ui.label('No errors or warnings recorded for this import').classes('text-green-600 text-center p-4')

            except:
                ui.label('Error log could not be parsed').classes('text-red-500 text-center p-4')

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Close', on_click=errors_dialog.close).classes('bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded')

        errors_dialog.open()

    def set_data_change_callback(self, callback):
        """Set callback to be called when data changes (for refreshing other tabs)"""
        self._on_data_change = callback