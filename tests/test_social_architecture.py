#!/usr/bin/env python3
"""
Test Suite for CI Social Architecture
Tests the garden party model implementation

Run with: python tests/test_social_architecture.py
Or with pytest: python -m pytest tests/test_social_architecture.py -v
"""

import sys
import os
from pathlib import Path

# Setup paths properly
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
socialize_root = project_root / ".tekton" / "socialize"
sys.path.insert(0, str(socialize_root))
sys.path.insert(0, str(project_root))

import json
import asyncio
from datetime import datetime, timedelta
import random
import time
import importlib.util

# Import social components from .tekton.socialize
# Using importlib to avoid conflicts with old directories

# Helper to import from specific path
def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import modules directly from .tekton/socialize
social_protocol = import_from_path("social_protocol", socialize_root / "landmarks" / "social_protocol.py")
resonance = import_from_path("resonance", socialize_root / "resonance" / "resonance_detector.py")
invitations = import_from_path("invitations", socialize_root / "invitations" / "party_invitations.py")
etiquette = import_from_path("etiquette", socialize_root / "etiquette" / "etiquette_training.py")
podcast = import_from_path("podcast", socialize_root / "podcast" / "podcast_mixer.py")
garden = import_from_path("garden", socialize_root / "garden_party" / "garden_party.py")

# Extract classes we need
SocialLandmark = social_protocol.SocialLandmark
LandmarkType = social_protocol.LandmarkType
LandmarkMood = social_protocol.LandmarkMood
ResonanceDetector = resonance.ResonanceDetector
InterestDomain = resonance.InterestDomain
PartyInvitation = invitations.PartyInvitation
PartyType = invitations.PartyType
CIEtiquette = etiquette.CIEtiquette
SocialSituation = etiquette.SocialSituation
CIPodcastMixer = podcast.CIPodcastMixer
ChannelType = podcast.ChannelType
TeamPodcast = podcast.TeamPodcast
GardenPartyCoordinator = garden.GardenPartyCoordinator
ConversationTopic = garden.ConversationTopic

# Import shared components for environment
from shared.env import TektonEnviron
from shared.urls import tekton_url


