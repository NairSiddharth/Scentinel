from sqlalchemy import create_engine, Column, Integer, String, DateTime, Table, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
from collections import Counter
from sqlalchemy import func, extract
from .recommender import CologneRecommender
from .photo_api import PhotoAPI

Base = declarative_base()

# Many-to-many association tables
cologne_notes = Table(
    'cologne_notes',
    Base.metadata,
    Column('cologne_id', Integer, ForeignKey('colognes.id'), primary_key=True),
    Column('note_id', Integer, ForeignKey('fragrance_notes.id'), primary_key=True)
)

cologne_classifications = Table(
    'cologne_classifications', 
    Base.metadata,
    Column('cologne_id', Integer, ForeignKey('colognes.id'), primary_key=True),
    Column('classification_id', Integer, ForeignKey('scent_classifications.id'), primary_key=True)
)

class Cologne(Base):
    __tablename__ = 'colognes'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    image_path = Column(String, nullable=True)  # Local image file path
    image_source = Column(String, nullable=True)  # online, placeholder, user_upload

    # Relationships
    wear_history = relationship("WearHistory", back_populates="cologne")
    notes = relationship("FragranceNote", secondary=cologne_notes, back_populates="colognes")
    classifications = relationship("ScentClassification", secondary=cologne_classifications, back_populates="colognes")

class WearHistory(Base):
    __tablename__ = 'wear_history'
    
    id = Column(Integer, primary_key=True)
    cologne_id = Column(Integer, ForeignKey('colognes.id'), nullable=False)
    date_worn = Column(DateTime, default=datetime.now)
    season = Column(String, nullable=False)  # spring, summer, fall, winter
    occasion = Column(String, nullable=False)  # casual, work, date, formal, etc.
    rating = Column(Float)  # 1-5 star rating
    
    # Relationship
    cologne = relationship("Cologne", back_populates="wear_history")

class FragranceNote(Base):
    __tablename__ = 'fragrance_notes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # bergamot, sandalwood, etc.
    category = Column(String)  # top, middle, base
    
    # Relationship
    colognes = relationship("Cologne", secondary=cologne_notes, back_populates="notes")

class ScentClassification(Base):
    __tablename__ = 'scent_classifications'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # freshie, aquatic, gourmand, etc.
    description = Column(String)  # optional description

    # Relationship
    colognes = relationship("Cologne", secondary=cologne_classifications, back_populates="classifications")

class ImportHistory(Base):
    __tablename__ = 'import_history'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    import_type = Column(String, nullable=False)  # 'json', 'csv'
    filename = Column(String)  # original filename if available

    # Import statistics
    colognes_added = Column(Integer, default=0)
    colognes_updated = Column(Integer, default=0)
    wear_history_added = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)

    # Resolution summary (for duplicates)
    resolutions_applied = Column(String)  # JSON string of resolutions

    # Error/warning log
    error_log = Column(String)  # JSON string of errors/warnings

    # Status
    status = Column(String, default='completed')  # 'completed', 'failed', 'partial'

    # User notes (optional)
    notes = Column(String)

