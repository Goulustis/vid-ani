from manim import *
import numpy as np

class ImageOnPlane(ThreeDScene):
    def construct(self):
        # Create visible axes
        axes = ThreeDAxes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            z_range=[-5, 5, 1],
            x_length=10,
            y_length=10,
            z_length=10,
            axis_config={"stroke_width": 2, "include_tip": True, "color": WHITE}
        )
        
        # Add axis labels
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")
        z_label = axes.get_z_axis_label("z")
        axis_labels = VGroup(x_label, y_label, z_label)
        
        # Create the dummy green image (using a square)
        dummy_image = Square(side_length=5)
        dummy_image.set_fill(BLACK, opacity=0.8)
        dummy_image.set_stroke(BLACK, width=0.5)
        
        # Place the image on the xy-plane with center at origin (0,0,0)
        dummy_image.move_to(ORIGIN)
        
        # Big Dipper star coordinates (normalized to fit in our square)
        # These are approximate positions of the 7 main stars in the Big Dipper
        star_coords = [
            [-1.8, 1.2, 0],    # Alkaid
            [-0.8, 1.0, 0],    # Mizar
            [-0.2, 0.7, 0],    # Alioth
            [0.5, 0.5, 0],     # Megrez
            [1.0, 1.0, 0],     # Phecda
            [2.0, 0.7, 0],      # Dubhe
            [1.5, 0.2, 0],     # Merak
        ]

        rot = np.array([
            [np.sqrt(2) / 2, -np.sqrt(2) / 2, 0],
            [np.sqrt(2) / 2,  np.sqrt(2) / 2, 0],
            [0,               0,              1]
        ])

        star_coords = np.array(star_coords) - np.array([[-0.2, 0.7, 0]])
        star_coords = (rot @ star_coords.T).T
        
        # Create stars (dots)
        stars = VGroup()
        for coord in star_coords:
            star = Dot(point=coord, color=WHITE, radius=0.1)
            stars.add(star)
        
        # Create lines connecting the stars to form the Big Dipper shape
        lines = VGroup()
        for i in range(len(star_coords) - 1):
            line = Line(
                start=star_coords[i],
                end=star_coords[i+1],
                color=YELLOW_A,
                stroke_width=2
            )
            lines.add(line)
        
        # Add constellation to the image
        constellation = VGroup(lines, stars)
        
        # Create a 3D Gaussian surface
        def gaussian_function(x, y):
            # Parameters for the Gaussian
            sigma = 1.0  # Standard deviation
            amplitude = 2.0  # Height of the peak
            return amplitude * np.exp(-(x**2 + y**2) / (2 * sigma**2))
        
        # Create the surface with a simple white color and no grid lines
        gaussian_surface = Surface(
            lambda u, v: np.array([
                u,
                v,
                gaussian_function(u, v)
            ]),
            u_range=[-2, 2],
            v_range=[-2, 2],
            resolution=(30, 30),
            fill_opacity=1,
            stroke_width=0,
            stroke_opacity=0,
            stroke_color=WHITE,
            fill_color=WHITE,
            should_make_jagged=False,
            checkerboard_colors=False
        )
        
        # Explicitly set the fill color to white with no stroke
        gaussian_surface.set_fill(WHITE, opacity=0.7)
        gaussian_surface.set_stroke(WHITE, width=0.5, opacity=0.5)
        
        # Group all elements to scale together later (except axes)
        scene_group = Group(dummy_image, constellation, gaussian_surface)
        
        # Add the scene group to the scene
        self.add(scene_group)
        
        # Stay at the default camera position for 4 seconds
        self.wait(4)
        
        # Now move the camera to the specified position
        self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES, run_time=2)
        self.wait(1)
        
        # Rotate the scene to show the image is on the plane and the gaussian above it
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        self.wait(1)
        
        # Define the off-center point coordinates
        off_center_x, off_center_y = 0.5, -0.5
        off_center_z = gaussian_function(off_center_x, off_center_y)
        off_center_point = np.array([off_center_x, off_center_y, off_center_z])
        
        # Now scale everything in the scene about the off-center point
        self.play(
            scene_group.animate.scale(5, about_point=off_center_point),  # Scale by 5x about the off-center point
            run_time=2
        )
        
        # Wait to observe the larger scene
        self.wait(1)
        
        # Create a small red dot to show the off-center point AFTER scaling
        off_center_marker = Sphere(radius=0.1, color=RED).move_to(off_center_point)
        self.play(Create(off_center_marker), run_time=1)
        
        # Calculate derivatives for tangent plane
        def partial_x(x, y):
            # Partial derivative with respect to x
            sigma = 1.0
            amplitude = 2.0
            return -amplitude * (x / sigma**2) * np.exp(-(x**2 + y**2) / (2 * sigma**2))
            
        def partial_y(x, y):
            # Partial derivative with respect to y
            sigma = 1.0
            amplitude = 2.0
            return -amplitude * (y / sigma**2) * np.exp(-(x**2 + y**2) / (2 * sigma**2))
        
        # Calculate the tangent plane equation
        dx = partial_x(off_center_x, off_center_y)
        dy = partial_y(off_center_x, off_center_y)
        
        # Equation of tangent plane: z = z0 + dx*(x-x0) + dy*(y-y0)
        def tangent_plane_function(x, y):
            return off_center_z + 0.1 + dx*(x-off_center_x) + dy*(y-off_center_y)
        
        # Create the tangent plane
        tangent_plane_size = 1.5  # Size of the tangent plane
        tangent_plane = Surface(
            lambda u, v: np.array([
                off_center_x + (u - 0.5) * tangent_plane_size,
                off_center_y + (v - 0.5) * tangent_plane_size,
                tangent_plane_function(
                    off_center_x + (u - 0.5) * tangent_plane_size,
                    off_center_y + (v - 0.5) * tangent_plane_size
                )
            ]),
            u_range=[0, 1],
            v_range=[0, 1],
            resolution=(10, 10),
            fill_opacity=0.7,
            fill_color=BLUE,
            stroke_width=1,
            stroke_color=BLUE,
            checkerboard_colors=False
        )
        
        # Add the tangent plane with an animation
        self.play(Create(tangent_plane), run_time=1.5)
        
        # Continue ambient camera rotation to show the tangent plane
        self.begin_ambient_camera_rotation(rate=-0.2)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        self.wait(2)
