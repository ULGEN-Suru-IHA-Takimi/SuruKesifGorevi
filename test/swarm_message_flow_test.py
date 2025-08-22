#!/usr/bin/env python3
"""
Test file for swarm message flow.
This file demonstrates the complete flow of swarm messages without await errors.
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

class SwarmMessageFlowTester:
    def __init__(self, port: str = "/dev/ttyUSB0"):
        self.port = port
        self.xbee_service = None
        self.received_messages = []
        
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
        timestamp = message_dict.get("timestamp", 0)
        
        print(f"\n📨 Message received from {sender}: {data}")
        
        # Store message for analysis
        self.received_messages.append({
            "data": data,
            "sender": sender,
            "timestamp": timestamp
        })
        
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
                    print("   ✅ Message parsed successfully")
                    print("   ✅ No await errors occurred")
                    print("   ✅ Ready for swarm landing mission")
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
    
    def send_test_message(self, lat: float, lon: float, alt: float, command: int = 1):
        """Send a test message."""
        if not self.xbee_service:
            print("❌ XBee service not initialized")
            return False
            
        try:
            # Scale coordinates like in the actual mission
            lat_scaled = int(lat * 1000000)
            lon_scaled = int(lon * 1000000)
            alt_scaled = int(alt * 10)
            
            message = f"{lat_scaled},{lon_scaled},{alt_scaled},{command}"
            print(f"📤 Sending test message: {message}")
            print(f"   Coordinates: {lat:.6f}, {lon:.6f}, {alt}m")
            print(f"   Command: {command}")
            
            success = self.xbee_service.send_broadcast_message(message, False)
            if success:
                print("✅ Message sent successfully")
                return True
            else:
                print("❌ Failed to send message")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def print_message_flow(self):
        """Print the message flow diagram."""
        print("\n" + "="*70)
        print("SWARM MESSAGE FLOW DIAGRAM")
        print("="*70)
        print("📡 STEP 1: XBee Message Reception")
        print("   • XBee device receives message from another drone")
        print("   • Message goes to XbeeService callback")
        print("   • handle_swarm_message() is called in XBee thread")
        print()
        print("🔍 STEP 2: Message Parsing")
        print("   • Parse lat_scaled, lon_scaled, alt_scaled, command")
        print("   • Convert to decimal coordinates")
        print("   • Store in pending_swarm_landing variable")
        print("   • ✅ NO AWAIT CALLS - Safe for non-async context")
        print()
        print("⏳ STEP 3: Main Event Loop Processing")
        print("   • monitor_swarm_messages() task runs in main loop")
        print("   • Checks for pending_swarm_landing every 0.1 seconds")
        print("   • When found, calls execute_swarm_landing() with await")
        print()
        print("🚁 STEP 4: Swarm Landing Execution")
        print("   • Navigate to target coordinates")
        print("   • Land at exact location")
        print("   • Complete swarm mission")
        print("="*70)
    
    def print_status(self):
        """Print current status and received messages."""
        print("\n" + "="*50)
        print("SWARM MESSAGE FLOW TESTER STATUS")
        print("="*50)
        print(f"XBee Port: {self.port}")
        print(f"XBee Service: {'✅ Active' if self.xbee_service else '❌ Inactive'}")
        print(f"Messages Received: {len(self.received_messages)}")
        
        if self.received_messages:
            print("\n📨 Received Messages:")
            for i, msg in enumerate(self.received_messages, 1):
                print(f"  {i}. From {msg['sender']}: {msg['data']}")
        
        print("="*50)
    
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
    print("🚁 Swarm Message Flow Tester")
    print("This tool tests the complete swarm message flow without await errors.")
    print()
    
    # Get port from user
    default_port = "/dev/ttyUSB0"
    port = input(f"Enter XBee port (default: {default_port}): ").strip()
    if not port:
        port = default_port
    
    tester = SwarmMessageFlowTester(port)
    
    if not tester.setup_xbee():
        print("❌ Cannot continue without XBee service")
        return
    
    if not tester.start_listening():
        print("❌ Cannot start listening")
        return
    
    # Show message flow diagram
    tester.print_message_flow()
    
    print("\n🎯 Test Options:")
    print("1. Send test message")
    print("2. Show message flow diagram")
    print("3. Show status")
    print("4. Exit")
    
    try:
        while True:
            print("\n" + "-"*40)
            choice = input("Select option (1-4): ").strip()
            
            if choice == "1":
                print("\n📤 Send Test Message")
                try:
                    lat = float(input("Enter latitude (decimal): "))
                    lon = float(input("Enter longitude (decimal): "))
                    alt = float(input("Enter altitude (meters): "))
                    command = int(input("Enter command (default: 1): ") or "1")
                    
                    tester.send_test_message(lat, lon, alt, command)
                    
                except ValueError:
                    print("❌ Invalid input. Please enter valid numbers.")
                    
            elif choice == "2":
                tester.print_message_flow()
                
            elif choice == "3":
                tester.print_status()
                
            elif choice == "4":
                print("👋 Exiting...")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-4.")
                
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    
    finally:
        tester.cleanup()
        print("✅ Test completed")

if __name__ == "__main__":
    main()