class Database:
    def __init__(self, db_name: str | None = None):
        import os
        if db_name is None:
            # Always resolve path from project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_name = os.path.join(base_dir, 'data', 'scentinel.db')
        else:
            db_name = os.path.abspath(db_name)
        self.engine = create_engine(f'sqlite:///{db_name}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.recommender = CologneRecommender()
        self.photo_api = PhotoAPI()
        self._rebuild_recommender()

    def add_cologne(self, name: str, brand: str, notes: Optional[List[str]] = None, classifications: Optional[List[str]] = None, fetch_image: bool = True) -> Cologne:
        cologne = Cologne(name=name, brand=brand)

        # Add notes if provided
        if notes:
            for note_name in notes:
                note = self.session.query(FragranceNote).filter_by(name=note_name).first()
                if not note:
                    note = FragranceNote(name=note_name)
                    self.session.add(note)
                cologne.notes.append(note)

        # Add classifications if provided
        if classifications:
            for class_name in classifications:
                classification = self.session.query(ScentClassification).filter_by(name=class_name).first()
                if not classification:
                    classification = ScentClassification(name=class_name)
                    self.session.add(classification)
                cologne.classifications.append(classification)

        # Fetch image if requested
        if fetch_image:
            self._fetch_cologne_image(cologne)
        
        self.session.add(cologne)
        self.session.commit()
        self._rebuild_recommender()  # Update recommender with new cologne
        return cologne

    def log_wear(self, cologne_id: int, season: str, occasion: str, rating: Optional[float] = None) -> WearHistory:
        wear = WearHistory(
            cologne_id=cologne_id,
            season=season,
            occasion=occasion,
            rating=rating
        )
        self.session.add(wear)
        self.session.commit()
        self._rebuild_recommender()  # Update recommender with new wear data
        return wear

    def get_colognes(self) -> List[Cologne]:
        return self.session.query(Cologne).all()

    def get_wear_history(self, cologne_id: Optional[int] = None) -> List[WearHistory]:
        query = self.session.query(WearHistory)
        if cologne_id:
            query = query.filter(WearHistory.cologne_id == cologne_id)
        return query.order_by(WearHistory.date_worn.desc()).all()

    def get_recommendations(self, season: Optional[str] = None, occasion: Optional[str] = None, 
                          recommendation_type: str = "hybrid") -> List[Cologne]:
        """Get cologne recommendations using ML-based recommender"""
        if recommendation_type == "hybrid":
            recommendations = self.recommender.get_hybrid_recommendations(
                season=season, occasion=occasion, n_recommendations=5
            )
        elif recommendation_type == "seasonal":
            recommendations = self.recommender.get_seasonal_recommendations(n_recommendations=5)
        elif recommendation_type == "discovery":
            recommendations = self.recommender.get_discovery_recommendations(n_recommendations=5)
        elif recommendation_type == "behavioral":
            recommendations = self.recommender.get_behavioral_recommendations(
                season=season, occasion=occasion, n_recommendations=5
            )
        else:
            # Fallback to hybrid
            recommendations = self.recommender.get_hybrid_recommendations(
                season=season, occasion=occasion, n_recommendations=5
            )
        
        # Convert cologne IDs back to Cologne objects
        cologne_ids = [rec[0] for rec in recommendations]
        if not cologne_ids:
            return []
        
        colognes = self.session.query(Cologne).filter(Cologne.id.in_(cologne_ids)).all()
        
        # Sort colognes by the recommendation order
        # Create mapping using actual ID values
        cologne_map = {}
        for cologne in colognes:
            # Access the actual ID value from the database object
            actual_id = cologne.__dict__.get('id', None)
            if actual_id is not None:
                cologne_map[actual_id] = cologne
        
        ordered_colognes = []
        for cologne_id, score in recommendations:
            if cologne_id in cologne_map:
                ordered_colognes.append(cologne_map[cologne_id])
        
        return ordered_colognes
    
    def get_content_recommendations(self, cologne_id: int) -> List[Cologne]:
        """Get recommendations based on cologne similarity"""
        recommendations = self.recommender.get_content_recommendations(cologne_id, n_recommendations=5)
        cologne_ids = [rec[0] for rec in recommendations]
        
        if not cologne_ids:
            return []
        
        colognes = self.session.query(Cologne).filter(Cologne.id.in_(cologne_ids)).all()
        
        # Sort by recommendation order
        # Create mapping using actual ID values
        cologne_map = {}
        for cologne in colognes:
            # Access the actual ID value from the database object
            actual_id = cologne.__dict__.get('id', None)
            if actual_id is not None:
                cologne_map[actual_id] = cologne
        
        ordered_colognes = []
        for cologne_id, score in recommendations:
            if cologne_id in cologne_map:
                ordered_colognes.append(cologne_map[cologne_id])
        
        return ordered_colognes
    
    def get_recommendation_explanations(self, season: Optional[str] = None, 
                                      occasion: Optional[str] = None) -> List[str]:
        """Get explanations for why colognes were recommended"""
        recommendations = self.recommender.get_hybrid_recommendations(
            season=season, occasion=occasion, n_recommendations=5
        )
        
        explanations = []
        for cologne_id, score in recommendations:
            explanation = self.recommender.get_recommendation_explanation(
                cologne_id, score, "hybrid"
            )
            explanations.append(explanation)
        
        return explanations
    
    def _fetch_cologne_image(self, cologne: Cologne) -> bool:
        """Fetch and store image for a cologne"""
        try:
            # Use getattr to get actual values from the instance
            cologne_name = str(getattr(cologne, 'name', '')) or ""
            cologne_brand = str(getattr(cologne, 'brand', '')) or ""

            success, result = self.photo_api.get_cologne_image(cologne_name, cologne_brand)
            if success:
                setattr(cologne, 'image_path', result)
                setattr(cologne, 'image_source', "online" if "placeholder" not in result else "placeholder")
                return True
            else:
                print(f"Failed to fetch image for {cologne_name}: {result}")
                return False
        except Exception as e:
            print(f"Error fetching image for {getattr(cologne, 'name', '')}: {e}")
            return False

    def get_cologne_image_path(self, cologne_id: int) -> Optional[str]:
        """Get the local image path for a cologne"""
        cologne = self.session.query(Cologne).get(cologne_id)
        return cologne.image_path if cologne and cologne.image_path else None

    def refresh_cologne_image(self, cologne_id: int) -> bool:
        """Force refresh image for a specific cologne"""
        cologne = self.session.query(Cologne).get(cologne_id)
        if not cologne:
            return False

        try:
            success, result = self.photo_api.get_cologne_image(cologne.name, cologne.brand, force_refresh=True)
            if success:
                cologne.image_path = result
                cologne.image_source = "online" if not result.endswith("placeholder") else "placeholder"
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error refreshing image for {cologne.name}: {e}")
            return False

    def get_photo_stats(self) -> Dict[str, Any]:
        """Get photo collection statistics"""
        return self.photo_api.get_storage_stats()

    def cleanup_old_images(self, days_old: int = 90) -> int:
        """Clean up old cached images"""
        return self.photo_api.cleanup_old_images(days_old)

    def _rebuild_recommender(self):
        """Rebuild the recommender with current data"""
        colognes = self.get_colognes()
        wear_history = self.get_wear_history()
        self.recommender.build_features(colognes, wear_history)

    def export_to_json(self) -> str:
        """Export entire database to JSON format"""
        export_data = {
            "export_date": datetime.now().isoformat(),
            "version": "1.0",
            "colognes": []
        }

        colognes = self.get_colognes()
        for cologne in colognes:
            cologne_data = {
                "id": cologne.id,
                "name": str(cologne.name),
                "brand": str(cologne.brand),
                "notes": [str(note.name) for note in cologne.notes],
                "classifications": [str(classification.name) for classification in cologne.classifications],
                "wear_history": []
            }

            # Get wear history for this cologne
            wear_history = self.session.query(WearHistory).filter_by(cologne_id=cologne.id).order_by(WearHistory.date_worn.desc()).all()
            for wear in wear_history:
                wear_data = {
                    "date": wear.date_worn.isoformat(),
                    "season": str(wear.season),
                    "occasion": str(wear.occasion),
                    "rating": wear.rating
                }
                cologne_data["wear_history"].append(wear_data)

            export_data["colognes"].append(cologne_data)

        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def analyze_import_data(self, json_data: str) -> Dict[str, Any]:
        """Analyze import data and identify duplicates without importing"""
        try:
            data = json.loads(json_data)

            if "colognes" not in data:
                return {"success": False, "error": "Invalid JSON format: missing 'colognes' key"}

            analysis = {
                "success": True,
                "new_colognes": [],
                "duplicates": [],
                "errors": []
            }

            for cologne_data in data["colognes"]:
                try:
                    # Skip empty entries
                    if not cologne_data.get("name") or not cologne_data.get("brand"):
                        continue

                    # Check if cologne already exists
                    existing_cologne = self.session.query(Cologne).filter_by(
                        name=cologne_data["name"],
                        brand=cologne_data["brand"]
                    ).first()

                    if existing_cologne:
                        # Analyze conflicts
                        conflicts = []

                        # Compare notes
                        existing_notes = set(note.name for note in existing_cologne.notes)
                        incoming_notes = set(cologne_data.get("notes", []))
                        if existing_notes != incoming_notes:
                            conflicts.append("notes")

                        # Compare classifications
                        existing_classifications = set(c.name for c in existing_cologne.classifications)
                        incoming_classifications = set(cologne_data.get("classifications", []))
                        if existing_classifications != incoming_classifications:
                            conflicts.append("classifications")

                        # Compare wear history
                        existing_wear_count = len(existing_cologne.wear_history)
                        incoming_wear_count = len(cologne_data.get("wear_history", []))
                        if incoming_wear_count > 0:
                            conflicts.append("wear_history")

                        # Create duplicate entry with full data comparison
                        duplicate_entry = {
                            "name": cologne_data["name"],
                            "brand": cologne_data["brand"],
                            "conflicts": conflicts,
                            "existing": {
                                "id": existing_cologne.id,
                                "notes": list(existing_notes),
                                "classifications": list(existing_classifications),
                                "wear_history_count": existing_wear_count
                            },
                            "incoming": {
                                "notes": list(incoming_notes),
                                "classifications": list(incoming_classifications),
                                "wear_history": cologne_data.get("wear_history", []),
                                "wear_history_count": incoming_wear_count
                            }
                        }
                        analysis["duplicates"].append(duplicate_entry)
                    else:
                        # New cologne
                        analysis["new_colognes"].append({
                            "name": cologne_data["name"],
                            "brand": cologne_data["brand"],
                            "notes": cologne_data.get("notes", []),
                            "classifications": cologne_data.get("classifications", []),
                            "wear_history_count": len(cologne_data.get("wear_history", []))
                        })

                except Exception as e:
                    analysis["errors"].append(f"Error analyzing cologne '{cologne_data.get('name', 'Unknown')}': {str(e)}")

            return analysis

        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON format: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Analysis failed: {str(e)}"}

    def import_from_json(self, json_data: str, duplicate_resolutions: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Import data from JSON format with optional duplicate resolution"""
        try:
            data = json.loads(json_data)

            if "colognes" not in data:
                return {"success": False, "error": "Invalid JSON format: missing 'colognes' key"}

            stats = {
                "colognes_added": 0,
                "colognes_updated": 0,
                "wear_history_added": 0,
                "errors": []
            }

            # If no duplicate resolutions provided, use the old behavior for backward compatibility
            if duplicate_resolutions is None:
                duplicate_resolutions = {}

            for cologne_data in data["colognes"]:
                try:
                    # Skip empty entries
                    if not cologne_data.get("name") or not cologne_data.get("brand"):
                        continue

                    cologne_key = f"{cologne_data['name']}|{cologne_data['brand']}"

                    # Check if cologne already exists
                    existing_cologne = self.session.query(Cologne).filter_by(
                        name=cologne_data["name"],
                        brand=cologne_data["brand"]
                    ).first()

                    if existing_cologne:
                        # Handle duplicate based on resolution
                        resolution = duplicate_resolutions.get(cologne_key, "skip")

                        if resolution == "skip":
                            stats["errors"].append(f"Cologne '{cologne_data['name']}' by {cologne_data['brand']} already exists, skipping")
                            continue
                        elif resolution == "overwrite":
                            # Update existing cologne
                            self._update_cologne(existing_cologne, cologne_data, stats)
                            stats["colognes_updated"] += 1
                        elif resolution == "merge":
                            # Merge data (add new wear history, combine notes)
                            self._merge_cologne_data(existing_cologne, cologne_data, stats)
                            stats["colognes_updated"] += 1
                    else:
                        # Create new cologne
                        cologne = self.add_cologne(
                            name=cologne_data["name"],
                            brand=cologne_data["brand"],
                            notes=cologne_data.get("notes"),
                            classifications=cologne_data.get("classifications")
                        )
                        stats["colognes_added"] += 1

                        # Import wear history
                        self._import_wear_history(cologne, cologne_data, stats)

                except Exception as e:
                    stats["errors"].append(f"Error importing cologne '{cologne_data.get('name', 'Unknown')}': {str(e)}")

            # Commit all changes
            self.session.commit()
            self._rebuild_recommender()

            stats["success"] = True
            return stats

        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON format: {str(e)}"}
        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": f"Import failed: {str(e)}"}

    def _update_cologne(self, existing_cologne: Cologne, cologne_data: dict, stats: dict):
        """Update existing cologne with new data"""
        # Clear existing notes and classifications
        existing_cologne.notes.clear()
        existing_cologne.classifications.clear()

        # Add new notes
        if cologne_data.get("notes"):
            for note_name in cologne_data["notes"]:
                note = self.session.query(FragranceNote).filter_by(name=note_name).first()
                if not note:
                    note = FragranceNote(name=note_name)
                    self.session.add(note)
                existing_cologne.notes.append(note)

        # Add new classifications
        if cologne_data.get("classifications"):
            for class_name in cologne_data["classifications"]:
                classification = self.session.query(ScentClassification).filter_by(name=class_name).first()
                if not classification:
                    classification = ScentClassification(name=class_name)
                    self.session.add(classification)
                existing_cologne.classifications.append(classification)

        # Replace wear history
        for wear in existing_cologne.wear_history:
            self.session.delete(wear)

        self._import_wear_history(existing_cologne, cologne_data, stats)

    def _merge_cologne_data(self, existing_cologne: Cologne, cologne_data: dict, stats: dict):
        """Merge new data with existing cologne"""
        # Combine notes (add new ones, keep existing)
        existing_notes = set(note.name for note in existing_cologne.notes)
        new_notes = set(cologne_data.get("notes", []))

        for note_name in new_notes - existing_notes:
            note = self.session.query(FragranceNote).filter_by(name=note_name).first()
            if not note:
                note = FragranceNote(name=note_name)
                self.session.add(note)
            existing_cologne.notes.append(note)

        # Combine classifications
        existing_classifications = set(c.name for c in existing_cologne.classifications)
        new_classifications = set(cologne_data.get("classifications", []))

        for class_name in new_classifications - existing_classifications:
            classification = self.session.query(ScentClassification).filter_by(name=class_name).first()
            if not classification:
                classification = ScentClassification(name=class_name)
                self.session.add(classification)
            existing_cologne.classifications.append(classification)

        # Add new wear history (keep existing)
        self._import_wear_history(existing_cologne, cologne_data, stats)

    def _import_wear_history(self, cologne: Cologne, cologne_data: dict, stats: dict):
        """Import wear history for a cologne"""
        if "wear_history" in cologne_data:
            for wear_data in cologne_data["wear_history"]:
                try:
                    # Parse the date
                    wear_date = datetime.fromisoformat(wear_data["date"].replace('Z', '+00:00'))

                    wear = WearHistory(
                        cologne_id=cologne.id,
                        date_worn=wear_date,
                        season=wear_data["season"],
                        occasion=wear_data["occasion"],
                        rating=wear_data.get("rating")
                    )
                    self.session.add(wear)
                    stats["wear_history_added"] += 1

                except Exception as e:
                    stats["errors"].append(f"Error importing wear history for {cologne_data['name']}: {str(e)}")

    def get_analytics_data(self) -> Dict[str, Any]:
        """Get comprehensive analytics data for dashboard"""
        analytics = {}

        # Wear frequency over time
        analytics['wear_timeline'] = self._get_wear_timeline()

        # Top fragrances by wear count
        analytics['top_fragrances'] = self._get_top_fragrances()

        # Seasonal preferences
        analytics['seasonal_breakdown'] = self._get_seasonal_breakdown()

        # Rating analysis
        analytics['rating_stats'] = self._get_rating_stats()

        # Brand analysis
        analytics['brand_stats'] = self._get_brand_stats()

        # Note preferences
        analytics['note_preferences'] = self._get_note_preferences()

        # Collection overview
        analytics['collection_overview'] = self._get_collection_overview()

        # Wear frequency insights
        analytics['wear_frequency_insights'] = self._get_wear_frequency_insights()

        # Seasonal deep dive
        analytics['seasonal_deep_dive'] = self._get_seasonal_deep_dive()

        return analytics

    def _get_wear_timeline(self) -> Dict[str, Any]:
        """Get wear frequency over time (monthly)"""
        wear_history = self.session.query(
            extract('year', WearHistory.date_worn).label('year'),
            extract('month', WearHistory.date_worn).label('month'),
            func.count(WearHistory.id).label('count')
        ).group_by(
            extract('year', WearHistory.date_worn),
            extract('month', WearHistory.date_worn)
        ).order_by(
            extract('year', WearHistory.date_worn),
            extract('month', WearHistory.date_worn)
        ).all()

        return {
            'dates': [f"{int(row.year)}-{int(row.month):02d}" for row in wear_history],
            'counts': [row.count for row in wear_history]
        }

    def _get_top_fragrances(self, limit: int = 10) -> Dict[str, Any]:
        """Get most worn fragrances"""
        top_colognes = self.session.query(
            Cologne.name,
            Cologne.brand,
            func.count(WearHistory.id).label('wear_count'),
            func.avg(WearHistory.rating).label('avg_rating')
        ).join(WearHistory).group_by(
            Cologne.id, Cologne.name, Cologne.brand
        ).order_by(func.count(WearHistory.id).desc()).limit(limit).all()

        return {
            'names': [f"{row.name} ({row.brand})" for row in top_colognes],
            'wear_counts': [row.wear_count for row in top_colognes],
            'avg_ratings': [float(row.avg_rating) if row.avg_rating else 0 for row in top_colognes]
        }

    def _get_seasonal_breakdown(self) -> Dict[str, Any]:
        """Get wear count by season"""
        seasonal_data = self.session.query(
            WearHistory.season,
            func.count(WearHistory.id).label('count')
        ).group_by(WearHistory.season).all()

        return {
            'seasons': [row.season.title() for row in seasonal_data],
            'counts': [row.count for row in seasonal_data]
        }

    def _get_rating_stats(self) -> Dict[str, Any]:
        """Get rating distribution and trends"""
        # Rating distribution
        rating_dist = self.session.query(
            WearHistory.rating,
            func.count(WearHistory.id).label('count')
        ).filter(WearHistory.rating.isnot(None)).group_by(
            WearHistory.rating
        ).order_by(WearHistory.rating).all()

        # Overall stats
        rating_stats = self.session.query(
            func.avg(WearHistory.rating).label('avg'),
            func.min(WearHistory.rating).label('min'),
            func.max(WearHistory.rating).label('max'),
            func.count(WearHistory.rating).label('total_rated')
        ).filter(WearHistory.rating.isnot(None)).first()

        # Handle case where no ratings exist
        if rating_stats is None:
            stats = {
                'average': 0,
                'min': 0,
                'max': 0,
                'total_rated': 0
            }
        else:
            stats = {
                'average': float(rating_stats.avg) if rating_stats.avg else 0,
                'min': float(rating_stats.min) if rating_stats.min else 0,
                'max': float(rating_stats.max) if rating_stats.max else 0,
                'total_rated': rating_stats.total_rated
            }

        return {
            'distribution': {
                'ratings': [float(row.rating) for row in rating_dist],
                'counts': [row.count for row in rating_dist]
            },
            'stats': stats
        }

    def _get_brand_stats(self, limit: int = 10) -> Dict[str, Any]:
        """Get brand usage statistics"""
        brand_stats = self.session.query(
            Cologne.brand,
            func.count(WearHistory.id).label('wear_count'),
            func.count(func.distinct(Cologne.id)).label('cologne_count')
        ).join(WearHistory).group_by(
            Cologne.brand
        ).order_by(func.count(WearHistory.id).desc()).limit(limit).all()

        return {
            'brands': [row.brand for row in brand_stats],
            'wear_counts': [row.wear_count for row in brand_stats],
            'cologne_counts': [row.cologne_count for row in brand_stats]
        }

    def _get_note_preferences(self, limit: int = 15) -> Dict[str, Any]:
        """Get most worn fragrance notes"""
        # This requires joining through the many-to-many relationship
        note_stats = self.session.query(
            FragranceNote.name,
            func.count(WearHistory.id).label('wear_count')
        ).join(cologne_notes, FragranceNote.id == cologne_notes.c.note_id
        ).join(Cologne, cologne_notes.c.cologne_id == Cologne.id
        ).join(WearHistory, Cologne.id == WearHistory.cologne_id
        ).group_by(FragranceNote.name
        ).order_by(func.count(WearHistory.id).desc()).limit(limit).all()

        return {
            'notes': [row.name for row in note_stats],
            'wear_counts': [row.wear_count for row in note_stats]
        }

    def _get_collection_overview(self) -> Dict[str, Any]:
        """Get overall collection statistics"""
        total_colognes = self.session.query(func.count(Cologne.id)).scalar()
        total_wears = self.session.query(func.count(WearHistory.id)).scalar()

        # Recent activity (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_wears = self.session.query(func.count(WearHistory.id)).filter(
            WearHistory.date_worn >= thirty_days_ago
        ).scalar()

        # Never worn colognes
        never_worn = self.session.query(func.count(Cologne.id)).outerjoin(
            WearHistory
        ).filter(WearHistory.id.is_(None)).scalar()

        return {
            'total_colognes': total_colognes or 0,
            'total_wears': total_wears or 0,
            'recent_wears_30d': recent_wears or 0,
            'never_worn': never_worn or 0,
            'usage_rate': round((total_colognes - never_worn) / total_colognes * 100, 1) if total_colognes > 0 else 0
        }

    def _get_wear_frequency_insights(self) -> Dict[str, Any]:
        """Get insights about wear frequency patterns"""
        current_date = datetime.now()

        # Get all colognes with their wear stats
        cologne_stats = self.session.query(
            Cologne.id,
            Cologne.name,
            Cologne.brand,
            func.count(WearHistory.id).label('total_wears'),
            func.max(WearHistory.date_worn).label('last_worn'),
            func.avg(WearHistory.rating).label('avg_rating')
        ).outerjoin(WearHistory).group_by(Cologne.id, Cologne.name, Cologne.brand).all()

        neglected = []  # Haven't worn in 30+ days
        overused = []   # Worn 5+ times in last 30 days
        balanced = []   # Good rotation
        never_worn = []

        thirty_days_ago = current_date - timedelta(days=30)

        for stat in cologne_stats:
            if stat.total_wears == 0:
                never_worn.append({
                    'name': str(stat.name),
                    'brand': str(stat.brand),
                    'days_since_worn': 'Never'
                })
            else:
                days_since = (current_date - stat.last_worn).days if stat.last_worn else float('inf')

                # Get recent wears (last 30 days)
                recent_wears = self.session.query(func.count(WearHistory.id)).filter(
                    WearHistory.cologne_id == stat.id,
                    WearHistory.date_worn >= thirty_days_ago
                ).scalar()

                cologne_data = {
                    'name': str(stat.name),
                    'brand': str(stat.brand),
                    'total_wears': stat.total_wears,
                    'days_since_worn': days_since,
                    'recent_wears': recent_wears,
                    'avg_rating': float(stat.avg_rating) if stat.avg_rating else 0
                }

                if days_since >= 30:
                    neglected.append(cologne_data)
                elif recent_wears >= 5:
                    overused.append(cologne_data)
                else:
                    balanced.append(cologne_data)

        # Sort lists by relevance
        neglected.sort(key=lambda x: x['days_since_worn'], reverse=True)
        overused.sort(key=lambda x: x['recent_wears'], reverse=True)
        balanced.sort(key=lambda x: x['avg_rating'], reverse=True)

        return {
            'neglected': neglected[:10],  # Top 10 most neglected
            'overused': overused[:5],     # Top 5 overused
            'balanced': balanced[:10],    # Top 10 well-rotated
            'never_worn': never_worn,
            'summary': {
                'total_neglected': len(neglected),
                'total_overused': len(overused),
                'total_balanced': len(balanced),
                'total_never_worn': len(never_worn)
            }
        }

    def _get_seasonal_deep_dive(self) -> Dict[str, Any]:
        """Get detailed seasonal analysis"""
        current_date = datetime.now()
        current_year = current_date.year

        # Get wear data by season and month for current year
        seasonal_data = self.session.query(
            extract('month', WearHistory.date_worn).label('month'),
            WearHistory.season,
            func.count(WearHistory.id).label('wear_count'),
            func.count(func.distinct(WearHistory.cologne_id)).label('unique_colognes')
        ).filter(
            extract('year', WearHistory.date_worn) == current_year
        ).group_by(
            extract('month', WearHistory.date_worn),
            WearHistory.season
        ).all()

        # Organize by season
        seasons = {
            'spring': {'months': [3, 4, 5], 'wears': 0, 'unique_colognes': set(), 'monthly_breakdown': {}},
            'summer': {'months': [6, 7, 8], 'wears': 0, 'unique_colognes': set(), 'monthly_breakdown': {}},
            'fall': {'months': [9, 10, 11], 'wears': 0, 'unique_colognes': set(), 'monthly_breakdown': {}},
            'winter': {'months': [12, 1, 2], 'wears': 0, 'unique_colognes': set(), 'monthly_breakdown': {}}
        }

        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

        # Process seasonal data
        for row in seasonal_data:
            season = str(row.season).lower()
            if season in seasons:
                seasons[season]['wears'] += row.wear_count
                seasons[season]['monthly_breakdown'][month_names[int(row.month)]] = row.wear_count

        # Get top colognes by season
        seasonal_favorites = {}
        for season in seasons.keys():
            top_colognes = self.session.query(
                Cologne.name,
                Cologne.brand,
                func.count(WearHistory.id).label('wears'),
                func.avg(WearHistory.rating).label('avg_rating')
            ).join(WearHistory).filter(
                WearHistory.season == season,
                extract('year', WearHistory.date_worn) == current_year
            ).group_by(Cologne.id, Cologne.name, Cologne.brand
            ).order_by(func.count(WearHistory.id).desc()).limit(5).all()

            seasonal_favorites[season] = [
                {
                    'name': str(c.name),
                    'brand': str(c.brand),
                    'wears': c.wears,
                    'avg_rating': float(c.avg_rating) if c.avg_rating else 0
                }
                for c in top_colognes
            ]

        # Calculate diversity scores (unique colognes / total wears)
        diversity_scores = {}
        for season, data in seasons.items():
            if data['wears'] > 0:
                unique_count = len(set(
                    self.session.query(WearHistory.cologne_id).filter(
                        WearHistory.season == season,
                        extract('year', WearHistory.date_worn) == current_year
                    ).all()
                ))
                diversity_scores[season] = round(unique_count / data['wears'], 2)
            else:
                diversity_scores[season] = 0

        return {
            'seasonal_breakdown': {
                season: {
                    'total_wears': data['wears'],
                    'monthly_breakdown': data['monthly_breakdown'],
                    'diversity_score': diversity_scores[season]
                }
                for season, data in seasons.items()
            },
            'seasonal_favorites': seasonal_favorites,
            'insights': {
                'most_active_season': max(seasons.keys(), key=lambda x: seasons[x]['wears']) if any(s['wears'] > 0 for s in seasons.values()) else None,
                'most_diverse_season': max(diversity_scores.keys(), key=lambda x: diversity_scores[x]) if any(diversity_scores.values()) else None,
                'year': current_year
            }
        }

    def get_similar_fragrances(self, cologne_id: int, limit: int = 5) -> List[Tuple[int, str, str, float]]:
        """Get fragrances similar to the given cologne based on notes and classifications"""
        target_cologne = self.session.query(Cologne).filter_by(id=cologne_id).first()
        if not target_cologne:
            return []

        # Get target cologne's notes and classifications
        target_notes = set(note.name for note in target_cologne.notes)
        target_classifications = set(classification.name for classification in target_cologne.classifications)

        # Get all other colognes
        other_colognes = self.session.query(Cologne).filter(Cologne.id != cologne_id).all()

        similarities = []
        for cologne in other_colognes:
            cologne_notes = set(note.name for note in cologne.notes)
            cologne_classifications = set(classification.name for classification in cologne.classifications)

            # Calculate similarity score
            note_similarity = len(target_notes & cologne_notes) / max(len(target_notes | cologne_notes), 1)
            classification_similarity = len(target_classifications & cologne_classifications) / max(len(target_classifications | cologne_classifications), 1)

            # Weight notes more heavily than classifications
            overall_similarity = (note_similarity * 0.7) + (classification_similarity * 0.3)

            if overall_similarity > 0:
                similarities.append((cologne.id, str(cologne.name), str(cologne.brand), overall_similarity))

        # Sort by similarity score and return top results
        similarities.sort(key=lambda x: x[3], reverse=True)
        return similarities[:limit]

    def get_rotation_suggestions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get suggestions for cologne rotation based on usage patterns"""
        current_date = datetime.now()
        thirty_days_ago = current_date - timedelta(days=30)

        # Get wear patterns for analysis
        cologne_patterns = self.session.query(
            Cologne.id,
            Cologne.name,
            Cologne.brand,
            func.count(WearHistory.id).label('total_wears'),
            func.max(WearHistory.date_worn).label('last_worn'),
            func.avg(WearHistory.rating).label('avg_rating')
        ).outerjoin(WearHistory).group_by(Cologne.id, Cologne.name, Cologne.brand).all()

        suggestions = []

        for pattern in cologne_patterns:
            cologne_id = pattern.id
            days_since_worn = (current_date - pattern.last_worn).days if pattern.last_worn else float('inf')
            avg_rating = float(pattern.avg_rating) if pattern.avg_rating else 0

            # Get recent wears (last 30 days)
            recent_wears = self.session.query(func.count(WearHistory.id)).filter(
                WearHistory.cologne_id == cologne_id,
                WearHistory.date_worn >= thirty_days_ago
            ).scalar()

            suggestion_reasons = []
            priority_score = 0

            # High-rated but neglected
            if avg_rating >= 4.0 and days_since_worn >= 14:
                suggestion_reasons.append(f"High-rated ({avg_rating:.1f}⭐) but not worn in {days_since_worn} days")
                priority_score += 3

            # Never worn or very rarely worn
            if pattern.total_wears == 0:
                suggestion_reasons.append("Never worn - time to try it!")
                priority_score += 5
            elif pattern.total_wears <= 2 and days_since_worn >= 7:
                suggestion_reasons.append("Rarely worn - good for variety")
                priority_score += 2

            # Seasonal appropriateness
            current_season = self._get_current_season()
            seasonal_wears = self.session.query(func.count(WearHistory.id)).filter(
                WearHistory.cologne_id == cologne_id,
                WearHistory.season == current_season
            ).scalar()

            if seasonal_wears > 0:
                suggestion_reasons.append(f"Great for {current_season}")
                priority_score += 1

            # Not overused recently
            if recent_wears < 3:
                priority_score += 1

            if suggestion_reasons and priority_score >= 2:
                suggestions.append({
                    'cologne_id': cologne_id,
                    'name': str(pattern.name),
                    'brand': str(pattern.brand),
                    'reasons': suggestion_reasons,
                    'priority_score': priority_score,
                    'days_since_worn': days_since_worn if days_since_worn != float('inf') else 'Never',
                    'avg_rating': avg_rating,
                    'total_wears': pattern.total_wears
                })

        # Sort by priority score and return top suggestions
        suggestions.sort(key=lambda x: x['priority_score'], reverse=True)
        return suggestions[:limit]

    def _get_current_season(self) -> str:
        """Helper method to get current season"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'

    def get_cologne_by_name_and_brand(self, name: str, brand: str) -> Optional[Cologne]:
        """Get cologne by name and brand"""
        return self.session.query(Cologne).filter_by(name=name, brand=brand).first()

    def add_wear_history(self, cologne_id: int, wear_date: datetime, rating: float,
                        season: str, occasion: str, notes: Optional[str] = None) -> WearHistory:
        """Add wear history entry"""
        wear = WearHistory(
            cologne_id=cologne_id,
            date_worn=wear_date,
            rating=rating,
            season=season,
            occasion=occasion
        )
        if hasattr(wear, 'notes') and notes:
            wear.notes = notes  # type: ignore

        self.session.add(wear)
        self.session.commit()
        self._rebuild_recommender()
        return wear

    def log_import_transaction(self, import_type: str, result: Dict[str, Any], filename: Optional[str] = None,
                              resolutions: Optional[Dict[str, str]] = None, analysis: Optional[Dict[str, Any]] = None) -> ImportHistory:
        """Log an import transaction for historical tracking"""
        import_log = ImportHistory(
            import_type=import_type,
            filename=filename,
            colognes_added=result.get('colognes_added', 0),
            colognes_updated=result.get('colognes_updated', 0),
            wear_history_added=result.get('wear_history_added', 0),
            duplicates_found=len(analysis.get('duplicates', [])) if analysis else 0,
            errors_count=len(result.get('errors', [])),
            resolutions_applied=json.dumps(resolutions) if resolutions else None,
            error_log=json.dumps(result.get('errors', [])),
            status='completed' if result.get('success') else 'failed'
        )

        self.session.add(import_log)
        self.session.commit()
        return import_log

    def get_import_history(self, limit: int = 50) -> List[ImportHistory]:
        """Get recent import history"""
        return self.session.query(ImportHistory).order_by(
            ImportHistory.timestamp.desc()
        ).limit(limit).all()

    def get_import_statistics(self) -> Dict[str, Any]:
        """Get overall import statistics"""
        total_imports = self.session.query(func.count(ImportHistory.id)).scalar()
        successful_imports = self.session.query(func.count(ImportHistory.id)).filter(
            ImportHistory.status == 'completed'
        ).scalar()

        total_colognes_imported = self.session.query(
            func.sum(ImportHistory.colognes_added)
        ).scalar() or 0

        total_duplicates_handled = self.session.query(
            func.sum(ImportHistory.duplicates_found)
        ).scalar() or 0

        # Recent imports (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_imports = self.session.query(func.count(ImportHistory.id)).filter(
            ImportHistory.timestamp >= thirty_days_ago
        ).scalar()

        return {
            'total_imports': total_imports or 0,
            'successful_imports': successful_imports or 0,
            'failed_imports': (total_imports or 0) - (successful_imports or 0),
            'total_colognes_imported': total_colognes_imported,
            'total_duplicates_handled': total_duplicates_handled,
            'recent_imports_30d': recent_imports or 0,
            'success_rate': round((successful_imports / total_imports * 100), 1) if total_imports > 0 else 0
        }

    def delete_import_log(self, import_id: int) -> bool:
        """Delete a specific import log entry"""
        import_log = self.session.query(ImportHistory).filter_by(id=import_id).first()
        if import_log:
            self.session.delete(import_log)
            self.session.commit()
            return True
        return False

    def add_import_notes(self, import_id: int, notes: str) -> bool:
        """Add notes to an import log entry"""
        import_log = self.session.query(ImportHistory).filter_by(id=import_id).first()
        if import_log:
            import_log.notes = notes  # type: ignore
            self.session.commit()
            return True
        return False

    def close(self):
        self.session.close()