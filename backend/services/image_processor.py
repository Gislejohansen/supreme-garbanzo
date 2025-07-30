import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
from typing import Dict, Tuple, Any
import asyncio
from skimage import filters, segmentation, measure
from scipy import ndimage

class ImageProcessor:
    """Service for processing and preparing images for analysis"""
    
    def __init__(self):
        self.target_size = (1024, 1024)  # Standard size for analysis
        self.blur_kernel_size = 5
        
    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """Process an uploaded image and prepare it for analysis"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Get original dimensions
            original_height, original_width = image.shape[:2]
            
            # Basic image info
            image_info = {
                "original_dimensions": {"width": original_width, "height": original_height},
                "file_size": os.path.getsize(image_path),
                "channels": image.shape[2] if len(image.shape) == 3 else 1
            }
            
            # Preprocess image
            processed_image = await self._preprocess_image(image)
            
            # Extract features
            features = await self._extract_features(processed_image)
            
            # Save processed image
            processed_path = image_path.replace(".jpg", "_processed.jpg").replace(".png", "_processed.png")
            cv2.imwrite(processed_path, processed_image)
            
            return {
                "image_info": image_info,
                "processed_path": processed_path,
                "features": features,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for analysis"""
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to target size while maintaining aspect ratio
        h, w = image.shape[:2]
        scale = min(self.target_size[0] / w, self.target_size[1] / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Create canvas and center the image
        canvas = np.zeros((self.target_size[1], self.target_size[0], 3), dtype=np.uint8)
        y_offset = (self.target_size[1] - new_h) // 2
        x_offset = (self.target_size[0] - new_w) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        # Enhance image quality
        enhanced = await self._enhance_image(canvas)
        
        return enhanced
    
    async def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better analysis"""
        # Convert to PIL for enhancement
        pil_image = Image.fromarray(image)
        
        # Enhance contrast slightly
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced = enhancer.enhance(1.1)
        
        # Enhance sharpness slightly
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(1.1)
        
        # Convert back to numpy
        return np.array(enhanced)
    
    async def _extract_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract basic features from the image"""
        # Color statistics
        color_stats = await self._analyze_colors(image)
        
        # Texture analysis
        texture_stats = await self._analyze_texture(image)
        
        # Edge detection
        edge_stats = await self._analyze_edges(image)
        
        return {
            "color": color_stats,
            "texture": texture_stats,
            "edges": edge_stats
        }
    
    async def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color distribution and statistics"""
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Calculate statistics for each channel
        rgb_stats = {
            "mean": np.mean(image, axis=(0, 1)).tolist(),
            "std": np.std(image, axis=(0, 1)).tolist(),
            "median": np.median(image, axis=(0, 1)).tolist()
        }
        
        hsv_stats = {
            "hue_mean": float(np.mean(hsv[:, :, 0])),
            "saturation_mean": float(np.mean(hsv[:, :, 1])),
            "value_mean": float(np.mean(hsv[:, :, 2])),
            "hue_std": float(np.std(hsv[:, :, 0]))
        }
        
        # Dominant colors using k-means
        dominant_colors = await self._get_dominant_colors(image)
        
        return {
            "rgb_stats": rgb_stats,
            "hsv_stats": hsv_stats,
            "dominant_colors": dominant_colors
        }
    
    async def _analyze_texture(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze texture properties"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Local Binary Pattern for texture
        try:
            from skimage.feature import local_binary_pattern
            lbp = local_binary_pattern(gray, 24, 8, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=26, range=(0, 26))
            lbp_hist = lbp_hist.astype(float)
            lbp_hist /= (lbp_hist.sum() + 1e-7)
        except:
            lbp_hist = np.zeros(26)
        
        # Texture energy using GLCM approximation
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        return {
            "lbp_uniformity": float(np.std(lbp_hist)),
            "gradient_magnitude_mean": float(np.mean(gradient_magnitude)),
            "gradient_magnitude_std": float(np.std(gradient_magnitude)),
            "texture_energy": float(np.mean(gradient_magnitude**2))
        }
    
    async def _analyze_edges(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze edge characteristics"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Contour analysis
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        return {
            "edge_density": float(edge_density),
            "num_contours": len(contours),
            "avg_contour_area": float(np.mean([cv2.contourArea(c) for c in contours])) if contours else 0.0
        }
    
    async def _get_dominant_colors(self, image: np.ndarray, k: int = 5) -> list:
        """Extract dominant colors using k-means clustering"""
        # Reshape image to be a list of pixels
        pixels = image.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        # Apply k-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert centers back to uint8 and calculate percentages
        centers = np.uint8(centers)
        unique, counts = np.unique(labels, return_counts=True)
        
        dominant_colors = []
        for i, center in enumerate(centers):
            percentage = (counts[i] / len(labels)) * 100
            dominant_colors.append({
                "color": center.tolist(),
                "percentage": float(percentage)
            })
        
        # Sort by percentage
        dominant_colors.sort(key=lambda x: x["percentage"], reverse=True)
        
        return dominant_colors