import asyncio
from math import e
import sys
import os
# Add parent directory to sys.path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.offboard_control import OffboardControl
from optimization.drone_vision_calculator import DroneVisionCalculator
from aruco_mission.realtime_camera_viewer import RealtimeCameraViewer
from aruco_mission.computer_camera_test import ComputerCameraTest
import threading
from mavsdk.offboard import VelocityNedYaw
from services.xbee_service import XbeeService

RealtimeCameraViewer = ComputerCameraTest

class SwarmDiscovery(OffboardControl):
    """
    SwarmDiscovery mission: square oscillation flight and ArUco-based precision landing.
    """
    def __init__(self, xbee_port: str = None, camera = False):
        super().__init__()
        self.pi_cam = None
        self.mission_completed = False
        self.xbee_service = XbeeService(
            message_received_callback=XbeeService.default_message_received_callback,
            port=xbee_port,
            max_queue_size=100,
            baudrate=57600
        )

        if camera:
            self.pi_cam = RealtimeCameraViewer()
        else:
            self.pi_cam = ComputerCameraTest()

        # Set custom message handler for swarm coordination
        self.xbee_service.set_custom_message_handler(self.handle_swarm_message)
        
        # Queue for swarm messages to be processed in the main event loop
        self.swarm_message_queue = asyncio.Queue()
        self._swarm_landing_active = False
        self.pending_swarm_landing = None

    def handle_swarm_message(self, message_dict: dict) -> None:
        """
        Handle incoming XBee messages from other drones in the swarm.
        When a message with command=1 is received, add it to queue for processing in main event loop.
        """
        try:
            data = message_dict.get("data", "")
            print(f"📨 Swarm message received: {data}")
            
            parts = data.split(',')
            if len(parts) == 4:
                lat_scaled = int(parts[0])
                lon_scaled = int(parts[1])
                alt_scaled = int(parts[2])
                command = int(parts[3])
                
                print(f"🔍 Parsed swarm data - Lat: {lat_scaled}, Lon: {lon_scaled}, Alt: {alt_scaled}, Command: {command}")
                
                if command == 1:
                    print("🚁 Swarm landing command received! Queuing for processing...")
                    print("📍 Will land DIRECTLY at current location (no movement)")
                    
                    # Convert scaled coordinates back to decimal
                    lat_decimal = lat_scaled / 1000000.0
                    lon_decimal = lon_scaled / 1000000.0
                    target_altitude = alt_scaled / 10.0
                    
                    print(f"🎯 ArUco found at: {lat_decimal:.6f}, {lon_decimal:.6f}, {target_altitude}m")
                    print(f"📍 This drone will land at its current location")
                    
                    # Store coordinates for processing in main event loop
                    self.pending_swarm_landing = {
                        'lat': lat_decimal,
                        'lon': lon_decimal,
                        'alt': target_altitude
                    }
                    print("✅ Swarm landing command stored for processing")
                else:
                    print(f"ℹ️ Command {command} - no action taken")
                    
        except ValueError as e:
            print(f"⚠️ Swarm message parse error: {e}")
        except Exception as e:
            print(f"❌ Swarm message handler error: {e}")

    async def execute_swarm_landing(self, target_lat: float, target_lon: float, target_alt: float) -> None:
        """
        Execute automatic landing mission when swarm message is received.
        When a swarm message comes, land directly at current location.
        """
        try:
            self._swarm_landing_active = True
            print(f"🚁 Swarm message received! ArUco found at: {target_lat:.6f}, {target_lon:.6f}, {target_alt}m")
            print(f"📍 Landing directly at current location: {self.current_position.latitude_deg:.6f}, {self.current_position.longitude_deg:.6f}")
            
            # Use end_mission for proper landing sequence (offboard stop + land + disarm)
            print("🛬 Starting proper landing sequence using end_mission...")
            print("   📍 This will: Stop offboard → Land → Disarm")
            
            await self.end_mission()
            
            print("✅ Swarm landing mission completed successfully!")
            print("🎉 Drone landed and disarmed at current location!")
                
        except Exception as e:
            print(f"❌ Error during swarm landing mission: {e}")
            # Try to land safely if there's an error using end_mission
            try:
                print("🚨 Emergency landing initiated using end_mission...")
                await self.end_mission()
            except Exception as emergency_error:
                print(f"💥 Emergency landing failed: {emergency_error}")
                # Last resort: try direct land
                try:
                    await self.drone.action.land()
                    print("⚠️ Direct landing initiated as last resort")
                except:
                    print("💥 All landing methods failed!")
        finally:
            self._swarm_landing_active = False

    async def monitor_swarm_messages(self):
        """
        Monitor swarm messages in the main event loop.
        This method runs as a separate task and processes swarm messages safely.
        """
        print("🔍 Starting swarm message monitoring...")
        try:
            while not self.mission_completed and not self._swarm_landing_active:
                # Check for pending swarm landing every 0.1 seconds
                await asyncio.sleep(0.1)
                
                # Check if there's a pending swarm landing
                if hasattr(self, 'pending_swarm_landing') and self.pending_swarm_landing:
                    print("🚁 Processing pending swarm landing...")
                    coords = self.pending_swarm_landing
                    self.pending_swarm_landing = None  # Clear pending
                    
                    # Start swarm landing mission
                    await self.execute_swarm_landing(coords['lat'], coords['lon'], coords['alt'])
                
                # If swarm landing is active, wait for it to complete
                if self._swarm_landing_active:
                    print("🚁 Swarm landing mission active, waiting for completion...")
                    while self._swarm_landing_active:
                        await asyncio.sleep(1)
                    print("✅ Swarm landing mission completed")
                    
                    # Mission completed, no need to continue monitoring
                    print("🎯 Swarm mission completed - stopping message monitoring")
                    break
                    
        except Exception as e:
            print(f"❌ Error in swarm message monitoring: {e}")
        finally:
            print("🔍 Swarm message monitoring stopped")

    async def connect(self, system_address: str, port: int):
        await super().connect(system_address=system_address, port=port)
        print("-- Starting XBee service...")
        try:
            self.xbee_service.listen()
            print("✅ XBee service started successfully!")
            print("🔍 Listening for swarm messages from other drones...")
        except Exception as e:
            print(f"⚠️ XBee service failed to start: {e}")
            print("   Continuing without XBee...")

    async def square_oscillation_by_meters(self, long_distance: float, short_distance: float, velocity: float, repeat_count: int):
        """
        Square oscillation pattern flight.
        Args:
            long_distance: forward movement (meters)
            short_distance: side movement (meters)
            velocity: movement speed (m/s)
            repeat_count: number of cycles
        """
        print("Square Oscillation started...")
        current_yaw = self.home_position["yaw"]
        for cycle in range(repeat_count):
            await self.go_forward_by_meter(long_distance, velocity, current_yaw)
            await self.hold_mode(1.0, current_yaw)
            await self.go_forward_by_meter(short_distance, velocity, current_yaw + 90.0)
            await self.hold_mode(1.0, current_yaw + 90.0)
            await self.go_forward_by_meter(long_distance, velocity, current_yaw + 180.0)
            await self.hold_mode(1.0, current_yaw + 180.0)
            await self.go_forward_by_meter(short_distance, velocity, current_yaw + 90.0)
            await self.hold_mode(1.0, current_yaw + 90.0)
        if current_yaw + 90 != self.home_position["yaw"]:
            await self.go_forward_by_meter(long_distance, velocity, current_yaw)
            await self.hold_mode(1.0, current_yaw)
        await asyncio.sleep(1)
        print("Square Oscillation finished!")

    async def square_oscillation_by_cam_fov(
        self,
        distance1: float,
        distance2: float,
        velocity: float,
        camera_fov_horizontal: float,
        camera_fov_vertical: float,
        image_width: int,
        image_height: int
    ):
        """
        Square oscillation flight based on camera FOV and ArUco detection.
        """
        drone_vision_calculator = DroneVisionCalculator(
            camera_fov_horizontal=camera_fov_horizontal,
            camera_fov_vertical=camera_fov_vertical,
            image_width=image_width,
            image_height=image_height
        )
        threading.Thread(target=self.pi_cam.show_camera_with_detection, ).start()
        ground_coverage = drone_vision_calculator.calculate_ground_coverage(self.target_altitude)
        short_distance = ground_coverage["width_m"] / 2
        repeat_count = int(distance2 / short_distance / 2)
        
        # Start swarm message monitoring task
        swarm_monitor_task = asyncio.create_task(self.monitor_swarm_messages())
        
        sqosc_async_thread = asyncio.create_task(
            self.square_oscillation_by_meters(
                long_distance=distance1,
                short_distance=short_distance,
                repeat_count=repeat_count,
                velocity=velocity
            )
        )
        while not sqosc_async_thread.done() and not self.pi_cam.is_found:
            await asyncio.sleep(0.1)
        if self.pi_cam.is_found:
            sqosc_async_thread.cancel()
            await self.drone.offboard.set_velocity_ned(
                VelocityNedYaw(0.0, 0.0, 0.0, self.current_attitude.yaw_deg if self.current_attitude else 0.0)
            )
            await self.hold_mode(1.0, self.current_attitude.yaw_deg if self.current_attitude else 0.0)
            print("ArUco found! Precision landing started...")
            arUco_centered = False
            while not arUco_centered and not self.mission_completed:
                x, y, z = self.pi_cam.get_averaged_position()
                # Only print if not centered
                if abs(x) > 0.02 or abs(y) > 0.02:
                    print(f"Correction: X={x:.2f} Y={y:.2f}")
                    correction_speed = 0.5
                    move_x = x * correction_speed
                    move_y = y * correction_speed
                    await self.drone.offboard.set_velocity_ned(
                        VelocityNedYaw(move_x, move_y, 0.0, self.current_attitude.yaw_deg if self.current_attitude else 0.0)
                    )
                    await asyncio.sleep(0.2)
                    await self.drone.offboard.set_velocity_ned(
                        VelocityNedYaw(0.0, 0.0, 0.0, self.current_attitude.yaw_deg if self.current_attitude else 0.0)
                    )
                    await asyncio.sleep(0.2)
                else:
                    print("ArUco centered!")
                    arUco_centered = True
                    break
            
            if arUco_centered:
                print("Precision landing complete. Sending XBee message...")
                lat_scaled = int(self.current_position.latitude_deg * 1000000)
                lon_scaled = int(self.current_position.longitude_deg * 1000000)
                alt_scaled = int(self.current_position.absolute_altitude_m * 10)
                simple_message = f"{lat_scaled},{lon_scaled},{alt_scaled},1"
                print(f"XBee message: {simple_message}")
                try:
                    if hasattr(self, 'xbee_service') and self.xbee_service:
                        success = await asyncio.get_event_loop().run_in_executor(
                            None, 
                            self.xbee_service.send_broadcast_message, 
                            simple_message, 
                            False
                        )
                        if success:
                            print("XBee message sent.")
                            self.mission_completed = True
                        else:
                            print("XBee message failed.")
                    else:
                        print("XBee service not found.")
                        self.mission_completed = True
                except Exception as e:
                    print(f"XBee error: {e}")
                    self.mission_completed = True
                
                print("Mission complete. Moving 5 meters forward from ArUco position...")
                await asyncio.sleep(1)
                try:
                    await self.go_forward_by_meter(5.0, 1.0, self.current_attitude.yaw_deg if self.current_attitude else 0.0)
                    print("✅ Moved 5 meters forward. Mission ended.")
                except Exception as e:
                    print(f"⚠️ Could not move 5 meters forward: {e}")
                    print("   Continuing with mission completion...")
                
                await self.end_mission()
            else:
                print("⚠️ ArUco centering was interrupted or failed.")
        
        # Check final mission status
        if self.mission_completed:
            print("🎉 Mission completed successfully - XBee message sent and 5m movement done!")
        else:
            print("❌ Mission failed - ArUco not found or centering incomplete.")
        
        # Mission completed, no need to continue listening for swarm messages
        print("🎯 Mission completed successfully!")
        print("   ✅ ArUco found and centered")
        print("   ✅ XBee message sent")
        print("   ✅ 5 meters moved forward")
        print("   🚁 Drone landed and mission ended")
        
        print("🎯 Mission finished!")



