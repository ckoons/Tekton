#!/bin/bash
#
# Test script for FAISS vector search with NumPy 2.x
#

echo "Testing FAISS with NumPy 2.x..."
python faiss_test.py

if [ $? -eq 0 ]; then
    echo -e "\n✅ FAISS test passed"
    echo -e "\nTesting simple embedding system..."
    python simple_embedding.py
    
    if [ $? -eq 0 ]; then
        echo -e "\n✅ Simple embedding test passed"
        echo -e "\nTesting vector store..."
        python vector_store.py
        
        if [ $? -eq 0 ]; then
            echo -e "\n✅ Vector store test passed"
            echo -e "\nTesting memory adapter..."
            python engram_memory_adapter.py
            
            if [ $? -eq 0 ]; then
                echo -e "\n✅ Memory adapter test passed"
                echo -e "\n🎉 All tests passed. You can now run Engram with FAISS:"
                echo -e "   ./engram_with_faiss_simple.py --model llama3:8b"
            else
                echo -e "\n❌ Memory adapter test failed"
            fi
        else
            echo -e "\n❌ Vector store test failed"
        fi
    else
        echo -e "\n❌ Simple embedding test failed"
    fi
else
    echo -e "\n❌ FAISS test failed"
fi