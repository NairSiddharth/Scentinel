#!/usr/bin/env python3
"""
CollectionTab class for managing cologne collection and wear logging.
"""
import os
from datetime import datetime
from typing import Any, Optional
from nicegui import ui

from .base_tab import BaseTab


class CollectionTab(BaseTab):
    """Tab for managing cologne collection and wear logging"""

    def __init__(self, database, settings_tab=None):
        super().__init__(database)
        self.settings_tab = settings_tab
        self.cologne_table_container = None
        self.recent_wears_container = None
        self.recent_recommendations = []  # Track last 3 recommendations
        self.recommendation_card = None
        self.data_change_callback = None
        self.selected_cologne_id = None  # Track selected cologne in grid

    def set_data_change_callback(self, callback):
        """Set callback for when collection data changes"""
        self.data_change_callback = callback

    def setup_tab_content(self, container):
        """Setup the collection tab UI within the provided container"""
        self.container = container

        with container:
            with ui.row().classes('w-full gap-6 p-6 pb-24'):
                # Left column - Collection table
                with ui.column().classes('flex-1'):
                    ui.label('Your Cologne Collection').classes(
                        'text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4'
                    )

                    self.cologne_table_container = ui.column().classes(
                        'w-full bg-white dark:bg-gray-800 rounded-xl shadow-lg border '
                        'border-gray-200 dark:border-gray-700 overflow-hidden smooth-transition'
                    )
                    self.refresh_cologne_table()

                with ui.column().classes('w-96 gap-6'):
                    # Recent Wears Card
                    with ui.card().classes(
                        'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                        'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                    ):
                        with ui.card_section().classes('p-6'):
                            ui.label('Recent Wears').classes(
                                'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4'
                            )
                            self.recent_wears_container = ui.column().classes('w-full gap-3')
                            self.refresh_recent_wears()

                    # Recommendation Card
                    with ui.card().classes(
                        'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                        'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                    ):
                        with ui.card_section().classes('p-6'):
                            with ui.row().classes('w-full items-center justify-between mb-4'):
                                ui.label('Today\'s Recommendation').classes(
                                    'text-xl font-semibold text-gray-800 dark:text-gray-200'
                                )
                                with ui.button(icon='help_outline').props('flat round size=sm').classes(
                                    'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                                ):
                                    ui.tooltip('Recommendations based on:\n'
                                              '• Wear history & ratings\n'
                                              '• Seasonal patterns\n'
                                              '• Similar fragrances\n'
                                              '• Recently neglected bottles\n'
                                              '• System learns from your usage!')
                            with ui.row().classes('w-full gap-2 mb-4'):
                                ui.button('Regenerate', on_click=self.refresh_recommendation).classes(
                                    'bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 '
                                    'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                                ).props('size=sm').tooltip('Get a new recommendation (requires wear history data)')
                                ui.button('Custom', on_click=self.show_custom_recommendation_dialog).classes(
                                    'border border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900 '
                                    'font-medium px-4 py-2 rounded-lg smooth-transition hover-lift'
                                ).props('size=sm outline')
                            self.recommendation_card = ui.column().classes('w-full')
                            self.refresh_recommendation()

    def refresh_cologne_table(self):
        """Refresh the cologne table with ag-grid"""
        if not self.cologne_table_container:
            return

        self.cologne_table_container.clear()

        try:
            # Get all colognes - filtering now handled by AG-Grid mini-filters
            colognes = self.db.get_colognes()

            if not colognes:
                with self.cologne_table_container:
                    with ui.column().classes('items-center w-full py-12 px-8'):
                        ui.label('No colognes found. Add some to get started!').classes(
                            'text-gray-500 dark:text-gray-400 text-center mb-6'
                        )
                        ui.button('Add Your First Cologne',
                                  on_click=self.show_add_cologne_dialog,
                                  icon='add').classes(
                            'bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 '
                            'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                        )
                return

            # Prepare data for ag-grid
            rows = []
            for cologne in colognes:
                cologne_id = getattr(cologne, 'id', None)
                wear_count = len(self.db.get_wear_history(cologne_id))
                notes_list = getattr(cologne, 'notes', [])
                notes_text = ', '.join([getattr(n, 'name', str(n)) for n in notes_list]) if notes_list else 'No notes'

                rows.append({
                    'id': cologne_id,
                    'name': getattr(cologne, 'name', 'Unknown'),
                    'brand': getattr(cologne, 'brand', 'Unknown'),
                    'notes': notes_text,
                    'wears': wear_count
                })

            # Column definitions
            columns = [
                {'field': 'name', 'headerName': 'Name', 'sortable': True, 'filter': True, 'resizable': True, 'flex': 1.5},
                {'field': 'brand', 'headerName': 'Brand', 'sortable': True, 'filter': True, 'resizable': True, 'flex': 1.5},
                {'field': 'notes', 'headerName': 'Notes', 'sortable': True, 'filter': True, 'resizable': True, 'flex': 2,
                 'tooltipField': 'notes', 'cellRenderer': 'agTooltipCellRenderer'},
                {'field': 'wears', 'headerName': 'Wears', 'sortable': True, 'width': 100, 'type': 'numericColumn'},
            ]

            with self.cologne_table_container:
                # Action buttons row
                with ui.row().classes('w-full justify-between items-center p-4 bg-gray-50 dark:bg-gray-700'):
                    # Left side - count and stacked action buttons
                    with ui.row().classes('items-center gap-4'):
                        ui.label(f'Showing {len(colognes)} cologne(s)').classes(
                            'text-sm text-gray-600 dark:text-gray-300'
                        )

                        # Stacked Log buttons to match right side design
                        with ui.column().classes('gap-1'):
                            ui.button('Log Wear', icon='event',
                                      on_click=self.show_log_wear_from_grid).classes(
                                'bg-blue-500 hover:bg-blue-600 text-white font-medium px-2 py-1 '
                                'rounded-lg shadow-sm hover:shadow-md smooth-transition hover-lift text-xs'
                            ).style('height: 21px; width: 100px; font-size: 10px;').tooltip('Select a cologne and log a wear')

                            ui.button('Quick Log', icon='flash_on',
                                      on_click=self.quick_log_from_grid).classes(
                                'bg-green-500 hover:bg-green-600 text-white font-medium px-2 py-1 '
                                'rounded-lg shadow-sm hover:shadow-md smooth-transition hover-lift text-xs'
                            ).style('height: 21px; width: 100px; font-size: 10px;').tooltip('Select a cologne and quick log a wear')

                    # Right side - add and import buttons
                    with ui.row().classes('items-center gap-2'):
                        # Bulk import button
                        if self.settings_tab:
                            with ui.element():
                                ui.upload(
                                    label="Bulk Import",
                                    on_upload=self.settings_tab.confirm_csv_upload,
                                    multiple=False
                                ).props('accept=".csv"').style('height: 44px;')
                                ui.tooltip('Upload CSV with columns:\n• name\n• brand\n• notes (semicolon separated)\n• classifications (semicolon separated)')

                        # Stacked Add/Remove buttons
                        with ui.column().classes('gap-1'):
                            ui.button('Add Cologne',
                                      on_click=self.show_add_cologne_dialog,
                                      icon='add').classes(
                                'bg-green-600 hover:bg-green-700 text-white font-medium px-2 py-1 '
                                'rounded-lg shadow-sm hover:shadow-md smooth-transition hover-lift text-xs'
                            ).style('height: 21px; width: 120px; font-size: 10px;')

                            ui.button('Remove Cologne',
                                      on_click=self.show_remove_cologne_dialog,
                                      icon='remove').classes(
                                'bg-red-600 hover:bg-red-700 text-white font-medium px-2 py-1 '
                                'rounded-lg shadow-sm hover:shadow-md smooth-transition hover-lift text-xs'
                            ).style('height: 21px; width: 120px; font-size: 10px;')

                # Ag-grid table
                self.selected_cologne_id = None  # Track selected cologne
                self.cologne_grid = ui.aggrid({
                    'columnDefs': columns,
                    'rowData': rows,
                    'defaultColDef': {
                        'sortable': True,
                        'filter': True,
                        'resizable': True,
                        'floatingFilter': True,  # Add mini-filters below headers
                    },
                    'domLayout': 'normal',
                    'pagination': True,
                    'paginationPageSize': 20,
                    'rowSelection': 'single',
                    'suppressRowClickSelection': False,  # Allow row selection by clicking
                }, html_columns=[0]).classes('w-full mb-20').style('height: 400px;')

                # Set up selection tracking - NiceGUI way
                self.cologne_grid.on('cellClicked', self._on_row_selected)

        except Exception as e:
            with self.cologne_table_container:
                ui.label(f'Error loading colognes: {str(e)}').classes('text-red-500 p-4')


    def _on_row_selected(self, event):
        """Handle row selection in ag-grid"""
        try:
            print(f"Row clicked event: {event}")  # Debug
            if hasattr(event, 'args'):
                print(f"Event args: {event.args}")  # Debug

                # Get the row data from the cellClicked event
                if 'data' in event.args:
                    row_data = event.args['data']
                    self.selected_cologne_id = row_data.get('id')
                    print(f"Selected cologne ID: {self.selected_cologne_id}")  # Debug
                    ui.notify(f'Selected: {row_data.get("name", "Unknown")}', type='info')
                else:
                    self.selected_cologne_id = None
                    print("No row data found")  # Debug
            else:
                self.selected_cologne_id = None
        except Exception as e:
            print(f"Selection error: {e}")  # Debug
            self.selected_cologne_id = None

    def show_log_wear_from_grid(self):
        """Show log wear dialog for selected cologne from grid"""
        print(f"Log wear clicked, selected ID: {self.selected_cologne_id}")  # Debug
        if self.selected_cologne_id:
            self.show_log_wear_dialog(self.selected_cologne_id)
        else:
            ui.notify('Please select a cologne from the table first', type='warning')

    def quick_log_from_grid(self):
        """Quick log wear for selected cologne from grid"""
        print(f"Quick log clicked, selected ID: {self.selected_cologne_id}")  # Debug
        if self.selected_cologne_id:
            self.quick_log_wear(self.selected_cologne_id)
        else:
            ui.notify('Please select a cologne from the table first', type='warning')


    def show_add_cologne_dialog(self):
        """Show dialog to add a new cologne"""
        with ui.dialog() as dialog, ui.card():
            ui.label('Add New Cologne').classes('text-h6 mb-4')

            name_input = ui.input('Cologne Name').classes('w-full mb-2')
            brand_input = ui.input('Brand').classes('w-full mb-2')
            notes_input = ui.input('Notes (comma separated)').classes('w-full mb-2')
            classifications_input = ui.input('Classifications (comma separated)').classes('w-full mb-4')

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Add Cologne',
                          on_click=lambda: self.add_cologne(
                              dialog, name_input.value, brand_input.value,
                              notes_input.value, classifications_input.value
                          )).classes('bg-green-600 hover:bg-green-700 text-white')

        dialog.open()

    def show_remove_cologne_dialog(self):
        """Show dialog to remove the selected cologne"""
        if not self.selected_cologne_id:
            ui.notify('Please select a cologne from the table first', type='warning')
            return

        # Get the selected cologne details
        from scentinel.database import Cologne
        cologne = self.db.session.query(Cologne).filter_by(id=self.selected_cologne_id).first()
        if not cologne:
            ui.notify('Selected cologne not found', type='warning')
            return

        with ui.dialog() as dialog, ui.card():
            ui.label('Remove Cologne from Collection').classes('text-h6 mb-4')
            ui.label(f'Are you sure you want to remove "{cologne.name}" by {cologne.brand}?').classes('mb-2')
            ui.label('This action cannot be undone and will remove all associated wear history.').classes('mb-4 text-red-600 text-sm')

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Remove Cologne',
                          on_click=lambda: self.remove_cologne(dialog, cologne)).classes('bg-red-600 hover:bg-red-700 text-white')

        dialog.open()

    def remove_cologne(self, dialog: Any, cologne):
        """Remove the selected cologne from the collection"""
        try:
            from scentinel.database import WearHistory

            # First, explicitly delete all wear history for this cologne
            wear_records = self.db.session.query(WearHistory).filter_by(cologne_id=cologne.id).all()
            for wear in wear_records:
                self.db.session.delete(wear)

            # Then delete the cologne
            self.db.session.delete(cologne)
            self.db.session.commit()

            # Clear selection
            self.selected_cologne_id = None

            # Refresh the table
            self.refresh_cologne_table()

            # Refresh recent wears to remove any that referenced this cologne
            self.refresh_recent_wears()

            # Notify data change callback if set
            if self.data_change_callback:
                self.data_change_callback()

            dialog.close()
            ui.notify(f'Removed "{cologne.name}" by {cologne.brand}', type='positive')

        except Exception as e:
            error_msg = str(e)
            ui.notify(f'Error removing cologne:\n{error_msg}', type='negative', multi_line=True)
            

    def add_cologne(self, dialog: Any, name: Optional[str], brand: Optional[str],
                    notes_str: Optional[str], classifications_str: Optional[str]):
        """Add a new cologne to the collection"""
        # Input validation
        if not name or not name.strip():
            ui.notify('Cologne name is required', type='warning')
            return
        if not brand or not brand.strip():
            ui.notify('Brand is required', type='warning')
            return

        # Sanitize inputs
        name = name.strip()[:100]  # Max 100 characters
        brand = brand.strip()[:100]  # Max 100 characters

        if len(name) < 2:
            ui.notify('Cologne name must be at least 2 characters', type='warning')
            return
        if len(brand) < 2:
            ui.notify('Brand must be at least 2 characters', type='warning')
            return

        # Validate notes and classifications format
        if notes_str and len(notes_str.strip()) > 500:
            ui.notify('Notes are too long (max 500 characters)', type='warning')
            return
        if classifications_str and len(classifications_str.strip()) > 200:
            ui.notify('Classifications are too long (max 200 characters)', type='warning')
            return

        try:
            # Parse notes and classifications
            notes = [n.strip() for n in (notes_str or '').split(',') if n.strip()] or None
            classifications = [c.strip() for c in (classifications_str or '').split(',') if c.strip()] or None

            self.db.add_cologne(name, brand, notes, classifications)
            self.refresh_cologne_table()

            # Notify data change callback if set
            if self.data_change_callback:
                self.data_change_callback()

            dialog.close()
            ui.notify(f'Added {name} by {brand}', type='positive')

        except Exception as e:
            error_msg = str(e)
            ui.notify(f'Error adding cologne:\n{error_msg}', type='negative', multi_line=True)

    def show_log_wear_dialog(self, cologne_id: Optional[int] = None):
        """Show dialog to log a wear for a specific cologne, or generic if cologne_id is None"""
        with ui.dialog() as dialog, ui.card():
            ui.label('Log Cologne Wear').classes('text-h6 mb-4')

            season_select = ui.select(['spring', 'summer', 'fall', 'winter'],
                                      label='Season', value='spring').classes('w-full mb-2')
            occasion_select = ui.select(['casual', 'work', 'formal', 'date', 'special'],
                                        label='Occasion', value='casual').classes('w-full mb-2')
            rating_input = ui.number('Rating (1-5)', value=4, min=1, max=5, step=1).classes('w-full mb-4')

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Log Wear',
                          on_click=lambda: self.log_wear(
                              dialog, cologne_id, season_select.value,
                              occasion_select.value, rating_input.value
                          )).classes('bg-blue-600 hover:bg-blue-700 text-white')

        dialog.open()

    def log_wear(self, dialog: Any, cologne_id: Optional[int], season: Optional[str],
                 occasion: Optional[str], rating: Optional[float]):
        """Log a wear for a cologne"""
        # Input validation
        if cologne_id is None:
            ui.notify('No cologne selected', type='warning')
            return

        if not season or season not in ['spring', 'summer', 'fall', 'winter']:
            ui.notify('Please select a valid season', type='warning')
            return

        if not occasion or occasion not in ['casual', 'work', 'formal', 'date', 'special']:
            ui.notify('Please select a valid occasion', type='warning')
            return

        if rating is None or not (1 <= rating <= 5):
            ui.notify('Rating must be between 1 and 5', type='warning')
            return

        try:
            self.db.log_wear(cologne_id, season, occasion, rating)
            self.refresh_recent_wears()
            self.refresh_recommendation()

            # Notify data change callback if set
            if self.data_change_callback:
                self.data_change_callback()

            dialog.close()
            ui.notify('Wear logged successfully!', type='positive')
        except Exception as e:
            error_msg = str(e)
            ui.notify(f'Error logging wear:\n{error_msg}', type='negative', multi_line=True)

    def quick_log_wear(self, cologne_id: Any):
        """Quick log wear with automatic season detection"""
        # Quick log with current season and casual occasion
        month = datetime.now().month
        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'fall'

        self.db.log_wear(cologne_id, season, 'casual')
        self.refresh_recent_wears()
        self.refresh_recommendation()

        # Notify data change callback if set
        if self.data_change_callback:
            self.data_change_callback()

        ui.notify('Wear logged!', type='positive')

    def refresh_recent_wears(self):
        """Refresh the recent wears section"""
        if not self.recent_wears_container:
            return

        self.recent_wears_container.clear()

        try:
            # Get all wears and show the 5 most recent
            all_wears = self.db.get_wear_history()
            recent_wears = all_wears[:5]

            if not recent_wears:
                with self.recent_wears_container:
                    ui.label('No wears logged yet').classes('text-gray-500 dark:text-gray-400 text-sm')
                return

            with self.recent_wears_container:
                for wear in recent_wears:
                    # Find cologne by id
                    cologne = next((c for c in self.db.get_colognes() if getattr(c, 'id', None) == getattr(wear, 'cologne_id', None)), None)
                    if cologne:
                        with ui.card().classes(
                            'w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 '
                            'dark:border-gray-600 hover:shadow-md smooth-transition hover-lift'
                        ):
                            with ui.card_section().classes('p-3'):
                                with ui.column().classes('w-full'):
                                        name_val = getattr(cologne, 'name', None)
                                        brand_val = getattr(cologne, 'brand', None)
                                        ui.label(str(name_val) if name_val else '').classes('font-semibold text-gray-800 dark:text-gray-200')
                                        ui.label(f"by {brand_val}" if brand_val else '').classes('text-sm text-gray-600 dark:text-gray-400')
                                        with ui.row().classes('w-full justify-between items-center mt-1'):
                                            season_val = getattr(wear, 'season', '')
                                            occasion_val = getattr(wear, 'occasion', '')
                                            ui.label(f"{str(season_val).title()}, {str(occasion_val).title()}").classes(
                                                'text-xs text-gray-500 dark:text-gray-500'
                                            )
                                            rating_val = getattr(wear, 'rating', None)
                                            if rating_val is not None:
                                                try:
                                                    stars = int(float(rating_val))
                                                    ui.label('★' * stars).classes('text-yellow-500 text-sm')
                                                except Exception:
                                                    pass

        except Exception as e:
            with self.recent_wears_container:
                ui.label(f'Error loading recent wears: {str(e)}').classes('text-red-500 text-sm')

    def refresh_recommendation(self):
        """Refresh the recommendation section"""
        if not self.recommendation_card:
            return

        self.recommendation_card.clear()

        try:
            # Force rebuild of recommender to get fresh recommendations
            self.db._rebuild_recommender()
            recs = self.db.get_recommendations()

            # Filter out recently recommended colognes
            if recs and self.recent_recommendations:
                excluded_ids = [rec['id'] for rec in self.recent_recommendations]
                filtered_recs = [rec for rec in recs if getattr(rec, 'id', None) not in excluded_ids]
                recs = filtered_recs if filtered_recs else recs  # Fallback to original if all are filtered

            recommendation = recs[0] if recs else None

            with self.recommendation_card:
                if recommendation:
                    name_val = getattr(recommendation, 'name', None)
                    brand_val = getattr(recommendation, 'brand', None)
                    notes_val = getattr(recommendation, 'notes', None)
                    class_val = getattr(recommendation, 'classifications', None)
                    rec_id = getattr(recommendation, 'id', None)
                    with ui.card().classes(
                        'w-full bg-gradient-to-r from-blue-50 to-purple-50 '
                        'dark:from-blue-900 dark:to-purple-900 border-l-4 border-blue-500'
                    ):
                        with ui.card_section().classes('p-4'):
                            ui.label(str(name_val) if name_val else '').classes('text-lg font-bold text-gray-800 dark:text-gray-200')
                            ui.label(f'by {brand_val}' if brand_val else '').classes('text-gray-600 dark:text-gray-400 mb-2')

                            if notes_val:
                                ui.label(f'Notes: {", ".join([getattr(n, "name", str(n)) for n in notes_val])}').classes('text-sm text-gray-700 dark:text-gray-300 mb-2')

                            if class_val:
                                with ui.row().classes('gap-1 flex-wrap mb-2'):
                                    for classification in class_val:
                                        class_name = getattr(classification, 'name', str(classification))
                                        ui.badge(class_name).classes('bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200')

                            ui.button('Wear This',
                                      on_click=lambda: self.quick_log_wear(rec_id)).classes('mt-2')

                    # Track this recommendation
                    if recommendation:
                        self._track_recommendation(recommendation)
                else:
                    # Check if we have colognes but no wear history
                    colognes = self.db.get_colognes()
                    if colognes:
                        ui.label('Add some wear history to get personalized recommendations!').classes('text-amber-600 dark:text-amber-400 text-center')
                        ui.label('Click "Log Wear" on any cologne to start tracking.').classes('text-gray-500 dark:text-gray-400 text-sm text-center mt-2')
                    else:
                        ui.label('Add some colognes to your collection first!').classes('text-gray-500 dark:text-gray-400 text-center')
                        ui.button('Add Cologne', on_click=self.show_add_cologne_dialog).classes('mt-2 bg-blue-600 text-white')

        except Exception as e:
            with self.recommendation_card:
                ui.label(f'Error loading recommendation: {str(e)}').classes('text-red-500 text-sm')

    def _track_recommendation(self, recommendation):
        """Track a recommendation to prevent immediate duplicates"""
        rec_id = getattr(recommendation, 'id', None)
        rec_name = getattr(recommendation, 'name', None)

        if rec_id and rec_name:
            # Add to recent recommendations
            rec_data = {'id': rec_id, 'name': rec_name}

            # Remove if already exists (to update position)
            self.recent_recommendations = [r for r in self.recent_recommendations if r['id'] != rec_id]

            # Add to front
            self.recent_recommendations.insert(0, rec_data)

            # Keep only last 3
            if len(self.recent_recommendations) > 3:
                self.recent_recommendations = self.recent_recommendations[:3]

    def show_custom_recommendation_dialog(self):
        """Show dialog for custom recommendation preferences"""
        with ui.dialog() as dialog, ui.card():
            ui.label('Custom Recommendation').classes('text-h6 mb-4')

            season_select = ui.select(['spring', 'summer', 'fall', 'winter'],
                                      label='Preferred Season').classes('w-full mb-2')
            occasion_select = ui.select(['casual', 'work', 'formal', 'date', 'special'],
                                        label='Occasion').classes('w-full mb-4')

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Get Recommendation',
                          on_click=lambda: self.get_custom_recommendation(
                              dialog, season_select.value, occasion_select.value
                          )).classes('bg-blue-600 hover:bg-blue-700 text-white')

        dialog.open()

    def get_custom_recommendation(self, dialog: Any, season: Optional[str], occasion: Optional[str]):
        """Get a custom recommendation based on preferences"""
        try:
            recs = self.db.get_recommendations(season=season, occasion=occasion)
            recommendation = recs[0] if recs else None
            dialog.close()

            if recommendation:
                if self.recommendation_card:
                    self.recommendation_card.clear()
                    name_val = getattr(recommendation, 'name', None)
                    brand_val = getattr(recommendation, 'brand', None)
                    notes_val = getattr(recommendation, 'notes', None)
                    class_val = getattr(recommendation, 'classifications', None)
                    rec_id = getattr(recommendation, 'id', None)
                    with self.recommendation_card:
                        with ui.card().classes(
                            'w-full bg-gradient-to-r from-green-50 to-blue-50 '
                            'dark:from-green-900 dark:to-blue-900 border-l-4 border-green-500'
                        ):
                            with ui.card_section().classes('p-4'):
                                ui.label('Custom Recommendation').classes('text-sm font-semibold text-green-600 dark:text-green-400 mb-1')
                                ui.label(str(name_val) if name_val else '').classes('text-lg font-bold text-gray-800 dark:text-gray-200')
                                ui.label(f'by {brand_val}' if brand_val else '').classes('text-gray-600 dark:text-gray-400 mb-2')

                                if notes_val:
                                    ui.label(f'Notes: {", ".join([getattr(n, "name", str(n)) for n in notes_val])}').classes('text-sm text-gray-700 dark:text-gray-300 mb-2')

                                if class_val:
                                    with ui.row().classes('gap-1 flex-wrap mb-2'):
                                        for classification in class_val:
                                            class_text = getattr(classification, 'name', str(classification)).replace('_', ' ').title()
                                            ui.badge(class_text).classes('bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200')

                                ui.button('Wear This',
                                          on_click=lambda: self.quick_log_wear(rec_id)).classes('mt-2')
                    ui.notify(f'Custom recommendation: {name_val}', type='positive')
            else:
                ui.notify('No recommendations found for those criteria', type='warning')

        except Exception as e:
            ui.notify(f'Error getting custom recommendation: {str(e)}', type='negative')
            dialog.close()

    def refresh_data(self):
        """Refresh all tab data"""
        self.refresh_cologne_table()
        self.refresh_recent_wears()
        self.refresh_recommendation()