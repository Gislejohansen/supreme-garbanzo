import cv2
import numpy as np
from typing import Dict, List, Tuple, Any
import json
import os
from datetime import datetime
import asyncio
from skimage import filters, segmentation, measure, color
from scipy import ndimage, spatial
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class PaintAnalyzer:
    """Core service for analyzing paint quality by comparing before/after images"""
    
    def __init__(self):
        self.color_tolerance = 30  # HSV color difference tolerance
        self.coverage_threshold = 0.1  # Minimum coverage difference to flag
        self.texture_threshold = 0.2  # Texture difference threshold
        self.min_region_size = 100  # Minimum pixel area for a problem region
        
    async def analyze_paint_quality(self, before_path: str, after_path: str, project_id: str) -> Dict[str, Any]:
        """Main analysis function comparing before and after images"""
        start_time = datetime.utcnow()
        
        try:
            # Load and preprocess images
            before_img = cv2.imread(before_path)
            after_img = cv2.imread(after_path)
            
            if before_img is None or after_img is None:
                raise ValueError("Could not load one or both images")
            
            # Align and resize images
            before_aligned, after_aligned = await self._align_images(before_img, after_img)
            
            # Perform various analyses
            color_analysis = await self._analyze_color_consistency(before_aligned, after_aligned)
            coverage_analysis = await self._analyze_paint_coverage(before_aligned, after_aligned)
            texture_analysis = await self._analyze_texture_consistency(before_aligned, after_aligned)
            
            # Detect problem regions
            problem_regions = await self._detect_problem_regions(
                before_aligned, after_aligned, color_analysis, coverage_analysis, texture_analysis
            )
            
            # Calculate overall score
            overall_score = await self._calculate_overall_score(
                color_analysis, coverage_analysis, texture_analysis, problem_regions
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                color_analysis, coverage_analysis, texture_analysis, problem_regions
            )
            
            # Create visualization
            visualization_path = await self._create_visualization(
                before_aligned, after_aligned, problem_regions, project_id
            )
            
            processing_duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Prepare result
            result = {
                "project_id": project_id,
                "overall_score": overall_score,
                "issues_detected": len(problem_regions),
                "analysis_time": start_time.isoformat(),
                "processing_duration": processing_duration,
                "color_analysis": color_analysis,
                "coverage_analysis": coverage_analysis,
                "texture_analysis": texture_analysis,
                "problem_regions": [self._region_to_dict(region) for region in problem_regions],
                "recommendations": recommendations,
                "visualization_path": visualization_path,
                "status": "completed"
            }
            
            # Save results
            await self._save_results(result, project_id)
            
            return result
            
        except Exception as e:
            return {
                "project_id": project_id,
                "status": "error",
                "error": str(e),
                "analysis_time": start_time.isoformat(),
                "processing_duration": (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def _align_images(self, before: np.ndarray, after: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Align two images to ensure proper comparison"""
        # Convert to grayscale for feature matching
        before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
        
        # Resize to same size if different
        h1, w1 = before.shape[:2]
        h2, w2 = after.shape[:2]
        
        if h1 != h2 or w1 != w2:
            # Resize to smaller dimensions to maintain quality
            target_h, target_w = min(h1, h2), min(w1, w2)
            before = cv2.resize(before, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            after = cv2.resize(after, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Simple alignment using template matching for rough alignment
        # For production, consider using SIFT/ORB features for better alignment
        try:
            # Use phase correlation for rough alignment
            before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
            after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            before_gray = cv2.GaussianBlur(before_gray, (5, 5), 0)
            after_gray = cv2.GaussianBlur(after_gray, (5, 5), 0)
            
        except Exception:
            # If alignment fails, return original resized images
            pass
        
        return before, after
    
    async def _analyze_color_consistency(self, before: np.ndarray, after: np.ndarray) -> Dict[str, Any]:
        """Analyze color consistency between before and after images"""
        # Convert to HSV for better color analysis
        before_hsv = cv2.cvtColor(before, cv2.COLOR_BGR2HSV)
        after_hsv = cv2.cvtColor(after, cv2.COLOR_BGR2HSV)
        
        # Calculate color difference map
        color_diff = np.sqrt(np.sum((before_hsv.astype(float) - after_hsv.astype(float))**2, axis=2))
        
        # Analyze color distribution
        before_colors = await self._get_color_distribution(before)
        after_colors = await self._get_color_distribution(after)
        
        # Calculate color consistency metrics
        mean_color_diff = float(np.mean(color_diff))
        std_color_diff = float(np.std(color_diff))
        max_color_diff = float(np.max(color_diff))
        
        # Find areas with significant color changes
        significant_change_mask = color_diff > (mean_color_diff + 2 * std_color_diff)
        change_percentage = float(np.sum(significant_change_mask) / significant_change_mask.size * 100)
        
        return {
            "mean_color_difference": mean_color_diff,
            "std_color_difference": std_color_diff,
            "max_color_difference": max_color_diff,
            "change_percentage": change_percentage,
            "before_colors": before_colors,
            "after_colors": after_colors,
            "color_difference_map": color_diff.tolist()
        }
    
    async def _analyze_paint_coverage(self, before: np.ndarray, after: np.ndarray) -> Dict[str, Any]:
        """Analyze paint coverage quality"""
        # Convert to grayscale
        before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
        
        # Calculate intensity difference
        intensity_diff = np.abs(after_gray.astype(float) - before_gray.astype(float))
        
        # Detect edges to identify surface boundaries
        before_edges = cv2.Canny(before_gray, 50, 150)
        after_edges = cv2.Canny(after_gray, 50, 150)
        
        # Calculate coverage metrics
        mean_intensity_change = float(np.mean(intensity_diff))
        std_intensity_change = float(np.std(intensity_diff))
        
        # Find regions with poor coverage (high variance in nearby areas)
        kernel = np.ones((15, 15), np.float32) / 225
        local_variance = cv2.filter2D(intensity_diff, -1, kernel)
        poor_coverage_mask = local_variance > np.percentile(local_variance, 85)
        poor_coverage_percentage = float(np.sum(poor_coverage_mask) / poor_coverage_mask.size * 100)
        
        return {
            "mean_intensity_change": mean_intensity_change,
            "std_intensity_change": std_intensity_change,
            "poor_coverage_percentage": poor_coverage_percentage,
            "edge_preservation_score": await self._calculate_edge_preservation(before_edges, after_edges)
        }
    
    async def _analyze_texture_consistency(self, before: np.ndarray, after: np.ndarray) -> Dict[str, Any]:
        """Analyze texture consistency"""
        before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
        
        # Calculate texture using Local Binary Patterns
        try:
            from skimage.feature import local_binary_pattern
            
            before_lbp = local_binary_pattern(before_gray, 24, 8, method='uniform')
            after_lbp = local_binary_pattern(after_gray, 24, 8, method='uniform')
            
            # Calculate texture difference
            texture_diff = np.abs(before_lbp - after_lbp)
            texture_consistency_score = 1.0 - (np.mean(texture_diff) / 26.0)  # 26 is max LBP value
            
        except ImportError:
            # Fallback to gradient-based texture analysis
            before_grad = cv2.Laplacian(before_gray, cv2.CV_64F)
            after_grad = cv2.Laplacian(after_gray, cv2.CV_64F)
            
            texture_diff = np.abs(before_grad - after_grad)
            texture_consistency_score = 1.0 - (np.mean(texture_diff) / 255.0)
        
        return {
            "texture_consistency_score": float(texture_consistency_score),
            "mean_texture_difference": float(np.mean(texture_diff)),
            "texture_variance_change": float(np.std(texture_diff))
        }
    
    async def _detect_problem_regions(self, before: np.ndarray, after: np.ndarray, 
                                    color_analysis: Dict, coverage_analysis: Dict, 
                                    texture_analysis: Dict) -> List[Dict]:
        """Detect specific regions with painting problems"""
        h, w = before.shape[:2]
        
        # Create problem maps
        color_diff_map = np.array(color_analysis["color_difference_map"])
        
        # Threshold for significant problems
        color_threshold = color_analysis["mean_color_difference"] + 2 * color_analysis["std_color_difference"]
        
        # Find connected components of problem areas
        problem_mask = color_diff_map > color_threshold
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        problem_mask = cv2.morphologyEx(problem_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
        problem_mask = cv2.morphologyEx(problem_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours of problem regions
        contours, _ = cv2.findContours(problem_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        problem_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_region_size:
                continue
                
            # Get bounding rectangle
            x, y, region_w, region_h = cv2.boundingRect(contour)
            
            # Calculate severity based on color difference in this region
            region_mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(region_mask, [contour], 255)
            
            region_color_diff = color_diff_map[region_mask > 0]
            severity = float(np.mean(region_color_diff) / 255.0)  # Normalize to 0-1
            
            # Determine issue type based on characteristics
            issue_type = await self._classify_issue_type(before[y:y+region_h, x:x+region_w], 
                                                       after[y:y+region_h, x:x+region_w])
            
            problem_regions.append({
                "x": int(x),
                "y": int(y),
                "width": int(region_w),
                "height": int(region_h),
                "area": float(area),
                "severity": min(1.0, severity),
                "confidence": min(1.0, severity * 1.2),  # Simple confidence calculation
                "issue_type": issue_type
            })
        
        return problem_regions
    
    async def _classify_issue_type(self, before_region: np.ndarray, after_region: np.ndarray) -> str:
        """Classify the type of painting issue in a region"""
        # Simple classification based on color and texture characteristics
        before_std = np.std(before_region)
        after_std = np.std(after_region)
        
        std_ratio = after_std / (before_std + 1e-7)
        
        if std_ratio > 1.5:
            return "uneven_coverage"
        elif std_ratio < 0.7:
            return "over_application"
        else:
            return "color_inconsistency"
    
    async def _calculate_overall_score(self, color_analysis: Dict, coverage_analysis: Dict, 
                                     texture_analysis: Dict, problem_regions: List) -> float:
        """Calculate overall paint quality score (0-100)"""
        # Base score starts at 100
        score = 100.0
        
        # Deduct points for color inconsistency
        color_penalty = min(30, color_analysis["change_percentage"] * 0.5)
        score -= color_penalty
        
        # Deduct points for poor coverage
        coverage_penalty = min(25, coverage_analysis["poor_coverage_percentage"] * 0.4)
        score -= coverage_penalty
        
        # Deduct points for texture issues
        texture_penalty = (1.0 - texture_analysis["texture_consistency_score"]) * 20
        score -= texture_penalty
        
        # Deduct points for number and severity of problem regions
        region_penalty = 0
        for region in problem_regions:
            region_penalty += region["severity"] * (region["area"] / 10000) * 5
        
        score -= min(20, region_penalty)
        
        return max(0.0, score)
    
    async def _generate_recommendations(self, color_analysis: Dict, coverage_analysis: Dict, 
                                      texture_analysis: Dict, problem_regions: List) -> List[str]:
        """Generate specific recommendations based on analysis"""
        recommendations = []
        
        if color_analysis["change_percentage"] > 15:
            recommendations.append("Consider applying additional coats for more uniform color coverage")
        
        if coverage_analysis["poor_coverage_percentage"] > 20:
            recommendations.append("Some areas show uneven paint application - consider touch-ups")
        
        if texture_analysis["texture_consistency_score"] < 0.7:
            recommendations.append("Paint texture appears inconsistent - check application technique")
        
        if len(problem_regions) > 5:
            recommendations.append("Multiple problem areas detected - comprehensive touch-up recommended")
        
        # Specific recommendations based on issue types
        issue_types = [region["issue_type"] for region in problem_regions]
        if "uneven_coverage" in issue_types:
            recommendations.append("Apply paint more evenly to avoid streaking and patchy areas")
        
        if "over_application" in issue_types:
            recommendations.append("Reduce paint thickness to avoid drips and texture issues")
        
        if not recommendations:
            recommendations.append("Paint quality looks good overall!")
        
        return recommendations
    
    async def _create_visualization(self, before: np.ndarray, after: np.ndarray, 
                                  problem_regions: List, project_id: str) -> str:
        """Create visualization with problem regions highlighted"""
        # Create results directory
        results_dir = f"results/{project_id}"
        os.makedirs(results_dir, exist_ok=True)
        
        # Create figure with before/after comparison
        fig, axes = plt.subplots(1, 2, figsize=(15, 7))
        
        # Show before image
        before_rgb = cv2.cvtColor(before, cv2.COLOR_BGR2RGB)
        axes[0].imshow(before_rgb)
        axes[0].set_title("Before Painting")
        axes[0].axis('off')
        
        # Show after image with problem regions highlighted
        after_rgb = cv2.cvtColor(after, cv2.COLOR_BGR2RGB)
        axes[1].imshow(after_rgb)
        axes[1].set_title("After Painting (Issues Highlighted)")
        
        # Add problem region overlays
        for region in problem_regions:
            # Color code by severity: green (minor) to red (severe)
            if region["severity"] < 0.3:
                color = 'yellow'
                alpha = 0.3
            elif region["severity"] < 0.6:
                color = 'orange'
                alpha = 0.4
            else:
                color = 'red'
                alpha = 0.5
            
            rect = Rectangle((region["x"], region["y"]), region["width"], region["height"],
                           linewidth=2, edgecolor=color, facecolor=color, alpha=alpha)
            axes[1].add_patch(rect)
        
        axes[1].axis('off')
        
        plt.tight_layout()
        
        # Save visualization
        viz_path = f"{results_dir}/analysis_visualization.png"
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return viz_path
    
    async def _save_results(self, result: Dict, project_id: str):
        """Save analysis results to file"""
        results_dir = f"results/{project_id}"
        os.makedirs(results_dir, exist_ok=True)
        
        # Remove non-serializable data for JSON storage
        json_result = result.copy()
        if "color_difference_map" in json_result.get("color_analysis", {}):
            # Don't save the full difference map in JSON (too large)
            del json_result["color_analysis"]["color_difference_map"]
        
        with open(f"{results_dir}/analysis_result.json", 'w') as f:
            json.dump(json_result, f, indent=2, default=str)
    
    async def _get_color_distribution(self, image: np.ndarray) -> Dict[str, Any]:
        """Get color distribution statistics"""
        # Convert to HSV and get dominant colors
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        return {
            "mean_hue": float(np.mean(hsv[:, :, 0])),
            "mean_saturation": float(np.mean(hsv[:, :, 1])),
            "mean_value": float(np.mean(hsv[:, :, 2])),
            "hue_std": float(np.std(hsv[:, :, 0]))
        }
    
    async def _calculate_edge_preservation(self, before_edges: np.ndarray, after_edges: np.ndarray) -> float:
        """Calculate how well edges are preserved after painting"""
        intersection = np.logical_and(before_edges > 0, after_edges > 0)
        union = np.logical_or(before_edges > 0, after_edges > 0)
        
        if np.sum(union) == 0:
            return 1.0
        
        return float(np.sum(intersection) / np.sum(union))
    
    def _region_to_dict(self, region: Dict) -> Dict:
        """Convert region to JSON-serializable dictionary"""
        return {
            "x": region["x"],
            "y": region["y"], 
            "width": region["width"],
            "height": region["height"],
            "severity": region["severity"],
            "confidence": region["confidence"],
            "issue_type": region["issue_type"]
        }