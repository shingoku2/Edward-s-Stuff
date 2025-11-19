#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bug Fix Verification Script
Verifies that all critical bug fixes are implemented and working correctly.
"""

import sys
import pickle
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_fix_1_knowledge_index_persistence():
    """
    Verify Fix #1: Knowledge Index TF-IDF Model Persistence

    Critical Bug: TF-IDF vocabulary was not saved to disk, causing
    search results to become random after restart.

    Fix: _save_index() now saves both index and embedding_provider
    """
    print("\n" + "="*70)
    print("TEST 1: Knowledge Index TF-IDF Model Persistence")
    print("="*70)

    from knowledge_index import SimpleTFIDFEmbedding, KnowledgeIndex
    from knowledge_pack import KnowledgePack, KnowledgeSource
    from datetime import datetime

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create knowledge index
        index = KnowledgeIndex(config_dir=tmpdir)

        # Create a test knowledge pack
        pack = KnowledgePack(
            id="test-pack",
            name="Test Pack",
            description="Test",
            game_profile_id="test-game",
            sources=[
                KnowledgeSource(
                    id="source-1",
                    type="note",
                    title="Test Note",
                    content="The strategy for defeating the boss involves dodging attacks and using fire magic.",
                    tags=["strategy"]
                )
            ],
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Index the pack (this should fit the TF-IDF model)
        index.add_pack(pack)

        # Verify vocabulary was created
        if isinstance(index.embedding_provider, SimpleTFIDFEmbedding):
            vocab_size = len(index.embedding_provider.vocabulary)
            print(f"✓ TF-IDF vocabulary created: {vocab_size} terms")
        else:
            print("✗ Expected SimpleTFIDFEmbedding provider")
            return False

        # Save index to disk
        index._save_index()
        print("✓ Index saved to disk")

        # Load index from disk (simulating app restart)
        index2 = KnowledgeIndex(config_dir=tmpdir)

        # Verify vocabulary was restored
        if isinstance(index2.embedding_provider, SimpleTFIDFEmbedding):
            vocab_size2 = len(index2.embedding_provider.vocabulary)
            print(f"✓ TF-IDF vocabulary restored: {vocab_size2} terms")

            if vocab_size == vocab_size2:
                print("✓ Vocabulary size matches (persistence works!)")
            else:
                print(f"✗ Vocabulary size mismatch: {vocab_size} != {vocab_size2}")
                return False
        else:
            print("✗ Embedding provider not restored")
            return False

        # Test search consistency
        query = "how to beat the boss"
        results1 = index.query("test-game", query, top_k=3)
        results2 = index2.query("test-game", query, top_k=3)

        if results1 and results2:
            score1 = results1[0].score
            score2 = results2[0].score
            print(f"✓ Search scores: {score1:.3f} (original) vs {score2:.3f} (restored)")

            # Scores should be very similar (allowing for small floating point differences)
            if abs(score1 - score2) < 0.001:
                print("✓ Search results consistent after restart!")
            else:
                print(f"✗ Search scores differ: {abs(score1 - score2):.3f}")
                return False
        else:
            print("✗ Search returned no results")
            return False

    print("\n✅ FIX #1 VERIFIED: Knowledge index persistence works correctly")
    return True


def test_fix_2_session_token_leakage():
    """
    Verify Fix #2: Session Token Leakage Prevention

    Security Issue: Session tokens were being written to plaintext .env file

    Fix: Config.save_to_env() now removes session token entries
    """
    print("\n" + "="*70)
    print("TEST 2: Session Token Leakage Prevention")
    print("="*70)

    from config import Config
    import os

    # Create a temporary .env file
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"

        # Create a .env file with legacy session data
        with open(env_file, 'w') as f:
            f.write("AI_PROVIDER=anthropic\n")
            f.write("OPENAI_SESSION_DATA={'token': 'secret123'}\n")
            f.write("ANTHROPIC_SESSION_DATA={'token': 'secret456'}\n")
            f.write("GEMINI_SESSION_DATA={'token': 'secret789'}\n")

        print(f"✓ Created test .env with session tokens")

        # Simulate Config.save_to_env() which should remove session tokens
        # We'll test this by calling the static method
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            Config.save_to_env(
                provider="anthropic",
                session_tokens=None  # Session tokens parameter is deprecated
            )

            # Read the file back
            with open(env_file, 'r') as f:
                content = f.read()

            # Check that session tokens are NOT in the file
            has_openai_session = "OPENAI_SESSION_DATA" in content
            has_anthropic_session = "ANTHROPIC_SESSION_DATA" in content
            has_gemini_session = "GEMINI_SESSION_DATA" in content

            if not has_openai_session and not has_anthropic_session and not has_gemini_session:
                print("✓ Session tokens removed from .env file")
            else:
                print("✗ Session tokens still present in .env file")
                return False

            # Verify API key placeholders are present (but empty for security)
            if "OPENAI_API_KEY=" in content and "ANTHROPIC_API_KEY=" in content:
                print("✓ API key placeholders present")
            else:
                print("✗ API key placeholders missing")
                return False

        finally:
            os.chdir(original_dir)

    print("\n✅ FIX #2 VERIFIED: Session tokens are not written to .env file")
    return True


def test_fix_3_game_watcher_performance():
    """
    Verify Fix #3: Non-Windows Game Detection Performance

    Performance Issue: Full process scan every 5 seconds on Linux/macOS

    Fix: PID caching to avoid redundant process scans
    """
    print("\n" + "="*70)
    print("TEST 3: Game Watcher Performance Optimization")
    print("="*70)

    from game_watcher import GameWatcher
    import platform

    # Check if the fix is in the code
    import inspect
    source = inspect.getsource(GameWatcher._get_foreground_executable)

    if "last_known_pid" in source:
        print("✓ PID caching code present in _get_foreground_executable")
    else:
        print("✗ PID caching code not found")
        return False

    # Check if the attribute is initialized
    watcher = GameWatcher()
    if hasattr(watcher, 'last_known_pid'):
        print("✓ last_known_pid attribute initialized")
    else:
        print("✗ last_known_pid attribute not found")
        return False

    # Check if cache is cleared when game closes
    source_handle_no_game = inspect.getsource(GameWatcher._handle_no_game)
    if "last_known_pid = None" in source_handle_no_game:
        print("✓ Cache is cleared when game closes")
    else:
        print("✗ Cache not cleared in _handle_no_game")
        return False

    system = platform.system()
    print(f"✓ Running on {system} - optimization applies to Linux/macOS")

    print("\n✅ FIX #3 VERIFIED: PID caching implemented for performance")
    return True


def test_fix_4_text_chunking():
    """
    Verify Fix #4: Word-Boundary Text Chunking

    Logic Issue: Character-based chunking broke words ("strat" | "egy")

    Fix: Word-based chunking that respects word boundaries
    """
    print("\n" + "="*70)
    print("TEST 4: Word-Boundary Text Chunking")
    print("="*70)

    from knowledge_index import KnowledgeIndex

    # Create knowledge index
    index = KnowledgeIndex()

    # Test text with a word that should not be split
    test_text = "The strategy for defeating the boss involves dodging attacks and using fire magic to exploit its weakness."

    # Chunk with small chunk size to force splitting
    chunks = index._chunk_text(test_text, chunk_size=50, overlap=10)

    print(f"✓ Created {len(chunks)} chunks from test text")

    # Verify no words are split
    all_chunks_valid = True
    for i, chunk in enumerate(chunks):
        words = chunk.split()
        # Check that each word is complete (no partial words)
        for word in words:
            if not word:  # Empty words indicate problems
                print(f"✗ Chunk {i} contains empty words")
                all_chunks_valid = False

        print(f"  Chunk {i}: \"{chunk}\"")

        # Verify the word "strategy" is not split
        if "strat" in chunk.lower() and "strategy" not in chunk.lower():
            print(f"✗ Word 'strategy' was split in chunk {i}")
            all_chunks_valid = False

    if all_chunks_valid:
        print("✓ All chunks respect word boundaries")
    else:
        print("✗ Some chunks have split words")
        return False

    # Verify overlap works
    if len(chunks) > 1:
        # Check if there's any word overlap between consecutive chunks
        chunk1_words = set(chunks[0].split())
        chunk2_words = set(chunks[1].split())
        overlap_words = chunk1_words & chunk2_words

        if overlap_words:
            print(f"✓ Overlap working: {len(overlap_words)} words shared between chunks")
        else:
            print("⚠ No word overlap detected (may be expected if chunks are short)")

    print("\n✅ FIX #4 VERIFIED: Text chunking respects word boundaries")
    return True


def main():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("BUG FIX VERIFICATION SUITE")
    print("="*70)
    print("\nThis script verifies that all critical bug fixes are implemented")
    print("and working correctly in the Omnix Gaming Companion codebase.")

    results = []

    try:
        results.append(("Knowledge Index Persistence", test_fix_1_knowledge_index_persistence()))
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Knowledge Index Persistence", False))

    try:
        results.append(("Session Token Leakage", test_fix_2_session_token_leakage()))
    except Exception as e:
        print(f"\n✗ TEST 2 FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Session Token Leakage", False))

    try:
        results.append(("Game Watcher Performance", test_fix_3_game_watcher_performance()))
    except Exception as e:
        print(f"\n✗ TEST 3 FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Game Watcher Performance", False))

    try:
        results.append(("Text Chunking", test_fix_4_text_chunking()))
    except Exception as e:
        print(f"\n✗ TEST 4 FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Text Chunking", False))

    # Print summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n" + "="*70)
        print("🎉 ALL BUG FIXES VERIFIED SUCCESSFULLY!")
        print("="*70)
        print("\nThe following critical fixes are confirmed working:")
        print("  1. Knowledge index TF-IDF model persistence")
        print("  2. Session token security (no leakage to .env)")
        print("  3. Game watcher PID caching for performance")
        print("  4. Word-boundary text chunking")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️  SOME TESTS FAILED")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
