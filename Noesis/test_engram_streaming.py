#!/usr/bin/env python3
"""
Test script for Engram streaming integration
"""

import asyncio
import sys
import os

# Add Noesis to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_streaming_integration():
    """Test the Engram streaming integration"""
    print("🧠 Testing Noesis Engram Streaming Integration")
    print("=" * 50)
    
    try:
        # Import and initialize components
        from noesis.core.integration.engram_stream import EngramDataStreamer, NoesisMemoryAnalyzer
        from noesis.core.integration.stream_manager import TheoreticalStreamManager
        
        print("✅ Successfully imported streaming components")
        
        # Test basic streamer initialization
        print("\n📡 Testing Engram Data Streamer...")
        streamer = EngramDataStreamer(poll_interval=2.0)  # Faster polling for testing
        print(f"✅ Streamer initialized with URL: {streamer.engram_url}")
        
        # Test memory analyzer
        print("\n🧮 Testing Memory Analyzer...")
        analyzer = NoesisMemoryAnalyzer()
        print("✅ Memory analyzer initialized")
        
        # Connect analyzer to streamer
        streamer.add_listener(analyzer)
        print("✅ Analyzer connected to streamer")
        
        # Test stream manager
        print("\n⚙️ Testing Stream Manager...")
        # Import Tekton URL utilities for proper URL construction
        import sys
        import os
        tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if tekton_root not in sys.path:
            sys.path.append(tekton_root)
        from shared.urls import engram_url
        
        stream_manager = TheoreticalStreamManager()
        await stream_manager.initialize({
            "engram": {
                "poll_interval": 2.0,
                "url": engram_url()  # Use Tekton URL builder for Engram
            }
        })
        print("✅ Stream manager initialized")
        
        # Test streaming for a short duration
        print("\n🔄 Testing streaming (10 seconds)...")
        await stream_manager.start_streaming()
        print("✅ Streaming started")
        
        # Let it run for a bit
        await asyncio.sleep(10)
        
        # Get status and results
        status = stream_manager.get_stream_status()
        print(f"\n📊 Stream Status:")
        print(f"   Active: {status['active']}")
        print(f"   Uptime: {status['uptime_minutes']:.1f} minutes")
        print(f"   Engram Streamer: {status['engram_streamer']['active']}")
        print(f"   Memory Analyzer Observations: {status['memory_analyzer']['observations']}")
        print(f"   Memory Analyzer Events: {status['memory_analyzer']['events']}")
        
        # Get theoretical insights
        insights = await stream_manager.get_theoretical_insights()
        print(f"\n🔍 Theoretical Insights:")
        print(f"   Found {len(insights.get('insights', []))} insights")
        for i, insight in enumerate(insights.get('insights', [])[:3]):  # Show first 3
            print(f"   {i+1}. {insight.get('type', 'unknown')}: {insight.get('insight', 'No description')}")
        
        # Get analysis results
        analysis = stream_manager.get_analysis_results()
        print(f"\n📈 Analysis Results:")
        if 'memory_statistics' in analysis:
            stats = analysis['memory_statistics']
            print(f"   Total Observations: {stats.get('total_observations', 0)}")
            print(f"   Vector Dimensionality: {stats.get('vector_dimensionality', 0)}")
            print(f"   Total Events: {stats.get('total_events', 0)}")
        
        # Stop streaming
        print("\n🛑 Stopping streaming...")
        await stream_manager.stop_streaming()
        print("✅ Streaming stopped")
        
        print("\n🎉 All tests completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install numpy scipy scikit-learn httpx")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_component_integration():
    """Test the full Noesis component integration"""
    print("\n🏗️ Testing Noesis Component Integration")
    print("=" * 50)
    
    try:
        from noesis.core.noesis_component import NoesisComponent
        
        # Initialize component
        print("🔧 Initializing Noesis component...")
        component = NoesisComponent()
        await component.init()
        print("✅ Component initialized")
        
        # Test capabilities
        capabilities = component.get_capabilities()
        print(f"\n📋 Component Capabilities ({len(capabilities)}):")
        for cap in capabilities:
            print(f"   • {cap}")
        
        # Test metadata
        metadata = component.get_metadata()
        print(f"\n📝 Component Metadata:")
        print(f"   Type: {metadata.get('type')}")
        print(f"   Description: {metadata.get('description')}")
        
        if 'components' in metadata:
            print(f"   Component Status:")
            for name, status in metadata['components'].items():
                print(f"     {name}: {'✅' if status else '❌'}")
        
        # Test streaming capabilities if available
        if component.stream_manager:
            print("\n🔄 Testing component streaming...")
            
            # Get streaming status
            status = await component.get_stream_status()
            print(f"   Streaming Active: {status.get('active', False)}")
            
            # Start streaming
            success = await component.start_streaming()
            print(f"   Start Streaming: {'✅' if success else '❌'}")
            
            if success:
                # Wait a bit for data
                await asyncio.sleep(5)
                
                # Get insights
                insights = await component.get_theoretical_insights()
                print(f"   Insights Generated: {len(insights.get('insights', []))}")
                
                # Stop streaming
                stop_success = await component.stop_streaming()
                print(f"   Stop Streaming: {'✅' if stop_success else '❌'}")
        
        # Cleanup
        await component.shutdown()
        print("✅ Component shut down cleanly")
        
        print("\n🎉 Component integration test completed!")
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Run all tests"""
    print("🧪 Noesis Engram Streaming Integration Tests")
    print("=" * 60)
    
    # Test 1: Basic streaming integration
    success1 = await test_streaming_integration()
    
    # Test 2: Component integration
    success2 = await test_component_integration()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Streaming Integration: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Component Integration: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎊 All tests passed! Engram streaming integration is working.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)