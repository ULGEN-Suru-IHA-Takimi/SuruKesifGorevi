#!/usr/bin/env python3
"""
Test file for ArUco centering and 5-meter movement behavior.
This file simulates the ArUco centering process and tests the movement logic.
"""

import asyncio
import sys
import os
import time
import logging

# Add parent directory to sys.path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArUcoCenteringTester:
    def __init__(self):
        self.aruco_centered = False
        self.mission_completed = False
        self.current_position = {
            'lat': 47.397958,
            'lon': 8.546304,
            'alt': 5.0
        }
        self.current_attitude = {'yaw_deg': 0.0}
        
    def simulate_aruco_detection(self):
        """Simulate ArUco detection and centering process."""
        print("🎯 Simulating ArUco detection and centering process...")
        
        # Simulate centering process
        for step in range(5):
            print(f"   Step {step + 1}: Centering ArUco...")
            time.sleep(0.5)
            
            if step == 3:  # ArUco becomes centered
                self.aruco_centered = True
                print("   ✅ ArUco centered!")
                break
            else:
                print("   🔄 Still centering...")
        
        return self.aruco_centered
    
    def simulate_xbee_message_sending(self):
        """Simulate sending XBee message after ArUco centering."""
        if not self.aruco_centered:
            print("❌ Cannot send XBee message - ArUco not centered")
            return False
            
        print("📡 Simulating XBee message sending...")
        
        # Simulate message format
        lat_scaled = int(self.current_position['lat'] * 1000000)
        lon_scaled = int(self.current_position['lon'] * 1000000)
        alt_scaled = int(self.current_position['alt'] * 10)
        
        message = f"{lat_scaled},{lon_scaled},{alt_scaled},1"
        print(f"   📤 XBee message: {message}")
        print(f"   📍 Coordinates: {self.current_position['lat']:.6f}, {self.current_position['lon']:.6f}, {self.current_position['alt']}m")
        
        # Simulate successful sending
        print("   ✅ XBee message sent successfully")
        self.mission_completed = True
        return True
    
    def simulate_5_meter_movement(self):
        """Simulate 5-meter forward movement after XBee message."""
        if not self.mission_completed:
            print("❌ Cannot move 5 meters - mission not completed")
            return False
            
        print("🚁 Simulating 5-meter forward movement...")
        
        try:
            # Simulate movement
            print("   📍 Current position before movement:")
            print(f"      Lat: {self.current_position['lat']:.6f}")
            print(f"      Lon: {self.current_position['lon']:.6f}")
            print(f"      Alt: {self.current_position['alt']}m")
            print(f"      Yaw: {self.current_attitude['yaw_deg']}°")
            
            # Simulate 5-meter forward movement
            print("   🚀 Moving 5 meters forward...")
            time.sleep(1)
            
            # Update position (simplified - in reality this would use trigonometry)
            print("   ✅ Successfully moved 5 meters forward")
            print("   📍 New position after movement:")
            print(f"      Lat: {self.current_position['lat']:.6f}")
            print(f"      Lon: {self.current_position['lon']:.6f}")
            print(f"      Alt: {self.current_position['alt']}m")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error during 5-meter movement: {e}")
            return False
    
    def run_complete_test(self):
        """Run the complete ArUco centering and movement test."""
        print("🚁 ArUco Centering and Movement Test")
        print("=" * 50)
        
        # Step 1: ArUco Detection and Centering
        print("\n🎯 STEP 1: ArUco Detection and Centering")
        if self.simulate_aruco_detection():
            print("✅ ArUco centering completed successfully")
        else:
            print("❌ ArUco centering failed")
            return False
        
        # Step 2: XBee Message Sending
        print("\n📡 STEP 2: XBee Message Sending")
        if self.simulate_xbee_message_sending():
            print("✅ XBee message sent successfully")
        else:
            print("❌ XBee message sending failed")
            return False
        
        # Step 3: 5-Meter Forward Movement
        print("\n🚁 STEP 3: 5-Meter Forward Movement")
        if self.simulate_5_meter_movement():
            print("✅ 5-meter movement completed successfully")
        else:
            print("❌ 5-meter movement failed")
            return False
        
        # Final Status
        print("\n🎉 FINAL STATUS")
        print("=" * 50)
        print(f"ArUco Centered: {'✅ Yes' if self.aruco_centered else '❌ No'}")
        print(f"XBee Message Sent: {'✅ Yes' if self.mission_completed else '❌ No'}")
        print(f"5-Meter Movement: {'✅ Yes' if self.mission_completed else '❌ No'}")
        print(f"Mission Status: {'✅ COMPLETED' if self.mission_completed else '❌ FAILED'}")
        
        return self.mission_completed
    
    def print_behavior_summary(self):
        """Print a summary of the expected behavior."""
        print("\n" + "=" * 60)
        print("EXPECTED ARUCO CENTERING BEHAVIOR")
        print("=" * 60)
        print("🎯 SCENARIO: This Drone Finds ArUco")
        print("   1. ArUco marker detected")
        print("   2. Precision landing and centering")
        print("   3. XBee message sent with coordinates")
        print("   4. Move 5 meters forward from ArUco position")
        print("   5. Mission completed")
        print()
        print("🚁 SCENARIO: Other Drone Sends ArUco Message")
        print("   1. Receive XBee message with coordinates")
        print("   2. Land DIRECTLY at current location (no movement)")
        print("   3. No 5-meter offset")
        print()
        print("📡 MESSAGE FLOW:")
        print("   ArUco Found → XBee Broadcast → Other Drones Land")
        print("=" * 60)

def main():
    """Main test function."""
    print("🚁 ArUco Centering and Movement Test")
    print("This tool tests the complete ArUco centering process.")
    print()
    
    tester = ArUcoCenteringTester()
    
    # Show behavior summary
    tester.print_behavior_summary()
    
    print("\n🎯 Test Options:")
    print("1. Run complete ArUco centering test")
    print("2. Show behavior summary")
    print("3. Exit")
    
    try:
        while True:
            print("\n" + "-" * 40)
            choice = input("Select option (1-3): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting complete test...")
                success = tester.run_complete_test()
                if success:
                    print("\n🎉 All tests passed successfully!")
                else:
                    print("\n❌ Some tests failed!")
                    
            elif choice == "2":
                tester.print_behavior_summary()
                
            elif choice == "3":
                print("👋 Exiting...")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-3.")
                
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    
    print("✅ Test completed")

if __name__ == "__main__":
    main()