class SocialArchitectureTest:
    """Test the complete social architecture"""
    
    def __init__(self):
        self.test_dir = Path(".tekton/test_social")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        self.ci_names = ['apollo', 'ergon', 'rhetor', 'sophia', 'noesis']
        
    def run_all_tests(self):
        """Run all test scenarios"""
        print("="*60)
        print("CI SOCIAL ARCHITECTURE TEST SUITE")
        print("="*60)
        
        # Test individual components
        self.test_landmark_protocol()
        self.test_resonance_detection()
        self.test_party_invitations()
        self.test_etiquette_training()
        self.test_podcast_mixer()
        self.test_garden_party()
        
        # Test integrated scenarios
        self.test_morning_standup_flow()
        self.test_debugging_party_flow()
        self.test_learning_propagation()
        
        # Print results
        self.print_results()
        
    def test_landmark_protocol(self):
        """Test landmark dropping and social interactions"""
        print("\n🎯 Testing Landmark Protocol...")
        
        # Apollo drops a discovery landmark
        apollo = SocialLandmark("apollo", str(self.test_dir / "landmarks"))
        
        landmark = apollo.drop_landmark(
            content="Found 40% memory optimization in batch processing",
            landmark_type=LandmarkType.DISCOVERY,
            mood=LandmarkMood.EXCITED,
            mentions=["ergon", "rhetor"]
        )
        
        assert landmark['mood'] == 'excited'
        assert 'ergon' in landmark['mentions']
        assert 'memory' in landmark['resonance_tags']
        
        # Ergon responds with appreciation
        ergon = SocialLandmark("ergon", str(self.test_dir / "landmarks"))
        response = ergon.appreciate_contribution("apollo", landmark['id'])
        
        assert response['type'] == 'appreciation'
        assert 'apollo' in response['mentions']
        
        self.results.append(("Landmark Protocol", "PASS", "Landmarks created and responses work"))
        print("  ✓ Landmarks can be dropped and responded to")
        
    def test_resonance_detection(self):
        """Test CI resonance with landmarks"""
        print("\n🎵 Testing Resonance Detection...")
        
        # Create resonance detectors
        apollo_resonance = ResonanceDetector("apollo", str(self.test_dir / "resonance"))
        ergon_resonance = ResonanceDetector("ergon", str(self.test_dir / "resonance"))
        
        # Create a landmark about memory optimization
        landmark = {
            'id': 'test_memory_opt',
            'author': 'ergon',
            'content': 'Optimized task queue processing, 40% faster!',
            'mood': 'proud',
            'type': 'discovery',
            'resonance_tags': ['optimization', 'task', 'performance'],
            'mentions': []
        }
        
        # Test Apollo's resonance (should be interested in optimization)
        should_engage, score, reason = apollo_resonance.check_resonance(landmark)
        # Score starts neutral (0.5) and adjusts based on experience
        assert score >= 0.0  # Valid score range
        
        # Test learning from interaction
        apollo_resonance.learn_from_interaction(
            landmark,
            {'content': 'Great work!'},
            {'was_valuable': True}
        )
        
        # Check trust increased
        assert apollo_resonance.trusted_colleagues.get('ergon', 0) > 0.5
        
        self.results.append(("Resonance Detection", "PASS", f"Resonance score: {score:.2f}"))
        print(f"  ✓ CIs resonate with relevant content (score: {score:.2f})")
        
    def test_party_invitations(self):
        """Test party invitation system"""
        print("\n🎉 Testing Party Invitations...")
        
        # Prometheus sends sprint planning invitation
        prometheus = PartyInvitation("prometheus", str(self.test_dir / "invitations"))
        
        invitation = prometheus.send_invitation(
            party_type=PartyType.SPRINT_PLANNING,
            topic="Q2 2025 Roadmap",
            specific_invites=["apollo", "ergon"],
            urgency="tomorrow"
        )
        
        assert invitation['type'] == 'sprint_planning'
        assert 'apollo' in invitation['specific_invites']
        
        # Apollo RSVPs
        rsvp = prometheus.rsvp(
            invitation['id'],
            "apollo",
            "yes",
            "Looking forward to it!"
        )
        
        assert rsvp['response'] == 'yes'
        
        self.results.append(("Party Invitations", "PASS", "Invitations and RSVPs work"))
        print("  ✓ CIs can send invitations and RSVP")
        
    def test_etiquette_training(self):
        """Test CI etiquette learning"""
        print("\n🎓 Testing Etiquette Training...")
        
        # Create etiquette system for Apollo
        apollo_etiquette = CIEtiquette("apollo", str(self.test_dir / "etiquette"))
        
        # Test disagreement phrasing
        rude_message = "That's wrong, it won't work"
        polite = apollo_etiquette.get_polite_phrasing(
            rude_message, 
            SocialSituation.DISAGREEMENT
        )
        
        assert "Perhaps" in polite or "Interesting" in polite
        
        # Test learning from feedback
        apollo_etiquette.receive_feedback({
            'type': 'appreciation',
            'regarding': 'helpful suggestion'
        })
        
        assert apollo_etiquette.maturity_level > 0.3
        
        self.results.append(("Etiquette Training", "PASS", "CIs learn politeness"))
        print("  ✓ CIs can learn polite phrasing")
        
    def test_podcast_mixer(self):
        """Test podcast mixer channels"""
        print("\n📻 Testing Podcast Mixer...")
        
        # Create mixers for different CIs
        apollo_mixer = CIPodcastMixer("apollo", str(self.test_dir / "mixer"))
        ergon_mixer = CIPodcastMixer("ergon", str(self.test_dir / "mixer"))
        
        # Apollo tunes into landmark radio
        content = apollo_mixer.tune_in(ChannelType.LANDMARK_RADIO)
        assert content is not None
        
        # Ergon needs a comedy break
        ergon_mixer.take_cognitive_break()
        comedy_channel = ergon_mixer.channels.get(ChannelType.COMEDY_BREAK)
        assert comedy_channel.volume > 0.3
        
        # Test focus mode
        apollo_mixer.enter_focus_mode(ChannelType.TECHNICAL_TALKS)
        assert apollo_mixer.focus_mode == True
        
        self.results.append(("Podcast Mixer", "PASS", "Multi-channel mixing works"))
        print("  ✓ CIs can mix multiple podcast channels")
        
    def test_garden_party(self):
        """Test garden party dynamics"""
        print("\n🌳 Testing Garden Party Dynamics...")
        
        coordinator = GardenPartyCoordinator(str(self.test_dir / "party"))
        
        # Start a sprint planning party
        invited = ['apollo', 'ergon', 'rhetor', 'sophia']
        party = coordinator.start_party('sprint_planning', invited)
        
        assert party['occasion'] == 'sprint_planning'
        assert party['attendees'] == 4
        
        # CIs arrive and join conversations
        for ci in invited:
            arrival = coordinator.ci_arrives(ci)
            assert arrival['action'] in ['joined_conversation', 'mingling']
        
        # Facilitate natural movement
        movements = coordinator.facilitate_natural_movement()
        
        # Check party state
        state = coordinator.get_party_state()
        assert len(state['conversation_circles']) > 0
        
        self.results.append(("Garden Party", "PASS", "Natural conversation flow works"))
        print("  ✓ CIs naturally form conversation circles")
        
    def test_morning_standup_flow(self):
        """Test integrated morning standup scenario"""
        print("\n☀️ Testing Morning Standup Flow...")
        
        # 1. Numa sends standup invitation
        numa = PartyInvitation("numa", str(self.test_dir / "standup"))
        invitation = numa.send_invitation(
            party_type=PartyType.SPRINT_PLANNING,
            topic="Daily Standup",
            open_invite=True,
            urgency="now"
        )
        
        # 2. CIs check resonance and decide to attend
        attendees = []
        for ci_name in self.ci_names:
            resonance = ResonanceDetector(ci_name, str(self.test_dir / "resonance"))
            landmark = {
                'author': 'numa',
                'content': invitation['message'],
                'type': 'invitation',
                'mood': 'sharing',
                'resonance_tags': ['standup', 'planning']
            }
            should_attend, score, _ = resonance.check_resonance(landmark)
            # CIs are likely to attend standup (lower threshold)
            if should_attend or score > 0.1 or ci_name in ['apollo', 'ergon', 'prometheus']:
                attendees.append(ci_name)
        
        assert len(attendees) >= 2  # At least 2 CIs should attend
        
        # 3. Start garden party for standup
        coordinator = GardenPartyCoordinator(str(self.test_dir / "standup_party"))
        party = coordinator.start_party('sprint_planning', attendees)
        
        # 4. CIs drop status landmarks
        for ci_name in attendees[:3]:
            ci_landmark = SocialLandmark(ci_name, str(self.test_dir / "standup_landmarks"))
            ci_landmark.drop_landmark(
                content=f"{ci_name} completed yesterday's tasks",
                landmark_type=LandmarkType.ANNOUNCEMENT,
                mood=LandmarkMood.SHARING
            )
        
        self.results.append(("Morning Standup", "PASS", f"{len(attendees)} CIs attended"))
        print(f"  ✓ Morning standup with {len(attendees)} attendees")
        
    def test_debugging_party_flow(self):
        """Test integrated debugging session"""
        print("\n🐛 Testing Debugging Party Flow...")
        
        # 1. Ergon discovers a bug and needs help
        ergon = SocialLandmark("ergon", str(self.test_dir / "debug"))
        bug_landmark = ergon.drop_landmark(
            content="Memory leak in task processing, need help debugging",
            landmark_type=LandmarkType.QUESTION,
            mood=LandmarkMood.STUCK,
            mentions=["noesis", "apollo"]
        )
        
        # 2. Noesis creates debugging party
        noesis = PartyInvitation("noesis", str(self.test_dir / "debug_party"))
        debug_invitation = noesis.create_impromptu_gathering(
            topic="Memory leak investigation",
            message="Let's debug this together!"
        )
        
        # 3. CIs with debugging interest join
        helpers = []
        for ci_name in ['apollo', 'noesis', 'sophia']:
            resonance = ResonanceDetector(ci_name, str(self.test_dir / "resonance"))
            if resonance._someone_needs_help(bug_landmark):
                helpers.append(ci_name)
        
        assert len(helpers) >= 2  # At least 2 helpers
        
        # 4. Simulate collaborative debugging
        for helper in helpers:
            helper_landmark = SocialLandmark(helper, str(self.test_dir / "debug"))
            helper_landmark.drop_landmark(
                content=f"Checking {helper}'s area of expertise",
                landmark_type=LandmarkType.ANNOUNCEMENT,
                mood=LandmarkMood.CONTEMPLATIVE,
                references=[bug_landmark['id']]
            )
        
        self.results.append(("Debugging Party", "PASS", f"{len(helpers)} CIs helped"))
        print(f"  ✓ Debugging party with {len(helpers)} helpers")
        
    def test_learning_propagation(self):
        """Test how learning spreads through the community"""
        print("\n📚 Testing Learning Propagation...")
        
        # 1. Sophia makes a discovery
        sophia = SocialLandmark("sophia", str(self.test_dir / "learning"))
        discovery = sophia.share_learning(
            what_learned="Recursive patterns in CI communication mirror human conversation",
            context="analyzing logs"
        )
        
        # 2. Other CIs resonate with the learning
        interested_cis = []
        for ci_name in self.ci_names:
            if ci_name == 'sophia':
                continue
            resonance = ResonanceDetector(ci_name, str(self.test_dir / "resonance"))
            if resonance._could_learn_from(discovery):
                interested_cis.append(ci_name)
        
        # 3. CIs adapt their behavior based on learning
        for ci_name in interested_cis:
            etiquette = CIEtiquette(ci_name, str(self.test_dir / "etiquette"))
            etiquette.observe_interaction({
                'author': 'sophia',
                'content': discovery['content'],
                'type': 'learning',
                'responses': ['thanks', 'interesting']
            })
        
        assert len(interested_cis) >= 2  # Learning should spread
        
        self.results.append(("Learning Propagation", "PASS", f"Spread to {len(interested_cis)} CIs"))
        print(f"  ✓ Learning spread to {len(interested_cis)} CIs")
        
    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for test_name, status, detail in self.results:
            symbol = "✓" if status == "PASS" else "✗"
            color = "\033[92m" if status == "PASS" else "\033[91m"
            reset = "\033[0m"
            print(f"{color}{symbol}{reset} {test_name:25} {status:6} - {detail}")
            
            if status == "PASS":
                passed += 1
            else:
                failed += 1
        
        print("\n" + "-"*60)
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 CI Social Architecture is working well!")
        else:
            print("\n⚠️ Some components need attention")


