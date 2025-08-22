#!/usr/bin/env python3
"""
Test file for swarm behavior differences.
This file demonstrates the different behaviors:
1. ArUco found: Move 5 meters forward
2. Swarm message: Go directly to location and land
"""

import asyncio
import sys
import os
import time
import logging

# Add parent directory to sys.path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.xbee_service import XbeeService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SwarmBehaviorTester:
    def __init__(self, port: str = "/dev/ttyUSB0"):
        self.port = port
        self.xbee_service = None
        
    def setup_xbee(self):
        """Initialize XBee service for testing."""
        try:
            self.xbee_service = XbeeService(
                message_received_callback=XbeeService.default_message_received_callback,
                port=self.port,
                max_queue_size=100,
                baudrate=57600
            )
            self.xbee_service.set_custom_message_handler(self.handle_test_message)
            print(f"✅ XBee service initialized on port {self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize XBee service: {e}")
            return False
    
    def handle_test_message(self, message_dict: dict):
        """Handle received messages for testing."""
        data = message_dict.get("data", "")
        sender = message_dict.get("sender", "Unknown")
        
        print(f"\n📨 Message received from {sender}: {data}")
        
        # Parse the message
        try:
            parts = data.split(',')
            if len(parts) == 4:
                lat_scaled = int(parts[0])
                lon_scaled = int(parts[1])
                alt_scaled = int(parts[2])
                command = int(parts[3])
                
                lat_decimal = lat_scaled / 1000000.0
                lon_decimal = lon_scaled / 1000000.0
                target_alt = alt_scaled / 10.0
                
                print(f"📍 Parsed coordinates: Lat={lat_decimal:.6f}, Lon={lon_decimal:.6f}, Alt={target_alt}m")
                print(f"🎯 Command: {command}")
                
                if command == 1:
                    print("🚁 LANDING COMMAND RECEIVED!")
                    print("   Behavior: Land DIRECTLY at current location (no movement)")
                    print("   This simulates what happens when another drone finds ArUco")
                    print("   Note: In real mission, this would trigger landing at current position")
                else:
                    print(f"ℹ️ Command {command} - no action taken")
                    
        except ValueError as e:
            print(f"⚠️ Failed to parse message: {e}")
    
    def start_listening(self):
        """Start listening for XBee messages."""
        if not self.xbee_service:
            print("❌ XBee service not initialized")
            return False
            
        try:
            self.xbee_service.listen()
            print("🔍 Started listening for XBee messages...")
            return True
        except Exception as e:
            print(f"❌ Failed to start listening: {e}")
            return False
    
    def send_aruco_discovery_message(self, lat: float, lon: float, alt: float):
        """Send a message simulating ArUco discovery."""
        if not self.xbee_service:
            print("❌ XBee service not initialized")
            return False
            
        try:
            # Scale coordinates like in the actual mission
            lat_scaled = int(lat * 1000000)
            lon_scaled = int(lon * 1000000)
            alt_scaled = int(alt * 10)
            
            message = f"{lat_scaled},{lon_scaled},{alt_scaled},1"
            print(f"📤 Sending ArUco discovery message: {message}")
            print(f"   This simulates: Drone found ArUco at {lat:.6f}, {lon:.6f}, {alt}m")
            print(f"   Expected behavior: Other drones go DIRECTLY to this location and land")
            
            success = self.xbee_service.send_broadcast_message(message, False)
            if success:
                print("✅ ArUco discovery message sent successfully")
                return True
            else:
                print("❌ Failed to send message")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def print_behavior_summary(self):
        """Print a summary of the different behaviors."""
        print("\n" + "="*60)
        print("SWARM BEHAVIOR SUMMARY")
        print("="*60)
        print("🎯 SCENARIO 1: ArUco Found by This Drone")
        print("   • Find ArUco marker")
        print("   • Precision landing on ArUco")
        print("   • Send XBee message with coordinates")
        print("   • Move 5 meters forward from ArUco position")
        print("   • Mission complete")
        print()
        print("🚁 SCENARIO 2: Swarm Message Received from Another Drone")
        print("   • Receive XBee message with coordinates")
        print("   • Land DIRECTLY at current location (no movement)")
        print("   • No navigation to other coordinates")
        print("   • No 5-meter offset movement")
        print()
        print("📡 MESSAGE FORMAT: lat_scaled,lon_scaled,alt_scaled,command")
        print("   • lat_scaled = latitude × 1,000,000")
        print("   • lon_scaled = longitude × 1,000,000")
        print("   • alt_scaled = altitude × 10")
        print("   • command = 1 (landing command)")
        print()
        print("🔧 TECHNICAL DETAILS:")
        print("   • Messages are received in XBee callback thread")
        print("   • Coordinates are stored for processing in main event loop")
        print("   • Swarm landing is executed safely in async context")
        print("="*60)
    
    def cleanup(self):
        """Clean up resources."""
        if self.xbee_service:
            try:
                self.xbee_service.close()
                print("🔌 XBee service closed")
            except:
                pass

def main():
    """Main test function."""
    print("🚁 Swarm Behavior Tester")
    print("This tool demonstrates the different behaviors between ArUco discovery and swarm messages.")
    print()
    
    # Get port from user
    default_port = "/dev/ttyUSB0"
    port = input(f"Enter XBee port (default: {default_port}): ").strip()
    if not port:
        port = default_port
    
    tester = SwarmBehaviorTester(port)
    
    if not tester.setup_xbee():
        print("❌ Cannot continue without XBee service")
        return
    
    if not tester.start_listening():
        print("❌ Cannot start listening")
        return
    
    # Show behavior summary
    tester.print_behavior_summary()
    
    print("\n🎯 Test Options:")
    print("1. Send ArUco discovery message (simulate finding ArUco)")
    print("2. Show behavior summary")
    print("3. Exit")
    
    try:
        while True:
            print("\n" + "-"*40)
            choice = input("Select option (1-3): ").strip()
            
            if choice == "1":
                print("\n📤 Send ArUco Discovery Message")
                print("This simulates what happens when a drone finds an ArUco marker.")
                try:
                    lat = float(input("Enter latitude (decimal): "))
                    lon = float(input("Enter longitude (decimal): "))
                    alt = float(input("Enter altitude (meters): "))
                    
                    tester.send_aruco_discovery_message(lat, lon, alt)
                    
                except ValueError:
                    print("❌ Invalid input. Please enter valid numbers.")
                    
            elif choice == "2":
                tester.print_behavior_summary()
                
            elif choice == "3":
                print("👋 Exiting...")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-3.")
                
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    
    finally:
        tester.cleanup()
        print("✅ Test completed")

if __name__ == "__main__":
    main()
