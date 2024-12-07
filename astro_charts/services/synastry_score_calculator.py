class SynastryScoreCalculator:
    def __init__(self):
        # Enhanced weights for powerful linkages
        self.weights = {
            'cinderella_linkages': {
                'conjunction': 30,    # Increased from 25
                'parallel': 30,       # Increased from 25
                'trine': 25,          # Increased from 20
                'quincunx': 20,       # Increased from 18
                'opposition': 20      # Increased from 18
            },
            'sexual_linkages': {
                'conjunction': 25,    # Increased from 22
                'parallel': 25,       # Increased from 22
                'trine': 20,          # Increased from 18
                'opposition': 20      # Increased from 18
            },
            'romance_linkages': {
                'conjunction': 25,    # Increased from 20
                'parallel': 25,       # Increased from 20
                'trine': 20,          # Increased from 15
                'opposition': 20      # Increased from 15
            },
            'marital_linkages': {
                'conjunction': 35,    # Increased from 25
                'parallel': 35,       # Increased from 25
                'trine': 30,          # Increased from 20
                'opposition': 25      # Increased from 20
            },
            'saturn_clashes': {
                'conjunction': -8,    # Reduced penalty from -12
                'parallel': -8,       # Reduced penalty from -12
                'opposition': -6,     # Reduced penalty from -10
                'quincunx': -4       # Reduced penalty from -8
            }
        }
        
        # Increased bonus points for multiple aspects
        self.multiple_aspect_bonus = 15  # Up from 10
        
        # Enhanced bonuses for significant aspects
        self.special_aspect_bonuses = {
            'venus_chiron': 25,      # Up from 15
            'jupiter_chiron': 20,    # Up from 12
            'chiron_neptune': 15,    # Up from 10
            'venus_venus': 20,       # New bonus
            'jupiter_jupiter': 20    # New bonus
        }

    def calculate_scores(self, aspect_data):
        # Initialize base scores
        raw_scores = {
            'romance': 35,  # Lower base scores
            'compatibility': 35,
            'longevity': 35
        }
        
        # More moderate weights for aspects
        aspect_weights = {
            'conjunction': 20,
            'trine': 15,
            'sextile': 12,
            'parallel': 15,
            'contraparallel': 12,
            'quincunx': 8,
            'opposition': -18  # Stronger negative impact
        }

        # Calculate romance score
        romance_aspects = aspect_data.get('romance_linkages', [])
        for aspect in romance_aspects:
            raw_scores['romance'] += aspect_weights.get(aspect['aspect_name'], 0)
        
        # Calculate compatibility score
        cinderella_aspects = aspect_data.get('cinderella_linkages', [])
        super_aspects = (aspect_data.get('person1_super_aspects', []) + 
                        aspect_data.get('person2_super_aspects', []))
        
        for aspect in cinderella_aspects + super_aspects:
            raw_scores['compatibility'] += aspect_weights.get(aspect['aspect_name'], 0)
        
        # Saturn clashes impact
        saturn_clashes = aspect_data.get('saturn_clashes', [])
        raw_scores['compatibility'] -= len(saturn_clashes) * 15  # Increased penalty
        
        # Calculate longevity score
        marital_aspects = aspect_data.get('marital_linkages', [])
        for aspect in marital_aspects:
            raw_scores['longevity'] += aspect_weights.get(aspect['aspect_name'], 0)

        # Smaller bonus for multiple aspects
        if len(romance_aspects) >= 3:
            raw_scores['romance'] += 10
        if len(cinderella_aspects) >= 3:
            raw_scores['compatibility'] += 10
        if len(marital_aspects) >= 3:
            raw_scores['longevity'] += 10

        # Normalize scores between 35-100
        normalized_scores = {}
        for category in raw_scores:
            score = raw_scores[category]
            normalized = min(max(int(score), 35), 100)
            normalized_scores[category] = normalized

        # Calculate overall score with balanced weights
        normalized_scores['overall'] = round(
            normalized_scores['romance'] * 0.33 +
            normalized_scores['compatibility'] * 0.34 +
            normalized_scores['longevity'] * 0.33
        )

        # Add aspect counts
        normalized_scores['aspect_counts'] = {
            'saturn_clashes': len(saturn_clashes),
            'cinderella_linkages': len(cinderella_aspects),
            'sexual_linkages': len(aspect_data.get('sexual_linkages', [])),
            'romance_linkages': len(romance_aspects),
            'marital_linkages': len(marital_aspects)
        }

        return normalized_scores

    def _apply_multiple_aspect_bonuses(self, aspect_data, scores):
        """Apply bonuses for multiple aspects between same planets"""
        planet_pairs = self._count_planet_pairs(aspect_data)
        
        for pair, count in planet_pairs.items():
            if count > 1:
                bonus = self.multiple_aspect_bonus * (count - 1)
                if 'venus' in pair or 'jupiter' in pair:
                    scores['longevity'] += bonus * 1.5
                scores['compatibility'] += bonus 

    def _count_planet_pairs(self, aspect_data):
        """Count how many aspects exist between each pair of planets"""
        planet_pairs = {}
        
        # Check all linkage types that indicate relationship strength
        linkage_types = [
            'marital_linkages',
            'cinderella_linkages',
            'romance_linkages',
            'sexual_linkages'
        ]
        
        for linkage_type in linkage_types:
            if linkage_type in aspect_data:
                for aspect in aspect_data[linkage_type]:
                    # Create a sorted tuple of the two planets to ensure consistent keys
                    planet_pair = tuple(sorted([
                        aspect['planet1_name'],
                        aspect['planet2_name']
                    ]))
                    
                    # Increment the count for this planet pair
                    if planet_pair in planet_pairs:
                        planet_pairs[planet_pair] += 1
                    else:
                        planet_pairs[planet_pair] = 1
        
        return planet_pairs