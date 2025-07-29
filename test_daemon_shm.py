#!/usr/bin/env python3
from multiprocessing import shared_memory

# Test connecting to the EXACT shared memory the daemon created
shm_name = 'tekton_ci_registry_5f58f9e9'

print(f'Testing connection to: {shm_name}')
try:
    shm = shared_memory.SharedMemory(name=shm_name)
    print(f'SUCCESS: Connected to {shm_name}!')
    print(f'Size: {len(shm.buf)} bytes')
    
    # Read first 200 bytes to see if there is data
    data = bytes(shm.buf[:200])
    non_zero_count = sum(1 for b in data if b != 0)
    print(f'Non-zero bytes in first 200: {non_zero_count}')
    
    if non_zero_count > 0:
        print('First non-zero bytes:', data[:50])
    
    shm.close()
    
except FileNotFoundError as e:
    print(f'FAILED: {e}')
    print('This confirms daemon shared memory is not accessible to clients')