import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class SportsPredictionService:
    """
    Service for analyzing sports events using astrological techniques.
    Predicts outcome based on multiple factors:
    1. Malefic planets in upachaya houses
    2. Shubha Kartari Yoga (SKY) - benefic planets flanking houses
    3. Papa Kartari Yoga (PKY) - malefic planets flanking houses
    4. Planetary strength (exaltation, debilitation, dig bala, retrograde)
    5. Cuspal strength - planets near house cusps
    """
    
    def __init__(self):
        # Malefic planets in Vedic/sidereal astrology
        self.malefic_planets = ["mars", "saturn", "rahu", "ketu", "sun"]
        
        # Strong malefics
        self.strong_malefics = ["mars", "saturn"]
        
        # Benefic planets in Vedic/sidereal astrology
        self.benefic_planets = ["jupiter", "venus", "mercury", "moon"]
        
        # Upachaya houses - favorable for malefic planets
        self.favorite_upachaya_houses = [1, 3, 6, 10, 11]  # for favorite/ascendant
        self.underdog_upachaya_houses = [7, 9, 12, 4, 5]   # for underdog/7th house
        
        # Primary cusps for favorite and underdog
        self.favorite_primary_cusps = [1, 4, 10]  # 1st, 4th, 10th houses
        self.underdog_primary_cusps = [7, 10, 4]  # 7th, 10th, 4th houses
        
        # Orb ranges for cuspal influence
        self.visible_planet_orb = 2.5  # 2°30' for visible planets
        self.invisible_planet_orb = 2.0  # 2° for invisible planets
        self.extra_special_orb = 1.0   # Extra strong influence if within 1°
        
        # Visible and invisible planets
        self.visible_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        self.invisible_planets = ["uranus", "neptune", "pluto", "chiron", "rahu", "ketu"]
        
        # Effects of planets on cusps (direct motion)
        self.cusp_effects = {
            "sun": {"effect": "negative", "description": "Burns up cusps it touches"},
            "moon": {"effect": "negative", "description": "Weakens energy, causes laziness"},
            "mars": {"effect": "mixed", "description": "Adds aggression on 6/12 axis, frustration on 4/10"},
            "jupiter": {"effect": "positive", "description": "Powerful benefic, boosts success for any cusp"},
            "saturn": {"effect": "mixed", "description": "Discipline on 4/10 and 6/12, slows teams on 1/7"},
            "venus": {"effect": "positive", "description": "Mild positive influence on all cusps"},
            "mercury": {"effect": "variable", "description": "Variable effects depending on house rulership"},
            "rahu": {"effect": "neutral", "description": "Adds ambition but with less force than visible planets"},
            "ketu": {"effect": "negative", "description": "Causes confusion and loss on all cusps"},
            "uranus": {"effect": "positive", "description": "Energizes cusps positively when direct"},
            "neptune": {"effect": "negative", "description": "Weakens teams due to lethargy when direct"},
            "pluto": {"effect": "mixed", "description": "Negative for favorites on 1/7, boosts underdogs on 4/10"},
            "chiron": {"effect": "positive", "description": "Provides strength and fighting spirit when direct"}
        }
        
        # Effects of planets on cusps when retrograde (if different from direct)
        self.retrograde_cusp_effects = {
            "jupiter": {"effect": "positive", "description": "Slightly stronger positive influence"},
            "saturn": {"effect": "positive", "description": "More empowering, especially on 4/10 and 6/12"},
            "venus": {"effect": "positive", "description": "Slightly more empowering due to retrograde motion"},
            "mercury": {"effect": "variable", "description": "Stronger but still variable based on rulership"},
            "uranus": {"effect": "negative", "description": "Becomes disruptive and destabilizing"},
            "neptune": {"effect": "positive", "description": "Reverses effect, inspires creativity and victory"},
            "chiron": {"effect": "negative", "description": "Causes injuries, penalties, or loss when retrograde"}
        }
        
        # Exaltation and debilitation signs
        self.exaltation_signs = {
            "sun": "Aries",
            "moon": "Taurus",
            "mercury": "Virgo",
            "venus": "Pisces",
            "mars": "Capricorn",
            "jupiter": "Cancer",
            "saturn": "Libra"
        }
        
        self.debilitation_signs = {
            "sun": "Libra",
            "moon": "Scorpio",
            "mercury": "Pisces",
            "venus": "Virgo",
            "mars": "Cancer",
            "jupiter": "Capricorn",
            "saturn": "Aries"
        }
        
        # Own signs
        self.own_signs = {
            "sun": ["Leo"],
            "moon": ["Cancer"],
            "mercury": ["Gemini", "Virgo"],
            "venus": ["Taurus", "Libra"],
            "mars": ["Aries", "Scorpio"],
            "jupiter": ["Sagittarius", "Pisces"],
            "saturn": ["Capricorn", "Aquarius"]
        }
        
        # Dig Bala (directional strength) houses
        self.dig_bala = {
            "sun": 10,
            "mars": 10,
            "jupiter": 1,
            "mercury": 1,
            "moon": 4,
            "venus": 4,
            "saturn": 7
        }

    def analyze_chart(self, chart_data: Dict[str, Any], favorite_name: str, 
                     underdog_name: str, event_name: str, event_date: str) -> Dict[str, Any]:
        """
        Analyze a chart for sports prediction using multiple astrological factors.
        
        Args:
            chart_data: The chart data JSON
            favorite_name: Name of the favorite/team 1
            underdog_name: Name of the underdog/team 2
            event_name: Name of the sports event
            event_date: Date of the event
            
        Returns:
            Dict containing prediction results
        """
        try:
            print(f"Chart data: {chart_data}")
            logger.info(f"Analyzing chart for {event_name}: {favorite_name} vs {underdog_name}")
            
            # Extract planets and houses data
            planets = chart_data.get("subject", {}).get("planets", {})
            houses = chart_data.get("subject", {}).get("houses", {})
            
            # Initialize analysis data structures
            favorite_malefic_count = 0
            underdog_malefic_count = 0
            
            favorite_planet_scores = []
            underdog_planet_scores = []
            
            # Track planet placements for reporting
            planet_placements = []
            favorite_placements = []
            underdog_placements = []
            
            # Check for SKY and PKY
            favorite_sky = self._check_sky(planets, 1)  # For favorite (1st house)
            underdog_sky = self._check_sky(planets, 7)  # For underdog (7th house)
            
            favorite_pky = self._check_pky(planets, 1)  # For favorite (1st house)
            underdog_pky = self._check_pky(planets, 7)  # For underdog (7th house)
            
            # Check for cuspal strengths
            favorite_cuspal = self._check_cuspal_strengths(planets, houses, self.favorite_primary_cusps)
            underdog_cuspal = self._check_cuspal_strengths(planets, houses, self.underdog_primary_cusps)
            
            # Add cuspal strength scores
            if favorite_cuspal["has_cuspal_influence"]:
                favorite_planet_scores.append({
                    "type": "cuspal_strength",
                    "score": favorite_cuspal["total_score"],
                    "influences": favorite_cuspal["influences"]
                })
            
            if underdog_cuspal["has_cuspal_influence"]:
                underdog_planet_scores.append({
                    "type": "cuspal_strength",
                    "score": underdog_cuspal["total_score"],
                    "influences": underdog_cuspal["influences"]
                })
            
            # Analyze each planet
            for planet_name, planet_data in planets.items():
                # Get planet house number
                house_num = self._get_house_number(planet_data.get("house", ""))
                
                if house_num is None:
                    continue
                
                # Get planet sign and determine strength
                planet_sign = planet_data.get("sign", "")
                is_retrograde = planet_data.get("isRetrograde", False)
                
                # Calculate planetary strength factors
                planet_strength = self._calculate_planet_strength(
                    planet_name, planet_sign, house_num, is_retrograde
                )
                
                # Determine if it's a malefic or benefic planet
                is_malefic = planet_name in self.malefic_planets
                is_benefic = planet_name in self.benefic_planets
                
                # Record placement details
                placement = {
                    "planet": planet_name,
                    "house": house_num,
                    "sign": planet_sign,
                    "is_malefic": is_malefic,
                    "is_benefic": is_benefic,
                    "is_retrograde": is_retrograde,
                    "strength": planet_strength
                }
                
                # Calculate impact for malefic planets in upachaya houses
                if is_malefic:
                    # Only count malefics for upachaya calculation
                    planet_placements.append(placement)
                    
                    # Calculate score based on strength and house placement
                    favorite_score = 0
                    underdog_score = 0
                    
                    # Check if in favorite's upachaya houses
                    if house_num in self.favorite_upachaya_houses:
                        favorite_malefic_count += 1
                        favorite_score = planet_strength
                        placement["favors"] = "favorite"
                        favorite_placements.append(placement.copy())
                    
                    # Check if in underdog's upachaya houses
                    if house_num in self.underdog_upachaya_houses:
                        underdog_malefic_count += 1
                        underdog_score = planet_strength
                        placement["favors"] = "underdog"
                        underdog_placements.append(placement.copy())
                    
                    # Add scores
                    if favorite_score > 0:
                        favorite_planet_scores.append({
                            "planet": planet_name,
                            "house": house_num,
                            "score": favorite_score,
                            "type": "malefic_in_upachaya"
                        })
                    
                    if underdog_score > 0:
                        underdog_planet_scores.append({
                            "planet": planet_name,
                            "house": house_num,
                            "score": underdog_score,
                            "type": "malefic_in_upachaya"
                        })
            
            # Add SKY and PKY scores
            if favorite_sky["has_sky"]:
                sky_score = favorite_sky["strength"] * 1.5  # SKY has 1.5x impact
                favorite_planet_scores.append({
                    "yoga": "SKY",
                    "score": sky_score,
                    "planets": favorite_sky["planets"],
                    "type": "sky"
                })
            
            if underdog_sky["has_sky"]:
                sky_score = underdog_sky["strength"] * 1.5  # SKY has 1.5x impact
                underdog_planet_scores.append({
                    "yoga": "SKY",
                    "score": sky_score,
                    "planets": underdog_sky["planets"],
                    "type": "sky"
                })
            
            if favorite_pky["has_pky"]:
                pky_score = -favorite_pky["strength"]  # PKY reduces score
                favorite_planet_scores.append({
                    "yoga": "PKY",
                    "score": pky_score,
                    "planets": favorite_pky["planets"],
                    "type": "pky"
                })
            
            if underdog_pky["has_pky"]:
                pky_score = -underdog_pky["strength"]  # PKY reduces score
                underdog_planet_scores.append({
                    "yoga": "PKY",
                    "score": pky_score,
                    "planets": underdog_pky["planets"],
                    "type": "pky"
                })
            
            # Calculate total scores
            favorite_total_score = sum(item["score"] for item in favorite_planet_scores)
            underdog_total_score = sum(item["score"] for item in underdog_planet_scores)
            
            # Determine predicted winner based on total scores
            is_tie = abs(favorite_total_score - underdog_total_score) < 0.5
            predicted_winner = favorite_name if favorite_total_score > underdog_total_score else underdog_name
            
            # Calculate confidence based on difference in scores
            difference = abs(favorite_total_score - underdog_total_score)
            confidence_level = self._calculate_confidence(difference)
            
            # Generate summary with cuspal information
            cuspal_summary = self._generate_cuspal_summary(favorite_cuspal, underdog_cuspal, favorite_name, underdog_name)
            
            if is_tie:
                prediction_summary = f"This match appears to be extremely close with both teams having similar astrological strengths. The favorite has {favorite_malefic_count} malefic planets in upachaya houses, and the underdog has {underdog_malefic_count}."
                
                # Add SKY/PKY info to summary
                sky_pky_summary = self._generate_sky_pky_summary(favorite_sky, underdog_sky, favorite_pky, underdog_pky, favorite_name, underdog_name)
                if sky_pky_summary:
                    prediction_summary += " " + sky_pky_summary
                
                # Add cuspal info to summary
                if cuspal_summary:
                    prediction_summary += " " + cuspal_summary
            else:
                prediction_summary = f"The astrological factors favor {predicted_winner} with {confidence_level} confidence. {predicted_winner} has stronger planetary configurations with a score of {max(favorite_total_score, underdog_total_score):.1f} compared to {min(favorite_total_score, underdog_total_score):.1f} for the opponent."
                
                # Add malefic counts to summary
                if predicted_winner == favorite_name:
                    prediction_summary += f" {favorite_name} has {favorite_malefic_count} malefic planets in upachaya houses."
                else:
                    prediction_summary += f" {underdog_name} has {underdog_malefic_count} malefic planets in upachaya houses."
                
                # Add SKY/PKY info to summary
                sky_pky_summary = self._generate_sky_pky_summary(favorite_sky, underdog_sky, favorite_pky, underdog_pky, favorite_name, underdog_name)
                if sky_pky_summary:
                    prediction_summary += " " + sky_pky_summary
                
                # Add cuspal info to summary
                if cuspal_summary:
                    prediction_summary += " " + cuspal_summary
            
            # Prepare response
            result = {
                "event_details": {
                    "event_name": event_name,
                    "event_date": event_date,
                    "favorite_name": favorite_name,
                    "underdog_name": underdog_name
                },
                "prediction": {
                    "predicted_winner": predicted_winner if not is_tie else "Tie",
                    "is_tie": is_tie,
                    "favorite_malefic_count": favorite_malefic_count,
                    "underdog_malefic_count": underdog_malefic_count,
                    "favorite_total_score": round(favorite_total_score, 2),
                    "underdog_total_score": round(underdog_total_score, 2),
                    "favorite_sky_count": len(favorite_sky["planets"]) if favorite_sky["has_sky"] else 0,
                    "underdog_sky_count": len(underdog_sky["planets"]) if underdog_sky["has_sky"] else 0,
                    "favorite_pky_count": len(favorite_pky["planets"]) if favorite_pky["has_pky"] else 0,
                    "underdog_pky_count": len(underdog_pky["planets"]) if underdog_pky["has_pky"] else 0,
                    "has_favorite_sky": favorite_sky["has_sky"],
                    "has_underdog_sky": underdog_sky["has_sky"],
                    "has_favorite_pky": favorite_pky["has_pky"],
                    "has_underdog_pky": underdog_pky["has_pky"],
                    "has_favorite_cuspal": favorite_cuspal["has_cuspal_influence"],
                    "has_underdog_cuspal": underdog_cuspal["has_cuspal_influence"],
                    "confidence_level": confidence_level,
                    "summary": prediction_summary
                },
                "analysis_details": {
                    "malefic_planets": self.malefic_planets,
                    "benefic_planets": self.benefic_planets,
                    "favorite_upachaya_houses": self.favorite_upachaya_houses,
                    "underdog_upachaya_houses": self.underdog_upachaya_houses,
                    "favorite_placements": favorite_placements,
                    "underdog_placements": underdog_placements,
                    "favorite_scores": favorite_planet_scores,
                    "underdog_scores": underdog_planet_scores,
                    "favorite_sky": favorite_sky,
                    "underdog_sky": underdog_sky,
                    "favorite_pky": favorite_pky,
                    "underdog_pky": underdog_pky,
                    "favorite_cuspal": favorite_cuspal,
                    "underdog_cuspal": underdog_cuspal
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sports prediction analysis: {str(e)}")
            logger.exception("Full traceback:")
            
            # Return error information
            return {
                "error": str(e),
                "event_name": event_name,
                "favorite_name": favorite_name,
                "underdog_name": underdog_name
            }
    
    def _get_house_number(self, house_name: str) -> int:
        """
        Parse house number from house name string (e.g., "First_House" -> 1)
        
        Args:
            house_name: House name string
            
        Returns:
            House number as integer
        """
        if not house_name or "_House" not in house_name:
            return None
            
        # Extract the word part before "_House"
        word_to_number = {
            "First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5, "Sixth": 6,
            "Seventh": 7, "Eighth": 8, "Ninth": 9, "Tenth": 10, "Eleventh": 11, "Twelfth": 12
        }
        
        house_word = house_name.split("_")[0]
        return word_to_number.get(house_word)
    
    def _calculate_confidence(self, difference: float) -> str:
        """
        Calculate confidence level based on difference in scores
        
        Args:
            difference: Absolute difference in scores
            
        Returns:
            Confidence level as string
        """
        if difference < 0.5:
            return "very low"
        elif difference < 1.5:
            return "low"
        elif difference < 3.0:
            return "moderate"
        elif difference < 5.0:
            return "high"
        else:
            return "very high"
    
    def _calculate_planet_strength(self, planet: str, sign: str, house: int, is_retrograde: bool) -> float:
        """
        Calculate the strength of a planet based on its position and status
        
        Args:
            planet: Planet name
            sign: Zodiac sign placement
            house: House placement
            is_retrograde: Whether the planet is retrograde
            
        Returns:
            Strength score (higher is stronger)
        """
        base_strength = 1.0
        
        # Check exaltation
        if planet in self.exaltation_signs and sign == self.exaltation_signs[planet]:
            base_strength += 0.5
        
        # Check debilitation
        if planet in self.debilitation_signs and sign == self.debilitation_signs[planet]:
            base_strength -= 0.5
        
        # Check own sign
        if planet in self.own_signs and sign in self.own_signs[planet]:
            base_strength += 0.3
        
        # Check dig bala (directional strength)
        if planet in self.dig_bala and house == self.dig_bala[planet]:
            base_strength += 0.3
        
        # Check retrograde status (retrograde malefics become more malefic)
        if is_retrograde:
            if planet in self.malefic_planets:
                base_strength += 0.2
            else:
                base_strength -= 0.1  # Retrograde benefics are slightly weakened
        
        return base_strength
    
    def _is_near_cusp(self, planet_data: Dict[str, Any], house_cusps: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine if a planet is near a house cusp and calculate its influence
        
        Args:
            planet_data: Planet information
            house_cusps: House cusp data
            
        Returns:
            Dict with cuspal influence information
        """
        planet_name = planet_data.get("name", "").lower()
        planet_abs_pos = planet_data.get("abs_pos", 0)
        is_retrograde = planet_data.get("retrograde", False)
        
        # Determine if it's a visible or invisible planet for orb calculation
        max_orb = self.visible_planet_orb if planet_name in self.visible_planets else self.invisible_planet_orb
        
        cuspal_influences = []
        
        # Check each house cusp
        for house_name, house_data in house_cusps.items():
            if not house_name.startswith("house_"):
                continue
                
            house_num = house_data.get("house_num", 0)
            cusp_abs_pos = house_data.get("abs_pos", 0)
            
            # Calculate angular distance from planet to cusp
            angle_diff = min(
                abs(planet_abs_pos - cusp_abs_pos), 
                360 - abs(planet_abs_pos - cusp_abs_pos)
            )
            
            # Check if planet is within orb of cusp
            if angle_diff <= max_orb:
                # Get base effect
                effect_data = self.retrograde_cusp_effects.get(planet_name, {}) if is_retrograde else self.cusp_effects.get(planet_name, {})
                effect = effect_data.get("effect", "neutral")
                description = effect_data.get("description", "")
                
                # Calculate strength based on distance to cusp
                strength_factor = 1.0
                
                # Extra special influence if very close to cusp
                if angle_diff <= self.extra_special_orb:
                    strength_factor = 2.0
                else:
                    # Linear falloff from 1.0 to 0.5 as we move from 1° to max_orb
                    strength_factor = 1.0 - (0.5 * (angle_diff - self.extra_special_orb) / (max_orb - self.extra_special_orb))
                
                cuspal_influences.append({
                    "planet": planet_name,
                    "house_num": house_num,
                    "angle_diff": angle_diff,
                    "effect": effect,
                    "effect_description": description,
                    "strength_factor": strength_factor,
                    "is_extra_special": angle_diff <= self.extra_special_orb
                })
        
        # Sort by closest influence
        cuspal_influences.sort(key=lambda x: x["angle_diff"])
        
        return {
            "has_cuspal_influence": len(cuspal_influences) > 0,
            "influences": cuspal_influences
        }
    
    def _calculate_cuspal_score(self, planet_name: str, house_num: int, effect: str, 
                               strength_factor: float, is_retrograde: bool) -> float:
        """
        Calculate score for cuspal influence
        
        Args:
            planet_name: Name of the planet
            house_num: House number of the cusp
            effect: Effect type (positive, negative, mixed, neutral, variable)
            strength_factor: Strength factor based on proximity to cusp
            is_retrograde: Whether planet is retrograde
            
        Returns:
            Score value (positive or negative)
        """
        base_score = 0.0
        
        # Base score by effect type
        if effect == "positive":
            base_score = 1.5
        elif effect == "negative":
            base_score = -1.5
        elif effect == "mixed":
            # Handle mixed effects differently based on which cusp/house
            if planet_name == "mars":
                if house_num in [6, 12]:
                    base_score = 1.0  # Positive on 6/12 axis
                elif house_num in [4, 10]:
                    base_score = -1.0  # Negative on 4/10 axis
                else:
                    base_score = 0.5  # Slight positive elsewhere
            elif planet_name == "saturn":
                if house_num in [4, 10, 6, 12]:
                    base_score = 1.0  # Positive on 4/10 and 6/12 axis
                elif house_num in [1, 7]:
                    base_score = -1.0  # Negative on 1/7 axis
                else:
                    base_score = 0.0  # Neutral elsewhere
            elif planet_name == "pluto":
                if house_num in [4, 10]:
                    base_score = 1.0  # Positive on 4/10 axis for underdogs
                elif house_num in [1, 7]:
                    base_score = -1.0  # Negative on 1/7 axis for favorites
                else:
                    base_score = 0.0  # Neutral elsewhere
        elif effect == "variable":
            # For Mercury, assume slightly positive but variable
            base_score = 0.5
        elif effect == "neutral":
            base_score = 0.0
        
        # Adjust score based on strength factor and retrograde status
        score = base_score * strength_factor
        
        # Jupiter and Venus get stronger when retrograde
        if is_retrograde and planet_name in ["jupiter", "venus"]:
            score *= 1.2
        
        return score
    
    def _check_cuspal_strengths(self, planets: Dict[str, Any], houses: Dict[str, Any], 
                              primary_cusps: List[int]) -> Dict[str, Any]:
        """
        Check for planets near house cusps and calculate their influences
        
        Args:
            planets: Planets data
            houses: Houses data
            primary_cusps: List of primary cusps to check (e.g., [1, 4, 10] for favorite)
            
        Returns:
            Dict with cuspal strength information
        """
        cuspal_influences = []
        total_score = 0.0
        
        # Check each planet for cuspal influence
        for planet_name, planet_data in planets.items():
            cusp_result = self._is_near_cusp(planet_data, houses)
            
            if cusp_result["has_cuspal_influence"]:
                # Filter to only consider primary cusps if specified
                relevant_influences = []
                
                for influence in cusp_result["influences"]:
                    house_num = influence["house_num"]
                    
                    # Only include if the house is one of the primary cusps
                    if house_num in primary_cusps:
                        is_retrograde = planet_data.get("retrograde", False)
                        
                        # Calculate score for this influence
                        score = self._calculate_cuspal_score(
                            planet_name,
                            house_num,
                            influence["effect"],
                            influence["strength_factor"],
                            is_retrograde
                        )
                        
                        influence["score"] = score
                        total_score += score
                        
                        relevant_influences.append(influence)
                
                if relevant_influences:
                    cuspal_influences.extend(relevant_influences)
        
        return {
            "has_cuspal_influence": len(cuspal_influences) > 0,
            "influences": cuspal_influences,
            "total_score": total_score
        }
    
    def _check_sky(self, planets: Dict[str, Any], house_to_check: int) -> Dict[str, Any]:
        """
        Check for Shubha Kartari Yoga (SKY) - benefic planets flanking a house
        
        Args:
            planets: Planets data
            house_to_check: House to check for SKY (usually 1 for favorite, 7 for underdog)
            
        Returns:
            Dict with SKY information
        """
        # Find houses on either side of the house_to_check
        left_house = house_to_check - 1 if house_to_check > 1 else 12
        right_house = house_to_check + 1 if house_to_check < 12 else 1
        
        left_benefics = []
        right_benefics = []
        
        sky_strength = 0.0
        
        # Check each planet
        for planet_name, planet_data in planets.items():
            # Skip non-benefic planets
            if planet_name not in self.benefic_planets:
                continue
                
            # Get planet house
            house_num = self._get_house_number(planet_data.get("house", ""))
            if house_num is None:
                continue
            
            # Check if planet is on either side
            if house_num == left_house:
                planet_sign = planet_data.get("sign", "")
                is_retrograde = planet_data.get("isRetrograde", False)
                
                planet_strength = self._calculate_planet_strength(
                    planet_name, planet_sign, house_num, is_retrograde
                )
                
                left_benefics.append({
                    "planet": planet_name,
                    "strength": planet_strength
                })
                
                sky_strength += planet_strength
                
            elif house_num == right_house:
                planet_sign = planet_data.get("sign", "")
                is_retrograde = planet_data.get("isRetrograde", False)
                
                planet_strength = self._calculate_planet_strength(
                    planet_name, planet_sign, house_num, is_retrograde
                )
                
                right_benefics.append({
                    "planet": planet_name,
                    "strength": planet_strength
                })
                
                sky_strength += planet_strength
        
        # Determine if SKY is present (requires at least one benefic on each side)
        has_sky = len(left_benefics) > 0 and len(right_benefics) > 0
        
        return {
            "has_sky": has_sky,
            "left_benefics": left_benefics,
            "right_benefics": right_benefics,
            "strength": sky_strength,
            "planets": left_benefics + right_benefics
        }
    
    def _check_pky(self, planets: Dict[str, Any], house_to_check: int) -> Dict[str, Any]:
        """
        Check for Papa Kartari Yoga (PKY) - malefic planets flanking a house
        
        Args:
            planets: Planets data
            house_to_check: House to check for PKY (usually 1 for favorite, 7 for underdog)
            
        Returns:
            Dict with PKY information
        """
        # Find houses on either side of the house_to_check
        left_house = house_to_check - 1 if house_to_check > 1 else 12
        right_house = house_to_check + 1 if house_to_check < 12 else 1
        
        left_malefics = []
        right_malefics = []
        
        pky_strength = 0.0
        
        # Check each planet
        for planet_name, planet_data in planets.items():
            # Skip non-malefic planets
            if planet_name not in self.malefic_planets:
                continue
                
            # Get planet house
            house_num = self._get_house_number(planet_data.get("house", ""))
            if house_num is None:
                continue
            
            # Check if planet is on either side
            if house_num == left_house:
                planet_sign = planet_data.get("sign", "")
                is_retrograde = planet_data.get("isRetrograde", False)
                
                planet_strength = self._calculate_planet_strength(
                    planet_name, planet_sign, house_num, is_retrograde
                )
                
                left_malefics.append({
                    "planet": planet_name,
                    "strength": planet_strength
                })
                
                # Only strong malefics contribute fully to PKY
                if planet_name in self.strong_malefics:
                    pky_strength += planet_strength
                else:
                    pky_strength += planet_strength * 0.5
                
            elif house_num == right_house:
                planet_sign = planet_data.get("sign", "")
                is_retrograde = planet_data.get("isRetrograde", False)
                
                planet_strength = self._calculate_planet_strength(
                    planet_name, planet_sign, house_num, is_retrograde
                )
                
                right_malefics.append({
                    "planet": planet_name,
                    "strength": planet_strength
                })
                
                # Only strong malefics contribute fully to PKY
                if planet_name in self.strong_malefics:
                    pky_strength += planet_strength
                else:
                    pky_strength += planet_strength * 0.5
        
        # Check if at least one strong malefic is present
        has_strong_malefic = any(m["planet"] in self.strong_malefics for m in left_malefics + right_malefics)
        
        # Determine if PKY is present (requires at least one malefic on each side, with at least one strong malefic)
        has_pky = len(left_malefics) > 0 and len(right_malefics) > 0 and has_strong_malefic
        
        return {
            "has_pky": has_pky,
            "left_malefics": left_malefics,
            "right_malefics": right_malefics,
            "strength": pky_strength,
            "planets": left_malefics + right_malefics
        }
    
    def _generate_cuspal_summary(self, favorite_cuspal: Dict[str, Any], underdog_cuspal: Dict[str, Any],
                               favorite_name: str, underdog_name: str) -> str:
        """
        Generate a summary of cuspal influences
        
        Args:
            favorite_cuspal: Cuspal information for favorite
            underdog_cuspal: Cuspal information for underdog
            favorite_name: Name of favorite team
            underdog_name: Name of underdog team
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Process favorite cuspal influences
        if favorite_cuspal["has_cuspal_influence"]:
            # Get the most significant influences (top 2)
            significant_influences = sorted(
                favorite_cuspal["influences"], 
                key=lambda x: abs(x["score"]), 
                reverse=True
            )[:2]
            
            for influence in significant_influences:
                planet = influence["planet"].capitalize()
                house = influence["house_num"]
                effect = "positive" if influence["score"] > 0 else "negative"
                strength = "strongly" if influence["is_extra_special"] else "significantly"
                
                if effect == "positive":
                    summary_parts.append(f"{planet} {strength} influences {favorite_name}'s {self._get_house_name(house)} cusp positively")
                else:
                    summary_parts.append(f"{planet} {strength} challenges {favorite_name} from the {self._get_house_name(house)} cusp")
        
        # Process underdog cuspal influences
        if underdog_cuspal["has_cuspal_influence"]:
            # Get the most significant influences (top 2)
            significant_influences = sorted(
                underdog_cuspal["influences"], 
                key=lambda x: abs(x["score"]), 
                reverse=True
            )[:2]
            
            for influence in significant_influences:
                planet = influence["planet"].capitalize()
                house = influence["house_num"]
                effect = "positive" if influence["score"] > 0 else "negative"
                strength = "strongly" if influence["is_extra_special"] else "significantly"
                
                if effect == "positive":
                    summary_parts.append(f"{planet} {strength} influences {underdog_name}'s {self._get_house_name(house)} cusp positively")
                else:
                    summary_parts.append(f"{planet} {strength} challenges {underdog_name} from the {self._get_house_name(house)} cusp")
        
        return " ".join(summary_parts)
    
    def _get_house_name(self, house_num: int) -> str:
        """
        Get the name of a house from its number
        
        Args:
            house_num: House number (1-12)
            
        Returns:
            House name
        """
        house_names = {
            1: "1st (self/identity)",
            2: "2nd (resources)",
            3: "3rd (communication)",
            4: "4th (home/foundation)",
            5: "5th (creativity)",
            6: "6th (service/health)",
            7: "7th (relationships/opponent)",
            8: "8th (transformation)",
            9: "9th (expansion)",
            10: "10th (career/status)",
            11: "11th (community)",
            12: "12th (subconscious)"
        }
        
        return house_names.get(house_num, f"{house_num}th")
    
    def _generate_sky_pky_summary(self, favorite_sky: Dict[str, Any], underdog_sky: Dict[str, Any], 
                               favorite_pky: Dict[str, Any], underdog_pky: Dict[str, Any],
                               favorite_name: str, underdog_name: str) -> str:
        """
        Generate a summary of SKY and PKY influences
        
        Args:
            favorite_sky: SKY information for favorite
            underdog_sky: SKY information for underdog
            favorite_pky: PKY information for favorite
            underdog_pky: PKY information for underdog
            favorite_name: Name of favorite team
            underdog_name: Name of underdog team
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Add SKY information
        if favorite_sky["has_sky"]:
            planets = [p["planet"] for p in favorite_sky["planets"]]
            planet_str = " and ".join(planets) if len(planets) <= 2 else ", ".join(planets[:-1]) + ", and " + planets[-1]
            summary_parts.append(f"{favorite_name} benefits from Shubha Kartari Yoga with {planet_str} protecting their ascendant")
            
        if underdog_sky["has_sky"]:
            planets = [p["planet"] for p in underdog_sky["planets"]]
            planet_str = " and ".join(planets) if len(planets) <= 2 else ", ".join(planets[:-1]) + ", and " + planets[-1]
            summary_parts.append(f"{underdog_name} benefits from Shubha Kartari Yoga with {planet_str} protecting their ascendant")
        
        # Add PKY information
        if favorite_pky["has_pky"]:
            planets = [p["planet"] for p in favorite_pky["planets"]]
            planet_str = " and ".join(planets) if len(planets) <= 2 else ", ".join(planets[:-1]) + ", and " + planets[-1]
            summary_parts.append(f"{favorite_name} is challenged by Papa Kartari Yoga with {planet_str} flanking their ascendant")
            
        if underdog_pky["has_pky"]:
            planets = [p["planet"] for p in underdog_pky["planets"]]
            planet_str = " and ".join(planets) if len(planets) <= 2 else ", ".join(planets[:-1]) + ", and " + planets[-1]
            summary_parts.append(f"{underdog_name} is challenged by Papa Kartari Yoga with {planet_str} flanking their ascendant")
        
        return " ".join(summary_parts) 