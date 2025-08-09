from manim import *
import numpy as np
import random

class HomographyVisualization(Scene):
    def construct(self):
        # Demonstrate homography transformation
        self.homography_demonstration()
    
    def homography_demonstration(self):
        # Title for the demonstration
        title = Text("Homography 转换", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Create a source image (square grid)
        source_grid = self.create_grid(4, 4, 3, BLUE, LEFT * 3)
        # source_label = Text("Source Image", font_size=24).next_to(source_grid, UP)
        source_label = Text("源图像", font_size=24).next_to(source_grid, UP)
        
        self.play(
            Create(source_grid),
            Write(source_label)
        )
        self.wait()
        
        # Create a target grid (perspective transformed)
        target_grid = self.create_warped_grid(4, 4, 3, RED, RIGHT * 3)
        target_label = Text("目标图像 (Homography 后)", font_size=24).next_to(target_grid, UP)
        
        self.play(
            Create(target_grid),
            Write(target_label)
        )
        self.wait()
        
        # Generate keypoint pairs and store them
        source_points, target_points, keypoint_colors = self.generate_keypoint_pairs()
        
        # Create source keypoints and connecting lines
        source_keypoints = VGroup()
        target_keypoints = VGroup()
        connecting_lines = VGroup()
        
        for i in range(len(source_points)):
            source_dot = Dot(source_points[i], color=keypoint_colors[i], radius=0.1)
            target_dot = Dot(target_points[i], color=keypoint_colors[i], radius=0.1)
            connect_line = DashedLine(
                source_points[i], 
                target_points[i], 
                color=keypoint_colors[i],
                dash_length=0.1
            )
            
            source_keypoints.add(source_dot)
            target_keypoints.add(target_dot)
            connecting_lines.add(connect_line)
        
        # Add keypoint matches
        self.play(
            Create(source_keypoints),
            Create(target_keypoints),
            Create(connecting_lines)
        )
        self.wait()
        
        # Animation showing the transformation
        # Instead of fading out connecting lines, we'll animate them to shrink
        # as source points move toward target points
        
        # Create updated connecting lines that will transform during the animation
        animated_lines = VGroup()
        for i in range(len(source_points)):
            # These will be transformed to zero-length lines at target points
            target_line = DashedLine(
                target_points[i],
                target_points[i],
                color=keypoint_colors[i],
                dash_length=0.1
            )
            animated_lines.add(target_line)
        
        # Animate the transformation
        self.play(
            Transform(source_grid, target_grid.copy().set_color(BLUE)),
            Transform(source_keypoints, target_keypoints),
            Transform(connecting_lines, animated_lines),
            run_time=3
        )
        self.wait()
        
       
        # Fade out
        self.play(
            *[FadeOut(mob) for mob in self.mobjects]
        )
        self.wait()
        
    def create_grid(self, rows, cols, size, color, position):
        # Create a grid of lines
        grid = VGroup()
        
        width = size
        height = size
        
        cell_width = width / cols
        cell_height = height / rows
        
        # Horizontal lines
        for i in range(rows + 1):
            y = height/2 - i * cell_height
            line = Line(
                start=[-width/2, y, 0],
                end=[width/2, y, 0],
                color=color
            )
            grid.add(line)
        
        # Vertical lines
        for i in range(cols + 1):
            x = -width/2 + i * cell_width
            line = Line(
                start=[x, -height/2, 0],
                end=[x, height/2, 0],
                color=color
            )
            grid.add(line)
        
        grid.shift(position)
        return grid
    
    def create_warped_grid(self, rows, cols, size, color, position, is_targ=False):
        # Create a grid with perspective warping
        grid = VGroup()
        
        width = size
        height = size
        
        # Define the corners of the warped grid
        tl = position + np.array([-width/2 - 0.3, height/2 + 0.2, 0])
        tr = position + np.array([width/2 + 0.5, height/2 - 0.1, 0])
        bl = position + np.array([-width/2 + 0.2, -height/2 - 0.3, 0])
        br = position + np.array([width/2 - 0.1, -height/2 + 0.4, 0])
        
        # Horizontal lines
        for i in range(rows + 1):
            t = i / rows
            start = tl * (1-t) + bl * t
            end = tr * (1-t) + br * t
            line = Line(start=start, end=end, color=color)
            grid.add(line)
        
        # Vertical lines
        for i in range(cols + 1):
            t = i / cols
            start = tl * (1-t) + tr * t
            end = bl * (1-t) + br * t
            line = Line(start=end, end=start, color=color)
            grid.add(line)
        
        return grid
    
    def generate_keypoint_pairs(self):
        # Generate keypoint pairs that will be transformed by the homography
        
        # Define homography corners for mapping
        source_corners = [
            np.array([-1.5, 1.5, 0]),  # top-left
            np.array([1.5, 1.5, 0]),   # top-right
            np.array([-1.5, -1.5, 0]), # bottom-left
            np.array([1.5, -1.5, 0])   # bottom-right
        ]
        
        target_corners = [
            np.array([2.2, 1.7, 0]),   # top-left
            np.array([5.0, 1.4, 0]),   # top-right
            np.array([2.7, -1.8, 0]),  # bottom-left
            np.array([4.4, -1.1, 0])   # bottom-right
        ]
        
        # Adjust the corners to be relative to the grid positions
        source_corners = [corner + LEFT * 3 for corner in source_corners]
        
        # Create keypoint matches at various positions
        num_matches = 8
        keypoint_colors = [
            YELLOW, GREEN, PURPLE, ORANGE, 
            TEAL, PINK, GOLD, MAROON
        ]
        
        source_points = []
        target_points = []
        
        # Generate internal points in the grid
        for i in range(num_matches):
            # Random point on source grid (biased toward interior points)
            source_t1 = random.uniform(0.2, 0.8)
            source_t2 = random.uniform(0.2, 0.8)
            
            # Interpolate between corners to find a point in the source grid
            source_point = (
                source_corners[0] * (1-source_t1) * (1-source_t2) +
                source_corners[1] * source_t1 * (1-source_t2) +
                source_corners[2] * (1-source_t1) * source_t2 +
                source_corners[3] * source_t1 * source_t2
            )
            
            # Apply the "same" transformation to find the corresponding point in target
            target_point = (
                target_corners[0] * (1-source_t1) * (1-source_t2) +
                target_corners[1] * source_t1 * (1-source_t2) +
                target_corners[2] * (1-source_t1) * source_t2 +
                target_corners[3] * source_t1 * source_t2
            )
            
            source_points.append(source_point)
            target_points.append(target_point)
        
        return source_points, target_points, keypoint_colors
