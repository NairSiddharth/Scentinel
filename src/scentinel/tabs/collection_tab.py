#!/usr/bin/env python3
"""
CollectionTab class for managing cologne collection and wear logging.
"""
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
        self.recommendation_card = None
        self.search_input = None
        self.data_change_callback = None

    def set_data_change_callback(self, callback):
        """Set callback for when collection data changes"""
        self.data_change_callback = callback

    def setup_tab_content(self, container):
        """Setup the collection tab UI within the provided container"""
        self.container = container

        with container:
            with ui.row().classes('w-full gap-6 p-6'):
                # Left column - Collection table
                with ui.column().classes('flex-1'):
                    ui.label('Your Cologne Collection').classes(
                        'text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4'
                    )
                    self.search_input = ui.input('Search colognes...', on_change=self.filter_colognes).classes(
                        'w-full mb-4 px-4 py-3 border border-gray-300 dark:border-gray-600 '
                        'rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent '
                        'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 '
                        'placeholder-gray-500 dark:placeholder-gray-400 smooth-transition'
                    )

                    # CSV upload uses settings_tab if available
                    if self.settings_tab:
                        ui.upload(on_upload=self.settings_tab.handle_csv_upload, multiple=False).props('flat accept=".csv"').classes(
                            'mb-4 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 '
                            'rounded-lg px-4 py-2 text-blue-700 dark:text-blue-300 hover:bg-blue-100 '
                            'dark:hover:bg-blue-800 smooth-transition'
                        ).tooltip('Upload CSV with columns: name, brand, notes (semicolon separated), classifications (semicolon separated)')

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
                            ui.label('Today\'s Recommendation').classes(
                                'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4'
                            )
                            with ui.row().classes('w-full gap-2 mb-4'):
                                ui.button('Regenerate', on_click=self.refresh_recommendation).classes(
                                    'bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 '
                                    'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                                ).props('size=sm')
                                ui.button('Custom', on_click=self.show_custom_recommendation_dialog).classes(
                                    'border border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900 '
                                    'font-medium px-4 py-2 rounded-lg smooth-transition hover-lift'
                                ).props('size=sm outline')
                            self.recommendation_card = ui.column().classes('w-full')
                            self.refresh_recommendation()

    def refresh_cologne_table(self, search_term: str = ''):
        """Refresh the cologne table with optional search filtering"""
        if not self.cologne_table_container:
            return

        self.cologne_table_container.clear()

        try:
            # Use get_colognes and filter manually if needed
            colognes = self.db.get_colognes()
            if search_term:
                colognes = [c for c in colognes if search_term.lower() in (c.name or '').lower() or search_term.lower() in (c.brand or '').lower()]

            if not colognes:
                with self.cologne_table_container:
                    ui.label('No colognes found. Add some to get started!').classes(
                        'text-gray-500 dark:text-gray-400 text-center p-8'
                    )
                    ui.button('Add Your First Cologne',
                              on_click=self.show_add_cologne_dialog,
                              icon='add').classes(
                        'bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 '
                        'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift mx-auto'
                    )
                return

            with self.cologne_table_container:
                # Action buttons
                with ui.row().classes('w-full justify-between items-center p-4 bg-gray-50 dark:bg-gray-700'):
                    ui.label(f'Showing {len(colognes)} cologne(s)').classes(
                        'text-sm text-gray-600 dark:text-gray-300'
                    )
                    ui.button('Add Cologne',
                              on_click=self.show_add_cologne_dialog,
                              icon='add').classes(
                        'bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 '
                        'rounded-lg shadow-sm hover:shadow-md smooth-transition hover-lift'
                    )

                # Table headers
                with ui.row().classes('w-full p-4 bg-gray-100 dark:bg-gray-600 font-semibold text-gray-800 dark:text-gray-200'):
                    ui.label('Name').classes('flex-1')
                    ui.label('Brand').classes('flex-1')
                    ui.label('Notes').classes('flex-1')
                    ui.label('Wears').classes('w-20 text-center')
                    ui.label('Actions').classes('w-32 text-center')

                # Cologne rows
                for cologne in colognes:
                    # Count wears using get_wear_history
                    wear_count = len(self.db.get_wear_history(getattr(cologne, 'id', None)))

                    with ui.row().classes(
                        'w-full p-4 border-b border-gray-200 dark:border-gray-600 '
                        'hover:bg-gray-50 dark:hover:bg-gray-700 smooth-transition items-center'
                    ):
                        name_val = getattr(cologne, 'name', None)
                        brand_val = getattr(cologne, 'brand', None)
                        ui.label(str(name_val) if name_val else 'Unknown').classes('flex-1 font-medium text-gray-900 dark:text-gray-100')
                        ui.label(str(brand_val) if brand_val else 'Unknown').classes('flex-1 text-gray-700 dark:text-gray-300')

                        # Notes with truncation
                        notes_text = ', '.join([getattr(n, 'name', str(n)) for n in getattr(cologne, 'notes', [])]) if getattr(cologne, 'notes', None) else 'No notes'
                        if len(notes_text) > 50:
                            notes_text = notes_text[:47] + '...'
                        ui.label(notes_text).classes('flex-1 text-sm text-gray-600 dark:text-gray-400')

                        ui.label(str(wear_count)).classes('w-20 text-center text-gray-800 dark:text-gray-200')

                        with ui.row().classes('w-32 gap-1 justify-center'):
                            ui.button(icon='event',
                                      on_click=lambda c=cologne: self.show_log_wear_dialog(getattr(c, 'id', None))).classes(
                                'bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-md smooth-transition'
                            ).tooltip(f'Log wear for {getattr(cologne, "name", "")}').props('size=sm')
                            ui.button(icon='flash_on',
                                      on_click=lambda c=cologne: self.quick_log_wear(getattr(c, 'id', None))).classes(
                                'bg-green-500 hover:bg-green-600 text-white p-2 rounded-md smooth-transition'
                            ).tooltip(f'Quick wear log for {getattr(cologne, "name", "")}').props('size=sm')

        except Exception as e:
            with self.cologne_table_container:
                ui.label(f'Error loading colognes: {str(e)}').classes('text-red-500 p-4')

    def filter_colognes(self):
        """Filter colognes based on search input"""
        if self.search_input:
            search_term = self.search_input.value or ''
            self.refresh_cologne_table(search_term)

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

    def add_cologne(self, dialog: Any, name: Optional[str], brand: Optional[str],
                    notes_str: Optional[str], classifications_str: Optional[str]):
        """Add a new cologne to the collection"""
        if not name or not brand:
            ui.notify('Name and brand are required', type='warning')
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
            ui.notify(f'Error adding cologne: {str(e)}', type='negative')

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
        try:
            # Only log if all required fields are present
            if cologne_id is not None and season and occasion:
                self.db.log_wear(cologne_id, season, occasion, rating)
                self.refresh_recent_wears()
                self.refresh_recommendation()

                # Notify data change callback if set
                if self.data_change_callback:
                    self.data_change_callback()

                dialog.close()
                ui.notify('Wear logged successfully!', type='positive')
            else:
                ui.notify('Missing required fields for logging wear.', type='warning')
        except Exception as e:
            ui.notify(f'Error logging wear: {str(e)}', type='negative')

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
                                name_val = getattr(cologne, 'name', None)
                                brand_val = getattr(cologne, 'brand', None)
                                ui.label(str(name_val) if name_val else '').classes('font-semibold text-gray-800 dark:text-gray-200')
                                ui.label(f"by {brand_val}" if brand_val else '').classes('text-sm text-gray-600 dark:text-gray-400')
                                with ui.row().classes('w-full justify-between items-center mt-2'):
                                    season_val = getattr(wear, 'season', '')
                                    occasion_val = getattr(wear, 'occasion', '')
                                    ui.label(f"{str(season_val).title()}, {str(occasion_val).title()}").classes(
                                        'text-xs text-gray-500 dark:text-gray-500'
                                    )
                                    rating_val = getattr(wear, 'rating', None)
                                    if rating_val is not None:
                                        try:
                                            stars = int(float(rating_val))
                                            ui.label('★' * stars).classes('text-yellow-500')
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
            # Use get_recommendations and pick the first
            recs = self.db.get_recommendations()
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
                else:
                    ui.label('No recommendations found').classes('text-gray-500 dark:text-gray-400')

        except Exception as e:
            with self.recommendation_card:
                ui.label(f'Error loading recommendation: {str(e)}').classes('text-red-500 text-sm')

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