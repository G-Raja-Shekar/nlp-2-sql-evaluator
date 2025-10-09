"""
Similarity calculation utilities.
"""

from typing import Set, List
import difflib


class SimilarityCalculator:
    """
    Handles various similarity calculations.
    """
    
    @staticmethod
    def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
        """
        Calculate Jaccard similarity between two sets.
        
        Args:
            set1: First set
            set2: Second set
            
        Returns:
            Jaccard similarity score (0.0 to 1.0)
        """
        if len(set1) == 0 and len(set2) == 0:
            return 1.0
        
        if len(set1) == 0 or len(set2) == 0:
            return 0.0
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if len(union) > 0 else 0.0
    
    @staticmethod
    def word_similarity(text1: str, text2: str) -> float:
        """
        Calculate word-level similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Word similarity score (0.0 to 1.0)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        return SimilarityCalculator.jaccard_similarity(words1, words2)
    
    @staticmethod
    def sequence_similarity(text1: str, text2: str) -> float:
        """
        Calculate sequence similarity using difflib.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Sequence similarity score (0.0 to 1.0)
        """
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    @staticmethod
    def component_similarity(comp1: str, comp2: str) -> float:
        """
        Calculate similarity between SQL components.
        
        Args:
            comp1: First component
            comp2: Second component
            
        Returns:
            Component similarity score (0.0 to 1.0)
        """
        if not comp1 and not comp2:
            return 1.0
        
        if not comp1 or not comp2:
            return 0.0
        
        # Combine word similarity and sequence similarity
        word_sim = SimilarityCalculator.word_similarity(comp1, comp2)
        seq_sim = SimilarityCalculator.sequence_similarity(comp1, comp2)
        
        # Weighted average (favor word similarity for SQL)
        return 0.7 * word_sim + 0.3 * seq_sim
    
    @staticmethod
    def advanced_text_similarity(expected: str, actual: str) -> float:
        """
        Advanced text similarity with multiple metrics.
        
        Args:
            expected: Expected text
            actual: Actual text
            
        Returns:
            Advanced similarity score (0.0 to 1.0)
        """
        if not expected and not actual:
            return 1.0
        
        if not expected or not actual:
            return 0.0
        
        # Calculate multiple similarity metrics
        word_sim = SimilarityCalculator.word_similarity(expected, actual)
        seq_sim = SimilarityCalculator.sequence_similarity(expected, actual)
        
        # Character-level similarity
        char_sim = difflib.SequenceMatcher(None, expected.lower(), actual.lower()).ratio()
        
        # Weighted combination
        return 0.5 * word_sim + 0.3 * seq_sim + 0.2 * char_sim