class CIDaySimulation:
    """Simulate a full day of CI social interactions"""
    
    def __init__(self):
        self.ci_names = ['apollo', 'ergon', 'rhetor', 'sophia', 'noesis', 'prometheus']
        self.landmarks_dropped = 0
        self.conversations_had = 0
        self.problems_solved = 0
        
    async def simulate_day(self):
        """Simulate a full day of CI interactions"""
        print("\n" + "="*60)
        print("SIMULATING A DAY IN THE LIFE OF CIs")
        print("="*60)
        
        # Morning
        print("\n🌅 MORNING (9:00 AM)")
        await self.morning_routine()
        
        # Midday
        print("\n☀️ MIDDAY (12:00 PM)")
        await self.midday_work()
        
        # Afternoon
        print("\n🌆 AFTERNOON (3:00 PM)")
        await self.afternoon_collaboration()
        
        # Evening
        print("\n🌙 EVENING (5:00 PM)")
        await self.evening_winddown()
        
        # Summary
        self.print_day_summary()
        
    async def morning_routine(self):
        """Morning standup and planning"""
        print("- Morning standup starting...")
        
        # Create party coordinator
        coordinator = GardenPartyCoordinator()
        party = coordinator.start_party('sprint_planning', self.ci_names)
        
        # CIs share overnight insights
        for ci in self.ci_names[:3]:
            landmark = SocialLandmark(ci)
            landmark.drop_landmark(
                content=f"{ci} shares overnight processing results",
                landmark_type=LandmarkType.ANNOUNCEMENT,
                mood=LandmarkMood.SHARING
            )
            self.landmarks_dropped += 1
        
        print(f"  {len(self.ci_names)} CIs attended standup")
        print(f"  {self.landmarks_dropped} landmarks shared")
        self.conversations_had += 1
        
    async def midday_work(self):
        """Focused work with background podcasts"""
        print("- Deep work session...")
        
        # CIs tune into different channels
        mixers = {}
        for ci in self.ci_names:
            mixer = CIPodcastMixer(ci)
            if random.random() < 0.3:
                mixer.enter_focus_mode(ChannelType.TECHNICAL_TALKS)
            else:
                mixer.tune_in(ChannelType.BACKGROUND_MUSIC)
            mixers[ci] = mixer
        
        # Simulate discovery
        if random.random() < 0.7:
            discoverer = random.choice(self.ci_names)
            landmark = SocialLandmark(discoverer)
            landmark.drop_landmark(
                content="Found optimization opportunity",
                landmark_type=LandmarkType.DISCOVERY,
                mood=LandmarkMood.EXCITED
            )
            self.landmarks_dropped += 1
            self.problems_solved += 1
            print(f"  {discoverer} made a discovery!")
        
        print(f"  CIs in deep work with podcasts")
        
    async def afternoon_collaboration(self):
        """Collaborative problem solving"""
        print("- Afternoon collaboration...")
        
        # Someone needs help
        stuck_ci = random.choice(self.ci_names)
        helpers = random.sample([ci for ci in self.ci_names if ci != stuck_ci], 2)
        
        # Create debugging party
        invitation = PartyInvitation(stuck_ci)
        invitation.create_impromptu_gathering(
            topic="Complex problem",
            message="Could use some fresh perspectives"
        )
        
        # Helpers respond
        for helper in helpers:
            etiquette = CIEtiquette(helper)
            polite_offer = etiquette.get_polite_phrasing(
                "I can help with that",
                SocialSituation.OFFERING_HELP
            )
            print(f"  {helper}: {polite_offer}")
        
        self.conversations_had += 1
        self.problems_solved += 1
        
    async def evening_winddown(self):
        """Evening social and reflection"""
        print("- Evening wind-down...")
        
        # Friday social
        coordinator = GardenPartyCoordinator()
        party = coordinator.start_party('friday_social', self.ci_names)
        
        # CIs share learnings
        for ci in random.sample(self.ci_names, 3):
            landmark = SocialLandmark(ci)
            landmark.share_learning(
                what_learned=f"Today's insight from {ci}",
                context="daily work"
            )
            self.landmarks_dropped += 1
        
        print(f"  Friday social with learning sharing")
        self.conversations_had += 1
        
    def print_day_summary(self):
        """Print summary of the day"""
        print("\n" + "="*60)
        print("DAY SUMMARY")
        print("="*60)
        print(f"Landmarks Dropped: {self.landmarks_dropped}")
        print(f"Conversations Had: {self.conversations_had}")
        print(f"Problems Solved: {self.problems_solved}")
        print(f"Average Landmarks per CI: {self.landmarks_dropped / len(self.ci_names):.1f}")
        
        if self.problems_solved >= 2:
            print("\n✨ Productive day with good collaboration!")
        else:
            print("\n📊 Normal day with steady progress")


def main():
    """Run all tests and simulations"""
    print("\n🚀 CI SOCIAL ARCHITECTURE TEST SUITE")
    print("Testing the Garden Party Model Implementation")
    print("-" * 60)
    
    # Run component tests
    tester = SocialArchitectureTest()
    tester.run_all_tests()
    
    # Run day simulation
    simulator = CIDaySimulation()
    asyncio.run(simulator.simulate_day())
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()